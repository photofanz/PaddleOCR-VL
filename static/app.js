/**
 * PaddleOCR-VL Web Application - 前端邏輯
 * 處理檔案上傳、OCR、AI 處理和下載
 */

// 全域狀態
const appState = {
    currentFileId: null,
    currentFilename: null,
    ocrRawText: null,
    processedText: null,
    markdownContent: null,
    txtContent: null,
    currentStep: 1
};

// 預設提示詞
const DEFAULT_PROMPTS = {
    structure: `你是一個專業的文件格式化助手。請將以下 OCR 辨識的原始文字，轉換為結構良好、易於閱讀的 Markdown 文件。

要求：
1. 保留所有原始內容，不要遺漏任何資訊
2. 準確識別並添加適當的標題層級（# ## ###）
3. 識別並格式化列表（有序或無序）
4. 識別並格式化表格
5. 識別並使用代碼塊標記程式碼
6. 適當地分段，提升可讀性
7. 保持專業術語的準確性
8. 如果有數學公式，使用 LaTeX 格式（$...$）

請直接輸出格式化後的 Markdown，不要添加額外的說明。`,

    summarize: `你是一個專業的總結助手。請為以下 OCR 辨識出的內容提供一個簡潔、準確、條列式的總結。

要求：
1. 提取主要觀點和關鍵資訊
2. 使用條列式呈現（使用 - 或數字）
3. 保持客觀，不添加個人觀點
4. 確保總結的完整性和準確性
5. 使用清晰易懂的語言
6. 適當使用 Markdown 格式（粗體、斜體等）

請直接輸出總結內容。`,

    academic: `你是一個專業的學術論文分析助手。請分析以下論文內容，並提供結構化導讀。

請按照以下結構組織內容（參考 Paper to Obsidian 格式）：

## 🧩 Paper-to-Outline (p2o)

### 一、研究基本資訊
* **標題**：[論文標題]
* **中文譯題**：[中文翻譯]（如適用）
* **作者**：[作者列表]
* **期刊/會議**：[發表場所]
* **年份**：[年份]
* **理論核心**：[核心理論]

### 二、研究動機與問題意識
[描述研究背景、gap 和核心問題]

### 三、理論架構
[理論基礎、主要構念、研究假設]

### 四、研究方法
[樣本、設計、分析工具、信效度]

### 五、主要發現
[關鍵研究結果]

### 六、理論與實務貢獻
[理論面和實務面的貢獻]

### 七、限制與未來研究方向
[研究限制和建議]

### 八、結論一句話
> [用一句話總結核心貢獻]

請根據提供的內容盡可能完整地填寫以上結構。如果某些資訊無法從文本中提取，可以標註 [資訊不足]。`
};

// DOM 載入完成後初始化
document.addEventListener('DOMContentLoaded', init);

function init() {
    console.log('🚀 PaddleOCR-VL 應用初始化中...');
    setupEventListeners();
    updatePromptPreview();
    checkSystemStatus();
}

// 設置所有事件監聽器
function setupEventListeners() {
    // 檔案上傳
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // 拖放
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);
    
    // 移除檔案
    document.getElementById('remove-file').addEventListener('click', resetUpload);
    
    // OCR
    document.getElementById('start-ocr-btn').addEventListener('click', startOCR);
    
    // Metadata
    document.getElementById('enable-metadata').addEventListener('change', toggleMetadata);
    document.getElementById('add-custom-field').addEventListener('click', addCustomField);
    
    // AI 處理
    document.getElementById('prompt-type').addEventListener('change', updatePromptPreview);
    document.getElementById('edit-prompt').addEventListener('change', togglePromptEdit);
    document.getElementById('process-with-ai-btn').addEventListener('click', processWithAI);
    document.getElementById('skip-ai-btn').addEventListener('click', skipAI);
    
    // 預覽標籤
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', switchTab);
    });
    
    // 下載
    document.getElementById('download-md-btn').addEventListener('click', () => downloadFile('md'));
    document.getElementById('download-txt-btn').addEventListener('click', () => downloadFile('txt'));
    document.getElementById('restart-btn').addEventListener('click', restartProcess);
}

// ============================================================================
// 檔案上傳處理
// ============================================================================

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}

function handleFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        processFile(file);
    }
}

async function processFile(file) {
    // 驗證檔案類型
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
        showToast('不支援的檔案類型', 'error');
        return;
    }
    
    // 驗證檔案大小 (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('檔案太大（最大 50MB）', 'error');
        return;
    }
    
    // 顯示檔案資訊
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    document.getElementById('upload-area').classList.add('hidden');
    document.getElementById('file-info').classList.remove('hidden');
    
    appState.currentFilename = file.name;
    
    // 上傳檔案
    await uploadFile(file);
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        console.log('📤 開始上傳檔案:', file.name);
        showToast('正在上傳檔案...', 'info');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            appState.currentFileId = data.file_id;
            showToast('檔案上傳成功！', 'success');
            moveToStep(2);
            document.getElementById('ocr-section').classList.remove('hidden');
        } else {
            throw new Error(data.detail || '上傳失敗');
        }
    } catch (error) {
        let errorMessage = '上傳失敗: ';
        if (error.message === 'Failed to fetch') {
            errorMessage += '無法連接到伺服器，請確認後端服務是否正常運行 (http://localhost:8000)';
        } else {
            errorMessage += error.message;
        }
        showToast(errorMessage, 'error');
        resetUpload();
    }
}

function resetUpload() {
    document.getElementById('upload-area').classList.remove('hidden');
    document.getElementById('file-info').classList.add('hidden');
    document.getElementById('file-input').value = '';
    document.getElementById('ocr-section').classList.add('hidden');
    appState.currentFileId = null;
    appState.currentFilename = null;
    moveToStep(1);
}

// ============================================================================
// OCR 處理
// ============================================================================

async function startOCR() {
    if (!appState.currentFileId) {
        showToast('請先上傳檔案', 'error');
        return;
    }
    
    const language = document.getElementById('ocr-language').value;
    const useTextlineOrientation = document.getElementById('use-angle-cls').checked;
    const btn = document.getElementById('start-ocr-btn');
    const progress = document.getElementById('ocr-progress');
    const progressFill = document.getElementById('ocr-progress-fill');
    const progressText = document.getElementById('ocr-progress-text');
    const progressTime = document.getElementById('ocr-progress-time');
    
    btn.disabled = true;
    btn.textContent = '處理中...';
    progress.classList.remove('hidden');
    
    // 動畫進度條與狀態顯示
    let progressValue = 0;
    let startTime = Date.now();
    let statusMessages = [
        "正在初始化 OCR 引擎...",
        "載入模型檔案...",
        "處理圖像檔案...",
        "執行文字辨識...",
        "分析文字佈局...",
        "完成處理..."
    ];
    let messageIndex = 0;
    
    const progressInterval = setInterval(() => {
        progressValue = Math.min(progressValue + 15, 90);
        progressFill.style.width = `${progressValue}%`;
        
        // 更新狀態訊息
        if (messageIndex < statusMessages.length) {
            progressText.textContent = statusMessages[messageIndex];
            messageIndex++;
        }
        
        // 計算預估剩餘時間
        const elapsed = (Date.now() - startTime) / 1000;
        const estimatedTotal = elapsed / (progressValue / 100);
        const remaining = Math.max(0, estimatedTotal - elapsed);
        
        if (remaining > 0) {
            progressTime.textContent = `預估剩餘時間: ${Math.round(remaining)} 秒`;
        } else {
            progressTime.textContent = '即將完成...';
        }
    }, 2000); // 每2秒更新一次狀態
    
    // 宣告變數在 try 區塊外
    let heartbeatInterval = null;
    
    try {
        // 創建 AbortController 用於超時控制
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5分鐘超時
        
        // 心跳檢測 - 每30秒檢查一次後端狀態
        heartbeatInterval = setInterval(async () => {
            try {
                const statusResponse = await fetch('/api/status');
                if (statusResponse.ok) {
                    console.log('✓ 後端服務正常運行');
                } else {
                    console.warn('⚠️ 後端服務狀態異常');
                }
            } catch (error) {
                console.error('❌ 無法連接到後端服務:', error);
            }
        }, 30000); // 每30秒檢查一次
        
        const response = await fetch('/api/process-ocr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: appState.currentFileId,
                language: language,
                use_textline_orientation: useTextlineOrientation
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval); // 清除心跳檢測
        }
        
        const data = await response.json();
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = '處理完成！';
        
        if (response.ok && data.success) {
            appState.ocrRawText = data.raw_text;
            
            // 顯示結果
            document.getElementById('ocr-output').value = data.raw_text;
            document.getElementById('processing-time').textContent = `${data.processing_time.toFixed(2)} 秒`;
            document.getElementById('char-count').textContent = data.raw_text.length.toLocaleString();
            
            // 顯示結果區域
            document.getElementById('result-section').classList.remove('hidden');
            document.getElementById('metadata-section').classList.remove('hidden');
            document.getElementById('ai-section').classList.remove('hidden');
            
            moveToStep(3);
            showToast('OCR 辨識完成！', 'success');
            
            // 滾動到結果區
            document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(data.detail || 'OCR 處理失敗');
        }
    } catch (error) {
        clearInterval(progressInterval);
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval); // 清除心跳檢測
        }
        progressText.textContent = '處理失敗';
        
        let errorMessage = 'OCR 處理失敗: ';
        
        if (error.name === 'AbortError') {
            errorMessage += '處理超時（5分鐘），請嘗試較小的檔案或稍後再試';
        } else if (error.message === 'Failed to fetch') {
            errorMessage += '無法連接到伺服器，請確認後端服務是否正常運行';
        } else {
            errorMessage += error.message;
        }
        
        showToast(errorMessage, 'error');
        console.error('OCR 處理錯誤:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = '🚀 開始 OCR 辨識';
        setTimeout(() => {
            progress.classList.add('hidden');
            progressFill.style.width = '0%';
        }, 1000);
    }
}

// ============================================================================
// Metadata 管理
// ============================================================================

function toggleMetadata() {
    const enabled = document.getElementById('enable-metadata').checked;
    const fields = document.getElementById('metadata-fields');
    
    if (enabled) {
        fields.classList.remove('hidden');
    } else {
        fields.classList.add('hidden');
    }
}

function addCustomField() {
    const container = document.getElementById('custom-fields-container');
    const row = document.createElement('div');
    row.className = 'custom-field-row';
    row.innerHTML = `
        <input type="text" placeholder="欄位名稱" class="custom-field-key">
        <input type="text" placeholder="欄位值" class="custom-field-value">
        <button class="btn-icon" onclick="removeCustomField(this)">🗑️</button>
    `;
    container.appendChild(row);
}

function removeCustomField(btn) {
    btn.parentElement.remove();
}

function collectMetadata() {
    const enabled = document.getElementById('enable-metadata').checked;
    
    if (!enabled) {
        return null;
    }
    
    const metadata = {
        title: document.getElementById('meta-title').value || null,
        chinese_title: document.getElementById('meta-chinese-title').value || null,
        authors: document.getElementById('meta-authors').value || null,
        source: document.getElementById('meta-source').value || null,
        year: parseInt(document.getElementById('meta-year').value) || null,
        keywords: null,
        abstract: document.getElementById('meta-abstract').value || null,
        custom_fields: {}
    };
    
    // 處理關鍵字
    const keywordsInput = document.getElementById('meta-keywords').value;
    if (keywordsInput) {
        metadata.keywords = keywordsInput.split(',').map(k => k.trim()).filter(k => k);
    }
    
    // 收集自訂欄位
    document.querySelectorAll('.custom-field-row').forEach(row => {
        const key = row.querySelector('.custom-field-key').value;
        const value = row.querySelector('.custom-field-value').value;
        if (key && value) {
            metadata.custom_fields[key] = value;
        }
    });
    
    return metadata;
}

// ============================================================================
// AI 處理
// ============================================================================

function updatePromptPreview() {
    const promptType = document.getElementById('prompt-type').value;
    const promptText = document.getElementById('prompt-text');
    const customContainer = document.getElementById('custom-prompt-container');
    
    if (promptType === 'custom') {
        customContainer.classList.remove('hidden');
        promptText.value = '';
    } else if (promptType === 'none') {
        customContainer.classList.add('hidden');
        promptText.value = '不使用 AI 處理，直接下載原始文字';
    } else {
        customContainer.classList.add('hidden');
        promptText.value = DEFAULT_PROMPTS[promptType] || '';
    }
}

function togglePromptEdit() {
    const editEnabled = document.getElementById('edit-prompt').checked;
    const promptText = document.getElementById('prompt-text');
    promptText.readOnly = !editEnabled;
}

async function processWithAI() {
    const promptType = document.getElementById('prompt-type').value;
    
    if (promptType === 'none') {
        skipAI();
        return;
    }
    
    if (!appState.ocrRawText) {
        showToast('請先完成 OCR 辨識', 'error');
        return;
    }
    
    const btn = document.getElementById('process-with-ai-btn');
    const progress = document.getElementById('ai-progress');
    
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-icon">⏳</span> 處理中...';
    progress.classList.remove('hidden');
    
    try {
        let customPrompt = null;
        
        if (promptType === 'custom') {
            customPrompt = document.getElementById('custom-prompt').value;
            if (!customPrompt) {
                throw new Error('請輸入自訂提示詞');
            }
        } else if (document.getElementById('edit-prompt').checked) {
            customPrompt = document.getElementById('prompt-text').value;
        }
        
        const response = await fetch('/api/enhance-with-gemini', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: appState.ocrRawText,
                prompt_type: promptType,
                custom_prompt: customPrompt
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            appState.processedText = data.processed_text;
            await generateFinalMarkdown();
            showToast('AI 處理完成！', 'success');
        } else {
            throw new Error(data.detail || 'AI 處理失敗');
        }
    } catch (error) {
        showToast(`AI 處理失敗: ${error.message}`, 'error');
        console.error(error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🤖</span> 使用 Gemini 處理';
        progress.classList.add('hidden');
    }
}

async function skipAI() {
    if (!appState.ocrRawText) {
        showToast('請先完成 OCR 辨識', 'error');
        return;
    }
    
    appState.processedText = appState.ocrRawText;
    await generateFinalMarkdown();
    showToast('已跳過 AI 處理', 'info');
}

async function generateFinalMarkdown() {
    const metadata = collectMetadata();
    const includeMetadata = document.getElementById('enable-metadata').checked;
    
    try {
        const response = await fetch('/api/generate-markdown', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: appState.currentFileId,
                content: appState.processedText,
                include_metadata: includeMetadata,
                metadata: metadata
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            appState.markdownContent = data.markdown_content;
            appState.txtContent = data.txt_content;
            
            // 顯示預覽
            displayPreview();
            
            // 顯示下載區
            document.getElementById('preview-section').classList.remove('hidden');
            document.getElementById('download-section').classList.remove('hidden');
            
            // 設置預設檔名
            const baseName = appState.currentFilename.replace(/\.[^/.]+$/, '');
            document.getElementById('download-filename').value = baseName;
            
            moveToStep(4);
            
            // 滾動到預覽區
            document.getElementById('preview-section').scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(data.detail || '生成 Markdown 失敗');
        }
    } catch (error) {
        showToast(`生成 Markdown 失敗: ${error.message}`, 'error');
    }
}

function displayPreview() {
    // Markdown 預覽（渲染）
    const markdownPreview = document.getElementById('markdown-preview');
    markdownPreview.innerHTML = marked.parse(appState.markdownContent);
    
    // 原始程式碼
    document.getElementById('markdown-raw').value = appState.markdownContent;
}

// ============================================================================
// 預覽標籤切換
// ============================================================================

function switchTab(event) {
    const targetTab = event.target.dataset.tab;
    
    // 更新按鈕狀態
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 更新內容顯示
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${targetTab}`).classList.add('active');
}

// ============================================================================
// 檔案下載
// ============================================================================

async function downloadFile(format) {
    if (!appState.currentFileId) {
        showToast('沒有可下載的檔案', 'error');
        return;
    }
    
    const filename = document.getElementById('download-filename').value || 'document';
    
    try {
        const response = await fetch(`/api/download/${appState.currentFileId}/${format}?filename=${encodeURIComponent(filename)}`);
        
        if (!response.ok) {
            throw new Error('下載失敗');
        }
        
        // 創建下載連結
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast(`已下載 ${filename}.${format}`, 'success');
    } catch (error) {
        showToast(`下載失敗: ${error.message}`, 'error');
    }
}

// ============================================================================
// 工具函數
// ============================================================================

function moveToStep(step) {
    appState.currentStep = step;
    
    document.querySelectorAll('.step').forEach((el, index) => {
        if (index + 1 <= step) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function checkSystemStatus() {
    try {
        console.log('🔍 檢查系統狀態...');
        const response = await fetch('/api/status');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📊 系統狀態:', data);
        
        // 只在真正需要時顯示警告
        if (!data.gemini_available) {
            console.warn('Gemini API 未就緒，部分功能將無法使用');
        }
        
        // 不顯示 OCR 警告，因為會觸發初始化
        console.log('✅ 系統狀態正常');
    } catch (error) {
        console.error('❌ 無法獲取系統狀態:', error);
        showToast('無法連接到後端服務，請確認伺服器是否正常運行', 'error');
    }
}

async function restartProcess() {
    // 清理後端檔案
    if (appState.currentFileId) {
        try {
            await fetch(`/api/cleanup/${appState.currentFileId}`, { method: 'DELETE' });
        } catch (error) {
            console.error('清理失敗:', error);
        }
    }
    
    // 重置狀態
    appState.currentFileId = null;
    appState.currentFilename = null;
    appState.ocrRawText = null;
    appState.processedText = null;
    appState.markdownContent = null;
    appState.txtContent = null;
    
    // 隱藏所有區塊
    document.querySelectorAll('.section').forEach(section => {
        if (section.id !== 'upload-section') {
            section.classList.add('hidden');
        }
    });
    
    // 重置上傳區
    resetUpload();
    
    // 滾動到頂部
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    showToast('已重置，可以處理新文件', 'info');
}

