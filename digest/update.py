"""Collect new items, summarize them, and rebuild the daily pages and README.

Files only change when new items arrive, so a quiet run produces no commit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from email.utils import format_datetime
from xml.sax.saxutils import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from .sources import HF_MIN_UPVOTES, HN_MIN_POINTS, collect, load_feeds
from .fulltext import fetch_text
from .summarize import DEFAULT_MODELS, explain, group_events, summarize


NEW_YORK = ZoneInfo("America/New_York")
ITEM_COLUMNS = ["id", "detected_et", "published_et", "source", "group", "title", "title_zh", "summary_zh",
                "category", "importance", "score", "link", "explain_zh", "event", "snippet"]
LOOKBACK_DAYS = 3
# New items Gemini could not summarize are stored as pending (no importance) and retried for this long.
PENDING_DAYS = 14
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
SITE_URL = "https://jiande.is-a.si/ai-frontier-digest/"
# The RSS feed covers this many recent days.
RECENT_DAYS = 14
# The README archive lists each day of the latest week, then ISO weeks, then months, then years,
# by age in days from the latest day.
ARCHIVE_DAY_AGE = 7
ARCHIVE_WEEK_AGE = 35
ARCHIVE_MONTH_AGE = 365


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


def mark_events(data_dir: Path, api_key: str, models: list[str], log=print) -> bool:
    """Group the two latest days' candidates by event; False if Gemini failed and nothing changed."""
    rows = load_items(data_dir)
    days = _latest_days(rows)
    candidates = [row for row in _rank([row for row in rows if row["detected_et"][:10] in days])
                  if int(row["importance"] or 0) >= PICK_MIN_IMPORTANCE][:EVENT_CANDIDATES]
    groups = group_events(candidates, api_key, models, log)
    if groups is None:
        return False
    updates = {row["id"]: {"event": ""} for row in candidates}
    for ids in groups:
        updates.update({identifier: {"event": min(ids)} for identifier in ids})
    update_rows(data_dir, updates)
    return True


def explain_picks(data_dir: Path, api_key: str, models: list[str], log=print) -> list[dict]:
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
    explanations = explain(readable, api_key, models, log)
    update_rows(data_dir, {identifier: {"explain_zh": text} for identifier, text in explanations.items()})
    return [row for row in candidates if row["id"] in explanations]


def is_pending(row: dict) -> bool:
    """Stored but not yet summarized; pending rows are never picked."""
    return not row["importance"]


def _summary_fields(summary: dict, title: str) -> dict:
    return {"title_zh": summary["title_zh"] or title, "summary_zh": summary["summary_zh"],
            "category": summary["category"], "importance": summary["importance"]}


def store_items(data_dir: Path, items: list[dict], summaries: dict[str, dict], now: datetime) -> list[dict]:
    """Store every new item; those without a summary are stored as pending so a Gemini outage loses nothing."""
    stored = []
    for item in items:
        summary = summaries.get(item["id"])
        stored.append({
            "id": item["id"], "detected_et": now.strftime("%Y-%m-%d %H:%M"),
            "published_et": item["published"].astimezone(NEW_YORK).strftime("%Y-%m-%d %H:%M"),
            "source": item["source"], "group": item["group"], "title": item["title"],
            **(_summary_fields(summary, item["title"]) if summary
               else dict.fromkeys(("title_zh", "summary_zh", "category", "importance"), "")),
            "score": item["score"], "link": item["link"], "snippet": item["snippet"],
        })
    if stored:
        path = data_dir / "items" / now.strftime("%Y") / f"{now:%Y-%m}.csv"
        rows = _read_csv(path) + stored
        rows.sort(key=lambda row: (row["detected_et"], row["published_et"], row["id"]), reverse=True)
        _write_csv(path, rows)
    return stored


def pending_items(data_dir: Path, now: datetime) -> list[dict]:
    """Pending rows detected within PENDING_DAYS, in the shape summarize() expects."""
    cutoff = (now - timedelta(days=PENDING_DAYS)).strftime("%Y-%m-%d %H:%M")
    return [{"id": row["id"], "source": row["source"], "title": row["title"], "snippet": row.get("snippet", "")}
            for row in load_items(data_dir) if is_pending(row) and row["detected_et"] >= cutoff]


def resolve_pending(data_dir: Path, summaries: dict[str, dict]) -> list[dict]:
    """Fill in the summaries of pending rows; they stay on the day they were detected."""
    rows = [row for row in load_items(data_dir) if is_pending(row) and row["id"] in summaries]
    update_rows(data_dir, {row["id"]: _summary_fields(summaries[row["id"]], row["title"]) for row in rows})
    return rows


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


def _day_link(day: str) -> str:
    return f"[{day}](../{day[:4]}/{day}.md)"


def _render_picks(picks: list[dict]) -> list[str]:
    lines = []
    for row in picks:
        lines += [f"## {_link(row['title_zh'], row['link'])}", "", f"{'★' * _importance(row)} · {_meta(row)}", ""]
        if row.get("_also"):
            lines += ["另见：" + "、".join(_link(other["source"], other["link"]) for other in row["_also"]), ""]
        if row.get("explain_zh") or row["summary_zh"]:
            lines += [row.get("explain_zh") or row["summary_zh"], ""]
        if row["title_zh"] != row["title"]:
            lines += [f"> {row['title']}", ""]
    return lines


def week_of(day: str) -> str:
    """ISO week key such as 2026-W44 (Monday to Sunday; the ISO year can differ near New Year)."""
    year, week, _ = date.fromisoformat(day).isocalendar()
    return f"{year}-W{week:02d}"


def _week_span(week: str) -> str:
    monday = date.fromisocalendar(int(week[:4]), int(week[6:]), 1)
    return f"{monday:%m-%d} 至 {monday + timedelta(days=6):%m-%d}"


def _period_path(key: str) -> str:
    """Page of a day (2026-10-28), ISO week (2026-W44), month (2026-10) or year (2026), under the digest dir."""
    return f"{key[:4]}/{key}.md"


def _period_link(key: str, label: str = "", base: str = "..") -> str:
    return f"[{label or key}]({base}/{_period_path(key)})"


def render_week(week: str, rows: list[dict], prev_week: str = "", next_week: str = "") -> str:
    picks = pick(rows)
    days = sorted({row["detected_et"][:10] for row in rows})
    collected = sum(1 for row in rows if not is_pending(row))
    lines = [f"# AI 前沿 {week}（{_week_span(week)}）", "",
             f"本周 {len(days)} 天共收集 {collected} 条，精选 {len(picks)} 条，按重要度排序。时间为美东时间。", ""]
    lines += _render_picks(picks)
    lines += ["---", "", "每天：" + " · ".join(_period_link(day, day[5:]) for day in days), ""]
    nav = [f"← {_period_link(prev_week)}" if prev_week else "", f"{_period_link(next_week)} →" if next_week else ""]
    if any(nav):
        lines += [" · ".join(part for part in nav if part), ""]
    return "\n".join(lines)


def render_month(month: str, week_counts: list[tuple[str, int]]) -> str:
    lines = [f"# AI 前沿 {month}", "", "各周精选：", ""]
    lines += [f"- {_period_link(week, f'{week}（{_week_span(week)}）')}：{count} 条精选" for week, count in week_counts]
    lines += ["", f"全年：{_period_link(month[:4])}", ""]
    return "\n".join(lines)


def render_year(year: str, month_weeks: list[tuple[str, int]]) -> str:
    lines = [f"# AI 前沿 {year}", ""]
    lines += [f"- {_period_link(month)}：{weeks} 周" for month, weeks in month_weeks]
    return "\n".join(lines + [""])


def rebuild_periods(data_dir: Path, digest_dir: Path) -> None:
    """Rewrite every week, month and year page; unchanged pages give unchanged files."""
    rows = load_items(data_dir)
    by_week = defaultdict(list)
    for row in rows:
        by_week[week_of(row["detected_et"][:10])].append(row)
    weeks = sorted(by_week)
    month_weeks = defaultdict(list)  # a week spanning two months is listed in both
    for i, week in enumerate(weeks):
        prev_week = weeks[i - 1] if i > 0 else ""
        next_week = weeks[i + 1] if i + 1 < len(weeks) else ""
        _write(digest_dir / _period_path(week), render_week(week, by_week[week], prev_week, next_week))
        count = len(pick(by_week[week]))
        for month in sorted({row["detected_et"][:7] for row in by_week[week]}):
            month_weeks[month].append((week, count))
    year_months = defaultdict(list)
    for month, week_counts in sorted(month_weeks.items()):
        _write(digest_dir / _period_path(month), render_month(month, sorted(week_counts, reverse=True)))
        year_months[month[:4]].append((month, len(week_counts)))
    for year, months in year_months.items():
        _write(digest_dir / _period_path(year), render_year(year, sorted(months, reverse=True)))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def archive_keys(days: list[str]) -> list[str]:
    """README archive entries, newest first: days of the latest week, then weeks, months and years."""
    if not days:
        return []
    latest, keys = date.fromisoformat(max(days)), []
    for day in sorted(days, reverse=True):
        age = (latest - date.fromisoformat(day)).days
        if age < ARCHIVE_DAY_AGE:
            key = day
        elif age < ARCHIVE_WEEK_AGE:
            key = week_of(day)
        elif age < ARCHIVE_MONTH_AGE:
            key = day[:7]
        else:
            key = day[:4]
        if key not in keys:
            keys.append(key)
    return keys


def render_day(day: str, rows: list[dict], prev_day: str = "", next_day: str = "") -> str:
    picks = pick(rows)
    collected = sum(1 for row in rows if not is_pending(row))
    lines = [f"# AI 前沿 {day}", "", f"从当天收集的 {collected} 条中精选 {len(picks)} 条，按重要度排序。时间为美东时间。", ""]
    lines += _render_picks(picks)
    nav = [f"← {_day_link(prev_day)}" if prev_day else "", f"{_day_link(next_day)} →" if next_day else ""]
    if any(nav):
        lines += ["---", "", " · ".join(part for part in nav if part), ""]
    return "\n".join(lines)


def rebuild_pages(data_dir: Path, digest_dir: Path, days: set[str]) -> None:
    """Rebuild the given days and their neighbors, whose previous/next links may point at a new day."""
    rows = load_items(data_dir)
    all_days = sorted({row["detected_et"][:10] for row in rows})
    targets = set()
    for i, day in enumerate(all_days):
        if day in days:
            targets.update(all_days[max(i - 1, 0):i + 2])
    for i, day in enumerate(all_days):
        if day not in targets:
            continue
        day_rows = [row for row in rows if row["detected_et"][:10] == day]
        prev_day = all_days[i - 1] if i > 0 else ""
        next_day = all_days[i + 1] if i + 1 < len(all_days) else ""
        path = digest_dir / day[:4] / f"{day}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_day(day, day_rows, prev_day, next_day), encoding="utf-8")


def render_readme_sections(data_dir: Path, digest_dir: Path) -> dict[str, str]:
    rows = load_items(data_dir)
    days = sorted({row["detected_et"][:10] for row in rows}, reverse=True)
    recent = [row for row in rows if row["detected_et"][:10] in days[:2]]
    latest = ["| 重要度 | 标题 | 摘要 | 来源 |", "|---|---|---|---|"]
    for row in pick(recent):
        latest.append(f"| {'★' * _importance(row)} | {_link(row['title_zh'], row['link'])} | "
                      f"{_cell(row['summary_zh'])} | {_cell(row['source'])} |")
    archive, base = [], digest_dir.as_posix()
    for key in archive_keys(days):
        if "-W" in key:
            count = len(pick([row for row in rows if week_of(row["detected_et"][:10]) == key]))
            archive.append(f"- {_period_link(key, f'{key}（{_week_span(key)}）', base)}：{count} 条精选")
        elif len(key) == 10:
            count = len(pick([row for row in rows if row["detected_et"][:10] == key]))
            archive.append(f"- {_period_link(key, base=base)}：{count} 条精选")
        else:
            archive.append(f"- {_period_link(key, base=base)}")
    return {"latest": "\n".join(latest), "archive": "\n".join(archive), "sources": render_sources(load_feeds())}


def render_feed(data_dir: Path) -> str:
    """RSS 2.0 of the recent daily picks, newest day first; no build time, so unchanged picks give an unchanged file."""
    rows = load_items(data_dir)
    days = sorted({row["detected_et"][:10] for row in rows}, reverse=True)[:RECENT_DAYS]
    items = []
    for day in days:
        page = f"{SITE_URL}digest/{day[:4]}/{day}.html"
        for row in pick([row for row in rows if row["detected_et"][:10] == day]):
            published = datetime.strptime(row["published_et"], "%Y-%m-%d %H:%M").replace(tzinfo=NEW_YORK)
            # The description is HTML, escaped once more to sit inside XML.
            body = (f"<p>{escape(row.get('explain_zh') or row['summary_zh'])}</p>"
                    f"<p>{'★' * _importance(row)} · {escape(row['source'])} · <a href=\"{page}\">{day} 精选</a></p>")
            items.append("\n".join([
                "<item>",
                f"<title>{escape(row['title_zh'])}</title>",
                f"<link>{escape(row['link'])}</link>",
                f'<guid isPermaLink="false">{row["id"]}</guid>',
                f"<pubDate>{format_datetime(published)}</pubDate>",
                f"<description>{escape(body)}</description>",
                "</item>",
            ]))
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        "<channel>",
        "<title>AI 前沿导读</title>",
        f"<link>{SITE_URL}</link>",
        "<description>每天精选 10 条以内最值得一读的 AI 前沿进展，附中文科普解释。</description>",
        "<language>zh-CN</language>",
        *items,
        "</channel>",
        "</rss>",
        "",
    ])


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
        # Blank lines keep kramdown (GitHub Pages) from folding a table under the comment into a paragraph.
        text = f"{head}{start}\n\n{body}\n\n{end}{rest.split(end, 1)[1]}"
    path.write_text(text, encoding="utf-8")


def commit_message(stored: list[dict], explained: int = 0, pending: int = 0) -> str:
    """stored: newly summarized rows; pending: rows still waiting for Gemini."""
    extras = ([f"explain {explained} pick(s)"] if explained else []) + ([f"{pending} pending"] if pending else [])
    if not stored:
        return f"digest: {'; '.join(extras)}" if extras else "digest: refresh"
    counts = Counter(row["source"] for row in stored)
    detail = ", ".join(f"{source} ×{n}" if n > 1 else source for source, n in counts.most_common(5))
    extra = "".join(f"; {text}" for text in extras)
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
    parser.add_argument("--feed", default="feed.xml")
    parser.add_argument("--models", default=os.environ.get("GEMINI_MODEL") or ",".join(DEFAULT_MODELS),
                        help="comma-separated Gemini models, tried in order")
    parser.add_argument("--message-file", default=os.environ.get("COMMIT_MESSAGE_FILE", ""))
    args = parser.parse_args(argv)

    data_dir, digest_dir, now = Path(args.data_dir), Path(args.digest_dir), datetime.now(NEW_YORK)
    models = [model.strip() for model in args.models.split(",") if model.strip()]
    problems = []

    def log(message: str) -> None:
        print(message)
        problems.append(message)

    fetched = collect(now, log)
    new = select_new(fetched, {row["id"] for row in load_items(data_dir)}, now)
    print(f"Fetched {len(fetched)} item(s); {len(new)} new.")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    pending = pending_items(data_dir, now)
    if pending:
        print(f"Retrying {len(pending)} pending item(s).")
    if api_key:
        summaries = summarize(pending + new, api_key, models, log)
    else:
        print("GEMINI_API_KEY is not set; new items are stored as pending.")
        summaries = {}
    stored = store_items(data_dir, new, summaries, now)
    resolved = resolve_pending(data_dir, summaries)
    summarized = [row for row in stored if not is_pending(row)] + resolved
    still_pending = len(pending) - len(resolved) + sum(1 for row in stored if is_pending(row))
    grouped = bool(summarized) and mark_events(data_dir, api_key, models, log)
    explained = explain_picks(data_dir, api_key, models, log) if api_key else []
    changed_days = {row["detected_et"][:10] for row in summarized + explained}
    if grouped:
        changed_days |= set(_latest_days(load_items(data_dir)))
    if changed_days:
        rebuild_pages(data_dir, digest_dir, changed_days)
    rebuild_periods(data_dir, digest_dir)
    update_readme(Path(args.readme), render_readme_sections(data_dir, digest_dir))
    Path(args.feed).write_text(render_feed(data_dir), encoding="utf-8")
    message = commit_message(summarized, len(explained), still_pending)
    lines = [f"Fetched {len(fetched)} item(s); {len(new)} new; {len(pending)} pending from earlier runs.",
             f"Summarized {len(summarized)} item(s) ({len(resolved)} of them pending before); "
             f"{still_pending} still pending; explained {len(explained)} pick(s).", message]
    print("\n".join(lines[1:]))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        write_summary(os.environ["GITHUB_STEP_SUMMARY"], lines, summarized, problems)
    if args.message_file:
        Path(args.message_file).write_text(message + "\n", encoding="utf-8")
    if api_key and (pending or new) and not summaries:
        # The workflow commits the pending rows first, then fails on this output so GitHub sends a notification.
        print(f"Gemini summarized none of {len(pending) + len(new)} item(s); they are stored as pending.")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
                handle.write("gemini_failed=true\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
