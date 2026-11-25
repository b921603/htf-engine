#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pit_report.py — engine pit-status emitter（pit-status/1 協議，HTF 版）。

只讀 state/done.json（guid 帳本）＋官方 RSS，產出 trail/pit-status.json。
main 與 Specials 分列；無 enclosure 的官方 dead link 列為 blocked（無法補，
不計債）。完成度以官方集數為準（分段/字幕狀態不影響）。零引擎改動：
本檔獨立運行，任何失敗不影響主流程。
"""
import json, os, re, html, time
import requests

BASE = os.environ.get("HTF_BASE", "state")
RSS = "https://feeds.megaphone.fm/howtofail"   # same feed as engine
UA = {"User-Agent": "Mozilla/5.0"}
SPECIAL_RE = re.compile(r"History'?s Greatest Fails|BONUS EPISODE|MID-?SEASON BONUS"
                        r"|BETWEEN SEASON BONUS|TWIXMAS BONUS|SPECIAL EPISODE|TRAILER",
                        re.I)


def rj(p, d=None):
    try:
        return json.load(open(p))
    except Exception:
        return d


def main():
    done = rj(os.path.join(BASE, "done.json"), {}) or {}
    done_keys = set(done.keys())
    latest_pub, latest_done = 0, 0
    for v in (done or {}).values():
        if isinstance(v, dict):
            try:
                import datetime
                t = datetime.datetime.strptime(v.get("at", ""), "%Y-%m-%d %H:%M:%S")
                latest_done = max(latest_done, t.timestamp())
            except Exception:
                pass
    feed = requests.get(RSS, headers=UA, timeout=90)
    subs = {"main": {"total": 0, "done": 0, "dead": 0, "missing": []},
            "specials": {"total": 0, "done": 0, "dead": 0, "missing": []}}
    rss_guids = set()
    for block in re.findall(r"<item>(.*?)</item>", feed.text or "", re.S):
        t = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block, re.S)
        g = re.search(r"<guid[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</guid>", block, re.S)
        enc = re.search(r'<enclosure[^>]*url="([^"]+)"', block)
        pub = re.search(r"<pubDate>([^<]+)</pubDate>", block)
        if not (t and g):
            continue
        try:
            import email.utils
            latest_pub = max(latest_pub, email.utils.parsedate_to_datetime(
                pub.group(1)).timestamp())
        except Exception:
            pass
        sub = subs["specials"] if SPECIAL_RE.search(html.unescape(t.group(1))) else subs["main"]
        sub["total"] += 1
        rss_guids.add(g.group(1).strip())
        if g.group(1).strip() in done_keys:
            sub["done"] += 1
        elif not enc:
            sub["dead"] += 1                      # 官方無音檔——無法補，不計債
        else:
            sub["missing"].append(html.unescape(t.group(1))[:60])
    follow_lag_days = round((latest_pub - latest_done) / 86400, 1) if (latest_pub and latest_done) else None
    retired, retired_check = None, "ok"
    if len(rss_guids) < len(done_keys) - 5:
        retired_check = "inconclusive (feed smaller than ledger — guard)"
    else:
        retired = sorted(done_keys - rss_guids)
    fixable_missing = subs["main"]["missing"] + subs["specials"]["missing"]
    total_fixable = (subs["main"]["total"] + subs["specials"]["total"]
                     - subs["main"]["dead"] - subs["specials"]["dead"])
    done_total = subs["main"]["done"] + subs["specials"]["done"]
    rep = {
        "protocol": "pit-status/1",
        "family": "htf",
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "backlog+specials-split",
        "official_total": subs["main"]["total"] + subs["specials"]["total"],
        "official_available": total_fixable,
        "completed_eps": done_total,
        "true_missing": len(fixable_missing),
        "completion": round(done_total / total_fixable, 3) if total_fixable else None,
        "status": "complete" if not fixable_missing else "in_progress",
        "follow_lag_days": follow_lag_days,
        "retired_count": len(retired) if retired is not None else None,
        "retired_sample": [str((done.get(g) or {}).get("title") or g)[:50]
                           for g in (retired or [])][:10],
        "retired_check": retired_check,
        "blocked_reason": f"official dead links {subs['main']['dead'] + subs['specials']['dead']} eps (no enclosure, unfixable)",
        "subs": {k: {"total": v["total"], "done": v["done"], "dead": v["dead"],
                     "missing": len(v["missing"]), "missing_sample": v["missing"][:10]}
                 for k, v in subs.items()},
        "notes": "dead links excluded from debt per engine policy; follow_lag = newest RSS pub - newest done",
    }
    os.makedirs("trail", exist_ok=True)
    json.dump(rep, open("trail/pit-status.json", "w"), ensure_ascii=False, indent=1)
    print(f"pit-status: {done_total}/{total_fixable} completion={rep['completion']} "
          f"missing={rep['true_missing']} dead={subs['main']['dead'] + subs['specials']['dead']} "
          f"retired={rep['retired_count'] if rep['retired_count'] is not None else '?'} "
          f"follow_lag={follow_lag_days}d")


if __name__ == "__main__":
    main()
