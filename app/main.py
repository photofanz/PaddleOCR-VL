"""
FastAPI Main Application
Provides all API endpoints
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import os
import uuid
import time
import logging
from pathlib import Path
from PIL import Image
import io

from . import __version__, __description__
from .models import (
    UploadResponse, OCRRequest, OCRResponse,
    GeminiRequest, GeminiResponse,
    GenerateMarkdownRequest, GenerateMarkdownResponse,
    StatusResponse, MetadataFields
)
from .services_simple import SimpleOCRService
from .gemini_service import get_gemini_service
from .utils import (
    convert_pdf_to_images,
    validate_file_type,
    clean_text,
    reconstruct_layout_for_txt
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="PaddleOCR-VL Web Application",
    description=__description__,
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定目錄
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
TEMP_DIR = Path(os.getenv("TEMP_DIR", "./temp"))
STATIC_DIR = Path("./static")

UPLOAD_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# 掛載靜態檔案
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 儲存處理中的檔案資料
file_data_store = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """主應用頁面"""
    app_html = STATIC_DIR / "app.html"
    if app_html.exists():
        async with aiofiles.open(app_html, mode='r', encoding='utf-8') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(
            content="<h1>PaddleOCR-VL Web Application</h1><p>請先設置前端檔案</p>",
            status_code=200
        )


@app.get("/guide", response_class=HTMLResponse)
async def guide():
    """部署指南頁面"""
    guide_html = STATIC_DIR / "guide.html"
    if guide_html.exists():
        async with aiofiles.open(guide_html, mode='r', encoding='utf-8') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(
            content="<h1>部署指南</h1><p>指南頁面尚未設置</p>",
            status_code=200
        )


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """獲取系統狀態"""
    # 不觸發 OCR 服務初始化，只檢查是否可用
    ocr_available = True  # 假設 OCR 可用，避免每次檢查都初始化
    
    try:
        gemini_service = get_gemini_service()
        gemini_available = gemini_service.is_available()
    except:
        gemini_available = False
    
    return StatusResponse(
        status="running",
        message="系統運行中",
        version=__version__,
        ocr_available=ocr_available,
        gemini_available=gemini_available
    )


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上傳 PDF 或圖像檔案
    """
    try:
        logger.info(f"收到上傳請求: {file.filename}, 類型: {file.content_type}")
        
        # 驗證檔案類型
        if not validate_file_type(file.filename, file.content_type):
            logger.error(f"檔案類型驗證失敗: {file.filename}, {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"不支援的檔案類型: {file.content_type} (檔案: {file.filename})"
            )
        
        # 生成唯一 ID
        file_id = str(uuid.uuid4())
        
        # 讀取檔案內容
        content = await file.read()
        
        # 檢查檔案大小
        max_size = int(os.getenv("MAX_UPLOAD_SIZE", 52428800))  # 50MB
        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"檔案太大（最大 {max_size / 1024 / 1024:.1f}MB）"
            )
        
        # 保存檔案
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        saved_path = UPLOAD_DIR / f"{file_id}.{file_ext}"
        
        async with aiofiles.open(saved_path, 'wb') as f:
            await f.write(content)
        
        # 儲存檔案資訊
        file_data_store[file_id] = {
            "filename": file.filename,
            "file_type": file.content_type,
            "file_path": str(saved_path),
            "upload_time": time.time(),
            "raw_text": None,
            "layout_info": None,
            "processed_text": None
        }
        
        logger.info(f"✓ 檔案上傳成功: {file.filename} (ID: {file_id})")
        
        return UploadResponse(
            success=True,
            file_id=file_id,
            filename=file.filename,
            file_type=file.content_type,
            message="檔案上傳成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"檔案上傳失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")


@app.post("/api/process-ocr", response_model=OCRResponse)
async def process_ocr(request: OCRRequest):
    """
    執行 OCR 辨識
    """
    try:
        file_id = request.file_id
        
        # 檢查檔案是否存在
        if file_id not in file_data_store:
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        file_info = file_data_store[file_id]
        file_path = Path(file_info["file_path"])
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="檔案已被刪除")
        
        start_time = time.time()
        
        # 獲取 OCR 服務（使用 CPU 模式確保穩定性）
        logger.info(f"正在獲取 OCR 服務: 語言={request.language}")
        ocr_service = SimpleOCRService(lang=request.language, use_gpu=False)
        logger.info("✓ OCR 服務已準備就緒")
        
        # 記錄處理開始
        logger.info(f"開始處理檔案: {file_info['filename']} ({file_info['file_type']})")
        
        # 讀取檔案
        async with aiofiles.open(file_path, 'rb') as f:
            file_content = await f.read()
        
        # 根據檔案類型處理
        images = []
        
        if file_info["file_type"] == "application/pdf":
            logger.info(f"處理 PDF 檔案: {file_info['filename']}")
            images = convert_pdf_to_images(file_content)
            logger.info(f"PDF 轉換完成，共 {len(images)} 頁")
        else:
            logger.info(f"處理圖像檔案: {file_info['filename']}")
            image = Image.open(io.BytesIO(file_content)).convert('RGB')
            images = [image]
            logger.info("圖像載入完成")
        
        if not images:
            raise HTTPException(status_code=500, detail="無法從檔案中提取圖像")
        
        logger.info(f"開始 OCR 辨識 ({len(images)} 張圖像)...")
        
        # 執行 OCR
        try:
            logger.info("開始執行 OCR 辨識...")
            raw_text, all_layouts = ocr_service.process_images(images)
            logger.info(f"OCR 辨識完成，辨識出 {len(raw_text)} 個字元")
        except Exception as e:
            logger.error(f"OCR 處理過程中發生錯誤: {str(e)}")
            import traceback
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            # 返回部分結果而不是完全失敗
            raw_text = f"[OCR 處理失敗: {str(e)}]"
            all_layouts = [[] for _ in images]
        
        processing_time = time.time() - start_time
        
        # 儲存結果
        file_data_store[file_id]["raw_text"] = raw_text
        file_data_store[file_id]["layout_info"] = all_layouts
        
        logger.info(f"✓ OCR 辨識完成，耗時 {processing_time:.2f} 秒")
        
        # 將佈局資訊簡化（避免回應過大）
        simplified_layout = []
        for page_idx, page_layout in enumerate(all_layouts[:5]):  # 最多返回 5 頁
            for item in page_layout[:10]:  # 每頁最多返回 10 條
                simplified_layout.append({
                    "page": page_idx,
                    "text": item["text"],
                    "confidence": item["confidence"],
                    "bbox": item.get("bbox", []),
                    "y_position": item.get("y_position", 0),
                    "x_position": item.get("x_position", 0)
                })
        
        return OCRResponse(
            success=True,
            file_id=file_id,
            raw_text=raw_text,
            layout_info=simplified_layout,
            message="OCR 辨識完成",
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR 處理失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR 處理失敗: {str(e)}")


@app.post("/api/enhance-with-gemini", response_model=GeminiResponse)
async def enhance_with_gemini(request: GeminiRequest):
    """
    使用 Gemini 處理文字
    """
    try:
        gemini_service = get_gemini_service()
        
        if not gemini_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Gemini API 不可用，請檢查 API Key 設定"
            )
        
        start_time = time.time()
        
        logger.info(f"使用 Gemini 處理文字 (類型: {request.prompt_type})...")
        
        # 處理文字
        processed_text = gemini_service.process_text(
            text=request.text,
            prompt_type=request.prompt_type,
            custom_prompt=request.custom_prompt,
            system_instruction=request.system_instruction
        )
        
        processing_time = time.time() - start_time
        
        logger.info(f"✓ Gemini 處理完成，耗時 {processing_time:.2f} 秒")
        
        return GeminiResponse(
            success=True,
            processed_text=processed_text,
            message="Gemini 處理完成",
            model_used=gemini_service.model_name,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini 處理失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gemini 處理失敗: {str(e)}")


@app.post("/api/generate-markdown", response_model=GenerateMarkdownResponse)
async def generate_markdown(request: GenerateMarkdownRequest):
    """
    生成 Markdown 檔案（帶或不帶 Metadata）
    """
    try:
        file_id = request.file_id
        
        # 檢查檔案是否存在
        if file_id not in file_data_store:
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        file_info = file_data_store[file_id]
        
        # 構建 Markdown 內容
        markdown_lines = []
        
        # 添加 Metadata（如果啟用）
        if request.include_metadata and request.metadata:
            frontmatter = request.metadata.to_yaml_frontmatter()
            markdown_lines.append(frontmatter)
        
        # 添加主要內容
        markdown_lines.append(request.content)
        
        markdown_content = "\n".join(markdown_lines)
        
        # 構建 TXT 內容（保持佈局）
        layout_info = file_info.get("layout_info", [])
        if layout_info:
            # 合併所有頁面的佈局資訊
            all_layout = []
            for page_layout in layout_info:
                all_layout.extend(page_layout)
            
            txt_content = reconstruct_layout_for_txt(all_layout)
        else:
            # 如果沒有佈局資訊，使用原始文字
            txt_content = file_info.get("raw_text", request.content)
        
        # 保存生成的內容
        file_data_store[file_id]["markdown_content"] = markdown_content
        file_data_store[file_id]["txt_content"] = txt_content
        
        logger.info(f"✓ Markdown 生成完成 (file_id: {file_id})")
        
        return GenerateMarkdownResponse(
            success=True,
            markdown_content=markdown_content,
            txt_content=txt_content,
            message="Markdown 生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Markdown 生成失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失敗: {str(e)}")


@app.get("/api/download/{file_id}/{format}")
async def download_file(file_id: str, format: str, filename: str = None):
    """
    下載檔案（.md 或 .txt）
    """
    try:
        # 檢查檔案是否存在
        if file_id not in file_data_store:
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        file_info = file_data_store[file_id]
        
        # 檢查格式
        if format not in ["md", "txt"]:
            raise HTTPException(status_code=400, detail="不支援的格式")
        
        # 獲取內容
        if format == "md":
            content = file_info.get("markdown_content")
            content_type = "text/markdown"
            default_filename = "document.md"
        else:  # txt
            content = file_info.get("txt_content") or file_info.get("raw_text")
            content_type = "text/plain"
            default_filename = "document.txt"
        
        if not content:
            raise HTTPException(status_code=404, detail=f"尚未生成 {format.upper()} 內容")
        
        # 設定檔名
        if not filename:
            original_name = file_info.get("filename", "document")
            base_name = original_name.rsplit('.', 1)[0]
            filename = f"{base_name}.{format}"
        
        # 保存到臨時檔案
        temp_file = TEMP_DIR / f"{file_id}_{format}.{format}"
        async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        logger.info(f"✓ 準備下載: {filename}")
        
        return FileResponse(
            path=str(temp_file),
            media_type=content_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下載失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下載失敗: {str(e)}")


@app.delete("/api/cleanup/{file_id}")
async def cleanup_file(file_id: str):
    """
    清理檔案（刪除上傳的檔案和臨時檔案）
    """
    try:
        if file_id not in file_data_store:
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        file_info = file_data_store[file_id]
        
        # 刪除上傳的檔案
        file_path = Path(file_info["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        # 刪除臨時檔案
        for format in ["md", "txt"]:
            temp_file = TEMP_DIR / f"{file_id}_{format}.{format}"
            if temp_file.exists():
                temp_file.unlink()
        
        # 從記憶體中刪除
        del file_data_store[file_id]
        
        logger.info(f"✓ 檔案清理完成 (file_id: {file_id})")
        
        return JSONResponse(content={"success": True, "message": "檔案已清理"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清理失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理失敗: {str(e)}")


# 應用啟動時的初始化
@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    logger.info("=" * 60)
    logger.info("PaddleOCR-VL Web Application 啟動中...")
    logger.info(f"版本: {__version__}")
    logger.info("=" * 60)
    
    # 初始化 OCR 服務
    try:
        default_lang = os.getenv("DEFAULT_OCR_LANGUAGE", "en")
        logger.info("正在初始化 OCR 服務...")
        ocr_service = SimpleOCRService(lang=default_lang, use_gpu=False)
        # 強制觸發 OCR 引擎初始化
        logger.info("正在觸發 OCR 引擎初始化...")
        ocr_service._initialize_engine()
        logger.info(f"✓ OCR 服務已初始化 (語言: {default_lang}, CPU 模式)")
    except Exception as e:
        logger.error(f"✗ OCR 服務初始化失敗: {str(e)}")
        logger.error(f"錯誤詳情: {str(e)}")
        import traceback
        logger.error(f"詳細錯誤: {traceback.format_exc()}")
    
    # 初始化 Gemini 服務
    try:
        gemini_service = get_gemini_service()
        if gemini_service.is_available():
            logger.info(f"✓ Gemini API 已就緒 (模型: {gemini_service.model_name})")
        else:
            logger.warning("⚠ Gemini API 未設定或不可用")
    except Exception as e:
        logger.warning(f"⚠ Gemini 服務初始化警告: {str(e)}")
    
    logger.info("=" * 60)
    logger.info("✓ 應用啟動完成")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    logger.info("應用正在關閉...")
    
    # 清理臨時檔案
    try:
        for file_path in TEMP_DIR.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        logger.info("✓ 臨時檔案已清理")
    except Exception as e:
        logger.error(f"清理臨時檔案失敗: {str(e)}")
    
    logger.info("✓ 應用已關閉")

