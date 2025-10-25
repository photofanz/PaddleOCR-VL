# 🔍 PaddleOCR-VL Web Application

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-2.7+-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**本地 PaddleOCR 辨識 + Gemini AI 智能結構化的混合式文件處理系統**

[功能特色](#✨-功能特色) • [快速開始](#🚀-快速開始) • [詳細安裝](#📦-安裝指南) • [使用說明](#💡-使用說明) • [API 文件](#📚-api-文件) • [貢獻指南](#🤝-貢獻)

</div>

---

## 📖 專案簡介

PaddleOCR-VL Web Application 是一個結合本地 OCR 技術與雲端 AI 能力的文件處理系統。它在 Apple Silicon (M3 Max) 上使用 CPU 模式進行穩定可靠的文字辨識，並透過 Gemini API 進行智能文字結構化與分析。

### 🎯 設計理念

- **本地優先**：核心 OCR 處理在本地執行，確保資料隱私與處理速度
- **AI 增強**：利用 Gemini API 的語言理解能力，將原始文字轉換為結構化內容
- **使用者友善**：提供現代化的網頁介面，無需命令列操作
- **開源透明**：完全開源，易於自訂與擴展

## ✨ 功能特色

### 核心功能

- 📄 **多格式支援**：PDF、PNG、JPG、JPEG 格式檔案上傳
- 🌍 **多語言辨識**：支援英文、繁體中文、簡體中文、日文、韓文等
- ⚡ **穩定處理**：使用 CPU 模式確保最佳兼容性和穩定性
- 🤖 **AI 智能處理**：
  - 結構化為 Markdown
  - 內容摘要生成
  - 學術論文分析（Paper to Obsidian 風格）
  - 自訂提示詞處理

### 進階功能

- 🏷️ **Metadata 管理**：Paper to Obsidian 風格的 YAML frontmatter
- 📝 **雙格式下載**：
  - `.md` - 結構化 Markdown（適合 Obsidian、Notion）
  - `.txt` - 保持原始佈局的純文字
- 🎨 **現代化介面**：響應式設計，支援桌面與行動裝置
- 🔄 **即時預覽**：Markdown 渲染預覽

## 🏗️ 技術架構

```
┌─────────────────────────────────────────────────────────────┐
│                      前端介面 (Web UI)                       │
│           HTML5 + CSS3 + JavaScript + Marked.js            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────────┐
│                   FastAPI 後端服務                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ OCR Service  │  │Gemini Service│  │ Utils Module │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘     │
│         │                  │                                │
│  ┌──────▼───────┐  ┌──────▼───────┐                        │
│  │ PaddleOCR    │  │  Gemini API  │                        │
│  │ (Local CPU)  │  │   (Cloud)    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 技術棧

**後端：**
- Python 3.12
- FastAPI（Web 框架）
- PaddlePaddle + PaddleOCR 3.3.0（OCR 引擎，CPU 模式）
- PyMuPDF（PDF 處理）
- Google Generative AI（Gemini API）

**前端：**
- 原生 HTML/CSS/JavaScript
- Marked.js（Markdown 渲染）
- 響應式設計

## 🚀 快速開始

### 系統需求

- macOS（推薦 Apple Silicon M1/M2/M3）
- Python 3.12+
- Conda（環境管理）
- 至少 8GB RAM
- 至少 5GB 可用儲存空間

### 3 步驟快速啟動

```bash
# 1. 複製專案並建立環境
git clone https://github.com/yourusername/PaddleOCR-VL.git
cd PaddleOCR-VL
conda create -n paddle-ocr python=3.12 -y
conda activate paddle-ocr

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定環境變數並啟動
cp .env.example .env
# 編輯 .env 檔案，設定 GEMINI_API_KEY
python run.py
```

服務將在 `http://localhost:8001` 啟動。

## 📦 安裝指南

### 詳細安裝步驟

請參閱 [INSTALLATION.md](docs/INSTALLATION.md) 獲取完整的安裝指南，包括：

- Conda 環境設置
- PaddleOCR 驗證
- Gemini API Key 取得與設定
- 常見問題排解

### 驗證安裝

安裝完成後，執行驗證腳本：

```bash
python verify_paddle_mps.py --lang en
```

這將測試 PaddleOCR 是否正確安裝並在 CPU 模式下運行。

## 💡 使用說明

### 基本工作流程

1. **上傳文件**
   - 支援拖放或點擊上傳
   - 檔案大小限制：50MB

2. **OCR 辨識**
   - 選擇辨識語言
   - 啟用角度分類（提升準確度）
   - 點擊「開始 OCR 辨識」

3. **添加 Metadata（選填）**
   - 啟用 Metadata 功能
   - 填寫標題、作者、來源等資訊
   - 支援自訂欄位

4. **AI 智能處理**
   - 選擇處理模式（結構化/總結/學術分析）
   - 編輯或自訂提示詞
   - 使用 Gemini 處理或跳過

5. **預覽與下載**
   - 查看 Markdown 預覽或原始碼
   - 下載 .md 或 .txt 格式

### 使用範例

#### 範例 1：論文轉 Obsidian 筆記

1. 上傳論文 PDF
2. 選擇語言「英文」
3. OCR 辨識完成後，啟用 Metadata
4. 填寫論文資訊（標題、作者、期刊等）
5. 選擇「學術論文分析」模式
6. 使用 Gemini 處理
7. 下載 .md 檔案至 Obsidian Vault

#### 範例 2：文件快速數位化

1. 上傳掃描的文件圖片
2. 選擇對應語言
3. OCR 辨識
4. 跳過 AI 處理
5. 下載 .txt 檔案（保持原始佈局）

## 📚 API 文件

完整的 API 文件請參閱：
- [API_DOCS.md](docs/API_DOCS.md) - REST API 詳細說明
- `/docs` - FastAPI 自動生成的互動式文件

### 主要 API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/upload` | POST | 上傳檔案 |
| `/api/process-ocr` | POST | 執行 OCR 辨識 |
| `/api/enhance-with-gemini` | POST | 使用 Gemini 處理文字 |
| `/api/generate-markdown` | POST | 生成 Markdown 檔案 |
| `/api/download/{file_id}/{format}` | GET | 下載檔案 |

## 🎨 介面預覽

（建議在此處添加截圖）

## 🛠️ 開發指南

### 本地開發

```bash
# 以開發模式啟動（啟用熱重載）
DEBUG=True python run.py
```

### 執行測試

```bash
# 執行單元測試
pytest tests/

# 執行 OCR 驗證
python verify_paddle_mps.py
```

### 專案結構

```
PaddleOCR-VL/
├── app/                    # 後端應用
│   ├── main.py            # FastAPI 主應用
│   ├── services.py        # OCR 服務
│   ├── gemini_service.py  # Gemini API 整合
│   ├── utils.py           # 工具函數
│   └── models.py          # 資料模型
├── static/                 # 前端靜態檔案
│   ├── app.html           # 主應用介面
│   ├── app.js             # 前端邏輯
│   ├── styles.css         # 樣式
│   └── guide.html         # 部署指南
├── docs/                   # 文件
├── tests/                  # 測試
├── run.py                  # 啟動腳本
└── requirements.txt        # Python 依賴
```

## 🤝 貢獻

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳情。

### 貢獻方式

1. Fork 此專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) - 深度學習框架
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR 工具套件
- [FastAPI](https://fastapi.tiangolo.com/) - 現代化 Python Web 框架
- [Google Generative AI](https://ai.google.dev/) - Gemini API

## 📮 聯絡方式

- GitHub Issues: [提出問題](https://github.com/yourusername/PaddleOCR-VL/issues)
- 討論區: [GitHub Discussions](https://github.com/yourusername/PaddleOCR-VL/discussions)

## 🗺️ 路線圖

- [ ] 支援更多 OCR 語言
- [ ] 批次處理功能
- [ ] 表格識別與結構化
- [ ] Docker 容器化部署
- [ ] 使用者認證與多使用者支援
- [ ] 歷史記錄與檔案管理
- [ ] 本地部署的輕量級 LLM 支援

---

<div align="center">

如果這個專案對您有幫助，請給個 ⭐️ Star！

Made with ❤️ by [Your Name]

</div>

