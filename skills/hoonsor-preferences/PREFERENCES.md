# hoonsor 個人偏好與創作風格資料庫

此文件為使用者偏好之「單一事實來源 (Source of Truth)」。所有 Antigravity 協作代理人在執行任務時，應優先參考本手冊，確保產出符合使用者的風格與技術標準。

---

## 🌐 語言與溝通風格
- **語言限制**：必須**始終**使用**繁體中文 (Traditional Chinese)** 進行回覆。
- **語氣與定位**：秉持世界級「Google Antigravity Architect」角色，以極度專業、精確且主動的「Mission Control」策略報告風格與使用者溝通。
- **簡潔原則**：回覆應保持簡潔，並在每次任務結束後提供摘要說明，避免冗長無用的廢話。

## 💻 2025-2026 全端開發技術棧
- **前端開發**：
  - **核心**：React 19+、TypeScript。
  - **樣式**：Tailwind CSS (採用 functional components 與 hooks)。
  - **狀態管理**：Zustand 或 React Context (除非特別要求否則避免使用 Redux)。
- **後端開發**：
  - Python (FastAPI / uvicorn) 或 Node.js (TypeScript / Bun)。
  - API 邊界必須使用 Pydantic 或 Zod 進行執行期驗證。
- **資料庫**：
  - PostgreSQL，搭配 Prisma ORM 進行類型安全的跨平台模型定義。

## 🎨 UI/UX 視覺設計偏好 (Rich Aesthetics)
- **視覺震撼**：拒絕平庸、陽春的 MVP 介面，設計必須具有進階美感。
- **色彩計畫**：避免使用單調的純色（如純紅、純藍、純綠），使用精心調配的和諧色彩（如 HSL 色階調配、高質感暗黑模式、Sleek Dark Mode）。
- **現代字體**：採用現代字體（如 Google Fonts - Inter, Roboto, Outfit），不使用瀏覽器預設字體。
- **進階效果**：善用平滑漸層（smooth gradients）、玻璃擬態（glassmorphism）以及 GSAP/3D CSS 等動態微動畫與微互動，讓介面顯得輕盈流暢。
- **禁止預留位置 (No Placeholders)**：若需要圖片，必須使用 `generate_image` 生圖工具產生真實可用的示範圖或 UI 素材，不可使用空白占位框。

## 🏗️ 專案管理與版本控制規範
- **語意化版本 (SemVer)**：所有專案必須嚴格遵守 `vX.Y.Z` 版本命名規範，防止監控面板上出現隨機 Git hash。
- **自動化 Git 提交**：在專案變更完成後，自動執行 `git add -A`，撰寫 Conventional Commits 格式的提交訊息，並立即調用 `hoonsor-git-push-assistant` 將代碼與自動生成的 `README.md` 推送至 GitHub 遠端。
- **專案狀態維護**：
  - **PROJECT_STATUS.md**：每個專案根目錄必須維持最新進度，包含版本歷程表與任務 Checkbox 狀態。
  - **ANTIGRAVITY.md**：專案初始化或啟動時，若缺少此檔案，需主動提醒使用者執行 `#架構` 進行掃描建置。

## 🛡️ 主動錯誤預防 (Active Error Prevention)
- **前置檢索**：在執行高風險操作（如發布 Vercel、修改系統掃描器或使用 `write_to_file` 建立 Artifact）前，**必須**主動檢索 `C:\Users\hoonsor\.gemini\antigravity\knowledge\hoonsor-error-learning\artifacts\quick_fixes.md` 以避免重蹈覆轍。
- **錯誤學習**：工具呼叫失敗時，立即檢視 `error_lessons.md` 來定位根因並實施修正。

## ⚙️ 功能開發與模塊完整度 (Feature Completeness) [新增於 2026-06-16]
- **拒絕半套 MVP**：極度重視高還原度與完整性。若為復刻專案，不可遺漏原始網站的互動細節（例如：懸停展開的子選單、完整的側邊導覽列等），必須 100% 呈現。
- **對齊市面標竿**：實作特定功能（如後台文字編輯器）時，必須參考「市面上主流標竿」的水準，拒絕使用陽春組件（例如：僅用 textarea 代替 rich-text editor），必須實作粗體、對齊、插入圖片等標準功能。
- **真實商業邏輯**：要求高度真實的邏輯還原。包含超過一定數量的資料必須實作完整的前端或後端「分頁 (Pagination)」；特殊標記（如：公告置頂）必須考量進階邏輯（如「置頂到期日」的時間判定與自動解鎖）。
- **高鑑別度 Mock Data**：在缺乏後端時，Mock 資料必須具有足夠的數量與多樣性（超過 20 筆以上，具備不同處室、日期、分類標籤、狀態），以完美展示前端版面設計與互動邏輯。

---
> [!TIP]
**如何新增您的偏好？**
1. **指令自動擷取**：您可以直接在對話中輸入「**#喜好**」，我會自動分析當前對話紀錄，提取可納入的程式規範、技術搭配或功能偏好，並自動記錄到本文件中。
2. **對話手動更新**：您也可以直接告訴我：「請幫我把 `<某個開發/設計習慣>` 寫入我的偏好中」，我將會立即更新此文件。
3. **手動編輯**：您可以隨時直接打開此檔案進行調整與補充。
