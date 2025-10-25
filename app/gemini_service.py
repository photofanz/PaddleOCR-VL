"""
Gemini API integration service
Handles text structuring, summarization and other AI features
"""

import google.generativeai as genai
from typing import Optional
import logging
import time
import os

logger = logging.getLogger(__name__)


# Default prompt library
DEFAULT_PROMPTS = {
    "structure": """你是一個專業的文件格式化助手。請將以下 OCR 辨識的原始文字，轉換為結構良好、易於閱讀的 Markdown 文件。

要求：
1. 保留所有原始內容，不要遺漏任何資訊
2. 準確識別並添加適當的標題層級（# ## ###）
3. 識別並格式化列表（有序或無序）
4. 識別並格式化表格
5. 識別並使用代碼塊標記程式碼
6. 適當地分段，提升可讀性
7. 保持專業術語的準確性
8. 如果有數學公式，使用 LaTeX 格式（$...$）

請直接輸出格式化後的 Markdown，不要添加額外的說明。""",

    "summarize": """你是一個專業的總結助手。請為以下 OCR 辨識出的內容提供一個簡潔、準確、條列式的總結。

要求：
1. 提取主要觀點和關鍵資訊
2. 使用條列式呈現（使用 - 或數字）
3. 保持客觀，不添加個人觀點
4. 確保總結的完整性和準確性
5. 使用清晰易懂的語言
6. 適當使用 Markdown 格式（粗體、斜體等）

請直接輸出總結內容。""",

    "academic": """你是一個專業的學術論文分析助手。請分析以下論文內容，並提供結構化導讀。

請按照以下結構組織內容（參考 Paper to Obsidian 格式）：

## 🧩 Paper-to-Outline (p2o)

### 一、研究基本資訊
* **標題**：[論文標題]
* **中文譯題**：[中文翻譯]（如適用）
* **作者**：[作者列表]
* **期刊/會議**：[發表場所]
* **年份**：[年份]
* **理論核心**：[核心理論]

### 二、研究動機與問題意識
[描述研究背景、gap 和核心問題]

### 三、理論架構
[理論基礎、主要構念、研究假設]

### 四、研究方法
[樣本、設計、分析工具、信效度]

### 五、主要發現
[關鍵研究結果]

### 六、理論與實務貢獻
[理論面和實務面的貢獻]

### 七、限制與未來研究方向
[研究限制和建議]

### 八、結論一句話
> [用一句話總結核心貢獻]

請根據提供的內容盡可能完整地填寫以上結構。如果某些資訊無法從文本中提取，可以標註 [資訊不足]。"""
}


class GeminiService:
    """Gemini API 服務類別"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-exp",
        max_retries: int = 3,
        timeout: int = 60
    ):
        """
        初始化 Gemini 服務
        
        Args:
            api_key: Gemini API 金鑰
            model_name: 模型名稱
            max_retries: 最大重試次數
            timeout: 請求超時時間（秒）
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.max_retries = max_retries
        self.timeout = timeout
        self.model = None
        
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.warning("Gemini API Key 未設定，Gemini 功能將無法使用")
            self.api_available = False
        else:
            self._initialize_client()
            self.api_available = True
    
    def _initialize_client(self):
        """初始化 Gemini 客戶端"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"✓ Gemini API 初始化成功 (模型: {self.model_name})")
        except Exception as e:
            logger.error(f"Gemini API 初始化失敗: {str(e)}")
            self.api_available = False
            raise RuntimeError(f"無法初始化 Gemini API: {str(e)}")
    
    def get_default_prompt(self, prompt_type: str) -> str:
        """
        獲取預設提示詞
        
        Args:
            prompt_type: 提示詞類型 (structure, summarize, academic)
            
        Returns:
            提示詞文字
        """
        return DEFAULT_PROMPTS.get(prompt_type, DEFAULT_PROMPTS["structure"])
    
    def process_text(
        self,
        text: str,
        prompt_type: str = "structure",
        custom_prompt: Optional[str] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        使用 Gemini 處理文字
        
        Args:
            text: 要處理的文字
            prompt_type: 提示詞類型
            custom_prompt: 自訂提示詞（覆蓋 prompt_type）
            system_instruction: 系統指令
            
        Returns:
            處理後的文字
        """
        if not self.api_available:
            raise RuntimeError("Gemini API 不可用，請檢查 API Key 設定")
        
        # 選擇提示詞
        if custom_prompt:
            system_prompt = custom_prompt
        else:
            system_prompt = self.get_default_prompt(prompt_type)
        
        # 構建完整提示
        full_prompt = f"{system_prompt}\n\n以下是需要處理的內容：\n\n{text}"
        
        # 如果有系統指令，使用新版 API
        if system_instruction:
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 8192,
            }
            
            model_with_system = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction,
                generation_config=generation_config
            )
            
            return self._generate_with_retry(model_with_system, full_prompt)
        else:
            return self._generate_with_retry(self.model, full_prompt)
    
    def _generate_with_retry(self, model, prompt: str) -> str:
        """
        帶重試機制的生成函數
        
        Args:
            model: Gemini 模型實例
            prompt: 提示詞
            
        Returns:
            生成的文字
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Gemini API 請求 (嘗試 {attempt + 1}/{self.max_retries})...")
                
                start_time = time.time()
                response = model.generate_content(prompt)
                elapsed_time = time.time() - start_time
                
                logger.info(f"✓ Gemini API 請求成功，耗時 {elapsed_time:.2f} 秒")
                
                if response.text:
                    return response.text
                else:
                    raise ValueError("Gemini API 返回空內容")
                
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini API 請求失敗 (嘗試 {attempt + 1}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 指數退避
                    logger.info(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
        
        # 所有重試都失敗
        error_msg = f"Gemini API 請求失敗（已重試 {self.max_retries} 次）: {str(last_error)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    def is_available(self) -> bool:
        """檢查 Gemini API 是否可用"""
        return self.api_available
    
    def get_info(self) -> dict:
        """獲取服務資訊"""
        return {
            "available": self.api_available,
            "model": self.model_name,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }


# 全域 Gemini 服務實例
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """
    獲取或創建 Gemini 服務實例（單例模式）
    
    Returns:
        GeminiService 實例
    """
    global _gemini_service
    
    if _gemini_service is None:
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
        timeout = int(os.getenv("GEMINI_TIMEOUT", "60"))
        
        _gemini_service = GeminiService(
            api_key=api_key,
            model_name=model_name,
            max_retries=max_retries,
            timeout=timeout
        )
    
    return _gemini_service

