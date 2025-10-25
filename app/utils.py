"""
Utility functions module
Mainly handles PDF to image conversion and other preprocessing tasks
"""

import fitz  # PyMuPDF
from PIL import Image
from typing import List, Tuple
import io
import logging

logger = logging.getLogger(__name__)


def convert_pdf_to_images(
    pdf_bytes: bytes,
    dpi: int = 100,  # Significantly reduced DPI for faster processing
    max_pages: int = 10  # Significantly reduced maximum page limit
) -> List[Image.Image]:
    """
    Convert PDF to image list
    
    Args:
        pdf_bytes: PDF file byte content
        dpi: Resolution (DPI)
        max_pages: Maximum pages to process
        
    Returns:
        List of PIL Image objects
    """
    images = []
    
    try:
        logger.info("開始轉換 PDF 為圖像...")
        
        # 開啟 PDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(pdf_document)
        
        logger.info(f"PDF 總頁數: {total_pages}")
        
        # 限制處理頁數
        pages_to_process = min(total_pages, max_pages)
        
        if total_pages > max_pages:
            logger.warning(f"PDF 頁數 ({total_pages}) 超過限制 ({max_pages})，僅處理前 {max_pages} 頁")
        
        # 計算縮放係數（DPI -> 縮放）
        zoom = dpi / 72  # 72 是 PDF 的預設 DPI
        mat = fitz.Matrix(zoom, zoom)
        
        logger.info(f"使用 DPI: {dpi}, 縮放係數: {zoom:.2f}")
        
        # 逐頁轉換
        for page_num in range(pages_to_process):
            try:
                logger.info(f"正在處理第 {page_num + 1}/{pages_to_process} 頁...")
                
                page = pdf_document[page_num]
                
                # 渲染為圖像（使用更小的尺寸）
                pix = page.get_pixmap(matrix=mat)
                
                # 轉換為 PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # 確保是 RGB 模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 進一步縮小圖像尺寸以節省記憶體
                if img.width > 1200 or img.height > 1200:
                    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                    logger.info(f"圖像已縮小至: {img.size}")
                
                images.append(img)
                logger.info(f"✓ 第 {page_num + 1} 頁處理完成，尺寸: {img.size}")
                
                # 清理記憶體
                pix = None
                img_data = None
                
                # 強制垃圾回收
                import gc
                gc.collect()
                
            except Exception as page_error:
                logger.error(f"第 {page_num + 1} 頁處理失敗: {str(page_error)}")
                import traceback
                logger.error(f"詳細錯誤: {traceback.format_exc()}")
                # 繼續處理下一頁
                continue
        
        pdf_document.close()
        logger.info(f"PDF 轉換完成，共生成 {len(images)} 張圖像")
        
    except Exception as e:
        logger.error(f"PDF 轉換失敗: {str(e)}")
        import traceback
        logger.error(f"詳細錯誤: {traceback.format_exc()}")
        raise ValueError(f"無法處理 PDF 檔案: {str(e)}")
    
    return images


def extract_layout_from_ocr_result(ocr_result: List) -> Tuple[str, List[dict]]:
    """
    從 PaddleOCR 結果中提取文字和佈局資訊
    
    Args:
        ocr_result: PaddleOCR 的原始輸出
        
    Returns:
        (純文字, 佈局資訊列表)
    """
    text_lines = []
    layout_info = []
    
    if not ocr_result or not ocr_result[0]:
        return "", []
    
    for line_data in ocr_result[0]:
        # line_data 格式: [[bbox], (text, confidence)]
        bbox = line_data[0]  # 邊界框座標
        text = line_data[1][0]  # 文字內容
        confidence = line_data[1][1]  # 信心度
        
        text_lines.append(text)
        
        # 儲存佈局資訊
        layout_info.append({
            "text": text,
            "bbox": bbox,
            "confidence": float(confidence),
            # 計算文字的 y 座標（用於排序）
            "y_position": (bbox[0][1] + bbox[2][1]) / 2,
            "x_position": (bbox[0][0] + bbox[2][0]) / 2
        })
    
    # 按照 y 座標排序（從上到下）
    layout_info.sort(key=lambda x: (x["y_position"], x["x_position"]))
    
    return "\n".join(text_lines), layout_info


def reconstruct_layout_for_txt(layout_info: List[dict], page_width: int = 100) -> str:
    """
    根據佈局資訊重建文字排版（用於 .txt 格式）
    
    Args:
        layout_info: 佈局資訊列表
        page_width: 虛擬頁面寬度（字元數）
        
    Returns:
        保持佈局的純文字
    """
    if not layout_info:
        return ""
    
    lines = []
    current_y = None
    current_line_texts = []
    
    # 按 y 座標分組（同一行）
    for item in layout_info:
        y = item["y_position"]
        
        # 如果 y 座標差異較大，表示是新的一行
        if current_y is None or abs(y - current_y) > 10:  # 10 是閾值
            if current_line_texts:
                # 按 x 座標排序
                current_line_texts.sort(key=lambda x: x["x_position"])
                line_text = " ".join([t["text"] for t in current_line_texts])
                lines.append(line_text)
            
            current_line_texts = [item]
            current_y = y
        else:
            current_line_texts.append(item)
    
    # 處理最後一行
    if current_line_texts:
        current_line_texts.sort(key=lambda x: x["x_position"])
        line_text = " ".join([t["text"] for t in current_line_texts])
        lines.append(line_text)
    
    return "\n".join(lines)


def validate_file_type(filename: str, content_type: str) -> bool:
    """
    驗證檔案類型
    
    Args:
        filename: 檔案名稱
        content_type: MIME 類型
        
    Returns:
        是否為有效的檔案類型
    """
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    allowed_content_types = {
        'application/pdf',
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/bmp',
        'image/tiff'
    }
    
    # 檢查副檔名
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    ext_valid = ext in allowed_extensions
    
    # 檢查 MIME 類型（更寬鬆的檢查）
    content_type_lower = content_type.lower() if content_type else ''
    content_type_valid = (
        content_type_lower in allowed_content_types or
        content_type_lower.startswith('image/') or
        content_type_lower == 'application/pdf'
    )
    
    # 如果副檔名有效，就允許上傳（更寬鬆的驗證）
    return ext_valid


def clean_text(text: str) -> str:
    """
    清理文字（移除多餘空白、統一換行等）
    
    Args:
        text: 原始文字
        
    Returns:
        清理後的文字
    """
    # 移除多餘的空白行
    lines = [line.rstrip() for line in text.split('\n')]
    
    # 移除連續的空白行，最多保留一個
    cleaned_lines = []
    prev_empty = False
    
    for line in lines:
        if line:
            cleaned_lines.append(line)
            prev_empty = False
        elif not prev_empty:
            cleaned_lines.append('')
            prev_empty = True
    
    return '\n'.join(cleaned_lines)

