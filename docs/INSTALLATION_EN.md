# 📦 Installation Guide

This guide will help you completely install and configure PaddleOCR-VL Web Application on macOS (Apple Silicon).

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Gemini API Setup](#gemini-api-setup)
- [Verify Installation](#verify-installation)
- [Common Issues](#common-issues)

---

## System Requirements

### Hardware Requirements

- **Processor**: Apple Silicon (M1/M2/M3) or Intel
  - Recommended: M3 Max or higher chips
- **Memory**: Minimum 8GB RAM
  - Recommended: 16GB or more
- **Storage**: Minimum 5GB available space
  - Includes model files and dependencies

### Software Requirements

- **Operating System**: macOS 12.0 (Monterey) or newer
- **Python**: 3.12 or newer
- **Conda**: Recommended to use Miniconda or Anaconda

---

## Installation Steps

### Step 1: Install Conda (if not already installed)

If you don't have Conda installed, follow these steps:

#### Method 1: Using Homebrew

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Miniconda
brew install --cask miniconda
```

#### Method 2: Manual Installation

1. Download Miniconda: https://docs.conda.io/en/latest/miniconda.html
2. Choose macOS Apple M1 (ARM64) version
3. Run the installer

Initialize Conda:

```bash
conda init zsh  # if using zsh
# or
conda init bash  # if using bash

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

### Step 2: Clone Project

```bash
# Clone project
git clone https://github.com/photofanz/PaddleOCR-VL.git
cd PaddleOCR-VL
```

### Step 3: Create Conda Environment

```bash
# Create environment named paddle-ocr with Python 3.12
conda create -n paddle-ocr python=3.12 -y

# Activate environment
conda activate paddle-ocr
```

**Important**: You need to activate this environment every time you use it:

```bash
conda activate paddle-ocr
```

### Step 4: Install Python Dependencies

```bash
# Install all dependency packages
pip install -r requirements.txt
```

This step will install:

- **PaddlePaddle**: Deep learning framework (CPU mode)
- **PaddleOCR 3.3.0**: OCR toolkit
- **FastAPI**: Web framework
- **PyMuPDF**: PDF processing
- **Google Generative AI**: Gemini API client
- Other related packages

**Note**: First installation may take 10-20 minutes depending on network speed.

### Step 5: Set Environment Variables

```bash
# Copy environment variable template
cp .env.example .env

# Open .env file with editor
nano .env  # or use vim, VSCode, etc.
```

Edit the `.env` file and set necessary parameters:

```ini
# Gemini API Settings
GEMINI_API_KEY=your_gemini_api_key_here  # Replace with your API Key

# Server Settings
HOST=0.0.0.0
PORT=8001
DEBUG=True

# File Upload Settings
MAX_UPLOAD_SIZE=52428800  # 50MB

# OCR Settings
DEFAULT_OCR_LANGUAGE=en
USE_GPU=False  # Use CPU mode for stability

# Gemini Settings
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_MAX_RETRIES=3
GEMINI_TIMEOUT=60
```

---

## Gemini API Setup

Gemini API is used for intelligent text processing. If you don't need AI processing features, you can skip this step.

### Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Log in with your Google account
3. Click "Get API Key"
4. Create a new API Key or use existing one
5. Copy the API Key

### Set API Key

Method 1: Set in `.env` file

```ini
GEMINI_API_KEY=AIza...your_actual_key
```

Method 2: Use environment variable (temporary)

```bash
export GEMINI_API_KEY="AIza...your_actual_key"
```

### Free Quota

Gemini API provides generous free quota:
- gemini-2.0-flash-exp: 15 requests per minute
- gemini-pro: 60 requests per minute

For details, see: https://ai.google.dev/pricing

---

## Verify Installation

### Verify PaddleOCR and CPU Mode

Run the verification script:

```bash
python verify_paddle_mps.py
```

**Expected Output:**

```
============================================================
  PaddleOCR CPU Verification Script
  Apple Silicon (M3 Max) Test
============================================================

============================================================
  1. Check PaddleOCR Installation
============================================================
✓ PaddleOCR installed
  Version: 2.7.3

============================================================
  2. Check PaddlePaddle Backend
============================================================
✓ PaddlePaddle installed
  Version: 3.0.0
  ℹ Using CPU mode (ensuring optimal stability)

============================================================
  3. Create Test Image
============================================================
✓ Test image created: test_image.png
  Size: (800, 400)

============================================================
  4. Test OCR (CPU mode, language: en)
============================================================
Initializing PaddleOCR (CPU)...
✓ Initialization complete, took 2.34 seconds
Processing image: test_image.png
✓ OCR complete, took 1.87 seconds

Recognition results:
  1. [0.98] PaddleOCR Test Image
  2. [0.96] Apple M3 Max
  3. [0.97] MacBook Pro 2024
  4. [0.95] This is a test for OCR recognition

============================================================
  5. Test OCR (CPU mode, language: ch)
============================================================
Initializing PaddleOCR (CPU)...
✓ Initialization complete, took 2.45 seconds
  ℹ Using CPU mode for stability
Processing image: test_image.png
✓ OCR complete, took 1.95 seconds

Recognition results:
  1. [0.98] PaddleOCR 測試圖像
  2. [0.96] Apple M3 Max
  3. [0.97] MacBook Pro 2024
  4. [0.95] 這是 OCR 辨識測試

============================================================
Test Summary
============================================================
CPU mode (English): ✓ Success
  Processing time: 1.87 seconds
CPU mode (Chinese): ✓ Success
  Processing time: 1.95 seconds
  Stability: Excellent

============================================================

✓ Verification complete!
```

If you see output similar to the above, the installation is successful!

### Verify Web Application

Start the application:

```bash
python run.py
```

**Expected Output:**

```
============================================================
PaddleOCR-VL Web Application
============================================================
Host: 0.0.0.0
Port: 8001
Debug mode: True
============================================================

🌐 Application URL: http://localhost:8001
📖 Deployment Guide: http://localhost:8001/guide
📊 API Documentation: http://localhost:8001/docs
🔍 System Status: http://localhost:8001/api/status

Press Ctrl+C to stop server

============================================================
INFO:     Will watch for changes in these directories: ['/path/to/PaddleOCR-VL']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
============================================================
  PaddleOCR-VL Web Application starting...
  Version: 1.0.0
============================================================
✓ OCR service initialized (language: en, CPU: True)
✓ Gemini API ready (model: gemini-2.0-flash-exp)
============================================================
✓ Application startup complete
============================================================
```

Open browser and visit:

- **Main Application**: http://localhost:8001
- **Deployment Guide**: http://localhost:8001/guide
- **API Documentation**: http://localhost:8001/docs
- **System Status**: http://localhost:8001/api/status

---

## Common Issues

### Q1: Error installing PaddlePaddle

**A1:** Ensure you're using Python 3.12 and the Conda environment is correctly activated:

```bash
# Check Python version
python --version  # Should show Python 3.12.x

# Confirm in correct environment
conda info --envs  # paddle-ocr should have asterisk

# Reinstall
pip install --upgrade pip
pip install paddlepaddle --no-cache-dir
```

### Q2: PaddleOCR model download failed

**A2:** PaddleOCR automatically downloads models on first OCR execution. If download fails:

1. Check network connection
2. Try using VPN (may be needed in some regions)
3. Manually download models:

```bash
# Go to PaddleOCR model repository
# https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_ch/models_list.md

# Download and place in ~/.paddleocr/ directory
```

### Q3: Gemini API returns 403 error

**A3:**

1. Check if API Key is correctly set
2. Confirm API Key is not expired
3. Check if API quota is exhausted
4. Visit Google AI Studio to confirm API status

### Q4: Can it be used on Intel Mac?

**A4:** Yes! This application uses CPU mode and runs normally on Intel Mac:

1. Ensure `USE_GPU` is set to `False` in `.env`
2. Processing speed is similar to Apple Silicon
3. All features are identical

### Q5: How to update to latest version?

**A5:**

```bash
# Pull latest code
git pull origin main

# Update dependencies
conda activate paddle-ocr
pip install -r requirements.txt --upgrade

# Restart application
python run.py
```

### Q6: Application won't start, port already in use

**A6:** Port 8001 is occupied by another program. Solutions:

Method 1: Change `PORT` in `.env` file

```ini
PORT=8002  # Change to other port
```

Method 2: Terminate program using port 8001

```bash
# Find the program using the port
lsof -i :8001

# Terminate the program (replace PID)
kill -9 <PID>
```

### Q7: Error when uploading large PDF

**A7:**

1. Check if file size exceeds 50MB limit
2. Modify `MAX_UPLOAD_SIZE` in `.env` (unit: bytes)
3. Large PDFs may require more memory

### Q8: OCR recognition results are inaccurate

**A8:** Methods to improve accuracy:

1. Ensure correct language is selected
2. Enable "Use angle classification"
3. Increase scan/photo resolution (recommend 300 DPI or higher)
4. Ensure images are clear without blur or distortion

---

## Need Help?

If you encounter other issues:

1. Check [GitHub Issues](https://github.com/photofanz/PaddleOCR-VL/issues)
2. Ask in [Discussions](https://github.com/photofanz/PaddleOCR-VL/discussions)
3. Refer to [PaddleOCR Official Documentation](https://github.com/PaddlePaddle/PaddleOCR/tree/main/doc)

---

**Enjoy using it!** 🎉
