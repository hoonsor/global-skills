# Antigravity-Setting-and-Skills

> 專案存放 Antigravity AI 代理的所有全域自訂設定與技能工作流。

## 📖 專案簡介 (Overview)

本專案是用於儲存與管理 Google Antigravity AI 代理之「全域設定與技能 (Antigravity Settings and Skills)」的核心倉庫。這些設定與技能提供了 AI 代理在面對複雜的程式開發、系統自動化、測試與除錯等任務時所需的重要能力。

### 為何需要此專案？
在與 AI 進行程式設計或自動化協作時，AI 往往缺乏與本地特定系統相匹配的私有化工具與領域設定。本專案透過結構化的設定檔案（如權限設定與套件定義）、自訂技能（如開發規範、流程指引）與自動化腳本，將全域開發環境進行版控。這使得 AI 能夠在不同專案的 Session 中隨時調用這些設定與技能，實現「無縫協作」的核心目標。

### 核心價值
相比於每次對話都要重新解釋開發規範或重複配置環境，本專案提供了一個集中的設定與技能中心，有效減輕了 AI 代理的 context 負載。同時，透過安全備份機制與自動敏感金鑰屏蔽，您能無痛將這些設定遷移與備份至新電腦。

---

## ✨ 核心功能 (Key Features)

- **全域設定管理**：統一管理 `config.json` 的權限設定以及 `plugins/` 載入的擴充套件，實現跨裝置一鍵復原。
- **全域技能架構**：整合了數十個 AI 自訂技能，為前端、後端、自動化等各領域提供即時的技術手冊與 SOP 指引。
- **金鑰隱私保護**：同步時自動將 `mcp_config.json` 去除敏感的金鑰與個人路徑，轉為乾淨的模板檔案 `mcp_config.json.template`。
- **本機路徑排除**：透過 `.gitignore` 排除本機特定專案的 UUID 絕對路徑設定 (`projects/`)，避免新電腦覆蓋出錯。
- **專案狀態自動監控**：透過內部腳本實時監控所有子專案的進度與變更歷程，並自動同步至專案狀態呈現網站。

---

## 🛠 技術棧 (Tech Stack)

- **核心架構**：Google Antigravity (AGY) SDK, Model Context Protocol (MCP)
- **腳本語言**：Python 3.8+, PowerShell, Bash Shell
- **資料交換**：JSON, Markdown
- **版本控制**：Git, Conventional Commits

---

## 🚀 快速開始 (Quick Start)

### 環境要求
- Windows (推薦使用 PowerShell) 或 Linux/macOS
- Git CLI 已安裝且配置 SSH/HTTPS 權限
- 已安裝 Python 3.8+

### 安裝與運行

```bash
# 1. 複製此全域設定與技能倉庫至您的 .gemini 設定目錄
git clone https://github.com/hoonsor/Antigravity-Setting-and-Skills.git C:\Users\hoonsor\.gemini\config

# 2. 復原設定
# 將 mcp_config.json.template 複製一份為 mcp_config.json 並填入您個人的 API Key 與本機 Token。
```

---

## 📁 專案結構 (Project Structure)

```text
config/
 ├── _meta_backups/               # 備份的外部全域設定 (如 gemini.md)
 ├── plugins/                     # 載入的擴充外掛套件
 ├── skills/                      # 全域自訂技能
 │    ├── 00-install-all/         # 一次安裝全部懶人包技能
 │    ├── 01-notebooklm/          # 連接 NotebookLM MCP 技能
 │    ├── 02-github/              # 連接 GitHub CLI 技能
 │    ├── hoonsor-sync-global-skills/ # 同步此倉庫的自動化腳本
 │    └── ...                     # 其他全域技能
 ├── config.json                  # 全域權限與設定
 ├── mcp_config.json.template     # 已遮蔽金鑰之 MCP 服務設定模板
 ├── .gitignore                   # 排除敏感與本機專用路徑
 ├── PROJECT_STATUS.md            # 本專案的進度與狀態追蹤
 └── README.md                    # 本專案說明文件
```

---

## 🔄 最新更新 (Recent Updates)

### v1.4.0 (2026-06-14)
- 重構備份範圍至整個 `config` 目錄，新增自動遮蔽金鑰與本機特定路徑排除機制。
- 支援產出安全模板 `mcp_config.json.template`，並將 `projects/` 與真實 `mcp_config.json` 進行排除。

### v1.3.1 (2026-06-13)
- 同步全域設定（gemini.md）及 hoonsor-error-learning 錯誤學習最新備份檔。

### v1.3.0 (2026-06-13)
- 建立 Skill Vault 冷儲存區，將 1061 個備用技能移出核心目錄，優化系統上下文載入效能。

---
*Generated and maintained by Google Antigravity Architect*
