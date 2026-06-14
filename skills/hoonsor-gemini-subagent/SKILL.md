---
name: hoonsor-gemini-subagent
description: Gemini CLI Sub-agent — 主從式代理架構，將批次處理或運算密集任務外包給 Gemini CLI 背景執行，避免本機進程卡死。
---

# Gemini CLI Sub-agent Skill

> **角色定位：** 本技能將當前 Antigravity session 作為「主代理 (Orchestrator)」，透過 `gemini` CLI 指令啟動一個或多個「子代理 (Sub-agent)」來並行處理批次任務，保護主進程不被長時間運算阻塞。

---

## 1. 觸發條件 (Triggers)

當使用者輸入包含以下意圖或關鍵字時，**自動調用**此技能：

| 關鍵字 | 語言 |
|---|---|
| `batch`、`process all`、`bulk` | English |
| `批量`、`並行`、`所有文件`、`大量處理`、`批次` | 繁體中文 |

> [!TIP]
> 觸發後無需使用者手動指定模型，技能將根據下方「模型路由」自動選擇。

---

## 2. 模型選擇邏輯 (Model Routing)

根據任務特性**自動分配模型**，遵循以下決策樹：

```
任務類型判斷
├─ 批次 OCR / 簡單文字擷取 / 格式轉換 / 講求速度
│   └─ ✅ Flash 模型：-m gemini-3.1-flash
│
└─ 跨檔案綜合分析 / 深度推理 / 需要長上下文理解
    └─ ✅ Pro 模型：-m gemini-3.1-pro-preview
```

### 選擇原則

| 情境 | 模型 | 旗標 |
|---|---|---|
| 單檔擷取、格式清洗、CSV 轉換、簡單摘要 | Flash | `-m gemini-3.1-flash` |
| 跨多檔比對、報告生成、邏輯推理、程式碼審查 | Pro | `-m gemini-3.1-pro-preview` |
| 不確定時 | Flash 優先 | 速度優先，失敗再升級 |

---

## 3. 執行指令規範 (Execution Rules)

### 3.1 基礎呼叫格式

```bash
gemini -m <模型> -p "<提示詞>" -o text 2>/dev/null
```

- `-p`：單次提示詞模式（非互動式）
- `-o text`：純文字輸出，避免 ANSI 色碼干擾
- `2>/dev/null`：靜默 stderr，僅保留 stdout 結果

### 3.2 多輪對話 / 保留上下文

當任務需要延續先前的上下文時，加入 `--resume latest`：

```bash
gemini -m <模型> --resume latest -p "<後續提示詞>" -o text 2>/dev/null
```

### 3.3 需要 AI 自主操作終端機

當子代理需要自主讀寫檔案、執行 shell 指令時，加入 `--yolo`：

```bash
gemini -m <模型> --yolo -p "<包含操作指令的提示詞>" -o text 2>/dev/null
```

> [!CAUTION]
> `--yolo` 模式會跳過所有確認提示，僅在使用者明確授權或任務本身為安全的批次讀取時使用。

### 3.4 指定檔案作為輸入

處理特定檔案時，使用 `-f` 旗標：

```bash
gemini -m gemini-3.1-flash -f "path/to/file.pdf" -p "摘要此文件" -o text 2>/dev/null
```

---

## 4. 進程保護與跨平台機制 (Process Management)

> [!IMPORTANT]
> 這是本技能最關鍵的規則。必須根據使用者 OS 選擇正確的背景執行方式。

### 4.1 任務規模分級
- 🟢 **小型 (< 10 檔):** 直接執行。
- 🔴 **大型 (> 50 檔 或 預計 > 10 分鐘):** **強制背景執行**。

### 4.2 執行模板 (按作業系統)

#### 🐧 Linux / macOS / WSL (使用 screen)
```bash
screen -dm -S <任務名稱> bash -c '<批次指令>; exec bash'
```

#### 🪟 Windows (使用 PowerShell 背景進程)
在 Windows 下，使用 `Start-Process` 配合 `Out-File` 紀錄日誌：
```powershell
$script = {
    # 設定編碼為 UTF8 避免中文亂碼
    $OutputEncoding = [System.Text.Encoding]::UTF8
    <批次指令邏輯>
    Write-Host "✅ 任務完成"
    Read-Host "按任意鍵結束..."
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", $script -WindowStyle Normal
```

### 4.3 背景執行回報模板 (Windows 版)

當在 Windows 啟動後，改用此回報方式：
```
✅ 任務已在獨立 PowerShell 視窗中啟動！

🤖 使用模型：<模型>
📂 處理範圍：<數量>
📝 執行狀態：我已開啟一個新的視窗執行此任務，您可以縮小該視窗，完成後它會保持開啟供您確認。

👉 如需強制停止：請直接關閉該 PowerShell 視窗。
```

---

## 5. 實作指引：如何寫批次指令 (以 Windows 為例)
當處理大量檔案時，請生成如下結構的 PowerShell 代碼：

```powershell
$files = Get-ChildItem "./input/*.pdf"
foreach ($f in $files) {
    Write-Host "Processing: $($f.Name)"
    gemini -m gemini-3.1-flash -f $f.FullName -p "摘要內容" -o text 2>$null | Out-File "./output/$($f.BaseName).md" -Encoding utf8
}
```

---

## 5. 組合使用模式 (Composition Patterns)

### 5.1 Fan-out / Fan-in 模式

適用於「拆分 → 並行處理 → 彙整」的場景：

```
主代理 (Antigravity)
  │
  ├─ 拆分任務清單
  │
  ├─ 啟動 Sub-agent (screen)
  │   ├─ Worker 1: 處理 file_001 ~ file_025
  │   ├─ Worker 2: 處理 file_026 ~ file_050
  │   ├─ Worker 3: 處理 file_051 ~ file_075
  │   └─ Worker 4: 處理 file_076 ~ file_100
  │
  └─ 等待完成 → 彙整結果
```

### 5.2 Pipeline 模式

適用於「前置處理 → 分析 → 後處理」的串聯場景：

```bash
# Stage 1: Flash 快速擷取
gemini -m gemini-3.1-flash -f input.pdf -p "擷取文字" -o text 2>/dev/null > stage1.txt

# Stage 2: Pro 深度分析
gemini -m gemini-3.1-pro-preview -f stage1.txt -p "分析並產出結構化報告" -o text 2>/dev/null > stage2.md
```

---

## 6. 安全護欄 (Safety Guardrails)

1. **永遠不在 `--yolo` 模式下執行刪除指令**（`rm`、`del`、`rmdir`）。
2. **批次輸出目錄必須與輸入目錄分開**，防止覆蓋原始資料。
3. **大型任務啟動前必須回報預估規模**，讓使用者確認。
4. **所有子代理的 stderr 必須被重導向或記錄**，不得汙染主代理的 stdout。

---

## 7. 快速參考卡 (Quick Reference)

```bash
# 🟢 小型任務 - 直接執行
gemini -m gemini-3.1-flash -p "..." -o text 2>/dev/null

# 🟡 帶上下文的連續任務
gemini -m gemini-3.1-pro-preview --resume latest -p "..." -o text 2>/dev/null

# 🔴 大型批次任務 - 背景執行
screen -dm -S my-task bash -c '...批次迴圈...; exec bash'

# 📋 查看背景任務
screen -r my-task

# 🛑 終止背景任務
screen -S my-task -X quit

# 📋 列出所有背景任務
screen -ls
```
