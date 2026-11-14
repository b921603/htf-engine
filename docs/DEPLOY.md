# DEPLOY — 兩種佈署路徑

## Plan A：給 agent 一把鑰匙（推薦，5 分鐘）

你只需要做兩件事：

1. **GitHub 帳號**（若沒有）：github.com 註冊（免費、免信用卡、只要 email）。
2. **建立 Personal Access Token**（Fine-grained）：
   - GitHub → Settings → Developer settings → Personal access tokens →
     Fine-grained tokens → Generate new token
   - Token name: `htf-deploy`
   - Repository access: **All repositories**（或先建空 repo `htf-eudic-sync` 後選 Only this repo）
   - Permissions：
     - Contents: **Read and write**
     - Secrets: **Read and write**
     - Actions: **Read and write**
     - Metadata: Read-only（預設）
   - 產生後把 token 貼給 agent（對話或 ntfy）。
3. agent 會自動完成：建 repo → 推送全部程式碼 → 設定兩個 secrets
   （`EUDIC_COOKIE`＝你的會話 cookie、`NTFY_TOPIC`＝ntfy 主題）→ 手動觸發首跑 → 驗證 → 回報。

> token 權限僅限單一 repo；若介意長期保存，佈署驗證完成後可撤銷，
> 之後 cookie 更新改走 Plan B 手動流程。

## Plan B：全程手動（不想給 token）

1. GitHub 建立新 **public** repo `htf-eudic-sync`（不要加 README）。
2. 從 agent 提供的 Drive 連結下載 `htf-eudic-sync.zip`，解壓後把全部檔案
   （含 `.github/` 目錄）透過網頁「Upload files」上傳。
3. Settings → Secrets and variables → Actions → New repository secret：
   - `EUDIC_COOKIE`：agent 會透過 ntfy/Drive 交給你一串 cookie（勿外流）。
   - `NTFY_TOPIC`：你的 ntfy 主題。
4. Actions 分頁 → 啟用 workflows → `htf-sync` → Run workflow。
5. 首次手動跑 `htf-audit` 前先跑一次 bootstrap：
   Actions → 選擇 workflow → Run workflow（agent 會提供 bootstrap 的 dispatch 指令）。

## cookie 更新（唯一的人工環節，數週一次）

引擎偵測到 cookie 失效會發 ntfy「HTF GA: cookie expired」：

1. 瀏覽器登入 my.eudic.net。
2. DevTools（F12）→ Network → 重新整理 → 點任一 `my.eudic.net` 請求 →
   Request Headers → 複製整串 `cookie:` 的值。
3. Plan A：把新 cookie 貼給 agent（更新 secret）；Plan B：自己貼進 repo secret。
