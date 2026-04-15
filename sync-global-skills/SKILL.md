---
name: sync-global-skills
description: 協助將所有的全域技能自動推送到指定的 GitHub 倉庫 (https://github.com/hoonsor/global-skills)，方便跨裝置同步與備份。
---

# Sync Global Skills (同步全域技能)

這個技能專門用於備份與同步你所有的全域技能至遠端 GitHub 倉庫，以便在其他裝置上輕鬆 `pull` 下來使用。

## 觸發條件 (Trigger)
當使用者要求「同步技能」、「備份技能」、「推送到遠端技能庫」，或者直接提到要將全域技能推送到 GitHub (如 `hoonsor/global-skills`) 時，請觸發此技能。

## 執行步驟 (Execution Steps)

當觸發此技能時，請依序執行以下步驟：

1. **確認技能資料夾路徑**：
   全域技能通常位於使用者電腦的 Antigravity App Data 目錄下的 `skills` 資料夾中。
   例如在 Windows 系統上通常是：`C:\Users\<username>\.gemini\antigravity\skills`

2. **確認 Git 狀態並初始化 (如果尚未初始化)**：
   使用 `run_command` 切換到該目錄。
   - 檢查是否已經是 Git 倉庫：`git status`
   - 如果不是，則執行 `git init`

3. **設置遠端倉庫 (如果尚未設置)**：
   - 檢查已有的遠端倉庫：`git remote -v`
   - 若尚未綁定目標倉庫，或遠端倉庫不是 `https://github.com/hoonsor/global-skills`，請執行：
     `git remote add origin https://github.com/hoonsor/global-skills`
     *(如果 `origin` 已經被占用但位置不對，可以使用 `git remote set-url origin https://github.com/hoonsor/global-skills` 更新)*

4. **自動產出或更新 `README.md` (可選)**：
   若目錄下沒有 `README.md`，可以簡單生成一個，內容說明這是全域技能庫的備份，並列出當前資料夾內所有的技能清單。

5. **執行提交與推送 (Commit and Push)**：
   依序執行以下命令：
   - `git add -A`
   - `git commit -m "chore: auto-sync global skills to remote"`
   - `git push -u origin main` (或 `master` 分支，具體依預設分支而定)

6. **回報使用者**：
   執行完畢後，向使用者確認推送結果。並告知若要在新電腦恢復，只需將倉庫 Clone 或 Pull 到新電腦的 Antigravity `skills` 資料夾即可直接使用，Antigravity 會自動偵測並載入。

## 注意事項
- 執行 Push 時可能會遇到需要授權認證 (Credentials) 的狀況，如果遇到權限錯誤，須引導使用者確認是否有正確設定 GitHub SSH key 或登入 GitHub 的 Credential Manager。
- 如果本地端與遠端出現衝突 (Conflicts)，請先嘗試 `git pull --rebase`，如需使用者介入，務必清楚說明衝突原因並請求確認。
