"""
啟動腳本
運行 FastAPI 應用程式
"""

import uvicorn
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定預設環境變數（確保穩定性）
os.environ.setdefault('USE_GPU', 'False')  # 預設使用 CPU 模式
os.environ.setdefault('PADDLE_OCR_USE_GPU', 'False')

if __name__ == "__main__":
    # 強制設定環境變數，確保使用正確的埠號
    os.environ["PORT"] = "8001"
    os.environ["HOST"] = "0.0.0.0"
    
    host = "0.0.0.0"
    port = 8001
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("=" * 60)
    print("PaddleOCR-VL Web Application")
    print("=" * 60)
    print(f"主機: {host}")
    print(f"埠號: {port}")
    print(f"除錯模式: {debug}")
    print("=" * 60)
    print(f"\n🌐 應用網址: http://localhost:{port}")
    print(f"📖 部署指南: http://localhost:{port}/guide")
    print(f"📊 API 文件: http://localhost:{port}/docs")
    print(f"🔍 系統狀態: http://localhost:{port}/api/status")
    print("\n按 Ctrl+C 停止伺服器\n")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )

