# 🔍 PaddleOCR-VL Web Application

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.3.0-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Local PaddleOCR Recognition + Gemini AI Intelligent Structuring Hybrid Document Processing System**

[Features](#✨-features) • [Quick Start](#🚀-quick-start) • [Installation Guide](#📦-installation-guide) • [Usage](#💡-usage) • [API Documentation](#📚-api-documentation) • [Contributing](#🤝-contributing)

</div>

---

## 📖 Project Overview

PaddleOCR-VL Web Application is a document processing system that combines local OCR technology with cloud AI capabilities. It uses CPU mode on Apple Silicon (M3 Max) for stable and reliable text recognition, and leverages Gemini API for intelligent text structuring and analysis.

### 🎯 Design Philosophy

- **Local First**: Core OCR processing runs locally, ensuring data privacy and processing speed
- **AI Enhanced**: Utilizes Gemini API's language understanding capabilities to convert raw text into structured content
- **User Friendly**: Provides a modern web interface without command-line operations
- **Open Source**: Fully open source, easy to customize and extend

## ✨ Features

### Core Features

- 📄 **Multi-format Support**: PDF, PNG, JPG, JPEG file uploads
- 🌍 **Multi-language Recognition**: Supports English, Traditional Chinese, Simplified Chinese, Japanese, Korean, etc.
- ⚡ **Stable Processing**: Uses CPU mode to ensure optimal compatibility and stability
- 🤖 **AI Intelligent Processing**:
  - Structured Markdown conversion
  - Content summarization
  - Academic paper analysis (Paper to Obsidian style)
  - Custom prompt processing

### Advanced Features

- 🏷️ **Metadata Management**: Paper to Obsidian style YAML frontmatter
- 📝 **Dual Format Download**:
  - `.md` - Structured Markdown (suitable for Obsidian, Notion)
  - `.txt` - Plain text maintaining original layout
- 🎨 **Modern Interface**: Responsive design supporting desktop and mobile devices
- 🔄 **Real-time Preview**: Markdown rendering preview

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Interface (Web UI)             │
│           HTML5 + CSS3 + JavaScript + Marked.js            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────────┐
│                   FastAPI Backend Service                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ OCR Service  │  │Gemini Service│  │ Utils Module │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘     │
│         │                  │                                │
│  ┌──────▼───────┐  ┌──────▼───────┐                        │
│  │ PaddleOCR    │  │  Gemini API  │                        │
│  │ (Local CPU)  │  │   (Cloud)   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.12
- FastAPI (Web framework)
- PaddlePaddle + PaddleOCR 3.3.0 (OCR engine, CPU mode)
- PyMuPDF (PDF processing)
- Google Generative AI (Gemini API)

**Frontend:**
- Native HTML/CSS/JavaScript
- Marked.js (Markdown rendering)
- Responsive design

## 🚀 Quick Start

### System Requirements

- macOS (recommended Apple Silicon M1/M2/M3)
- Python 3.12+
- Conda (environment management)
- At least 8GB RAM
- At least 5GB available storage

### 3-Step Quick Launch

```bash
# 1. Clone project and create environment
git clone https://github.com/photofanz/PaddleOCR-VL.git
cd PaddleOCR-VL
conda create -n paddle-ocr python=3.12 -y
conda activate paddle-ocr

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables and start
cp .env.example .env
# Edit .env file, set GEMINI_API_KEY
python run.py
```

The service will start at `http://localhost:8001`.

## 📦 Installation Guide

### Detailed Installation Steps

Please refer to [INSTALLATION_EN.md](docs/INSTALLATION_EN.md) for complete installation guide, including:

- Conda environment setup
- PaddleOCR verification
- Gemini API Key acquisition and configuration
- Common troubleshooting

### Verify Installation

After installation, run the verification script:

```bash
python verify_paddle_mps.py --lang en
```

This will test if PaddleOCR is correctly installed and running in CPU mode.

## 💡 Usage

### Basic Workflow

1. **Upload Document**
   - Support drag-and-drop or click to upload
   - File size limit: 50MB

2. **OCR Recognition**
   - Select recognition language
   - Enable angle classification (improves accuracy)
   - Click "Start OCR Recognition"

3. **Add Metadata (Optional)**
   - Enable Metadata functionality
   - Fill in title, author, source, etc.
   - Support custom fields

4. **AI Intelligent Processing**
   - Choose processing mode (structured/summary/academic analysis)
   - Edit or customize prompts
   - Use Gemini processing or skip

5. **Preview and Download**
   - View Markdown preview or source code
   - Download .md or .txt format

### Usage Examples

#### Example 1: Paper to Obsidian Notes

1. Upload paper PDF
2. Select language "English"
3. After OCR recognition, enable Metadata
4. Fill in paper information (title, author, journal, etc.)
5. Select "Academic Paper Analysis" mode
6. Use Gemini processing
7. Download .md file to Obsidian Vault

#### Example 2: Quick Document Digitization

1. Upload scanned document images
2. Select corresponding language
3. OCR recognition
4. Skip AI processing
5. Download .txt file (maintains original layout)

## 📚 API Documentation

Complete API documentation:
- [API_DOCS_EN.md](docs/API_DOCS_EN.md) - Detailed REST API documentation
- `/docs` - FastAPI auto-generated interactive documentation

### Main API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload file |
| `/api/process-ocr` | POST | Execute OCR recognition |
| `/api/enhance-with-gemini` | POST | Use Gemini to process text |
| `/api/generate-markdown` | POST | Generate Markdown file |
| `/api/download/{file_id}/{format}` | GET | Download file |

## 🎨 Interface Preview

(Screenshots recommended here)

## 🛠️ Development Guide

### Local Development

```bash
# Start in development mode (enable hot reload)
DEBUG=True python run.py
```

### Run Tests

```bash
# Run unit tests
pytest tests/

# Run OCR verification
python verify_paddle_mps.py
```

### Project Structure

```
PaddleOCR-VL/
├── app/                    # Backend application
│   ├── main.py            # FastAPI main application
│   ├── services.py        # OCR service
│   ├── gemini_service.py  # Gemini API integration
│   ├── utils.py           # Utility functions
│   └── models.py       # Data models
├── static/                 # Frontend static files
│   ├── app.html           # Main application interface
│   ├── app.js             # Frontend logic
│   ├── styles.css         # Styles
│   └── guide.html         # Deployment guide
├── docs/                   # Documentation
├── tests/                  # Tests
├── run.py                  # Startup script
└── requirements.txt        # Python dependencies
```

## 🤝 Contributing

Contributions are welcome! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) - Deep learning framework
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR toolkit
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Google Generative AI](https://ai.google.dev/) - Gemini API

## 📮 Contact

- GitHub Issues: [Report Issues](https://github.com/photofanz/PaddleOCR-VL/issues)
- Discussion: [GitHub Discussions](https://github.com/photofanz/PaddleOCR-VL/discussions)

## 🗺️ Roadmap

- [ ] Support more OCR languages
- [ ] Batch processing functionality
- [ ] Table recognition and structuring
- [ ] Docker containerized deployment
- [ ] User authentication and multi-user support
- [ ] History and file management
- [ ] Local deployment lightweight LLM support

---

<div align="center">

If this project helps you, please give it a ⭐️ Star!

Made with ❤️ by [Your Name]

</div>
