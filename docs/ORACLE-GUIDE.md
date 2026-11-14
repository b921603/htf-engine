# HTF 寫入層佈署指南 — Oracle Cloud Always Free（15 分鐘）

> 背景一句話：GitHub Actions（Azure 出口）對歐路的「讀取」全通、但「上傳」被限速到 ~4-23KB/s，
> 12MB 音檔傳不完（實測 3 次全滅，證據在 GitHub Actions 日誌）。所以：**GA 當腦（偵測/告警/審計），
> 寫入交給一台亞洲 IP 的免費 VM**——Oracle Always Free（永久免費、可開 4 核 24GB、獨立於任何對話）。

## 你要做的（三步，約 15 分鐘）

### ① 註冊 Oracle Cloud（免費，要一張信用卡「驗證身分」——不會扣款）
- https://cloud.oracle.com → Start for free
- 選 **Home region：South Korea (Seoul)**（備選：Osaka / Tokyo / Singapore / Chuncheon）

### ② 開一台 VM（貼上 cloud-init，全程不用 SSH）
- 控制台 → Compute → Instances → **Create instance**
- Image：**Ubuntu 22.04**（或 24.04）
- Shape：**Ampere A1 Flex**（先試 2 OCPU / 12 GB；若顯示 capacity 不足 → 換 region 上面的備選，或改 VM.Standard.E2.1.Micro）
- **往下滾到「Add cloud-init script」→ 貼上 Drive 裡《HTF-Oracle-cloud-init.txt》的全部內容**
- Create → 等 2-3 分鐘開機

### ③ 完成（真的沒了）
- 開機後 VM 自動：裝 ffmpeg → clone 引擎 → 寫入 secrets → 掛 cron（同步 ：23／輪換 ：41／keepalive 6h）→ 發「HTF VM: online」ntfy → 開始自舉輪換快取
- 第一次 keepalive 會從 VM 發出（ntfy 標題跟 GA 一致：`HTF keepalive`）——**從此這是常駐軌**
- 之後 ntfy 標題統一：VM 發的都帶 `HTF VM:` 或沿用 `HTF GA:` 前綴（同一引擎代碼）

## 之後的運維
| 情況 | 動作 |
|---|---|
| `HTF GA: cookie expired` | 歐路重新登入拿 cookie → 給 agent → agent 出一行指令，你在 VM 上貼（或 Oracle 網頁 Cloud Shell） |
| 想看執行日誌 | VM 上 `/var/log/htf/*.log`（agent 會教你 Cloud Shell 一行命令；或之後幫你掛遠端查詢） |
| 引擎更新 | agent push 到 GitHub → 你在 VM 上 `cd /opt/htf && sudo git pull`（或叫 agent 出指令） |
| PAT 過期 | 不影響運行——VM 只在安裝時用過它，之後可撤銷 |

## 安全邊界
- cloud-init 內含：repo 唯讀 token（用完即失效無妨）＋歐路 cookie＋ntfy topic——**只存在你的 Drive 檔與你自己的 VM 上**，未進 GitHub repo、未進任何公開處
- cookie 會過期（歐路慣例幾個月）；過期引擎會 ntfy 告警，不會寫壞任何東西

## 為什麼不是別的
- **HF Spaces（免費）**：出口同屬 AWS（沙盒證明可寫），但 48 小時無人訪問會沉睡＋重建，需 self-ping 續命，穩定性不如 VM——列為備選 D
- **GA 直寫**：已實測三次，上行限速無解——GA 保留當偵測/告警/審計（probes 會一直可用）
