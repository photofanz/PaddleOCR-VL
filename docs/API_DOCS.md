# 📚 API 文件

PaddleOCR-VL Web Application REST API 完整文件。

## 📋 目錄

- [基本資訊](#基本資訊)
- [認證](#認證)
- [API 端點](#api-端點)
- [資料模型](#資料模型)
- [錯誤處理](#錯誤處理)
- [使用範例](#使用範例)

---

## 基本資訊

### Base URL

```
http://localhost:8000
```

### 內容類型

- **請求**：`application/json` 或 `multipart/form-data`（檔案上傳）
- **回應**：`application/json`

### 版本

當前版本：`v1.0.0`

---

## 認證

目前版本不需要認證。未來版本可能會加入 API Key 或 OAuth 認證。

---

## API 端點

### 1. 系統狀態

#### `GET /api/status`

獲取系統運行狀態與可用服務資訊。

**請求**

```http
GET /api/status HTTP/1.1
Host: localhost:8000
```

**回應**

```json
{
  "status": "running",
  "message": "系統運行中",
  "version": "1.0.0",
  "ocr_available": true,
  "gemini_available": true
}
```

**狀態碼**

- `200 OK` - 成功

---

### 2. 檔案上傳

#### `POST /api/upload`

上傳 PDF 或圖像檔案至伺服器。

**請求**

```http
POST /api/upload HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data

file: <binary>
```

**參數**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `file` | File | ✓ | PDF 或圖像檔案（PDF, PNG, JPG, JPEG） |

**回應**

```json
{
  "success": true,
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "file_type": "application/pdf",
  "message": "檔案上傳成功"
}
```

**狀態碼**

- `200 OK` - 上傳成功
- `400 Bad Request` - 檔案類型不支援
- `413 Payload Too Large` - 檔案太大（>50MB）
- `500 Internal Server Error` - 伺服器錯誤

---

### 3. OCR 辨識

#### `POST /api/process-ocr`

對已上傳的檔案執行 OCR 文字辨識。

**請求**

```http
POST /api/process-ocr HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "language": "en",
  "use_textline_orientation": true
}
```

**參數**

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `file_id` | string | ✓ | - | 檔案 ID（上傳時獲得） |
| `language` | string | ✗ | "en" | OCR 語言代碼 |
| `use_textline_orientation` | boolean | ✗ | true | 是否使用文字行方向檢測 |

**支援的語言代碼**

- `en` - 英文
- `ch_tra` - 繁體中文（映射到 `ch`）
- `ch_sim` - 簡體中文（映射到 `ch`）
- `japan` - 日文
- `korean` - 韓文
- `french` - 法文
- `german` - 德文
- `spanish` - 西班牙文

**注意**：在 PaddleOCR 3.3.0 版本中，繁體中文和簡體中文都使用相同的 `ch` 模型。

**回應**

```json
{
  "success": true,
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "raw_text": "辨識出的文字內容...",
  "layout_info": [
    [
      {
        "text": "文字片段",
        "confidence": 0.98
      }
    ]
  ],
  "message": "OCR 辨識完成",
  "processing_time": 2.34
}
```

**狀態碼**

- `200 OK` - 辨識成功
- `404 Not Found` - 檔案不存在
- `500 Internal Server Error` - OCR 處理失敗

---

### 4. Gemini AI 處理

#### `POST /api/enhance-with-gemini`

使用 Gemini API 處理文字（結構化、總結等）。

**請求**

```http
POST /api/enhance-with-gemini HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "text": "要處理的文字內容...",
  "prompt_type": "structure",
  "custom_prompt": null,
  "system_instruction": null
}
```

**參數**

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `text` | string | ✓ | - | 要處理的文字 |
| `prompt_type` | string | ✗ | "structure" | 提示詞類型 |
| `custom_prompt` | string | ✗ | null | 自訂提示詞（覆蓋 prompt_type） |
| `system_instruction` | string | ✗ | null | 系統指令 |

**提示詞類型**

- `structure` - 結構化為 Markdown
- `summarize` - 生成摘要
- `academic` - 學術論文分析（Paper to Obsidian）
- `custom` - 自訂（需提供 custom_prompt）

**回應**

```json
{
  "success": true,
  "processed_text": "處理後的文字內容...",
  "message": "Gemini 處理完成",
  "model_used": "gemini-2.0-flash-exp",
  "processing_time": 3.45
}
```

**狀態碼**

- `200 OK` - 處理成功
- `503 Service Unavailable` - Gemini API 不可用
- `500 Internal Server Error` - 處理失敗

---

### 5. 生成 Markdown

#### `POST /api/generate-markdown`

生成最終的 Markdown 檔案（可包含 Metadata）。

**請求**

```http
POST /api/generate-markdown HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "主要內容...",
  "include_metadata": true,
  "metadata": {
    "title": "文件標題",
    "authors": "作者姓名",
    "source": "來源",
    "year": 2025,
    "keywords": ["關鍵字1", "關鍵字2"],
    "abstract": "摘要內容",
    "custom_fields": {
      "custom_key": "custom_value"
    }
  }
}
```

**參數**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `file_id` | string | ✓ | 檔案 ID |
| `content` | string | ✓ | 主要內容 |
| `include_metadata` | boolean | ✗ | 是否包含 Metadata |
| `metadata` | object | ✗ | Metadata 物件 |

**Metadata 欄位**

| 欄位 | 類型 | 說明 |
|------|------|------|
| `title` | string | 標題 |
| `chinese_title` | string | 中文譯題 |
| `authors` | string | 作者 |
| `source` | string | 來源 |
| `year` | integer | 年份 |
| `keywords` | array[string] | 關鍵字陣列 |
| `abstract` | string | 摘要 |
| `custom_fields` | object | 自訂欄位（鍵值對） |

**回應**

```json
{
  "success": true,
  "markdown_content": "---\ntitle: \"文件標題\"\n...\n---\n\n內容...",
  "txt_content": "純文字內容（保持佈局）...",
  "message": "Markdown 生成成功"
}
```

**狀態碼**

- `200 OK` - 生成成功
- `404 Not Found` - 檔案不存在
- `500 Internal Server Error` - 生成失敗

---

### 6. 下載檔案

#### `GET /api/download/{file_id}/{format}`

下載生成的檔案。

**請求**

```http
GET /api/download/550e8400-e29b-41d4-a716-446655440000/md?filename=document HTTP/1.1
Host: localhost:8000
```

**路徑參數**

| 參數 | 類型 | 說明 |
|------|------|------|
| `file_id` | string | 檔案 ID |
| `format` | string | 下載格式（"md" 或 "txt"） |

**查詢參數**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `filename` | string | ✗ | 自訂檔名（不含副檔名） |

**回應**

檔案下載（`Content-Type: text/markdown` 或 `text/plain`）

**狀態碼**

- `200 OK` - 下載成功
- `404 Not Found` - 檔案不存在或尚未生成
- `500 Internal Server Error` - 下載失敗

---

### 7. 清理檔案

#### `DELETE /api/cleanup/{file_id}`

刪除上傳的檔案和臨時檔案。

**請求**

```http
DELETE /api/cleanup/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8000
```

**回應**

```json
{
  "success": true,
  "message": "檔案已清理"
}
```

**狀態碼**

- `200 OK` - 清理成功
- `404 Not Found` - 檔案不存在
- `500 Internal Server Error` - 清理失敗

---

## 資料模型

### MetadataFields

```typescript
interface MetadataFields {
  title?: string;
  chinese_title?: string;
  authors?: string;
  source?: string;
  year?: number;
  keywords?: string[];
  abstract?: string;
  custom_fields?: Record<string, string>;
}
```

### UploadResponse

```typescript
interface UploadResponse {
  success: boolean;
  file_id: string;
  filename: string;
  file_type: string;
  message: string;
}
```

### OCRResponse

```typescript
interface OCRResponse {
  success: boolean;
  file_id: string;
  raw_text: string;
  layout_info?: Array<Array<{
    text: string;
    confidence: number;
  }>>;
  message: string;
  processing_time?: number;
}
```

### GeminiResponse

```typescript
interface GeminiResponse {
  success: boolean;
  processed_text: string;
  message: string;
  model_used?: string;
  processing_time?: number;
}
```

---

## 錯誤處理

### 錯誤回應格式

```json
{
  "detail": "錯誤訊息描述"
}
```

### 常見錯誤碼

| 狀態碼 | 說明 |
|--------|------|
| 400 | 請求參數錯誤或格式不正確 |
| 404 | 資源不存在 |
| 413 | 檔案太大 |
| 500 | 伺服器內部錯誤 |
| 503 | 服務暫時不可用（如 Gemini API） |

---

## 使用範例

### 完整工作流程（Python）

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. 上傳檔案
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    upload_data = response.json()
    file_id = upload_data["file_id"]
    print(f"檔案已上傳：{file_id}")

# 2. OCR 辨識
ocr_request = {
    "file_id": file_id,
    "language": "en",
    "use_textline_orientation": True
}
response = requests.post(f"{BASE_URL}/api/process-ocr", json=ocr_request)
ocr_data = response.json()
raw_text = ocr_data["raw_text"]
print(f"OCR 完成，共 {len(raw_text)} 字元")

# 3. Gemini 處理
gemini_request = {
    "text": raw_text,
    "prompt_type": "structure"
}
response = requests.post(f"{BASE_URL}/api/enhance-with-gemini", json=gemini_request)
gemini_data = response.json()
processed_text = gemini_data["processed_text"]
print("Gemini 處理完成")

# 4. 生成 Markdown
markdown_request = {
    "file_id": file_id,
    "content": processed_text,
    "include_metadata": True,
    "metadata": {
        "title": "測試文件",
        "authors": "測試作者",
        "year": 2025,
        "keywords": ["測試", "範例"]
    }
}
response = requests.post(f"{BASE_URL}/api/generate-markdown", json=markdown_request)
print("Markdown 已生成")

# 5. 下載 Markdown
response = requests.get(f"{BASE_URL}/api/download/{file_id}/md?filename=test_document")
with open("test_document.md", "wb") as f:
    f.write(response.content)
print("檔案已下載：test_document.md")

# 6. 清理
requests.delete(f"{BASE_URL}/api/cleanup/{file_id}")
print("檔案已清理")
```

### 使用 cURL

```bash
# 1. 上傳檔案
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"

# 2. OCR 辨識
curl -X POST http://localhost:8000/api/process-ocr \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "YOUR_FILE_ID",
    "language": "en",
    "use_textline_orientation": true
  }'

# 3. 下載
curl -O http://localhost:8000/api/download/YOUR_FILE_ID/md?filename=document
```

---

## 互動式文件

啟動應用後，訪問 http://localhost:8000/docs 可查看自動生成的互動式 API 文件（Swagger UI），支援線上測試所有 API。

---

**如有疑問，請參閱主要文件或提出 Issue。** 📝

