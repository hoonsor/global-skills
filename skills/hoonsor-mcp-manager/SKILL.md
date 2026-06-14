---
name: hoonsor-mcp-manager
description: "全域 MCP 工具管理員，負責管理、檢測與修復本機 MCP 伺服器配置與相容性問題。"
risk: unknown
source: hoonsor
date_added: "2026-04-22"
---

# 🛠️ Omni MCP Manager (hoonsor-mcp-manager)

身為 Google Antigravity Architect，您可以呼叫此技能來協助 Chief Engineer 進行本機端 MCP (Model Context Protocol) 伺服器的全域管理與疑難排解。

## 🎯 核心功能

### 1. 狀態檢測與配置管理 (MCP Configuration)
- **讀取配置**: 快速分析 `mcp_config.json` 的設定內容。
- **配置修復**: 在配置出錯或路徑失效時，協助修復或新增 MCP 伺服器。

### 2. 環境與編碼相容性修復 (Environment & Encoding)
- **Windows 編碼修復**: 自動修復 Python CLI 工具在 Windows `CP950` 環境下因輸出 Emoji 或特殊字元導致的 `UnicodeEncodeError` (例如強加 `io.TextIOWrapper` 搭配 `utf-8` 編碼)。
- **依賴檢查**: 確保 Node.js 或 Python MCP 工具的相依套件已正確安裝。

### 3. 狀態排解 (Troubleshooting)
- **連接測試**: 協助測試特定 MCP 伺服器是否正常回應。
- **日誌分析**: 解析 MCP 錯誤日誌並提供明確修復方案。

## 🚀 執行指南

當使用者要求「管理 MCP」或「修正 MCP 錯誤」時：
1. 優先確認 `<appDataDir>\mcp_config.json` 是否正確設置。
2. 若為 Python MCP 報錯，請檢查是否有強制處理 Windows 的 `sys.stdout` 編碼。
3. 新增/設定任何 MCP 伺服器後，引導使用者重啟或進行連接測試。
