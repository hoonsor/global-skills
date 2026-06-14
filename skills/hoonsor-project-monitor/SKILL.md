---
name: hoonsor-project-monitor
description: Scan, generate, and sync project status files (PROJECT_STATUS.md) across all project directories. Produces unified JSON output for the monitoring website. Use when the user asks to scan projects, update project status, generate project overview, sync project data, monitor project progress, or when working with the 監控AI各專案進度之網站 project. Also triggers when user mentions PROJECT_STATUS, project scanning, or wants to see all project statuses at once.
---

# Project Monitor Skill

## 概述

此技能用於掃描並彙整「全能 AI 互動網站」所需的三大資料來源：

1. **全域技能呈現模組** — 掃描所有 Antigravity 全域技能
2. **工作流呈現模組** — 掃描所有 Antigravity 全域工作流
3. **AI 專案呈現模組** — 掃描所有程式專案資料夾

產出統一的 JSON 資料供監控網站前端介接。

## 觸發條件

- 使用者要求掃描/監控所有專案狀態
- 使用者要求掃描全域技能或工作流
- 使用者要求產生或更新 `PROJECT_STATUS.md`
- 使用者要求同步專案資料至監控網站
- 操作 `08-監控AI各專案進度之網站` 專案時

---

## 核心功能

### 1. 掃描全域技能 & 工作流

執行 `scripts/scan_skills.py`：

```powershell
python "C:\Users\hoonsor\.gemini\antigravity\skills\project-monitor\scripts\scan_skills.py"
```

**功能**：
- 掃描 `C:\Users\hoonsor\.gemini\antigravity\skills\` 下所有技能
- 掃描 `C:\Users\hoonsor\.gemini\antigravity\global_workflows\` 下所有工作流
- 解析每個技能的 SKILL.md：提取名稱、描述、功能概述、檔案結構
- 自動產生功能性標籤（12 類，如 `#前端設計`、`#文件處理`、`#AI工具`）
- 提取工作流的完整內容（供網站呈現程式碼區塊，點擊可複製）
- 產生標籤索引，方便前端多標籤檢索
- 輸出至 `D:\01-Project\08-監控AI各專案進度之網站\data\skills.json`

**技能輸出欄位**：
- `name` — 技能名稱（供點擊複製用）
- `display_name` — 顯示名稱
- `description` — 技能功能概述
- `tags` — 自動產生的功能標籤（供多標籤檢索）
- `structure` — 檔案結構（has_scripts, has_templates 等）
- `skill_md_lines` — SKILL.md 行數
- `last_modified` — 最後修改時間

**工作流輸出欄位**：
- `name` — 工作流名稱（供點擊複製用）
- `content` — 工作流完整程式碼內容（供呈現與複製）
- `description` — 工作流描述

### 2. 掃描所有專案

執行 `scripts/scan_projects.py`：

```powershell
python "C:\Users\hoonsor\.gemini\antigravity\skills\project-monitor\scripts\scan_projects.py"
```

**功能**：
- 掃描 `D:\01-Project\` 下所有子資料夾
- 提取每個專案的：名稱、版本、GitHub URL、任務進度、版本歷程，以及 README 中多行且詳盡的專案描述（支援跨行顯示）。
- 偵測技術棧（React, Next.js, Python, C#, Electron 等）
- 輸出至 `D:\01-Project\08-監控AI各專案進度之網站\data\projects.json`

### 3. 為個別專案產生 PROJECT_STATUS.md

執行 `scripts/generate_status.py`：

```powershell
python "C:\Users\hoonsor\.gemini\antigravity\skills\project-monitor\scripts\generate_status.py" --project "D:\01-Project\{project_folder}"
```

**功能**：
- 讀取專案的 git 資訊、package.json 等
- 使用 `templates/PROJECT_STATUS_TEMPLATE.md` 模板
- 產生或更新 `PROJECT_STATUS.md`

### 4. 完整同步至監控網站

執行 `scripts/sync_to_website.py`：

```powershell
python "C:\Users\hoonsor\.gemini\antigravity\skills\project-monitor\scripts\sync_to_website.py"
```

**功能**：
- 執行完整掃描（技能 + 工作流 + 專案）
- 將所有 JSON 輸出同步至監控網站 `data/` 目錄
- 產生同步報告

---

## 輸出檔案

| 檔案 | 內容 | 供應模組 |
|------|------|----------|
| `data/skills.json` | 全域技能 + 工作流 + 標籤索引 | 全域技能呈現模組、工作流呈現模組 |
| `data/projects.json` | 所有專案資訊 + 進度 + 版本歷程 | AI 專案呈現模組 |
| `data/sync_report.json` | 同步報告 | 儀表板 |

## 標籤系統

自動標籤對照表（共 12 類）：

| 標籤 | 觸發關鍵詞範例 |
|------|----------------|
| `#前端設計` | React, HTML, CSS, UI, dashboard, website |
| `#後端開發` | FastAPI, API, server, endpoint |
| `#文件處理` | PDF, Word, docx, pptx, spreadsheet |
| `#視覺設計` | image, poster, canvas, brand, GIF, theme |
| `#資料處理` | data, xlsx, csv, table, chart |
| `#系統整合` | MCP, SDK, protocol, external service |
| `#AI工具` | Claude, Anthropic, LLM, Gemini, NotebookLM |
| `#專案管理` | project, monitor, status, version, git |
| `#開發工具` | testing, debug, playwright, browser |
| `#心智圖` | mind map, xmind, brainstorm, diagram |
| `#溝通協作` | communication, documentation, proposal |
| `#程式碼生成` | code, component, generate, template |

## 注意事項

- 所有腳本使用 Python 3.8+ 標準庫，不需額外安裝套件
- git 相關操作需要系統已安裝 git CLI
- 所有文字輸出使用 UTF-8 編碼，支援繁體中文
- Windows cp950 編碼問題已透過 `io.TextIOWrapper` 修正
