# Gemini 全域規則 (Global Rules)

## 技能命名規範
- **自建或修改衍生技能**：我（AI）自己建立或修改現有技能建立而成的新技能，都請務必加上「`hoonsor-`」前綴。

## 🛡️ 錯誤預防黃金法則（來自 hoonsor-error-learning）

> 以下規則從歷次對話中萃取，必須在相關操作前**無條件遵守**，不需查閱知識庫。

1. **Windows + Python** → 執行前必須先設 `$env:PYTHONIOENCODING="utf-8"`，防止 CP950 編碼崩潰
2. **SPA 頁面（Angular/React/Vue）** → 第一時間用 `page.inner_text('body')` 文字解析，**不要用 CSS selector**（歷史浪費 30,000+ tokens）
3. **ModuleNotFoundError** → 直接用 `.venv\Scripts\pip.exe install <pkg>`，不依賴 wrapper 自動安裝
4. **MCP 伺服器不通** → 用完整絕對路徑執行，不依賴 PATH
5. **同一方法嘗試 2 次失敗** → **立即停止，換方向**，並查閱 `knowledge/hoonsor-error-learning/artifacts/quick_fixes.md`

### 錯誤時的分層查閱策略
- **遇到錯誤** → 先檢查上方 5 條規則是否適用
- **規則未覆蓋** → 讀取 `quick_fixes.md`（~800 tokens，按關鍵字速查）
- **速查表未命中** → 讀取 `error_lessons.md`（~2,500 tokens，完整教訓）
- **全新錯誤** → 正常排錯，結束後呼叫 `hoonsor-error-learning` 技能歸檔
