# 🤝 貢獻指南

感謝您考慮為 PaddleOCR-VL Web Application 做出貢獻！本指南將協助您了解如何參與這個專案。

## 📋 目錄

- [行為準則](#行為準則)
- [如何貢獻](#如何貢獻)
- [開發流程](#開發流程)
- [程式碼規範](#程式碼規範)
- [提交訊息規範](#提交訊息規範)
- [Pull Request 流程](#pull-request-流程)

---

## 行為準則

### 我們的承諾

為了營造一個開放且友善的環境，我們承諾：

- 尊重不同的觀點和經驗
- 優雅地接受建設性批評
- 關注對社群最有利的事情
- 對其他社群成員表現同理心

### 不可接受的行為

- 使用性別化語言或圖像，以及不受歡迎的性關注
- 惡意評論、侮辱/貶損性評論，以及個人或政治攻擊
- 公開或私下騷擾
- 未經明確許可，發布他人的私人資訊
- 其他在專業環境中可能被認為不適當的行為

---

## 如何貢獻

### 回報 Bug

在提交 Bug 報告之前：

1. **檢查現有 Issues**：確認該問題是否已被報告
2. **使用最新版本**：確認問題在最新版本中是否仍然存在
3. **收集資訊**：準備詳細的環境資訊和重現步驟

提交 Bug 時，請包含：

- **清晰的標題**：簡潔描述問題
- **環境資訊**：
  - 作業系統版本
  - Python 版本
  - 相關套件版本
- **重現步驟**：詳細說明如何觸發問題
- **預期行為**：描述您期望發生什麼
- **實際行為**：描述實際發生了什麼
- **截圖/日誌**：如果適用，提供截圖或錯誤日誌

**Bug 報告範本**：

```markdown
**環境資訊**
- OS: macOS 14.0
- Python: 3.12.0
- PaddleOCR: 2.7.3

**重現步驟**
1. 上傳 PDF 檔案
2. 選擇繁體中文語言
3. 點擊「開始 OCR 辨識」
4. 觀察到錯誤

**預期行為**
應該成功辨識繁體中文文字

**實際行為**
拋出錯誤：`KeyError: 'ch_tra'`

**錯誤日誌**
```python
Traceback (most recent call last):
  ...
```
```

### 建議新功能

提交功能建議時，請包含：

- **使用情境**：描述為什麼需要這個功能
- **建議方案**：詳細說明您的構想
- **替代方案**：考慮過的其他方案
- **優先級**：您認為的重要程度

### 改善文件

文件改善永遠受歡迎！包括：

- 修正錯字或語法錯誤
- 改善範例或說明
- 新增缺少的資訊
- 翻譯文件

---

## 開發流程

### 1. Fork 專案

點擊 GitHub 頁面右上角的「Fork」按鈕。

### 2. 複製儲存庫

```bash
git clone https://github.com/YOUR_USERNAME/PaddleOCR-VL.git
cd PaddleOCR-VL
```

### 3. 設定開發環境

```bash
# 建立 Conda 環境
conda create -n paddle-ocr-dev python=3.12 -y
conda activate paddle-ocr-dev

# 安裝依賴
pip install -r requirements.txt

# 安裝開發依賴
pip install pytest pytest-asyncio black flake8 mypy
```

### 4. 創建分支

```bash
# 從 main 分支創建新分支
git checkout -b feature/your-feature-name

# 或
git checkout -b fix/your-bug-fix
```

**分支命名規範**：

- `feature/` - 新功能
- `fix/` - Bug 修復
- `docs/` - 文件改善
- `refactor/` - 程式碼重構
- `test/` - 測試相關
- `chore/` - 其他維護工作

### 5. 進行開發

- 保持小而專注的變更
- 遵循程式碼規範
- 撰寫清晰的程式碼註解
- 更新相關文件

### 6. 執行測試

```bash
# 執行所有測試
pytest tests/

# 執行特定測試
pytest tests/test_services.py

# 檢查程式碼風格
black app/ --check
flake8 app/

# 類型檢查
mypy app/
```

### 7. 提交變更

```bash
git add .
git commit -m "feat: add support for Korean language"
```

### 8. 推送到 GitHub

```bash
git push origin feature/your-feature-name
```

### 9. 建立 Pull Request

前往 GitHub 頁面，點擊「New Pull Request」。

---

## 程式碼規範

### Python 程式碼風格

我們遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 風格指南，並使用以下工具：

#### Black（程式碼格式化）

```bash
# 格式化所有 Python 檔案
black app/ tests/

# 檢查但不修改
black app/ --check
```

#### Flake8（程式碼檢查）

```bash
flake8 app/ tests/
```

配置在 `.flake8` 檔案中：

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv,env
ignore = E203, W503
```

#### 類型提示

使用類型提示以提高程式碼可讀性：

```python
def process_image(image: Image.Image, lang: str = 'en') -> Tuple[str, List[dict]]:
    """處理圖像並返回文字與佈局資訊"""
    pass
```

### 前端程式碼風格

#### JavaScript

- 使用現代 ES6+ 語法
- 使用 `const` 和 `let`，避免 `var`
- 使用箭頭函數
- 清晰的變數和函數命名

#### CSS

- 使用有意義的類別名稱
- 遵循 BEM 命名規範（Block Element Modifier）
- 使用 CSS 變數定義主題

### 文件字串

使用 Google 風格的 docstring：

```python
def example_function(param1: str, param2: int) -> bool:
    """
    簡短描述函數功能
    
    更詳細的說明（如果需要）
    
    Args:
        param1: 第一個參數的說明
        param2: 第二個參數的說明
        
    Returns:
        返回值的說明
        
    Raises:
        ValueError: 當參數無效時
    """
    pass
```

---

## 提交訊息規範

我們使用 [Conventional Commits](https://www.conventionalcommits.org/) 規範。

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type（類型）

- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文件變更
- `style`: 程式碼格式（不影響程式碼運行的變更）
- `refactor`: 重構（既不是新增功能，也不是修復 bug）
- `perf`: 性能改善
- `test`: 新增測試或修正現有測試
- `chore`: 建置過程或輔助工具的變更

### 範例

```
feat(ocr): add support for Korean language

Add Korean language support to OCR service with proper
model initialization and error handling.

Closes #123
```

```
fix(api): resolve file upload size limit issue

Fixed issue where files larger than 10MB would fail to upload
even though the limit was set to 50MB.

Fixes #456
```

```
docs(readme): update installation instructions

Updated the README with more detailed installation steps
for Apple Silicon Macs.
```

---

## Pull Request 流程

### 提交 PR 前的檢查清單

- [ ] 程式碼遵循專案的風格規範
- [ ] 已執行並通過所有測試
- [ ] 已更新相關文件
- [ ] 提交訊息遵循規範
- [ ] PR 描述清楚說明變更內容

### PR 描述範本

```markdown
## 描述
簡要描述這個 PR 的目的和內容

## 變更類型
- [ ] Bug 修復
- [ ] 新功能
- [ ] 文件更新
- [ ] 程式碼重構
- [ ] 其他

## 測試
描述您如何測試這些變更

## 相關 Issue
關閉 #123

## 截圖（如適用）
如果有 UI 變更，請提供截圖

## 檢查清單
- [ ] 程式碼遵循專案風格
- [ ] 已執行測試
- [ ] 已更新文件
```

### 審查流程

1. **自動檢查**：CI/CD 會自動執行測試和檢查
2. **程式碼審查**：至少一位維護者會審查您的程式碼
3. **討論與修改**：根據反饋進行必要的修改
4. **合併**：審查通過後，維護者會合併您的 PR

### 審查要點

審查者會關注：

- 程式碼品質和可讀性
- 是否遵循專案規範
- 測試覆蓋率
- 文件完整性
- 是否引入新的依賴
- 性能影響

---

## 開發建議

### 良好的實踐

1. **小而專注的 PR**
   - 每個 PR 只做一件事
   - 更容易審查和測試
   - 降低衝突風險

2. **清晰的命名**
   - 變數、函數、類別使用描述性名稱
   - 避免縮寫和模糊的名稱

3. **程式碼註解**
   - 解釋「為什麼」而不是「是什麼」
   - 複雜邏輯需要註解說明

4. **錯誤處理**
   - 適當的異常處理
   - 有意義的錯誤訊息
   - 記錄重要錯誤

5. **測試**
   - 為新功能撰寫測試
   - 確保測試覆蓋邊界情況
   - 測試應該快速且穩定

### 避免的做法

- ❌ 大量未經測試的變更
- ❌ 混合多個不相關的變更
- ❌ 直接修改 main 分支
- ❌ 忽略 CI/CD 失敗
- ❌ 不遵循程式碼規範

---

## 需要協助？

如果您有任何問題：

- 查看現有的 [Issues](https://github.com/yourusername/PaddleOCR-VL/issues)
- 在 [Discussions](https://github.com/yourusername/PaddleOCR-VL/discussions) 提問
- 聯絡維護者

---

## 致謝

感謝所有貢獻者的付出！您的貢獻讓這個專案變得更好。

[![Contributors](https://contrib.rocks/image?repo=yourusername/PaddleOCR-VL)](https://github.com/yourusername/PaddleOCR-VL/graphs/contributors)

---

**再次感謝您的貢獻！** 🎉

