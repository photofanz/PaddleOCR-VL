"""
PaddleOCR 核心服務
處理圖像辨識與文字提取
"""

import paddleocr
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
import logging
import time

logger = logging.getLogger(__name__)


class OCRService:
    """PaddleOCR 服務類別"""
    
    def __init__(self, lang: str = 'en', use_gpu: bool = False):
        """
        初始化 OCR 服務
        
        Args:
            lang: 語言代碼 (en, ch_tra, ch_sim, etc.)
            use_gpu: 是否使用 GPU/MPS 加速（預設關閉以確保穩定性）
        """
        # 語言代碼映射（PaddleOCR 3.3.0 版本）
        self.lang_mapping = {
            'en': 'en',
            'ch_tra': 'ch',  # 繁體中文
            'ch_sim': 'ch',  # 簡體中文（都使用 ch）
            'japan': 'japan',
            'korean': 'korean',
            'french': 'french',
            'german': 'german',
            'spanish': 'spanish'
        }
        
        self.original_lang = lang
        self.lang = self.lang_mapping.get(lang, lang)
        self.use_gpu = use_gpu
        self.ocr_engine = None
        # 延遲初始化，只在第一次使用時才初始化
    
    def _initialize_engine(self):
        """初始化 PaddleOCR 引擎（延遲初始化）"""
        if self.ocr_engine is not None:
            return  # 已經初始化過了
        
        try:
            logger.info(f"正在初始化 PaddleOCR (語言: {self.lang}, GPU: {self.use_gpu})...")
            
            # 添加詳細的初始化日誌
            logger.info("開始創建 PaddleOCR 實例...")
            
            # 簡化的初始化方法，避免複雜的超時機制
            try:
                logger.info("正在創建 PaddleOCR 實例...")
                logger.info("使用簡化的初始化方法，避免複雜的超時機制")
                
                # 使用最基本的初始化參數
                self.ocr_engine = paddleocr.PaddleOCR(
                    lang=self.lang
                )
                logger.info("PaddleOCR 實例創建完成")
                
            except Exception as init_error:
                logger.error(f"PaddleOCR 實例創建失敗: {str(init_error)}")
                logger.error(f"錯誤類型: {type(init_error).__name__}")
                import traceback
                logger.error(f"詳細錯誤: {traceback.format_exc()}")
                
                # 嘗試使用更簡單的初始化方法
                logger.info("嘗試使用更簡單的初始化方法...")
                try:
                    self.ocr_engine = paddleocr.PaddleOCR(lang=self.lang)
                    logger.info("PaddleOCR 實例創建完成（簡化方法）")
                except Exception as simple_error:
                    logger.error(f"簡化方法也失敗: {str(simple_error)}")
                    raise init_error
            
            logger.info(f"✓ PaddleOCR 初始化成功 (CPU 模式)")
            
            # 測試 OCR 引擎是否正常工作
            logger.info("測試 OCR 引擎...")
            try:
                # 創建一個簡單的測試圖像
                import numpy as np
                test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255  # 白色圖像
                test_result = self.ocr_engine.ocr(test_image)
                logger.info("✓ OCR 引擎測試通過")
            except Exception as test_error:
                logger.warning(f"OCR 引擎測試失敗，但引擎已初始化: {test_error}")
                # 不拋出錯誤，因為引擎本身已經初始化成功
                
            logger.info("=" * 60)
            logger.info("✓ OCR 服務初始化完成！")
            logger.info("=" * 60)
                
        except Exception as e:
            logger.error(f"PaddleOCR 初始化失敗: {str(e)}")
            logger.error(f"錯誤類型: {type(e).__name__}")
            import traceback
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            raise RuntimeError(f"無法初始化 PaddleOCR: {str(e)}")
    
    def change_language(self, new_lang: str):
        """
        切換 OCR 語言
        
        Args:
            new_lang: 新的語言代碼
        """
        if new_lang != self.lang:
            logger.info(f"切換 OCR 語言: {self.lang} -> {new_lang}")
            self.lang = new_lang
            self._initialize_engine()
    
    def process_image(
        self,
        image: Image.Image,
        use_cls: bool = True
    ) -> Tuple[str, List[dict]]:
        """
        處理單張圖像
        
        Args:
            image: PIL Image 物件
            use_cls: 是否使用角度分類
            
        Returns:
            (純文字, 佈局資訊列表)
        """
        if self.ocr_engine is None:
            raise RuntimeError("OCR 引擎未初始化")
        
        try:
            # 轉換 PIL Image 為 NumPy array (BGR 格式)
            image_np = np.array(image.convert('RGB'))
            image_bgr = image_np[:, :, ::-1]  # RGB -> BGR
            
            # 執行 OCR（使用最基本的參數）
            logger.info("正在執行 OCR...")
            result = self.ocr_engine.ocr(image_bgr)
            
            # 提取文字和佈局資訊
            text_lines = []
            layout_info = []
            
            # 詳細記錄 OCR 結果格式
            logger.info(f"OCR 結果類型: {type(result)}")
            logger.info(f"OCR 結果長度: {len(result) if result else 0}")
            
            # 檢查結果是否為 None 或空
            if result is None:
                logger.warning("OCR 結果為 None")
                return "", []
            
            if not result:
                logger.warning("OCR 結果為空")
                return "", []
            
            # 檢查結果是否為空列表
            if isinstance(result, list) and len(result) == 0:
                logger.warning("OCR 結果為空列表")
                return "", []
            
            # 檢查第一層是否為空
            if isinstance(result, list) and len(result) > 0 and (not result[0] or len(result[0]) == 0):
                logger.warning("OCR 結果第一層為空")
                return "", []
            
            if result and len(result) > 0:
                logger.info(f"第一層結果類型: {type(result[0])}")
                logger.info(f"第一層結果長度: {len(result[0]) if result[0] else 0}")
                
                # 檢查是否是新的 PaddleOCR 3.3.0 格式
                if isinstance(result[0], dict):
                    # 新格式：result[0] 直接是字典
                    first_item = result[0]
                elif result[0] and len(result[0]) > 0:
                    # 舊格式：result[0] 是列表，取第一個元素
                    first_item = result[0][0]
                else:
                    logger.warning("OCR 結果第一層為空")
                    return "", []
                
                logger.info(f"第一項資料類型: {type(first_item)}")
                logger.info(f"第一項資料內容: {first_item}")
                
                # 檢查是否是字典格式（新格式）
                if isinstance(first_item, dict):
                    logger.info("檢測到新的 PaddleOCR 3.3.0 字典格式")
                    
                    # 處理新格式的結果
                    if 'rec_texts' in first_item and 'rec_scores' in first_item:
                        texts = first_item.get('rec_texts', [])
                        scores = first_item.get('rec_scores', [])
                        boxes = first_item.get('rec_boxes', [])
                        
                        logger.info(f"找到 {len(texts)} 個文字項目")
                        
                        for i, (text, score, box) in enumerate(zip(texts, scores, boxes)):
                            if text and text.strip():
                                logger.info(f"提取文字 {i}: '{text}', 信心度: {score}")
                                text_lines.append(text.strip())
                                
                                # 安全處理 bbox 格式
                                y_pos = 0
                                x_pos = 0
                                try:
                                    if isinstance(box, (list, tuple)) and len(box) >= 4:
                                        if isinstance(box[0], (list, tuple)) and len(box[0]) >= 2:
                                            # 格式：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                                            y_pos = (box[0][1] + box[2][1]) / 2
                                            x_pos = (box[0][0] + box[2][0]) / 2
                                        else:
                                            # 格式：[x1, y1, x2, y2]
                                            y_pos = (box[1] + box[3]) / 2
                                            x_pos = (box[0] + box[2]) / 2
                                except (IndexError, TypeError) as e:
                                    logger.warning(f"無法解析 bbox 格式: {box}, 錯誤: {e}")
                                    y_pos = 0
                                    x_pos = 0
                                
                                # 將 numpy array 轉換為 Python list
                                bbox_list = []
                                try:
                                    if hasattr(box, 'tolist'):
                                        # numpy array
                                        bbox_list = box.tolist()
                                    elif isinstance(box, (list, tuple)):
                                        # 已經是 list 或 tuple
                                        bbox_list = list(box)
                                    else:
                                        # 其他類型，嘗試轉換
                                        bbox_list = [float(x) for x in box] if hasattr(box, '__iter__') else [box]
                                except Exception as e:
                                    logger.warning(f"無法轉換 bbox: {box}, 錯誤: {e}")
                                    bbox_list = []
                                
                                layout_info.append({
                                    "text": text.strip(),
                                    "bbox": bbox_list,
                                    "confidence": float(score),
                                    "y_position": y_pos,
                                    "x_position": x_pos
                                })
                    else:
                        logger.warning("新格式中未找到 rec_texts 或 rec_scores")
                        logger.info(f"可用欄位: {list(first_item.keys())}")
                else:
                    # 處理舊格式的結果
                    logger.info("使用舊格式處理邏輯")
                    for idx, line_data in enumerate(result[0]):
                        try:
                            logger.info(f"處理第 {idx} 行資料: {type(line_data)}")
                            
                            # 檢查結果格式
                            if isinstance(line_data, list) and len(line_data) >= 2:
                                bbox = line_data[0]
                                text_info = line_data[1]
                                
                                logger.info(f"邊界框: {bbox}")
                                logger.info(f"文字資訊: {text_info}")
                                
                                if isinstance(text_info, list) and len(text_info) >= 2:
                                    text = text_info[0]
                                    confidence = text_info[1]
                                    
                                    logger.info(f"提取文字: '{text}', 信心度: {confidence}")
                                    
                                    text_lines.append(text)
                                    
                                    # 安全處理 bbox 格式
                                    y_pos = 0
                                    x_pos = 0
                                    try:
                                        if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                                            if isinstance(bbox[0], (list, tuple)) and len(bbox[0]) >= 2:
                                                # 格式：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                                                y_pos = (bbox[0][1] + bbox[2][1]) / 2
                                                x_pos = (bbox[0][0] + bbox[2][0]) / 2
                                            else:
                                                # 格式：[x1, y1, x2, y2]
                                                y_pos = (bbox[1] + bbox[3]) / 2
                                                x_pos = (bbox[0] + bbox[2]) / 2
                                    except (IndexError, TypeError) as e:
                                        logger.warning(f"無法解析 bbox 格式: {bbox}, 錯誤: {e}")
                                        y_pos = 0
                                        x_pos = 0
                                    
                                    # 將 numpy array 轉換為 Python list
                                    bbox_list = []
                                    try:
                                        if hasattr(bbox, 'tolist'):
                                            # numpy array
                                            bbox_list = bbox.tolist()
                                        elif isinstance(bbox, (list, tuple)):
                                            # 已經是 list 或 tuple
                                            bbox_list = list(bbox)
                                        else:
                                            # 其他類型，嘗試轉換
                                            bbox_list = [float(x) for x in bbox] if hasattr(bbox, '__iter__') else [bbox]
                                    except Exception as e:
                                        logger.warning(f"無法轉換 bbox: {bbox}, 錯誤: {e}")
                                        bbox_list = []
                                    
                                    layout_info.append({
                                        "text": text,
                                        "bbox": bbox_list,
                                        "confidence": float(confidence),
                                        "y_position": y_pos,
                                        "x_position": x_pos
                                    })
                                else:
                                    logger.warning(f"OCR 文字資訊格式異常: {text_info}")
                            else:
                                logger.warning(f"OCR 行資料格式異常: {line_data}")
                        except Exception as e:
                            logger.warning(f"OCR 結果處理錯誤: {e}, 資料: {line_data}")
                            import traceback
                            logger.warning(f"詳細錯誤: {traceback.format_exc()}")
            else:
                logger.warning("OCR 結果為空")
            
            # 按 y 座標排序
            layout_info.sort(key=lambda x: (x["y_position"], x["x_position"]))
            
            return "\n".join(text_lines), layout_info
            
        except Exception as e:
            logger.error(f"圖像處理失敗: {str(e)}")
            logger.error(f"錯誤類型: {type(e).__name__}")
            import traceback
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            # 返回空結果而不是拋出異常，避免整個服務崩潰
            return "", []
    
    def process_images(
        self,
        images: List[Image.Image],
        use_cls: bool = True
    ) -> Tuple[str, List[List[dict]]]:
        """
        處理多張圖像
        
        Args:
            images: PIL Image 物件列表
            use_cls: 是否使用角度分類
            
        Returns:
            (合併的文字, 每頁的佈局資訊)
        """
        # 確保 OCR 引擎已初始化（只初始化一次）
        if self.ocr_engine is None:
            logger.info("OCR 引擎未初始化，正在初始化...")
            self._initialize_engine()
        else:
            logger.info("OCR 引擎已初始化，直接使用")
        
        all_text = []
        all_layouts = []
        
        start_time = time.time()
        
        for i, image in enumerate(images, 1):
            logger.info(f"處理第 {i}/{len(images)} 張圖像...")
            logger.info(f"圖像尺寸: {image.size}, 模式: {image.mode}")
            
            try:
                # 添加超時機制，避免單頁處理時間過長
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"第 {i} 頁處理超時")
                
                # 設定 30 秒超時
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)
                
                try:
                    text, layout = self.process_image(image, use_cls)
                    signal.alarm(0)  # 取消超時
                    
                    all_text.append(f"--- 第 {i} 頁 ---\n{text}")
                    all_layouts.append(layout)
                    logger.info(f"✓ 第 {i} 頁處理完成，辨識出 {len(text)} 個字元")
                    
                except TimeoutError as te:
                    signal.alarm(0)  # 取消超時
                    error_msg = f"第 {i} 頁處理超時: {str(te)}"
                    logger.error(error_msg)
                    all_text.append(f"--- 第 {i} 頁 ---\n[錯誤: {error_msg}]")
                    all_layouts.append([])
                
            except Exception as e:
                error_msg = f"第 {i} 頁處理失敗: {str(e)}"
                logger.error(error_msg)
                import traceback
                logger.error(f"詳細錯誤: {traceback.format_exc()}")
                all_text.append(f"--- 第 {i} 頁 ---\n[錯誤: {error_msg}]")
                all_layouts.append([])
        
        processing_time = time.time() - start_time
        logger.info(f"✓ 處理完成，耗時 {processing_time:.2f} 秒")
        
        combined_text = "\n\n".join(all_text)
        return combined_text, all_layouts
    
    def get_info(self) -> dict:
        """獲取服務資訊"""
        return {
            "original_language": self.original_lang,
            "mapped_language": self.lang,
            "use_cpu": True,  # 現在固定使用 CPU 模式
            "engine_status": "initialized" if self.ocr_engine else "not initialized"
        }


# 全域 OCR 服務實例
_ocr_service_cache = {}


def get_ocr_service(lang: str = 'en', use_gpu: bool = False) -> OCRService:
    """
    獲取或創建 OCR 服務實例（單例模式）
    
    Args:
        lang: 語言代碼
        use_gpu: 是否使用 GPU（已棄用，現在固定使用 CPU）
        
    Returns:
        OCRService 實例
    """
    cache_key = f"{lang}_cpu"  # 現在固定使用 CPU 模式
    
    if cache_key not in _ocr_service_cache:
        logger.info(f"創建新的 OCR 服務實例: {cache_key}")
        try:
            _ocr_service_cache[cache_key] = OCRService(lang=lang, use_gpu=False)
            logger.info(f"✓ OCR 服務實例創建成功: {cache_key}")
        except Exception as e:
            logger.error(f"✗ OCR 服務實例創建失敗: {e}")
            # 如果創建失敗，嘗試使用預設的英文服務
            if cache_key != "en_cpu" and "en_cpu" in _ocr_service_cache:
                logger.warning(f"使用預設英文服務替代: {cache_key}")
                return _ocr_service_cache["en_cpu"]
            raise
    
    return _ocr_service_cache[cache_key]

