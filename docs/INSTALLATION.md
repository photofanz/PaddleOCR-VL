# 📦 安裝指南

本指南將協助您在 macOS (Apple Silicon) 上完整安裝與設定 PaddleOCR-VL Web Application。

## 📋 目錄

- [系統需求](#系統需求)
- [安裝步驟](#安裝步驟)
- [Gemini API 設定](#gemini-api-設定)
- [驗證安裝](#驗證安裝)
- [常見問題](#常見問題)

---

## 系統需求

### 硬體需求

- **處理器**：Apple Silicon (M1/M2/M3) 或 Intel
  - 推薦：M3 Max 或更高階晶片
- **記憶體**：最少 8GB RAM
  - 推薦：16GB 或更多
- **儲存空間**：最少 5GB 可用空間
  - 包含模型檔案與依賴套件

### 軟體需求

- **作業系統**：macOS 12.0 (Monterey) 或更新版本
- **Python**：3.12 或更新版本
- **Conda**：建議使用 Miniconda 或 Anaconda

---

## 安裝步驟

### 步驟 1：安裝 Conda（如果尚未安裝）

如果您還沒有安裝 Conda，請執行以下步驟：

#### 方法 1：使用 Homebrew

```bash
# 安裝 Homebrew（如果尚未安裝）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安裝 Miniconda
brew install --cask miniconda
```

#### 方法 2：手動安裝

1. 下載 Miniconda：https://docs.conda.io/en/latest/miniconda.html
2. 選擇 macOS Apple M1 (ARM64) 版本
3. 執行安裝程式

初始化 Conda：

```bash
conda init zsh  # 如果使用 zsh
# 或
conda init bash  # 如果使用 bash

# 重新載入 shell
source ~/.zshrc  # 或 source ~/.bashrc
```

### 步驟 2：複製專案

```bash
# 複製專案
git clone https://github.com/yourusername/PaddleOCR-VL.git
cd PaddleOCR-VL
```

### 步驟 3：建立 Conda 環境

```bash
# 建立名為 paddle-ocr 的環境，使用 Python 3.12
conda create -n paddle-ocr python=3.12 -y

# 啟用環境
conda activate paddle-ocr
```

**重要**：之後每次使用時都需要啟用此環境：

```bash
conda activate paddle-ocr
```

### 步驟 4：安裝 Python 依賴

```bash
# 安裝所有依賴套件
pip install -r requirements.txt
```

此步驟將安裝：

- **PaddlePaddle**：深度學習框架（CPU 模式）
- **PaddleOCR 3.3.0**：OCR 工具套件
- **FastAPI**：Web 框架
- **PyMuPDF**：PDF 處理
- **Google Generative AI**：Gemini API 客戶端
- 其他相關套件

**注意**：首次安裝可能需要 10-20 分鐘，視網路速度而定。

### 步驟 5：設定環境變數

```bash
# 複製環境變數範本
cp .env.example .env

# 使用編輯器開啟 .env 檔案
nano .env  # 或使用 vim、VSCode 等編輯器
```

編輯 `.env` 檔案，設定必要的參數：

```ini
# Gemini API 設定
GEMINI_API_KEY=your_gemini_api_key_here  # 替換為您的 API Key

# 伺服器設定
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 檔案上傳設定
MAX_UPLOAD_SIZE=52428800  # 50MB

# OCR 設定
DEFAULT_OCR_LANGUAGE=en
USE_GPU=False  # 使用 CPU 模式確保穩定性

# Gemini 設定
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_MAX_RETRIES=3
GEMINI_TIMEOUT=60
```

---

## Gemini API 設定

Gemini API 用於智能文字處理。如果您不需要 AI 處理功能，可以跳過此步驟。

### 取得 Gemini API Key

1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登入您的 Google 帳號
3. 點擊「Get API Key」
4. 創建新的 API Key 或使用現有的
5. 複製 API Key

### 設定 API Key

方法 1：在 `.env` 檔案中設定

```ini
GEMINI_API_KEY=AIza...your_actual_key
```

方法 2：使用環境變數（臨時）

```bash
export GEMINI_API_KEY="AIza...your_actual_key"
```

### 免費額度

Gemini API 提供慷慨的免費額度：
- gemini-2.0-flash-exp: 每分鐘 15 個請求
- gemini-pro: 每分鐘 60 個請求

詳情請參閱：https://ai.google.dev/pricing

---

## 驗證安裝

### 驗證 PaddleOCR 與 CPU 模式

執行驗證腳本：

```bash
python verify_paddle_mps.py
```

**預期輸出：**

```
============================================================
  PaddleOCR CPU 驗證腳本
  Apple Silicon (M3 Max) 測試
============================================================

============================================================
  1. 檢查 PaddleOCR 安裝
============================================================
✓ PaddleOCR 已安裝
  版本: 2.7.3

============================================================
  2. 檢查 PaddlePaddle 後端
============================================================
✓ PaddlePaddle 已安裝
  版本: 3.0.0
  ℹ 使用 CPU 模式（確保最佳穩定性）

============================================================
  3. 創建測試圖像
============================================================
✓ 測試圖像已創建: test_image.png
  尺寸: (800, 400)

============================================================
  4. 測試 OCR (CPU 模式, 語言: en)
============================================================
正在初始化 PaddleOCR (CPU)...
✓ 初始化完成，耗時 2.34 秒
正在處理圖像: test_image.png
✓ OCR 完成，耗時 1.87 秒

辨識結果:
  1. [0.98] PaddleOCR Test Image
  2. [0.96] Apple M3 Max
  3. [0.97] MacBook Pro 2024
  4. [0.95] This is a test for OCR recognition

============================================================
  5. 測試 OCR (CPU 模式, 語言: ch)
============================================================
正在初始化 PaddleOCR (CPU)...
✓ 初始化完成，耗時 2.45 秒
  ℹ 使用 CPU 模式確保穩定性
正在處理圖像: test_image.png
✓ OCR 完成，耗時 1.95 秒

辨識結果:
  1. [0.98] PaddleOCR 測試圖像
  2. [0.96] Apple M3 Max
  3. [0.97] MacBook Pro 2024
  4. [0.95] 這是 OCR 辨識測試

============================================================
測試總結
============================================================
CPU 模式 (英文): ✓ 成功
  處理時間: 1.87 秒
CPU 模式 (中文): ✓ 成功
  處理時間: 1.95 秒
  穩定性: 優秀

============================================================

✓ 驗證完成！
```

如果看到類似上述輸出，表示安裝成功！

### 驗證 Web 應用

啟動應用：

```bash
python run.py
```

**預期輸出：**

```
============================================================
PaddleOCR-VL Web Application
============================================================
主機: 0.0.0.0
埠號: 8001
除錯模式: True
============================================================

🌐 應用網址: http://localhost:8001
📖 部署指南: http://localhost:8001/guide
📊 API 文件: http://localhost:8001/docs
🔍 系統狀態: http://localhost:8001/api/status

按 Ctrl+C 停止伺服器

============================================================
INFO:     Will watch for changes in these directories: ['/path/to/PaddleOCR-VL']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
============================================================
  PaddleOCR-VL Web Application 啟動中...
  版本: 1.0.0
============================================================
✓ OCR 服務已初始化 (語言: en, CPU: True)
✓ Gemini API 已就緒 (模型: gemini-2.0-flash-exp)
============================================================
✓ 應用啟動完成
============================================================
```

開啟瀏覽器訪問：

- **主應用**：http://localhost:8001
- **部署指南**：http://localhost:8001/guide
- **API 文件**：http://localhost:8001/docs
- **系統狀態**：http://localhost:8001/api/status

---

## 常見問題

### Q1: 安裝 PaddlePaddle 時出現錯誤

**A1:** 確保您使用的是 Python 3.12，並且 Conda 環境已正確啟用：

```bash
# 檢查 Python 版本
python --version  # 應顯示 Python 3.12.x

# 確認在正確的環境
conda info --envs  # paddle-ocr 應該有星號標記

# 重新安裝
pip install --upgrade pip
pip install paddlepaddle --no-cache-dir
```

### Q2: PaddleOCR 下載模型失敗

**A2:** 首次執行 OCR 時，PaddleOCR 會自動下載模型。如果下載失敗：

1. 檢查網路連線
2. 嘗試使用 VPN（某些地區可能需要）
3. 手動下載模型：

```bash
# 前往 PaddleOCR 模型庫
# https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_ch/models_list.md

# 下載後放置於 ~/.paddleocr/ 目錄
```

### Q3: Gemini API 回應 403 錯誤

**A3:** 

1. 檢查 API Key 是否正確設定
2. 確認 API Key 未過期
3. 檢查 API 配額是否已用盡
4. 訪問 Google AI Studio 確認 API 狀態

### Q4: 在 Intel Mac 上能否使用？

**A4:** 可以！本應用使用 CPU 模式，在 Intel Mac 上也能正常運行：

1. 確保 `.env` 中的 `USE_GPU` 設為 `False`
2. 處理速度與 Apple Silicon 相近
3. 所有功能完全相同

### Q5: 如何更新至最新版本？

**A5:**

```bash
# 拉取最新程式碼
git pull origin main

# 更新依賴
conda activate paddle-ocr
pip install -r requirements.txt --upgrade

# 重新啟動應用
python run.py
```

### Q6: 應用無法啟動，顯示埠號已被佔用

**A6:** 8001 埠被其他程式佔用。解決方法：

方法 1：修改 `.env` 檔案中的 `PORT`

```ini
PORT=8002  # 改為其他埠號
```

方法 2：終止佔用 8001 埠的程式

```bash
# 找出佔用的程式
lsof -i :8001

# 終止該程式（替換 PID）
kill -9 <PID>
```

### Q7: 上傳大型 PDF 時出現錯誤

**A7:** 

1. 檢查檔案大小是否超過 50MB 限制
2. 修改 `.env` 中的 `MAX_UPLOAD_SIZE`（單位：位元組）
3. 大型 PDF 可能需要更多記憶體

### Q8: OCR 辨識結果不準確

**A8:** 改善準確度的方法：

1. 確保選擇正確的語言
2. 啟用「使用角度分類」
3. 提高掃描/照片的解析度（建議 300 DPI 以上）
4. 確保圖像清晰，無模糊或扭曲

---

## 需要協助？

如果您遇到其他問題：

1. 查看 [GitHub Issues](https://github.com/yourusername/PaddleOCR-VL/issues)
2. 在 [Discussions](https://github.com/yourusername/PaddleOCR-VL/discussions) 提問
3. 查閱 [PaddleOCR 官方文件](https://github.com/PaddlePaddle/PaddleOCR/tree/main/doc)

---

**祝您使用愉快！** 🎉

