# 📝 更新日誌

本文件記錄 PaddleOCR-VL Web Application 的所有重要變更。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
本專案遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## [未發布]

### 計劃中的功能
- 批次處理多個檔案
- 表格識別與結構化
- 使用者認證系統
- Docker 容器化部署
- 歷史記錄與檔案管理

---

## [1.0.0] - 2025-01-XX

### 🎉 初始發布

#### 新增功能

**核心功能**
- ✨ PDF 和圖像檔案上傳功能
- ✨ 多語言 OCR 辨識（支援英文、繁中、簡中、日文、韓文等）
- ✨ Apple Silicon MPS 加速支援
- ✨ Gemini API 整合，提供智能文字處理
- ✨ 三種預設處理模式：
  - 結構化為 Markdown
  - 內容摘要生成
  - 學術論文分析（Paper to Obsidian 風格）
- ✨ 自訂提示詞功能
- ✨ Paper to Obsidian 風格的 Metadata 管理
- ✨ 雙格式下載（.md 和 .txt）

**使用者介面**
- ✨ 現代化響應式網頁介面
- ✨ 拖放檔案上傳
- ✨ 即時處理進度顯示
- ✨ Markdown 預覽功能
- ✨ 步驟式工作流程指引

**API**
- ✨ RESTful API 設計
- ✨ 完整的 API 文件（Swagger UI）
- ✨ 檔案上傳 API
- ✨ OCR 處理 API
- ✨ Gemini 處理 API
- ✨ Markdown 生成 API
- ✨ 檔案下載 API

**文件**
- 📚 完整的 README.md
- 📚 詳細的 INSTALLATION.md
- 📚 API 文件（API_DOCS.md）
- 📚 部署指南網頁版
- 📚 貢獻指南（CONTRIBUTING.md）

**開發工具**
- 🛠️ PaddleOCR MPS 驗證腳本
- 🛠️ 環境變數配置範本
- 🛠️ 完整的依賴管理（requirements.txt）
- 🛠️ 啟動腳本（run.py）

#### 技術細節

**後端**
- Python 3.12
- FastAPI 0.115.0
- PaddlePaddle 3.0.0
- PaddleOCR 2.7.3+
- PyMuPDF 1.24.13
- Google Generative AI 0.8.3

**前端**
- 原生 HTML/CSS/JavaScript
- Marked.js for Markdown 渲染
- 響應式設計

**支援平台**
- macOS（Apple Silicon 和 Intel）
- 理論上支援 Linux 和 Windows（未完整測試）

---

## 版本號說明

### 主版本號（Major）
當有不相容的 API 變更時遞增

### 次版本號（Minor）
當新增向下相容的功能時遞增

### 修訂號（Patch）
當進行向下相容的問題修正時遞增

---

## 類型標籤說明

- ✨ `新增` - 新功能
- 🐛 `修復` - Bug 修復
- 📚 `文件` - 文件變更
- 🎨 `樣式` - 程式碼格式變更（不影響功能）
- ♻️ `重構` - 程式碼重構
- ⚡ `性能` - 性能改善
- ✅ `測試` - 測試相關
- 🔧 `配置` - 配置檔案變更
- 🗑️ `移除` - 移除功能或檔案
- ⚠️ `不相容` - 不向下相容的變更
- 🔒 `安全` - 安全性相關修復

---

## 連結

- [未發布]: https://github.com/yourusername/PaddleOCR-VL/compare/v1.0.0...HEAD
- [1.0.0]: https://github.com/yourusername/PaddleOCR-VL/releases/tag/v1.0.0

