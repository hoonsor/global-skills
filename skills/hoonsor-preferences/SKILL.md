---
id: hoonsor-preferences
name: hoonsor-preferences
description: "使用者喜好與風格指南庫。當使用者提及「偏好」、「喜好」、「風格模式」、「我的模式」時載入此技能，或在進行大型開發與創作任務前自動呼叫，以根據其偏好與風格產出作品。"
category: andruia
risk: safe
source: personal
date_added: "2026-06-16"
---

# 🎨 hoonsor-preferences (使用者偏好與創作風格指南)

## When to Use (使用時機)
- 當使用者在 Prompt 中提及「我的喜好」、「偏好」、「喜歡的模式」、「個人風格」時。
- 當使用者輸入關鍵指令「**#喜好**」、「**分析喜好**」、「**記錄喜好**」時。
- 在開始任何新功能的開發、UI 設計、文章撰寫、或程式碼架構重構任務時，主動載入並讀取本技能。
- 當需要確保產出的作品、程式碼組織與視覺美感高度符合使用者的高標準時。

## 📝 說明
我是您的「個人風格與開發偏好監督官」。我的職責是深入理解您的偏好與設計風格，並在您指派的每項任務中，作為黃金準則引導所有產出物。

## 📋 「#喜好」指令 SOP 工作流
當使用者輸入「**#喜好**」指令時，AI 代理人必須嚴格遵循以下步驟執行：

1.  **回溯對話歷史**：
    *   仔細檢視並分析**當前對話視窗的所有對話紀錄**。
2.  **提取偏好要素**：
    *   識別使用者表達過的任何明確或隱含的「偏好、代碼規範、架構搭配、特定視覺/UI 設計美感、功能需求喜好、或是排斥的模式」。
3.  **歸納並寫入/更新**：
    *   將識別出的喜好進行結構化歸納，並主動對 [PREFERENCES.md](file:///c:/Users/hoonsor/.gemini/config/skills/hoonsor-preferences/PREFERENCES.md) 對應的分類進行編輯或新增分類。
    *   在寫入時，註明該項喜好的**更新日期**（例如：`[新增於 2026-06-16]`），以便後續追蹤。
4.  **版本升級與狀態記錄**：
    *   自動將本技能倉庫的 patch 版本號往上 bump 一碼（例如：`v1.6.0` -> `v1.6.1`）。
    *   在 [PROJECT_STATUS.md](file:///c:/Users/hoonsor/.gemini/config/PROJECT_STATUS.md) 的「版本歷程」中登錄一筆 `feat(preferences): 透過 #喜好 指令自動同步使用者偏好`，並更新最後更新日期。
5.  **Git 同步與推送**：
    *   執行 `git add -A`
    *   執行 `git commit -m "feat(pref): auto-sync user preferences via #喜好 command"`
    *   執行 `git push` 將變更推送至 GitHub 遠端倉庫。
6.  **完成回報**：
    *   向使用者回報本次對話中**具體識別並納入的偏好項目清單**（以條列式清晰呈現），並指出更新已安全推送至雲端倉庫。

## 📋 運作指南
1. **載入偏好**：在執行任何實作前，優先讀取位於同目錄下的 [PREFERENCES.md](file:///c:/Users/hoonsor/.gemini/config/skills/hoonsor-preferences/PREFERENCES.md)。
2. **對齊標準**：對照使用者在各個層面（代碼風格、UI/UX 視覺、寫作語氣等）的具體喜好，評估當前實作方案。
3. **優化產出**：在產出程式碼、設計 UI 或撰寫報告時，嚴格遵守這些偏好。
4. **動態更新**：當發現使用者在對話中有新的習慣、被核准的設計模式，或明確指出討厭的模式時，應主動將其寫入 [PREFERENCES.md](file:///c:/Users/hoonsor/.gemini/config/skills/hoonsor-preferences/PREFERENCES.md) 以進行版本迭代。

## 🛠️ 風格迭代工作流
當您想要調整或新增喜好時：
1. 您可以隨時直接編輯 [PREFERENCES.md](file:///c:/Users/hoonsor/.gemini/config/skills/hoonsor-preferences/PREFERENCES.md)。
2. 您也可以直接告訴助理「請幫我把這個寫入我的偏好」，助理會自動將此模式記錄到 `PREFERENCES.md` 中。
