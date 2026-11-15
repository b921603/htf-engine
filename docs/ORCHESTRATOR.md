# Orchestrator — FINAL (2026-11-15): GitHub Actions does EVERYTHING
#
# RESOLVED: the write path works from runners. Root cause of the three early
# failures was NOT egress throttling per se — it was cubic TCP congestion
# control collapsing on the lossy Azure→eudic path. Enabling BBR in every
# workflow step 1:
#     sudo modprobe tcp_bbr && sudo sysctl -w net.ipv4.tcp_congestion_control=bbr
# lifted uploads from ~4 KB/s (12MB never finishing) to 299 KB/s (12MB in 42s).
#
# Full live-fire pipeline (run 43657334572, 543s): ffmpeg bootstrap → cover fid
# → 12MB audio upload → article create → LRC timing post=OK (patient retry for
# "还在处理" — fast uploads reach the edit step before server-side transcoding
# finishes) → guard verify → ntfy → ledger commit → state cache.
#
# The planned Oracle Always Free write-executor (Option C) is CANCELLED —
# unnecessary now. HF Space remains backup option D if GitHub-hosted runners
# ever lose BBR/sudo.
#
# Sandbox (Arena) demotes to interactive repair layer. Its rotation keeps
# running until the GA rotate cache fully self-bootstraps (~11 hourly runs),
# then can be disabled to halve WAF load.
