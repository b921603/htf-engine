# How To Fail → Eudic Auto-Sync Engine

**podcast 高忠實度搬運 × 每日英語聽力（eudic）頻道零人工維運**
*A fully-automated, faithful podcast mirror running on GitHub Actions free runners.*

> 官方 RSS 一出新集 → 本引擎在 ~1 小時內自動完成：
> 音檔轉存（32k mono）→ **podscripts 句級逐字稿字幕** → 聽眾向導讀（含真實英文開場金句）
> → **官方原版封面** → 建文章 → 驗收修復 → 加入封面輪換守恆 → ntfy 通知。
> 使用者只需要在想聽的時候打開 App。

---

## 為什麼長這樣 — 三個平台真相（對照實驗確立）

| 平台事實 | 實證 | 對策 |
|---|---|---|
| 封面上傳的檔案 id ~**80 秒即被 GC** | 上傳 10:00:51 → 10:02:12 已 404 | **即傳即用**：建文章當下才上傳封面 fid |
| 封面渲染快取 **15 分–3.4h 失效** | 08:49 官方圖 → 10:05 全文字卡 | **輪換重 POST**：lrc/desc/intros 位元組不變＋新 fid；每小時 LRU 分片（每次最久未 POST 的優先） |
| 所有持久圖路徑全部不通 | type=media 拒圖／偽裝 mp3 被內容校驗拒／intros 剝除／RebuildSource 不重繪 | 輪換是數學上唯一站得住的守恆解（平台若恢復舊制，輪換自動變成無害冗餘） |

## 誠實來源政策（不可協商）

- **字幕**：podscripts.co 句級秒碼逐字稿優先（408 集）；無外部稿才用 eudic AI 字幕（22 集）——
  描述與查證件如實標注。LRC 是逐字稿的**時間化容器，不是 ASR**。
- **導讀**：中文導讀＋**真實開場金句（英文原句）**＋出版方英文文案原樣保留。
- **封面**：官方 RSS artwork（自製美化封面已否決並停用）。
- **防污染**：podscripts 2026-11-13 新增「00:00」顯示晶片元素 → 抓取時過濾裸時間戳。
- **帳本**：`trail/sync_ledger.jsonl` 每次搬運一行（how/lrc_lines/desc_len/slug/parts）——
  「宣稱同步了」與「真的同步了」之間有帳可查。

## 工作流

| Workflow | 排程 | 做什麼 |
|---|---|---|
| `htf-sync` | 每小時 | RSS diff → 新集全管線（下載/ffmpeg 32k/逐字稿 LRC/導讀/官方封面即傳即用/建文章/驗收修復/註冊輪換）→ ntfy「🆕 新集已同步」 |
| `htf-rotate` | 每小時（2 分片） | LRU 封面輪換重 POST（位元組不變＋新 fid）；每集觸達週期 ≈ 60–90 分 ＜ 1.7h 失效窗 |
| `htf-keepalive` | 每 6 小時 | 靜音存活訊號（缺訊 >8h = 引擎停了）＋ heartbeat commit 防止 60 天不活動自動停用 |
| `htf-audit` | 每月 1 日 | 全頻道漂移稽核：LRC 行數漂移／可見時間戳／缺導讀／缺封面 fid → ntfy 報告 |

狀態持久化：`actions/cache`（`state/`＝done/ledger/rotate_cache；`rotstate/`＝各分片 LRU 狀態）。
新集由 sync 註冊進 rotate_cache → 下一輪輪換自動納入守恆（無需改 code）。

## 部署（10 分鐘，全免費）

1. Fork 或建立 **public** repo（公開 runner 無限分鐘；本倉庫不含任何機密）。
2. Settings → Secrets → Actions → 新增兩個 secret：
   - `EUDIC_COOKIE`：登入 my.eudic.net 後，DevTools → Network → 任一請求的整串
     `Cookie:` header 原樣貼上。
   - `NTFY_TOPIC`：你的 ntfy 主題 URL（如 `https://ntfy.sh/xxxx`），訊息會發到該主題。
3. Actions 頁面手動 Run 一次 `htf-sync`（workflow_dispatch）→ 觀察日誌。
4. 首次部署跑一次 `htf-rotate` 前，先手動觸發一次 bootstrap（見 docs/DEPLOY.md），
   為既有全部集數建立輪換快取（~25 分鐘）。

**cookie 會過期（數週～數月）**：輪換/同步會自動發 ntfy「HTF GA: cookie expired」→
登入 eudic 官網複製新 cookie → 更新 `EUDIC_COOKIE` secret。這是唯一需要人工的環節。

## 已知邊界（誠實聲明）

- GitHub 定時工作流有 3–60 分鐘的排程漂移 → 新集同步延遲最壞 ~1.5 小時。
- 官方 RSS 就是發行源（412 集）；跨平台比對確認無遺漏，RSS 外的已發行集
  （18 集）由一次性搬遷完成（見 `extras_art.json`）。
- 訂閱者專屬 bonus（HELP!）無公開音檔——**不搬運、不偽造**。

## 證據

- 430/430 對帳閉合（RSS 412＋補漏 18）；428/430 有字幕；430/430 無可見時間戳。
- 乾跑排練：805 句逐字稿／導讀 4,019 字／封面 fid 即傳即用全綠。
- 沙盒時代 8 次沙盒重置全部自動復原；本倉庫把執行層遷到 GitHub Actions 後，
  同步不再依賴任何會休眠的沙盒。
- 完整設計與證據鏈：沙盒 `HTF-自動同步引擎設計.md`、`HTF-運維手冊.md`（同步於 Google Drive）。

---
*Engine: `htf_engine.py`（單檔、相依僅 requests+pillow、ffmpeg 由 runner 提供）。*
*"To fail is not the opposite of success — it's part of it." — Elizabeth Day*
