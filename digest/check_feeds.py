"""Report each feed's latest post; exit 1 if any feed fails or has gone quiet.

Run monthly in CI (or by hand) to decide which rows of feeds.csv to drop or fix.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from .http import get
from .sources import USER_AGENT, load_feeds, parse_feed


STALE_DAYS = 365


def check(feed: dict, now: datetime) -> tuple[str, str]:
    """(status, detail) where status is ok, stale or failed."""
    try:
        items = parse_feed(get(feed["url"], {"User-Agent": USER_AGENT}, attempts=2), feed["name"], feed["group"])
    except Exception as exc:
        return "failed", f"{type(exc).__name__}: {str(exc)[:120]}"
    dates = [item["published"] for item in items if item["published"]]
    if not dates:
        return "failed", f"{len(items)} item(s), none dated"
    latest = max(dates)
    recent = sum(1 for date in dates if date > now - timedelta(days=90))
    status = "stale" if latest < now - timedelta(days=STALE_DAYS) else "ok"
    return status, f"latest {latest:%Y-%m-%d}, {recent} post(s) in 90 days"


def main() -> int:
    now = datetime.now(timezone.utc)
    feeds = load_feeds()
    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(lambda feed: check(feed, now), feeds))
    lines = ["| 状态 | 来源 | 详情 | feed |", "|---|---|---|---|"]
    for feed, (status, detail) in sorted(zip(feeds, results), key=lambda pair: (pair[1][0] == "ok", pair[0]["name"])):
        lines.append(f"| {status} | {feed['name']} | {detail} | {feed['url']} |")
    report = "\n".join(lines)
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(f"## Feed check\n\n{report}\n")
    return 1 if any(status != "ok" for status, _ in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
