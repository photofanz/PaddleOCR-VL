"""
Simplified OCR Service
Focused on handling PaddleOCR 3.3.0 standard output format
"""

import paddleocr
import numpy as np
from PIL import Image
from typing import List, Tuple, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)


class SimpleOCRService:
    """Simplified OCR service class"""
    
    def __init__(self, lang: str = 'en', use_gpu: bool = False):
        """
        Initialize OCR service
        
        Args:
            lang: Language code (en, ch_tra, ch_sim, etc.)
            use_gpu: Whether to use GPU/MPS acceleration (disabled by default for stability)
        """
        # Language code mapping (PaddleOCR 3.3.0 version)
        self.lang_mapping = {
            'en': 'en',
            'ch_tra': 'ch',  # Traditional Chinese
            'ch_sim': 'ch',  # Simplified Chinese (both use ch)
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
            
            # 使用最基本的初始化參數
            self.ocr_engine = paddleocr.PaddleOCR(
                lang=self.lang
            )
            logger.info(f"✓ PaddleOCR 初始化成功 (CPU 模式)")
            
            # 測試 OCR 引擎是否正常工作
            logger.info("測試 OCR 引擎...")
            try:
                # 創建一個簡單的測試圖像
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
    
    def process_image(self, image: Image.Image) -> Tuple[str, List[dict]]:
        """
        處理單張圖像
        
        Args:
            image: PIL Image 物件
            
        Returns:
            (純文字, 佈局資訊列表)
        """
        if self.ocr_engine is None:
            raise RuntimeError("OCR 引擎未初始化")
        
        try:
            # 轉換 PIL Image 為 NumPy array (BGR 格式)
            image_np = np.array(image.convert('RGB'))
            image_bgr = image_np[:, :, ::-1]  # RGB -> BGR
            
            # 執行 OCR
            logger.info("正在執行 OCR...")
            result = self.ocr_engine.ocr(image_bgr)
            
            # 提取文字和佈局資訊
            text_lines = []
            layout_info = []
            
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
            
            # 處理 PaddleOCR 3.3.0 的輸出格式
            if result and len(result) > 0 and result[0]:
                logger.info(f"處理 OCR 結果，共 {len(result[0])} 個文字區域")
                logger.info(f"OCR 結果詳細內容: {result}")
                
                # 檢查是否是新的字典格式
                if isinstance(result[0], dict):
                    logger.info("檢測到新的 PaddleOCR 3.3.0 字典格式")
                    
                    # 處理新格式的結果
                    if 'rec_texts' in result[0] and 'rec_scores' in result[0]:
                        texts = result[0].get('rec_texts', [])
                        scores = result[0].get('rec_scores', [])
                        boxes = result[0].get('rec_boxes', [])
                        
                        logger.info(f"找到 {len(texts)} 個文字項目")
                        
                        for i, (text, score, box) in enumerate(zip(texts, scores, boxes)):
                            if text and text.strip():
                                logger.info(f"提取文字 {i}: '{text}', 信心度: {score}")
                                text_lines.append(text.strip())
                                
                                # 計算位置資訊
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
                                
                                # 轉換 bbox 為 Python list
                                bbox_list = []
                                try:
                                    if hasattr(box, 'tolist'):
                                        bbox_list = box.tolist()
                                    elif isinstance(box, (list, tuple)):
                                        bbox_list = list(box)
                                    else:
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
                        logger.info(f"可用欄位: {list(result[0].keys())}")
                else:
                    # 處理標準的列表格式
                    logger.info("使用標準列表格式處理邏輯")
                    for idx, line_data in enumerate(result[0]):
                        try:
                            # 標準 PaddleOCR 格式：[[bbox], (text, confidence)]
                            if isinstance(line_data, list) and len(line_data) >= 2:
                                bbox = line_data[0]
                                text_info = line_data[1]
                                
                                if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                    text = text_info[0]
                                    confidence = text_info[1]
                                    
                                    if text and text.strip():
                                        logger.info(f"提取文字 {idx}: '{text}', 信心度: {confidence}")
                                        text_lines.append(text.strip())
                                        
                                        # 計算位置資訊
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
                                        
                                        # 轉換 bbox 為 Python list
                                        bbox_list = []
                                        try:
                                            if hasattr(bbox, 'tolist'):
                                                bbox_list = bbox.tolist()
                                            elif isinstance(bbox, (list, tuple)):
                                                bbox_list = list(bbox)
                                            else:
                                                bbox_list = [float(x) for x in bbox] if hasattr(bbox, '__iter__') else [bbox]
                                        except Exception as e:
                                            logger.warning(f"無法轉換 bbox: {bbox}, 錯誤: {e}")
                                            bbox_list = []
                                        
                                        layout_info.append({
                                            "text": text.strip(),
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
                logger.warning("OCR 結果為空或格式異常")
            
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
    
    def process_images(self, images: List[Image.Image]) -> Tuple[str, List[List[dict]]]:
        """
        處理多張圖像
        
        Args:
            images: PIL Image 物件列表
            
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
        
        # 限制處理的圖像數量，避免記憶體問題
        max_images = min(len(images), 5)  # 最多處理 5 張圖像
        if len(images) > max_images:
            logger.warning(f"圖像數量 ({len(images)}) 超過限制 ({max_images})，僅處理前 {max_images} 張")
        
        for i, image in enumerate(images[:max_images], 1):
            logger.info(f"處理第 {i}/{max_images} 張圖像...")
            logger.info(f"圖像尺寸: {image.size}, 模式: {image.mode}")
            
            try:
                # 添加超時機制
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"第 {i} 頁處理超時")
                
                # 設定 60 秒超時
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(60)
                
                try:
                    text, layout = self.process_image(image)
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
                
                # 清理記憶體
                import gc
                gc.collect()
                
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
