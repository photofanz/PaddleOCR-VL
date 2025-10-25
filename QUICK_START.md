# ⚡ 快速開始指南

5 分鐘內完成 PaddleOCR-VL 的安裝與啟動。

---

## 📋 前置需求

- macOS（Apple Silicon 推薦）
- 已安裝 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 Anaconda
- 至少 8GB RAM
- 至少 5GB 可用空間

---

## 🚀 3 步驟安裝

### 步驟 1：複製並設置環境

```bash
# 複製專案
git clone https://github.com/yourusername/PaddleOCR-VL.git
cd PaddleOCR-VL

# 建立 Conda 環境
conda create -n paddle-ocr python=3.12 -y
conda activate paddle-ocr

# 安裝依賴（需要 5-10 分鐘）
pip install -r requirements.txt
```

### 步驟 2：設定環境變數

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案（選填，但建議設定 Gemini API Key）
nano .env
```

**最低配置（僅 OCR 功能）**：
```ini
USE_GPU=True
DEFAULT_OCR_LANGUAGE=en
```

**完整配置（包含 AI 功能）**：
```ini
GEMINI_API_KEY=your_api_key_here
USE_GPU=True
DEFAULT_OCR_LANGUAGE=en
```

> 💡 **如何取得 Gemini API Key**：訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)

### 步驟 3：啟動應用

```bash
python run.py
```

看到以下訊息表示成功：

```
============================================================
PaddleOCR-VL Web Application
============================================================
🌐 應用網址: http://localhost:8000
📖 部署指南: http://localhost:8000/guide
📊 API 文件: http://localhost:8000/docs
============================================================
```

---

## 🎯 開始使用

### 方法 1：網頁介面（推薦）

1. 開啟瀏覽器訪問 `http://localhost:8000`
2. 拖放或點擊上傳 PDF/圖像
3. 選擇語言，點擊「開始 OCR 辨識」
4. （選填）啟用 Metadata，填寫文件資訊
5. （選填）使用 Gemini 處理文字
6. 預覽並下載結果

### 方法 2：API（開發者）

```bash
# 檢查系統狀態
curl http://localhost:8000/api/status

# 上傳檔案
curl -X POST http://localhost:8000/api/upload \
  -F "file=@your_document.pdf"

# 查看互動式 API 文件
open http://localhost:8000/docs
```

---

## ✅ 驗證安裝

執行驗證腳本測試 OCR 功能：

```bash
python verify_paddle_mps.py
```

預期輸出應包含：

```
✓ PaddleOCR 已安裝
✓ PaddlePaddle 已安裝
✓ OCR 完成
```

---

## 📝 基本使用範例

### 範例 1：快速辨識英文 PDF

```bash
# 1. 啟動應用
python run.py

# 2. 開啟瀏覽器
open http://localhost:8000

# 3. 上傳 PDF
# 4. 選擇「English」
# 5. 點擊「開始 OCR 辨識」
# 6. 點擊「下載 .txt」
```

### 範例 2：論文轉 Obsidian 筆記

```bash
# 1. 上傳論文 PDF
# 2. 選擇語言
# 3. OCR 辨識完成後
# 4. 啟用「Metadata」
# 5. 填寫論文資訊（標題、作者等）
# 6. 選擇「學術論文分析」模式
# 7. 使用 Gemini 處理
# 8. 下載 .md 到 Obsidian Vault
```

---

## 🔧 常見問題

### Q: 安裝依賴時出現錯誤？

**A:** 確保使用正確的 Python 版本：

```bash
python --version  # 應顯示 3.12.x
conda activate paddle-ocr
```

### Q: 無法啟動應用？

**A:** 檢查埠號是否被佔用：

```bash
# 查看 8000 埠
lsof -i :8000

# 或修改 .env 中的 PORT
PORT=8001
```

### Q: OCR 辨識很慢？

**A:** 確認已啟用 MPS 加速：

1. 檢查 `.env` 中 `USE_GPU=True`
2. 在 Apple Silicon 上應該會自動使用 MPS
3. 首次執行會下載模型（較慢），之後會快很多

### Q: Gemini 功能無法使用？

**A:** 

1. 確認已設定 `GEMINI_API_KEY`
2. 檢查 API Key 是否有效
3. 可以跳過 AI 處理，直接下載原始 OCR 結果

---

## 📚 進階資訊

- **完整文件**：查看 [README.md](README.md)
- **詳細安裝**：查看 [docs/INSTALLATION.md](docs/INSTALLATION.md)
- **API 文件**：查看 [docs/API_DOCS.md](docs/API_DOCS.md)
- **部署指南**：訪問 http://localhost:8000/guide

---

## 🆘 需要幫助？

- 💬 [GitHub Discussions](https://github.com/yourusername/PaddleOCR-VL/discussions)
- 🐛 [回報問題](https://github.com/yourusername/PaddleOCR-VL/issues)
- 📖 [完整文件](docs/)

---

## 🎉 開始探索

現在您已經準備好使用 PaddleOCR-VL 了！

- 試試不同的 OCR 語言
- 體驗 AI 智能處理
- 自訂提示詞
- 探索 API

**祝您使用愉快！** 🚀

