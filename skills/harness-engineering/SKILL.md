---
name: harness-engineering
description: "馬鞍工程與駕馭工程 (Harness Engineering) 專家。提供測試駕馭 (Test Harness)、AI 代理控制架構 (Agent Scaffold/Harness)、評估駕馭 (Evaluation Harness) 與安全防護欄 (Guardrails) 的整合實作指引。"
category: engineering
risk: safe
source: personal
date_added: "2026-06-18"
---

# 🐴 馬鞍工程與駕馭工程 (Harness Engineering) 技能指南

## 📝 技能概述

「馬鞍工程」（Harness Engineering，亦譯作「駕馭工程」）是現代軟體工程與 AI 代理人（AI Agent）架構中的核心設計方法。其宗旨是為強大但具備不確定性的系統（例如：AI 模型、複雜的異步系統）建立一套**約束與支撐的「馬具/馬鞍 (Scaffolding)」**，以確保系統能夠穩定、可靠、且安全地在生產環境中運行。

本技能整合了以下三大馬鞍工程支柱：
1. **測試駕馭 (Test Harness)**：自動化測試執行器、模擬環境與網頁端到端測試。
2. **代理人駕馭 (Agent Harness)**：圍繞 LLM 建立的控制流、工具調用約束、狀態管理與記憶體。
3. **評估駕馭 (Evaluation Harness)**：整合 AI 單元測試與 CI/CD，持續監控代理人品質。

---

## 🛠️ 核心工具鏈與技術指南

### 1. 測試駕馭 (Test Harness)
為待測程式碼提供執行環境、測試腳本、測試資料與斷言（Assertion）的整套框架。
*   **Web 自動化**：優先使用 **Playwright**。配合 `playwright-skill` 進行無頭瀏覽器測試與視覺回歸校對。
*   **單元與整合測試**：使用 `pytest` 配合 `pytest-mock`、`pytest-cov`，實現測試覆蓋率監控與依賴隔離。
*   **混沌工程**：引入測試環境的隨機性，驗證系統在異常狀態下的恢復能力（Fail-Safe 機制）。

### 2. 代理人駕馭 (Agent Harness / Scaffolding)
將 AI 模型包裝成具備確定性行為的代理人系統。
*   **工具約束 (Tool Constraints)**：嚴格定義代理人可用的 Tool schemas，在執行前進行 Schema 校驗，防止工具濫用。
*   **安全圍欄 (Guardrails / Safety Harness)**：
    *   使用 **Guardrails AI** 或 **NeMo Guardrails** 對輸入進行提示詞注入（Prompt Injection）檢測，對輸出進行幻覺與敏感詞過濾。
    *   結合全域 `007` 安全審計技能，定期執行 OWASP Top 10 for LLM 安全掃描。
*   **狀態與記憶體管理**：採用短期 Context 管理與長期向量資料庫（如 Milvus、Chroma），確保常駐型代理人（Long-running Agents）的對話上下文穩定性。

### 3. 評估駕馭 (Evaluation Harness)
評估 LLM 與 Agent 的表現指標。
*   **DeepEval**：將評估寫成單元測試，支援 G-Eval、幻覺度量、答案相關性、毒性檢測等。
*   **lm-evaluation-harness**：學術與基礎模型評估，評估模型在基礎常識、推理解題上的客觀指標。
*   **自動化 CI/CD 阻斷**：在 Jenkins、GitHub Actions 或 Harness.io 平台中整合 Eval 測試，評估得分低於閾值（如 0.85）時自動阻斷部署。

---

## 📋 實作規範與工作流

### FASE 1: 建立測試駕馭 (Setup Test Harness)
在開發功能前，應先編寫測試案例（遵循 TDD 流程）：
1. 建立獨立的測試資料庫與 Mock 服務。
2. 撰寫基礎的測試套件，確保程式碼變更時能立刻獲得反饋。

### FASE 2: 設計代理人安全圍欄 (Apply Guardrails)
1. 在代理人接收到用戶 Input 時，先通過 **Guardrails 驗證層**。
2. 限制 Agent 每次任務的最大 Tool 呼叫次數，防止因無效循環（Infinite Loops）耗盡 Token。

### FASE 3: 自動化評估 (Run Evaluation)
1. 在發佈 PR 之前，運行 `deepeval test run`。
2. 檢查測試報告中的指標（如：Hallucination Rate, Relevancy, Latency）。
3. 確保測試通過後才進行 Git 提交與部署。

---

## 🔗 與現有技能的協調工作

當你在「馬鞍工程」專案中開發時，可以動態組合以下技能：
*   **`playwright-skill`** ➡️ 用於測試駕馭中的 Web UI 自動化與 E2E 測試。
*   **`tdd-workflow`** ➡️ 指導 TDD（紅燈-綠燈-重構）流程的實作。
*   **`agent-manager-skill`** ➡️ 用於管理、啟動、重啟常駐型代理人背景進程。
*   **`007` / `security-auditor`** ➡️ 執行 Harness 漏洞掃描與代理人特權提升防護。
*   **`hoonsor-preferences`** ➡️ 提供 Harness 在調整參數時的決策偏好。
