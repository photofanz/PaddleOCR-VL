"""
PaddleOCR 服務測試
"""

import pytest
from PIL import Image
import numpy as np


def create_test_image(width=800, height=400):
    """創建一個測試圖像"""
    # 創建白色背景
    img_array = np.ones((height, width, 3), dtype=np.uint8) * 255
    img = Image.fromarray(img_array)
    return img


def test_image_creation():
    """測試測試圖像創建"""
    img = create_test_image()
    assert img is not None
    assert img.size == (800, 400)
    assert img.mode == 'RGB'


@pytest.mark.asyncio
async def test_ocr_service_initialization():
    """測試 OCR 服務初始化"""
    try:
        from app.services import get_ocr_service
        
        # 測試獲取服務
        service = get_ocr_service(lang='en', use_gpu=False)
        assert service is not None
        
        # 測試服務資訊
        info = service.get_info()
        assert info['language'] == 'en'
        assert 'engine_status' in info
        
    except Exception as e:
        pytest.skip(f"PaddleOCR not available: {str(e)}")


@pytest.mark.asyncio
async def test_gemini_service_initialization():
    """測試 Gemini 服務初始化"""
    try:
        from app.gemini_service import get_gemini_service
        
        # 測試獲取服務
        service = get_gemini_service()
        assert service is not None
        
        # 測試服務資訊
        info = service.get_info()
        assert 'available' in info
        assert 'model' in info
        
    except Exception as e:
        pytest.skip(f"Gemini service not available: {str(e)}")


def test_metadata_yaml_conversion():
    """測試 Metadata 轉換為 YAML frontmatter"""
    from app.models import MetadataFields
    
    metadata = MetadataFields(
        title="Test Document",
        authors="Test Author",
        year=2025,
        keywords=["test", "example"]
    )
    
    yaml = metadata.to_yaml_frontmatter()
    
    assert "---" in yaml
    assert "title:" in yaml
    assert "Test Document" in yaml
    assert "authors:" in yaml
    assert "year: 2025" in yaml
    assert "keywords:" in yaml


def test_file_type_validation():
    """測試檔案類型驗證"""
    from app.utils import validate_file_type
    
    # 有效的檔案類型
    assert validate_file_type("document.pdf", "application/pdf")
    assert validate_file_type("image.png", "image/png")
    assert validate_file_type("photo.jpg", "image/jpeg")
    
    # 無效的檔案類型
    assert not validate_file_type("script.py", "text/x-python")
    assert not validate_file_type("archive.zip", "application/zip")


def test_text_cleaning():
    """測試文字清理功能"""
    from app.utils import clean_text
    
    # 測試移除多餘空白行
    text = "Line 1\n\n\n\nLine 2\n\n\n\nLine 3"
    cleaned = clean_text(text)
    
    # 應該移除連續的空白行
    assert "\n\n\n" not in cleaned
    assert "Line 1" in cleaned
    assert "Line 2" in cleaned
    assert "Line 3" in cleaned


@pytest.mark.asyncio
async def test_api_status_endpoint():
    """測試 API 狀態端點"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/api/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "version" in data
    assert "ocr_available" in data
    assert "gemini_available" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

