# 📚 API Documentation

Complete REST API documentation for PaddleOCR-VL Web Application.

## 📋 Table of Contents

- [Basic Information](#basic-information)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

---

## Basic Information

### Base URL

```
http://localhost:8001
```

### Content Types

- **Request**: `application/json` or `multipart/form-data` (file upload)
- **Response**: `application/json`

### Version

Current version: `v1.0.0`

---

## Authentication

Current version does not require authentication. Future versions may include API Key or OAuth authentication.

---

## API Endpoints

### 1. System Status

#### `GET /api/status`

Get system running status and available service information.

**Request**

```http
GET /api/status HTTP/1.1
Host: localhost:8001
```

**Response**

```json
{
  "status": "running",
  "message": "System is running",
  "version": "1.0.0",
  "ocr_available": true,
  "gemini_available": true
}
```

**Status Codes**

- `200 OK` - Success

---

### 2. File Upload

#### `POST /api/upload`

Upload PDF or image files to server.

**Request**

```http
POST /api/upload HTTP/1.1
Host: localhost:8001
Content-Type: multipart/form-data

file: <binary>
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✓ | PDF or image file (PDF, PNG, JPG, JPEG) |

**Response**

```json
{
  "success": true,
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "file_type": "application/pdf",
  "message": "File uploaded successfully"
}
```

**Status Codes**

- `200 OK` - Upload successful
- `400 Bad Request` - Unsupported file type
- `413 Payload Too Large` - File too large (>50MB)
- `500 Internal Server Error` - Server error

---

### 3. OCR Recognition

#### `POST /api/process-ocr`

Execute OCR text recognition on uploaded files.

**Request**

```http
POST /api/process-ocr HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "language": "en",
  "use_textline_orientation": true
}
```

**Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_id` | string | ✓ | - | File ID (obtained from upload) |
| `language` | string | ✗ | "en" | OCR language code |
| `use_textline_orientation` | boolean | ✗ | true | Whether to use text line orientation detection |

**Supported Language Codes**

- `en` - English
- `ch_tra` - Traditional Chinese (mapped to `ch`)
- `ch_sim` - Simplified Chinese (mapped to `ch`)
- `japan` - Japanese
- `korean` - Korean
- `french` - French
- `german` - German
- `spanish` - Spanish

**Note**: In PaddleOCR 3.3.0, both Traditional and Simplified Chinese use the same `ch` model.

**Response**

```json
{
  "success": true,
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "raw_text": "Recognized text content...",
  "layout_info": [
    [
      {
        "text": "Text fragment",
        "confidence": 0.98
      }
    ]
  ],
  "message": "OCR recognition completed",
  "processing_time": 2.34
}
```

**Status Codes**

- `200 OK` - Recognition successful
- `404 Not Found` - File not found
- `500 Internal Server Error` - OCR processing failed

---

### 4. Gemini AI Processing

#### `POST /api/enhance-with-gemini`

Use Gemini API to process text (structuring, summarization, etc.).

**Request**

```http
POST /api/enhance-with-gemini HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "text": "Text content to process...",
  "prompt_type": "structure",
  "custom_prompt": null,
  "system_instruction": null
}
```

**Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | ✓ | - | Text to process |
| `prompt_type` | string | ✗ | "structure" | Prompt type |
| `custom_prompt` | string | ✗ | null | Custom prompt (overrides prompt_type) |
| `system_instruction` | string | ✗ | null | System instruction |

**Prompt Types**

- `structure` - Structure as Markdown
- `summarize` - Generate summary
- `academic` - Academic paper analysis (Paper to Obsidian)
- `custom` - Custom (requires custom_prompt)

**Response**

```json
{
  "success": true,
  "processed_text": "Processed text content...",
  "message": "Gemini processing completed",
  "model_used": "gemini-2.0-flash-exp",
  "processing_time": 3.45
}
```

**Status Codes**

- `200 OK` - Processing successful
- `503 Service Unavailable` - Gemini API unavailable
- `500 Internal Server Error` - Processing failed

---

### 5. Generate Markdown

#### `POST /api/generate-markdown`

Generate final Markdown file (may include Metadata).

**Request**

```http
POST /api/generate-markdown HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Main content...",
  "include_metadata": true,
  "metadata": {
    "title": "Document Title",
    "authors": "Author Name",
    "source": "Source",
    "year": 2025,
    "keywords": ["keyword1", "keyword2"],
    "abstract": "Abstract content",
    "custom_fields": {
      "custom_key": "custom_value"
    }
  }
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | ✓ | File ID |
| `content` | string | ✓ | Main content |
| `include_metadata` | boolean | ✗ | Whether to include Metadata |
| `metadata` | object | ✗ | Metadata object |

**Metadata Fields**

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Title |
| `chinese_title` | string | Chinese translation title |
| `authors` | string | Authors |
| `source` | string | Source |
| `year` | integer | Year |
| `keywords` | array[string] | Keywords array |
| `abstract` | string | Abstract |
| `custom_fields` | object | Custom fields (key-value pairs) |

**Response**

```json
{
  "success": true,
  "markdown_content": "---\ntitle: \"Document Title\"\n...\n---\n\nContent...",
  "txt_content": "Plain text content (maintaining layout)...",
  "message": "Markdown generation successful"
}
```

**Status Codes**

- `200 OK` - Generation successful
- `404 Not Found` - File not found
- `500 Internal Server Error` - Generation failed

---

### 6. Download File

#### `GET /api/download/{file_id}/{format}`

Download generated files.

**Request**

```http
GET /api/download/550e8400-e29b-41d4-a716-446655440000/md?filename=document HTTP/1.1
Host: localhost:8001
```

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_id` | string | File ID |
| `format` | string | Download format ("md" or "txt") |

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filename` | string | ✗ | Custom filename (without extension) |

**Response**

File download (`Content-Type: text/markdown` or `text/plain`)

**Status Codes**

- `200 OK` - Download successful
- `404 Not Found` - File not found or not generated
- `500 Internal Server Error` - Download failed

---

### 7. Cleanup Files

#### `DELETE /api/cleanup/{file_id}`

Delete uploaded files and temporary files.

**Request**

```http
DELETE /api/cleanup/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8001
```

**Response**

```json
{
  "success": true,
  "message": "Files cleaned up"
}
```

**Status Codes**

- `200 OK` - Cleanup successful
- `404 Not Found` - File not found
- `500 Internal Server Error` - Cleanup failed

---

## Data Models

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

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Request parameter error or incorrect format |
| 404 | Resource not found |
| 413 | File too large |
| 500 | Internal server error |
| 503 | Service temporarily unavailable (e.g., Gemini API) |

---

## Usage Examples

### Complete Workflow (Python)

```python
import requests
import json

BASE_URL = "http://localhost:8001"

# 1. Upload file
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    upload_data = response.json()
    file_id = upload_data["file_id"]
    print(f"File uploaded: {file_id}")

# 2. OCR recognition
ocr_request = {
    "file_id": file_id,
    "language": "en",
    "use_textline_orientation": True
}
response = requests.post(f"{BASE_URL}/api/process-ocr", json=ocr_request)
ocr_data = response.json()
raw_text = ocr_data["raw_text"]
print(f"OCR completed, {len(raw_text)} characters")

# 3. Gemini processing
gemini_request = {
    "text": raw_text,
    "prompt_type": "structure"
}
response = requests.post(f"{BASE_URL}/api/enhance-with-gemini", json=gemini_request)
gemini_data = response.json()
processed_text = gemini_data["processed_text"]
print("Gemini processing completed")

# 4. Generate Markdown
markdown_request = {
    "file_id": file_id,
    "content": processed_text,
    "include_metadata": True,
    "metadata": {
        "title": "Test Document",
        "authors": "Test Author",
        "year": 2025,
        "keywords": ["test", "example"]
    }
}
response = requests.post(f"{BASE_URL}/api/generate-markdown", json=markdown_request)
print("Markdown generated")

# 5. Download Markdown
response = requests.get(f"{BASE_URL}/api/download/{file_id}/md?filename=test_document")
with open("test_document.md", "wb") as f:
    f.write(response.content)
print("File downloaded: test_document.md")

# 6. Cleanup
requests.delete(f"{BASE_URL}/api/cleanup/{file_id}")
print("Files cleaned up")
```

### Using cURL

```bash
# 1. Upload file
curl -X POST http://localhost:8001/api/upload \
  -F "file=@document.pdf"

# 2. OCR recognition
curl -X POST http://localhost:8001/api/process-ocr \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "YOUR_FILE_ID",
    "language": "en",
    "use_textline_orientation": true
  }'

# 3. Download
curl -O http://localhost:8001/api/download/YOUR_FILE_ID/md?filename=document
```

---

## Interactive Documentation

After starting the application, visit http://localhost:8001/docs to view auto-generated interactive API documentation (Swagger UI), supporting online testing of all APIs.

---

**For questions, please refer to the main documentation or submit an Issue.** 📝
