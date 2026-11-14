# Orchestrator options — where the WRITE-capable executor lives
#
# Evidence (2026-11-14, repo actions logs):
#   GitHub runners (Azure) → my.eudic.net  READ ✓ (auth / channels / articles /
#     RSS 3.3MB / podscripts all <2s)   WRITE ✗ — uplink throttled: 1MB POST
#     took 44s (~23 KB/s) and sustained 12MB transfers degrade to ~4 KB/s
#     (~50 min, still unfinished → socket timeouts). Not fixable client-side.
#   Arena sandbox → writes fine (~128 KB/s) but sandbox is conversation-bound.
#
# ⇒ GA keeps the BRAIN (detection/audit/keepalive — all proven green), while a
#   semi-permanent free executor with a friendlier egress performs the writes.

## Option C (recommended): Oracle Cloud Always Free VM (Asia region)
- 4 OCPU ARM Ampere + 24 GB RAM (A1.Flex) — always free, no charge, semi-permanent
- Region: ap-seoul-1 → fallback ap-osaka-1 / ap-tokyo-1 / ap-singapore-1
- Setup: paste the generated cloud-init (agent provides, contains repo URL +
  token + eudic cookie) into Instance → Advanced → "Add cloud-init script".
  The VM self-installs ffmpeg/python/deps, clones this repo, writes
  /etc/htf.env, installs cron:
      23 * * * *  sync     (HTF_BASE=/var/lib/htf/state)
      41 * * * *  rotate   (shard 0/2 + 1/2, HTF_ROTDIR=/var/lib/htf/rot)
      37 */6 * * * keepalive
  No SSH needed from the agent; cookie/ntfy secrets live only on your VM.

## Option D (backup): Hugging Face Space (free cpu-basic)
Same AWS egress family as the proven-working sandbox; runs the engine loop in
a Docker Space with self-ping keepalive. Less deterministic (48h inactivity
sleep on free tier, rebuilds on push) — use only if Oracle signup is a blocker.

## What stays on GitHub regardless
- Version control for the engine + workflows (audit trail, public accountability)
- htf-probe / htf-probe2 (dispatch diagnostics)
- The 4 workflows keep working: probe ✓, keepalive ✓, sync-read ✓, audit ✓
- If a write-capable executor is later lost, GA can still detect new episodes
  and ntfy-alert (sync failure alert wired).
