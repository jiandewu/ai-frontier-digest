"""Collect new items, summarize them, and rebuild the daily pages and README.

Files only change when new items arrive, so a quiet run produces no commit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .sources import HF_MIN_UPVOTES, HN_MIN_POINTS, collect, load_feeds
from .fulltext import fetch_text
from .summarize import explain, group_events, summarize


NEW_YORK = ZoneInfo("America/New_York")
ITEM_COLUMNS = ["id", "detected_et", "published_et", "source", "group", "title", "title_zh", "summary_zh",
                "category", "importance", "score", "link", "explain_zh", "event"]
LOOKBACK_DAYS = 3
# Pages show a short daily pick, not everything collected; the CSV keeps every summarized item.
DAILY_PICKS = 10
PICKS_PER_SOURCE = 2
PICK_MIN_IMPORTANCE = 3
# Long-form posts by individual researchers rank above news; the CSV keeps Gemini's raw rating.
GROUP_BONUS = {"个人博客": 1}
# An event covered by two or more sources is hot: one more star, and only its best report is picked.
COVERAGE_BONUS = 1
EVENT_CANDIDATES = 60
SOURCE_GROUP_TITLES = {"个人博客": "研究者与作者"}


def item_id(link: str) -> str:
    return hashlib.sha1(link.strip().rstrip("/").encode("utf-8")).hexdigest()[:12]


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ITEM_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_items(data_dir: Path) -> list[dict]:
    """All stored rows; row["_also"] lists other sources' rows on the same event (not written back)."""
    rows = [row for path in sorted((data_dir / "items").rglob("*.csv")) for row in _read_csv(path)]
    events = defaultdict(list)
    for row in rows:
        if row.get("event"):
            events[row["event"]].append(row)
    for row in rows:
        also, sources = [], {row["source"]}
        for other in events.get(row.get("event") or "", []):
            if other["source"] not in sources:
                sources.add(other["source"])
                also.append(other)
        row["_also"] = also
    return rows


def select_new(fetched: list[dict], known_ids: set[str], now: datetime) -> list[dict]:
    """Unseen items published within the lookback window; undated items are skipped.

    Future dates (some feeds round to the end of the month) are treated as now.
    """
    cutoff = now - timedelta(days=LOOKBACK_DAYS)
    new, seen = [], set(known_ids)
    for item in fetched:
        identifier = item_id(item["link"])
        if identifier in seen or not item["published"] or item["published"] < cutoff:
            continue
        seen.add(identifier)
        new.append({**item, "id": identifier, "published": min(item["published"], now)})
    return new


def update_rows(data_dir: Path, updates: dict[str, dict]) -> None:
    """Merge fields into stored rows by id, rewriting only the files that change."""
    for path in sorted((data_dir / "items").rglob("*.csv")):
        rows = _read_csv(path)
        if any(row["id"] in updates for row in rows):
            _write_csv(path, [{**row, **updates.get(row["id"], {})} for row in rows])


def _latest_days(rows: list[dict], count: int = 2) -> list[str]:
    return sorted({row["detected_et"][:10] for row in rows}, reverse=True)[:count]


def mark_events(data_dir: Path, api_key: str, model: str, log=print) -> bool:
    """Group the two latest days' candidates by event; False if Gemini failed and nothing changed."""
    rows = load_items(data_dir)
    days = _latest_days(rows)
    candidates = [row for row in _rank([row for row in rows if row["detected_et"][:10] in days])
                  if int(row["importance"] or 0) >= PICK_MIN_IMPORTANCE][:EVENT_CANDIDATES]
    groups = group_events(candidates, api_key, model, log)
    if groups is None:
        return False
    updates = {row["id"]: {"event": ""} for row in candidates}
    for ids in groups:
        updates.update({identifier: {"event": min(ids)} for identifier in ids})
    update_rows(data_dir, updates)
    return True


def explain_picks(data_dir: Path, api_key: str, model: str, log=print) -> list[dict]:
    """Add full-text explanations to the picks of the two latest days that lack one."""
    rows = load_items(data_dir)
    candidates = [row for day in _latest_days(rows) for row in pick([row for row in rows if row["detected_et"][:10] == day])
                  if not row.get("explain_zh")]
    readable = []
    for row in candidates:
        text = fetch_text(row["link"])
        if text:
            readable.append({"id": row["id"], "title": row["title"], "text": text})
        else:
            log(f"No readable text: {row['link']}")
    explanations = explain(readable, api_key, model, log)
    update_rows(data_dir, {identifier: {"explain_zh": text} for identifier, text in explanations.items()})
    return [row for row in candidates if row["id"] in explanations]


def store_items(data_dir: Path, items: list[dict], summaries: dict[str, dict], now: datetime) -> list[dict]:
    stored = []
    for item in items:
        summary = summaries.get(item["id"])
        if summary is None:
            continue
        stored.append({
            "id": item["id"], "detected_et": now.strftime("%Y-%m-%d %H:%M"),
            "published_et": item["published"].astimezone(NEW_YORK).strftime("%Y-%m-%d %H:%M"),
            "source": item["source"], "group": item["group"], "title": item["title"],
            "title_zh": summary["title_zh"] or item["title"], "summary_zh": summary["summary_zh"],
            "category": summary["category"], "importance": summary["importance"],
            "score": item["score"], "link": item["link"],
        })
    if stored:
        path = data_dir / "items" / now.strftime("%Y") / f"{now:%Y-%m}.csv"
        rows = _read_csv(path) + stored
        rows.sort(key=lambda row: (row["detected_et"], row["published_et"], row["id"]), reverse=True)
        _write_csv(path, rows)
    return stored


def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def _link(text: str, url: str) -> str:
    return f"[{_cell(text).replace('[', '(').replace(']', ')')}]({url.replace(' ', '%20').replace(')', '%29')})"


def _importance(row: dict) -> int:
    """Gemini's rating plus group and coverage bonuses; off-topic posts (below 3) get no bonus."""
    base = int(row["importance"] or 0)
    if base < 3:
        return base
    return min(5, base + GROUP_BONUS.get(row["group"], 0) + (COVERAGE_BONUS if row.get("_also") else 0))


def _rank(rows: list[dict]) -> list[dict]:
    """Most important first, newest first within the same importance."""
    newest = sorted(rows, key=lambda row: row["published_et"], reverse=True)
    return sorted(newest, key=lambda row: -_importance(row))


def pick(rows: list[dict], limit: int = DAILY_PICKS) -> list[dict]:
    """Top-ranked items, one per event and at most PICKS_PER_SOURCE from any one source.

    An event is represented by its most important report, the earliest (usually the original) on ties.
    """
    best = {}
    for row in sorted(rows, key=lambda row: (-_importance(row), row["published_et"])):
        best.setdefault(row.get("event") or row["id"], row["id"])
    picks, per_source = [], Counter()
    for row in _rank(rows):
        if (_importance(row) < PICK_MIN_IMPORTANCE or per_source[row["source"]] >= PICKS_PER_SOURCE
                or best[row.get("event") or row["id"]] != row["id"]):
            continue
        per_source[row["source"]] += 1
        picks.append(row)
        if len(picks) == limit:
            break
    return picks


def _meta(row: dict) -> str:
    score = ""
    if row["score"]:
        score = f" · {row['score']} {'赞' if row['source'] == 'HF Daily Papers' else '分'}"
    return f"{row['source']} · {row['category']} · {row['published_et']}{score}"


def render_day(day: str, rows: list[dict]) -> str:
    picks = pick(rows)
    lines = [f"# AI 前沿 {day}", "", f"从当天收集的 {len(rows)} 条中精选 {len(picks)} 条，按重要度排序。时间为美东时间。", ""]
    for row in picks:
        lines += [f"## {_link(row['title_zh'], row['link'])}", "", f"{'★' * _importance(row)} · {_meta(row)}", ""]
        if row.get("_also"):
            lines += ["另见：" + "、".join(_link(other["source"], other["link"]) for other in row["_also"]), ""]
        if row.get("explain_zh") or row["summary_zh"]:
            lines += [row.get("explain_zh") or row["summary_zh"], ""]
        if row["title_zh"] != row["title"]:
            lines += [f"> {row['title']}", ""]
    return "\n".join(lines)


def rebuild_pages(data_dir: Path, digest_dir: Path, days: set[str]) -> None:
    rows = load_items(data_dir)
    for day in days:
        day_rows = [row for row in rows if row["detected_et"][:10] == day]
        path = digest_dir / day[:4] / f"{day}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_day(day, day_rows), encoding="utf-8")


def render_readme_sections(data_dir: Path, digest_dir: Path) -> dict[str, str]:
    rows = load_items(data_dir)
    days = sorted({row["detected_et"][:10] for row in rows}, reverse=True)
    recent = [row for row in rows if row["detected_et"][:10] in days[:2]]
    latest = ["| 重要度 | 标题 | 摘要 | 来源 |", "|---|---|---|---|"]
    for row in pick(recent):
        latest.append(f"| {'★' * _importance(row)} | {_link(row['title_zh'], row['link'])} | "
                      f"{_cell(row['summary_zh'])} | {_cell(row['source'])} |")
    archive = []
    for day in days[:14]:
        count = len(pick([row for row in rows if row["detected_et"][:10] == day]))
        archive.append(f"- [{day}]({digest_dir.as_posix()}/{day[:4]}/{day}.md)：{count} 条精选")
    return {"latest": "\n".join(latest), "archive": "\n".join(archive), "sources": render_sources(load_feeds())}


def render_sources(feeds: list[dict]) -> str:
    names: dict[str, list[str]] = {}
    for feed in feeds:
        label = f"{feed['name']}（{feed['note']}）" if feed.get("note") else feed["name"]
        if label not in names.setdefault(feed["group"], []):
            names[feed["group"]].append(label)
    lines = [f"- **{SOURCE_GROUP_TITLES.get(group, group)}**：{'、'.join(labels)}" for group, labels in names.items()]
    lines.append(f"- **社区**：Hacker News 首页 AI 相关讨论（{HN_MIN_POINTS} 分以上）、"
                 f"Hugging Face Daily Papers（{HF_MIN_UPVOTES} 赞以上）")
    return "\n".join(lines)


def update_readme(path: Path, sections: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    for name, body in sections.items():
        start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
        head, rest = text.split(start, 1)
        text = f"{head}{start}\n{body}\n{end}{rest.split(end, 1)[1]}"
    path.write_text(text, encoding="utf-8")


def commit_message(stored: list[dict], explained: int = 0) -> str:
    if not stored:
        return f"digest: explain {explained} pick(s)" if explained else "digest: refresh"
    counts = Counter(row["source"] for row in stored)
    detail = ", ".join(f"{source} ×{n}" if n > 1 else source for source, n in counts.most_common(5))
    extra = f"; explain {explained} pick(s)" if explained else ""
    return f"digest: {len(stored)} new item(s) ({detail}{', ...' if len(counts) > 5 else ''}){extra}"


def write_summary(path: str, lines: list[str], stored: list[dict], problems: list[str]) -> None:
    """Markdown run report for the GitHub Actions job summary."""
    report = ["## Digest run", "", *[f"- {line}" for line in lines], ""]
    if stored:
        report += ["| 来源 | 新条目 |", "|---|---|"]
        report += [f"| {source} | {n} |" for source, n in Counter(row["source"] for row in stored).most_common()]
        report.append("")
    report += ["### 问题", "", *([f"- {problem}" for problem in problems] or ["- 无"]), ""]
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(report))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--digest-dir", default="digest")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL") or "gemini-3.8-flash")
    parser.add_argument("--message-file", default=os.environ.get("COMMIT_MESSAGE_FILE", ""))
    args = parser.parse_args(argv)

    data_dir, digest_dir, now = Path(args.data_dir), Path(args.digest_dir), datetime.now(NEW_YORK)
    problems = []

    def log(message: str) -> None:
        print(message)
        problems.append(message)

    fetched = collect(now, log)
    new = select_new(fetched, {row["id"] for row in load_items(data_dir)}, now)
    print(f"Fetched {len(fetched)} item(s); {len(new)} new.")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        summaries = summarize(new, api_key, args.model, log)
    else:
        # Keep items unseen so they are summarized once the key is configured.
        print("GEMINI_API_KEY is not set; nothing stored.")
        summaries = {}
    stored = store_items(data_dir, new, summaries, now)
    grouped = bool(stored) and mark_events(data_dir, api_key, args.model, log)
    explained = explain_picks(data_dir, api_key, args.model, log) if api_key else []
    changed_days = {row["detected_et"][:10] for row in stored + explained}
    if grouped:
        changed_days |= set(_latest_days(load_items(data_dir)))
    if changed_days:
        rebuild_pages(data_dir, digest_dir, changed_days)
    update_readme(Path(args.readme), render_readme_sections(data_dir, digest_dir))
    message = commit_message(stored, len(explained))
    lines = [f"Fetched {len(fetched)} item(s); {len(new)} new.",
             f"Stored {len(stored)} item(s); {len(new) - len(stored)} left for the next run; "
             f"explained {len(explained)} pick(s).", message]
    print("\n".join(lines[1:]))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        write_summary(os.environ["GITHUB_STEP_SUMMARY"], lines, stored, problems)
    if args.message_file:
        Path(args.message_file).write_text(message + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
