---
name: hoonsor-error-learning
description: 從對話記錄中自動提取錯誤教訓、識別無效嘗試模式、建立持久化知識庫，避免重複犯錯與浪費 tokens。使用者呼叫時自動分析當前對話並歸檔學習成果。
---

# 🧠 hoonsor-error-learning — 錯誤學習與教訓歸檔技能

> **核心理念**: 每一次犯錯都是一次學習機會。本技能將對話中的錯誤、無效嘗試、成功修復全部結構化歸檔，
> 確保同樣的錯誤**永遠不會第二次浪費 tokens**。

---

## 🏗️ 三層防線架構（Token 最佳化設計）

本技能採用分層設計，確保錯誤預防以最低 Token 成本運作：

### 第一層：零成本黃金法則（每次對話自動生效）
- **位置**: `antigravity/gemini.md` → 隨系統指令自動載入
- **Token 成本**: ~150 tokens（寫入系統指令的一部分）
- **內容**: 5 條從歷史錯誤中萃取的黃金法則
- **觸發**: ✅ 每次對話自動生效，無需任何操作

### 第二層：速查表查閱（遇到錯誤時觸發）
- **位置**: `knowledge/hoonsor-error-learning/artifacts/quick_fixes.md`
- **Token 成本**: ~800 tokens（僅在需要時讀取）
- **內容**: 按錯誤關鍵字索引的速查修復表
- **觸發**: 當遇到錯誤且第一層規則未覆蓋時，Agent 主動讀取

### 第三層：完整教訓庫（速查未命中時觸發）
- **位置**: `knowledge/hoonsor-error-learning/artifacts/error_lessons.md`
- **Token 成本**: ~2,500 tokens（僅在極端情況讀取）
- **內容**: 完整的錯誤根因分析、無效嘗試記錄、正確解法
- **觸發**: 僅在速查表未找到匹配時才讀取

---

## 🎯 觸發條件

### 模式 A：被動防禦（自動觸發，不需使用者呼叫）

Agent 在**任何對話**中遇到以下情況時，應**主動查閱**知識庫：

```
觸發條件（滿足任一即觸發）:
├── 1. 執行指令出現錯誤訊息 (stderr 非空)
├── 2. Python 拋出 Exception
├── 3. 同一操作嘗試第 2 次仍失敗
├── 4. 使用者反映「之前也遇過這個問題」
└── 5. 正在操作已知易錯領域（NotebookLM、MCP、瀏覽器自動化）

查閱流程:
Step 1: 先對照 gemini.md 中的 5 條黃金法則（0 額外 tokens）
Step 2: 若未覆蓋 → view_file quick_fixes.md（~800 tokens）
Step 3: 若未命中 → view_file error_lessons.md（~2,500 tokens）
```

### 模式 B：主動學習（使用者明確呼叫）

當使用者說出以下關鍵詞時，執行完整的 Phase 1-5 流程：
- 「記錄這次的錯誤」/ 「學習這次教訓」/ 「error learning」
- 「把這次的經驗記下來」
- 「分析這次浪費了多少 tokens」
- 「更新錯誤知識庫」

---

## 📋 完整執行流程（模式 B）

### Phase 1: 對話分析（Conversation Scan）

1. **讀取當前對話紀錄**
   - 路徑: `C:\Users\hoonsor\.gemini\antigravity\brain\<conversation-id>\.system_generated\logs\overview.txt`
   - 如果對話紀錄太長，聚焦於包含以下關鍵詞的段落：
     - `error`, `Error`, `failed`, `Failed`, `exception`, `Exception`
     - `ModuleNotFoundError`, `UnicodeEncodeError`, `TypeError`, `ImportError`
     - `不到`, `找不到`, `失敗`, `錯誤`, `無法`
     - `重試`, `再試`, `換個方法`, `改用`

2. **識別錯誤事件**
   - 提取每個獨立的錯誤事件，包括：
     - 🔴 **錯誤訊息** (Error message)
     - 🟡 **觸發上下文** (什麼操作導致了此錯誤？)
     - 🟢 **最終解決方案** (最後成功的修復方法)
     - ⏱️ **嘗試次數** (在找到正確解法前嘗試了多少輪)

### Phase 2: 無效嘗試偵測（Token Waste Detection）

識別以下「Token 浪費模式」：

| 模式代碼 | 模式名稱 | 描述 |
|----------|---------|------|
| `TW-01` | **盲目重試** | 同一方法反覆嘗試 3+ 次，每次只做微小改動 |
| `TW-02` | **方向錯誤** | 花費大量 tokens 在根本不可行的技術路線上 |
| `TW-03` | **忽略已知解法** | Knowledge Item 已有記錄但未查閱就開始嘗試 |
| `TW-04` | **環境假設錯誤** | 假設了錯誤的 OS/編碼/PATH/版本，導致連鎖錯誤 |
| `TW-05` | **過度工程** | 用複雜方案解決簡單問題，最終回到簡單解法 |
| `TW-06` | **依賴混淆** | 在錯誤的套件/模組/版本上反覆安裝卸載 |
| `TW-07` | **Selector 地獄** | 對動態渲染頁面反覆嘗試不同 CSS/XPath selector |

**偵測邏輯**:
- 如果同一個錯誤在對話中出現 3 次以上 → 標記為 `TW-01`
- 如果某個技術方案被嘗試後完全放棄，改用不同方案 → 標記為 `TW-02`
- 如果 Knowledge Item 中已有相關記錄但未被查閱 → 標記為 `TW-03`
- 計算每個無效嘗試的**預估 tokens 浪費量**（每輪交互約 2,000-5,000 tokens）

### Phase 3: 教訓萃取（Lesson Distillation）

對每個錯誤事件，生成結構化教訓：

```markdown
## 📌 教訓 #N: [簡短標題]

**錯誤分類**: [環境/編碼/依賴/邏輯/前端/配置/認證]
**嚴重等級**: [🔴 高頻/🟡 中等/🟢 偶發]
**Token 浪費模式**: [TW-XX 或 無]
**預估浪費 Tokens**: [N,000]

### 症狀
[完整的錯誤訊息或行為描述]

### 根因分析
[深入分析為什麼會發生此錯誤]

### ❌ 無效嘗試（避免重蹈覆轍）
1. [嘗試 A — 為什麼失敗]
2. [嘗試 B — 為什麼失敗]

### ✅ 正確解法
[最終成功的解決步驟]

### 🛡️ 預防措施
[未來如何在第一時間避免此錯誤]

### 📎 關聯
- 對話 ID: [conversation-id]
- 日期: [YYYY-MM-DD]
- 相關 Knowledge Item: [如有]
```

### Phase 4: 持久化歸檔（Knowledge Persistence）

1. **更新主教訓庫**
   - 路徑: `C:\Users\hoonsor\.gemini\antigravity\knowledge\hoonsor-error-learning\artifacts\error_lessons.md`
   - **只追加不覆蓋**：新教訓追加到檔案末尾
   - 更新檔案頂部的**教訓索引表**

2. **更新速查表**
   - 路徑: `C:\Users\hoonsor\.gemini\antigravity\knowledge\hoonsor-error-learning\artifacts\quick_fixes.md`
   - 新增錯誤關鍵字 → 正確解法的映射

3. **更新浪費模式統計**
   - 路徑: `C:\Users\hoonsor\.gemini\antigravity\knowledge\hoonsor-error-learning\artifacts\token_waste_patterns.md`
   - 更新各模式的累計次數和 token 浪費量

4. **評估黃金法則是否需要更新**
   - 如果新教訓的嚴重等級為 🔴 且浪費超過 10,000 tokens
   - → 將其濃縮為一行規則，追加到 `gemini.md` 的黃金法則中
   - → 這樣下次對話就會自動防禦，不需查閱知識庫

5. **更新 metadata.json**
   - 更新 `updated_at`、`total_lessons`、`total_estimated_tokens_saved` 等欄位
   - 追加新的 `references` 條目

### Phase 5: 產出報告（Session Report）

向使用者產出結構化的學習報告：

```
🧠 錯誤學習報告 — [日期]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 統計摘要
  • 發現錯誤事件: N 件
  • Token 浪費模式: N 件
  • 預估總浪費: ~N,000 tokens
  • 新增教訓: N 條
  • 已知教訓命中: N 條（之前已記錄過）

📌 關鍵教訓
  1. [教訓標題] — [一句話摘要]
  2. ...

🛡️ 防線更新
  • 黃金法則: [是否新增/修改]
  • 速查表: [新增 N 條]
  • 完整教訓: [新增 N 條]

📁 已歸檔至: knowledge/hoonsor-error-learning/
```

---

## 📁 知識庫結構

```
知識庫 (Knowledge)
C:\Users\hoonsor\.gemini\antigravity\knowledge\hoonsor-error-learning\
├── metadata.json                        # KI 元數據
└── artifacts/
    ├── error_lessons.md                 # 主教訓庫（持續追加）
    ├── token_waste_patterns.md          # Token 浪費模式統計
    └── quick_fixes.md                   # 常見錯誤速查表（高頻錯誤的快速修復）

第一層防線 (Golden Rules)
C:\Users\hoonsor\.gemini\antigravity\gemini.md  # 黃金法則（自動載入）
```

---

## ⚙️ 配置常量

```yaml
# 知識庫路徑
KNOWLEDGE_BASE: C:\Users\hoonsor\.gemini\antigravity\knowledge\hoonsor-error-learning\
LESSONS_FILE: artifacts/error_lessons.md
PATTERNS_FILE: artifacts/token_waste_patterns.md
QUICK_FIXES_FILE: artifacts/quick_fixes.md
GOLDEN_RULES_FILE: C:\Users\hoonsor\.gemini\antigravity\gemini.md

# 分析參數
MIN_RETRY_COUNT_FOR_TW01: 3        # 重試 3 次以上視為 TW-01
TOKEN_PER_ROUND_ESTIMATE: 3000     # 每輪交互估計 token 數
SEVERITY_THRESHOLD_HIGH: 10000     # 浪費超過此 token 數標記為高嚴重度
GOLDEN_RULE_THRESHOLD: 10000       # 浪費超過此值則升級為黃金法則

# Token 成本估算
COST_GOLDEN_RULES: 150             # 黃金法則每次對話固定成本
COST_QUICK_FIXES: 800              # 速查表讀取成本
COST_FULL_LESSONS: 2500            # 完整教訓庫讀取成本
```

---

## 🚫 反模式警告

> [!CAUTION]
> **在執行本技能時，絕對不要：**
> 1. 跳過 Phase 2（無效嘗試偵測）— 這是本技能的核心價值
> 2. 只記錄錯誤而不記錄「無效嘗試」— 知道什麼不該做比知道什麼該做更重要
> 3. 覆蓋 `error_lessons.md` 的舊內容 — 只追加，不刪除
> 4. 忽略 token 浪費估算 — 這是衡量改善效果的唯一指標
> 5. 每次對話都讀完整教訓庫 — 遵守三層防線，逐層遞進
> 6. 將超過 5 條規則寫入黃金法則 — 保持精簡，只放最高頻最高危的
