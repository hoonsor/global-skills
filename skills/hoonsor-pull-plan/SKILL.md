---
name: hoonsor-pull-plan
description: >
  從 Vercel 遠端網站拉取最新的互動式任務計畫到本地 ACTIVE_TASKS.md，並依照任務清單逐項開始實作。
  觸發條件：使用者說「執行修正任務」、「拉取任務計畫」、「下載任務」、「pull plan」等。
---

# Pull Plan & Execute（拉取任務計畫並執行）

## 概述

此技能用於從部署在 Vercel 上的監控網站拉取使用者在網頁上編輯的任務計畫，
下載到本地的 `ACTIVE_TASKS.md`，然後依照計畫內容逐項開始實作。

## 觸發條件

- 使用者說「執行修正任務」
- 使用者說「拉取任務計畫」、「下載任務」
- 使用者提到 `pull plan`、`pull-plan`
- 使用者要求從網站同步任務到本地

## 執行流程

### 步驟 1：偵測專案目錄

確認使用者當前工作的專案目錄。如果使用者在特定專案目錄中，
以該目錄為基準執行。否則預設使用 `D:\01-Project\08-監控AI各專案進度之網站`。

### 步驟 2：執行拉取腳本

在目標專案目錄中執行：

```powershell
node scripts/pull-plan.js
```

此腳本會：
- 從 Vercel 遠端（`SYNC_SERVER_URL`）的 `/api/sync` API 拉取最新任務計畫
- 使用 `SYNC_API_KEY` 進行身份驗證
- 將任務內容寫入 `ACTIVE_TASKS.md`

### 步驟 3：讀取任務計畫

成功拉取後，讀取 `ACTIVE_TASKS.md` 的內容，向使用者展示當前任務清單。

### 步驟 4：開始實作

依照 `ACTIVE_TASKS.md` 中的任務清單，逐項開始實作：
1. 先標記當前任務為「進行中」
2. 完成後標記為「已完成」
3. 自動進入下一項任務

## 環境需求

- `.env.local` 中需設定：
  - `SYNC_SERVER_URL`（Vercel 網站網址）
  - `SYNC_API_KEY`（API 金鑰）

## 注意事項

- 若拉取失敗，檢查 `.env.local` 中的 `SYNC_SERVER_URL` 和 `SYNC_API_KEY` 是否正確
- 若尚未設定環境變數，引導使用者設定
- `ACTIVE_TASKS.md` 不會覆蓋 `PROJECT_STATUS.md`，兩者獨立運作
