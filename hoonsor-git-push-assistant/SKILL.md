---
name: hoonsor-git-push-assistant
description: Automatically writes or updates the project's README.md with a comprehensive large-scale project template before pushing code to GitHub. Trigger this whenever the user confirms they want to push to remote.
---

# Git Push Assistant & README Documenter

## 簡介 (Overview)

當使用者在完成某個功能的程式碼修改並要求 `git push` 至遠端倉庫（例如 GitHub）時，你必須**自動觸發此技能**。這不僅僅是推送程式碼，更是確保專案的文件 (README) 永遠保持在最詳盡、專業且最新的狀態。

此技能會先讀取當前專案狀態，套用「大型開源專案通用 README 模板」重新撰寫或更新 README.md，並將變更提交後才執行 `git push`。

## 觸發時機 (Trigger)

- 當使用者明確表示「請幫我 push」、「推送至 GitHub」、「可以推送到遠端了」。
- 根據全球規則 (`GEMINI.md`) 中，當你在完成一般程式碼任務並詢問「是否要推送至遠端？」，而使用者回答「是」時。

## 執行流程 (Workflow)

### 步驟 1：蒐集專案資訊 (Gather Context)

在撰寫 README 之前，需快速了解專案的當前資訊：
1. 讀取 `PROJECT_STATUS.md` 以獲取專案名稱、當前版本號 (`vX.Y.Z`)、任務進度、最近版本歷程。
2. 掃描專案的技術棧 (從 `package.json`, `pyproject.toml`, 或檢查關鍵源碼目錄)。
3. 確認目前的主要功能有哪些（掃描 `src/` 結構或閱讀過往 README）。

### 步驟 2：生成/更新 README.md (Update README)

利用以下「大型專案通用模板」來撰寫或更新專案根目錄的 `README.md`。

**要求：** 
- **多段落描述**：標題底下的第一段「專案簡介 (Overview)」必須包含至少一段詳細介紹（建議 100~300 字，分段落），因為 `hoonsor-project-monitor` 技能會抓取此部分展現在網站上。
- **全 Traditional Chinese** 輸出（除了技術名詞）。
- 覆蓋或擴展現有的 README.md。

#### 🛡 README.md 通用模板結構 (Template)

```markdown
# [專案名稱 Project Name]

> [一段簡潔有力的高階描述，例如：這是一個基於 React 的高效能儀表板系統...]

## 📖 專案簡介 (Overview)
[此處請撰寫非常詳細的多行介紹，重點務必放在以下面向（依優先序）：
1. **功能說明**：這個程式做什麼事？提供哪些功能？使用者使用它可以完成什麼？
2. **使用場景與痛點**：為了解決什麼問題或滿足什麼需求而開發？目標使用者是誰？
3. **核心價值**：相比手動或其他方案，這個程式提供了哪些獨特的好處？
⚠️ 請避免只介紹技術架構（如 React, GSAP, Framer Motion 等），應以使用者能理解的語言說明「這個程式能幫你做什麼」。
請全程使用繁體中文撰寫。請確保保留多行與換行排版，方便前端網站抓取並提供優美的閱讀體驗。]

## ✨ 核心功能 (Key Features)
- **功能一**：詳細說明...
- **功能二**：詳細說明...
- **功能三**：詳細說明...

## 🛠 技術棧 (Tech Stack)
- **前端 / UI**：例如 React 19, Tailwind CSS, Framer Motion
- **後端 / API**：例如 FastAPI, Node.js
- **資料庫**：例如 PostgreSQL, Prisma
- **建置工具**：例如 Vite, Webpack

## 🚀 快速開始 (Quick Start)

### 環境要求
- Node.js >= 18 (或 Python >= 3.10)
- ...

### 安裝與運行
\`\`\`bash
# 1. 複製專案
git clone <repository-url>

# 2. 安裝依賴
npm install

# 3. 啟動開發伺服器
npm run dev
\`\`\`

## 📁 專案結構 (Project Structure)
\`\`\`text
src/
 ├── components/    # 共通 UI 元件
 ├── hooks/         # 狀態邏輯鉤子
 ├── views/         # 頁面檢視模組
 └── ...
\`\`\`

## 🔄 最新更新 (Recent Updates)
[從 PROJECT_STATUS.md 抓取最近的 2~3 筆變更歷程或目前版本號：vX.Y.Z]

---
*Generated and maintained by Google Antigravity Architect*
```

### 步驟 3：再次 Commit (Stage & Commit README)

因為 README.md 被更新了，請執行：
```bash
git add README.md
git commit -m "docs: update README with comprehensive template for vX.Y.Z"
```

### 步驟 4：推送至遠端 (Push to Remote)

執行終端機命令：
```bash
git push
```
（如果是首次推送且尚未設定 upstream，請自動判斷並使用 `git push -u origin main` 或對應的分支）

### 步驟 5：完成回報 (Reporting)

向使用者回報：
- 已成功套用大型專案 README 模板並更新 `README.md`。
- 已將最新變更推送到遠端伺服器 🚀。
