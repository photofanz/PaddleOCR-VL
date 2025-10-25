"""
Data model definitions
Using Pydantic for data validation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MetadataField(BaseModel):
    """Single Metadata field"""
    key: str
    value: str
    required: bool = False


class MetadataFields(BaseModel):
    """Paper to Obsidian style Metadata field collection"""
    title: Optional[str] = Field(None, description="Title")
    chinese_title: Optional[str] = Field(None, description="Chinese translation title")
    authors: Optional[str] = Field(None, description="Authors")
    source: Optional[str] = Field(None, description="Source (journal/conference/book)")
    year: Optional[int] = Field(None, description="Year")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Keywords")
    abstract: Optional[str] = Field(None, description="Abstract")
    custom_fields: Optional[Dict[str, str]] = Field(default_factory=dict, description="Custom fields")
    
    def to_yaml_frontmatter(self) -> str:
        """Convert to YAML frontmatter format"""
        lines = ["---"]
        
        if self.title:
            lines.append(f'title: "{self.title}"')
        if self.chinese_title:
            lines.append(f'chinese_title: "{self.chinese_title}"')
        if self.authors:
            lines.append(f'authors: "{self.authors}"')
        if self.source:
            lines.append(f'source: "{self.source}"')
        if self.year:
            lines.append(f'year: {self.year}')
        if self.keywords:
            keywords_str = ", ".join(self.keywords)
            lines.append(f'keywords: [{keywords_str}]')
        if self.abstract:
            # 處理多行摘要
            abstract_lines = self.abstract.replace('"', '\\"').split('\n')
            if len(abstract_lines) == 1:
                lines.append(f'abstract: "{abstract_lines[0]}"')
            else:
                lines.append('abstract: |')
                for line in abstract_lines:
                    lines.append(f'  {line}')
        
        # 添加自訂欄位
        if self.custom_fields:
            for key, value in self.custom_fields.items():
                lines.append(f'{key}: "{value}"')
        
        lines.append("---")
        lines.append("")  # 空行分隔
        return "\n".join(lines)


class UploadResponse(BaseModel):
    """檔案上傳回應"""
    success: bool
    file_id: str
    filename: str
    file_type: str
    message: str


class OCRRequest(BaseModel):
    """OCR 辨識請求"""
    file_id: str
    language: str = Field(default="en", description="OCR 語言：en, ch_tra, ch_sim 等")
    use_textline_orientation: bool = Field(default=True, description="是否使用文字行方向檢測")


class OCRResponse(BaseModel):
    """OCR 辨識回應"""
    success: bool
    file_id: str
    raw_text: str
    layout_info: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="文字位置資訊，用於重建佈局"
    )
    message: str
    processing_time: Optional[float] = None


class GeminiRequest(BaseModel):
    """Gemini 處理請求"""
    text: str = Field(..., description="要處理的文字")
    prompt_type: str = Field(
        default="structure",
        description="提示詞類型：structure, summarize, academic, custom"
    )
    custom_prompt: Optional[str] = Field(None, description="自訂提示詞")
    system_instruction: Optional[str] = Field(None, description="系統指令")


class GeminiResponse(BaseModel):
    """Gemini 處理回應"""
    model_config = {"protected_namespaces": ()}
    
    success: bool
    processed_text: str
    message: str
    model_used: Optional[str] = None
    processing_time: Optional[float] = None


class GenerateMarkdownRequest(BaseModel):
    """生成 Markdown 請求"""
    file_id: str
    content: str = Field(..., description="主要內容")
    include_metadata: bool = Field(default=False, description="是否包含 Metadata")
    metadata: Optional[MetadataFields] = None


class GenerateMarkdownResponse(BaseModel):
    """生成 Markdown 回應"""
    success: bool
    markdown_content: str
    txt_content: str
    message: str


class DownloadRequest(BaseModel):
    """下載請求"""
    file_id: str
    format: str = Field(..., description="下載格式：md 或 txt")
    filename: Optional[str] = Field(None, description="自訂檔名")


class StatusResponse(BaseModel):
    """狀態回應"""
    status: str
    message: str
    version: str
    ocr_available: bool
    gemini_available: bool

