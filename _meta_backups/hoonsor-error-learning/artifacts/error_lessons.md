# 🧠 錯誤教訓知識庫

> **用途**: Agent 遇到錯誤時，先查閱此索引，命中已知教訓則直接使用正確解法。
> **規則**: 只追加不刪除。每次呼叫 `hoonsor-error-learning` 技能後更新。

---

## 📑 教訓索引

| # | 標題 | 分類 | 等級 | 浪費模式 | 預估浪費 | 日期 |
|---|------|------|------|---------|---------|------|
| 1 | Windows CP950 編碼崩潰 | 環境 | 🔴 | TW-04 | ~6,000 | 2026-04-22 |
| 2 | Angular SPA Selector 地獄 | 前端 | 🔴 | TW-07, TW-02 | ~30,000 | 2026-04-22 |
| 3 | Python venv 依賴不完整 | 依賴 | 🟡 | TW-06 | ~4,000 | 2026-04-22 |
| 4 | MCP 伺服器指令衝突 | 配置 | 🟡 | TW-06 | ~5,000 | 2026-04-22 |

---

## 📌 教訓 #1: Windows CP950 編碼崩潰

**錯誤分類**: 環境
**嚴重等級**: 🔴 高頻
**Token 浪費模式**: TW-04（環境假設錯誤）
**預估浪費 Tokens**: ~6,000

### 症狀
```
UnicodeEncodeError: 'cp950' codec can't encode character '\U0001f4da' in position 0: illegal multibyte sequence
```

### 根因分析
Windows 終端預設使用 CP950（Big5）編碼，無法輸出 Emoji 或部分 Unicode 字元。
Python 的 `print()` 會嘗試用 `sys.stdout.encoding`（即 CP950）編碼所有輸出。
任何包含 Emoji、特殊符號的輸出都會觸發此錯誤。

### ❌ 無效嘗試（避免重蹈覆轍）
1. 嘗試修改程式碼移除 Emoji → 治標不治本，新的 Unicode 字元仍會出錯
2. 直接在腳本內設定 `encoding='utf-8'` 但沒有包裝 `sys.stdout` → 無效

### ✅ 正確解法
**方法 A（推薦）**: 執行前設定環境變數
```powershell
$env:PYTHONIOENCODING="utf-8"
```

**方法 B**: 在 Python 腳本最開頭加入
```python
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

### 🛡️ 預防措施
- **每次在 Windows 上執行 Python 腳本前，必須設定 `PYTHONIOENCODING=utf-8`**
- 所有新建的 Python 腳本都應在開頭包含方法 B 的防護碼
- 特別注意：`run_command` 工具執行 Python 時，也需要在 CommandLine 前加 `$env:PYTHONIOENCODING="utf-8"; `

### 📎 關聯
- 對話 ID: `2e069690-a87b-494b-b532-2f7667e8eac1`
- 日期: 2026-04-22
- 相關 KI: `notebooklm-mcp-guide`

---

## 📌 教訓 #2: Angular SPA Selector 地獄

**錯誤分類**: 前端
**嚴重等級**: 🔴 高頻
**Token 浪費模式**: TW-07（Selector 地獄）, TW-02（方向錯誤）
**預估浪費 Tokens**: ~30,000（最大單筆浪費！）

### 症狀
```python
page.query_selector('a[href*="/notebook/"]')  # → None
page.query_selector('[data-notebook-id]')     # → None
page.query_selector('.notebook-card')         # → None
page.query_selector('mat-card')              # → None
# 所有 CSS selector 均返回 None
```

### 根因分析
NotebookLM 使用 Angular 框架，採用深度動態渲染：
- 筆記本 UUID 不出現在 DOM 的 `href` 或 `data-*` 屬性中
- Angular 組件使用影子 DOM 或虛擬 DOM，標準 selector 無法穿透
- 頁面載入後 Angular 還需要額外渲染時間，DOM 結構持續變化
- `_ngcontent-*` 等隨機屬性讓 selector 不可靠

### ❌ 無效嘗試（避免重蹈覆轍）
1. `a[href*="/notebook/"]` → UUID 不在 href 中
2. `[data-notebook-id]` → 不存在此屬性
3. `.notebook-card`, `mat-card` → 類名不存在或動態生成
4. `querySelectorAll('a')` 然後過濾 → href 中沒有 notebook 路徑
5. 等待特定 selector 出現（`wait_for_selector`）→ 永遠不會出現
6. JavaScript 反射 (`__zone_symbol__`)  → 部分成功但不穩定
7. 修改 `client.py` 的 `_list_notebooks_sync` 反覆嘗試不同 selector → 10+ 輪全部失敗
8. 嘗試用 `evaluate()` 注入 JS 讀取 Angular 內部狀態 → 太脆弱

### ✅ 正確解法
**方法 A（最穩定）**: 使用 `page.inner_text('body')` 獲取純文字，然後解析
```python
body_text = page.inner_text('body')
# 從文字中用正則解析筆記本名稱、來源數、日期
```

**方法 B（需要 UUID 時）**: 模擬點擊遍歷
```python
# 1. 取得列表中所有可點擊元素
# 2. 逐一點擊 → 等待導航 → 從 URL 提取 UUID → 返回上一頁
# 3. 重複直到遍歷完成
```

### 🛡️ 預防措施
- **遇到 Angular/React/Vue 等 SPA 框架的頁面，第一時間使用 `inner_text('body')` 而非 CSS selector**
- 如果 `inner_text` 不夠，改用 `page.content()` 獲取完整 HTML 後用正則解析
- 絕對不要花超過 2 輪嘗試 CSS selector，如果前兩次失敗就立即切換策略
- 記住：**SPA 框架的 DOM 是動態生成的，selector 策略本質上不可靠**

### 📎 關聯
- 對話 ID: `2e069690-a87b-494b-b532-2f7667e8eac1`, `a8a8d866-7ee5-4772-9ee5-af7f42e502d9`
- 日期: 2026-04-22
- 相關 KI: `notebooklm-mcp-guide`

---

## 📌 教訓 #3: Python venv 依賴不完整

**錯誤分類**: 依賴
**嚴重等級**: 🟡 中等
**Token 浪費模式**: TW-06（依賴混淆）
**預估浪費 Tokens**: ~4,000

### 症狀
```
ModuleNotFoundError: No module named 'patchright'
```
即使 `.venv` 目錄存在且 `requirements.txt` 列出了 `patchright`。

### 根因分析
`run.py` wrapper 的 `ensure_venv()` 函數只在 venv 目錄不存在時才建立並安裝依賴。
如果 venv 已存在但依賴不完整（例如手動刪除了某個套件，或 requirements.txt 新增了條目），
wrapper 不會自動重新安裝。

### ❌ 無效嘗試（避免重蹈覆轍）
1. 反覆用 `python scripts/run.py ...` 執行 → 不會自動修復依賴
2. 刪除 venv 重建 → 可以但太慢

### ✅ 正確解法
```powershell
# 直接用 venv 內的 pip 安裝缺失依賴
& "C:\Users\hoonsor\.gemini\antigravity\skills\notebooklm\.venv\Scripts\pip.exe" install patchright
# 或安裝所有依賴
& "C:\Users\hoonsor\.gemini\antigravity\skills\notebooklm\.venv\Scripts\pip.exe" install -r requirements.txt
```

### 🛡️ 預防措施
- 遇到 `ModuleNotFoundError` 時，先用 `pip list` 檢查套件是否在 venv 中
- 不要依賴 wrapper 的自動安裝邏輯
- 安裝後用 `pip show <package>` 確認版本

### 📎 關聯
- 對話 ID: `2e069690-a87b-494b-b532-2f7667e8eac1`
- 日期: 2026-04-22

---

## 📌 教訓 #4: MCP 伺服器指令衝突

**錯誤分類**: 配置
**嚴重等級**: 🟡 中等
**Token 浪費模式**: TW-06（依賴混淆）
**預估浪費 Tokens**: ~5,000

### 症狀
```
notebooklm-mcp : 無法辨識 'notebooklm-mcp' 這個名稱
```
或 MCP 伺服器啟動後無回應/當機。

### 根因分析
`notebooklm-mcp` pip 套件被卸載後重裝為 `notebooklm-mcp-server`，
但 `mcp_config.json` 中的指令仍指向舊的入口點。
同時，PATH 未包含 Python Scripts 目錄，導致命令列找不到入口。

### ❌ 無效嘗試（避免重蹈覆轍）
1. 反覆卸載重裝 pip 套件 → 入口點名稱不同
2. 修改 `opencode.json` 指向錯誤的指令 → 啟動失敗
3. 嘗試用 `python -m notebooklm_mcp` → 模組結構不支援

### ✅ 正確解法
- 不依賴 MCP CLI，改用 `notebooklm` skill 的 Python 腳本直接執行
- 如果需要 MCP，在配置文件中使用**完整絕對路徑**
- 確認 `mcp_config.json` 中的 `command` 對應實際安裝的入口點名稱

### 🛡️ 預防措施
- pip 安裝後立即用 `where <command>` 確認入口點名稱和位置
- MCP 配置一律使用完整路徑，不依賴 PATH
- 維護 `hoonsor-mcp-manager` skill 來集中管理 MCP 伺服器配置

### 📎 關聯
- 對話 ID: `2e069690-a87b-494b-b532-2f7667e8eac1`
- 日期: 2026-04-22
- 相關 KI: `notebooklm-mcp-guide`
