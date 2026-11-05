import json
import xml.etree.ElementTree as ET
from collections import Counter
from unittest import mock
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digest.fulltext import extract_text  # noqa: E402
from digest.sources import load_feeds, parse_feed, parse_hf_papers, parse_hn  # noqa: E402
from digest import summarize  # noqa: E402
from digest.summarize import Unavailable, group_events  # noqa: E402
from digest.update import (NEW_YORK, archive_keys, rebuild_periods, week_of, is_pending, pending_items, resolve_pending, mark_events, _importance, commit_message, explain_picks, item_id, load_items, rebuild_pages,  # noqa: E402
                           pick, render_feed, render_readme_sections, render_sources, select_new, store_items,
                           update_readme)


NOW = datetime(2026, 10, 20, 16, 0, tzinfo=NEW_YORK)

RSS = """<?xml version="1.0"?><rss><channel>
<item><title>New model &amp; benchmark</title><link>https://lab.example/a</link>
<pubDate>Tue, 20 Oct 2026 14:00:00 GMT</pubDate><description>&lt;p&gt;We release it.&lt;/p&gt;</description></item>
<item><title>No link</title></item>
</channel></rss>"""

ATOM = """<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Atom post</title><link href="https://blog.example/p" rel="alternate"/>
<published>2026-10-19T09:00:00+00:00</published><summary>Notes</summary></entry></feed>"""


def _item(link, hours_ago=1):
    return {"title": f"T {link}", "link": link, "published": NOW - timedelta(hours=hours_ago), "snippet": "",
            "source": "Blog", "group": "个人博客", "score": ""}


class SourceTests(unittest.TestCase):
    def test_parse_rss_and_atom(self):
        rss = parse_feed(RSS, "Lab", "实验室")
        self.assertEqual([(item["title"], item["snippet"]) for item in rss], [("New model & benchmark", "We release it.")])
        atom = parse_feed(ATOM, "Blog", "个人博客")
        self.assertEqual(atom[0]["link"], "https://blog.example/p")
        self.assertEqual(atom[0]["published"], datetime(2026, 10, 19, 9, tzinfo=timezone.utc))

    def test_parse_feed_ignores_bytes_after_root(self):
        items = parse_feed(RSS + "stale tail</description></item></channel></rss>", "Lab", "实验室")
        self.assertEqual(len(items), 1)

    def test_parse_hn_filters_points_and_topic(self):
        hits = {"hits": [
            {"objectID": "1", "title": "DeepSeek releases new LLM", "points": 900, "url": "https://x/1", "created_at": "2026-10-20T10:00:00Z"},
            {"objectID": "2", "title": "Apple iPad bug", "points": 900, "url": "https://x/2", "created_at": "2026-10-20T10:00:00Z"},
            {"objectID": "3", "title": "Small AI tool", "points": 50, "url": "https://x/3", "created_at": "2026-10-20T10:00:00Z"},
        ]}
        items = parse_hn(json.dumps(hits))
        self.assertEqual([item["link"] for item in items], ["https://x/1"])
        self.assertEqual(items[0]["score"], "900")

    def test_feeds_csv_is_valid(self):
        feeds = load_feeds()
        self.assertTrue(feeds)
        for feed in feeds:
            self.assertTrue(feed["name"] and feed["group"] and feed["url"].startswith("https://"), feed)
            self.assertNotIn(".substack.com", feed["url"])  # blocked on GitHub-hosted runners
        urls = [feed["url"] for feed in feeds]
        self.assertEqual(len(urls), len(set(urls)))

    def test_render_sources_merges_names_and_notes(self):
        feeds = [{"name": "A", "group": "个人博客", "url": "u1", "note": ""},
                 {"name": "A", "group": "个人博客", "url": "u2", "note": ""},
                 {"name": "B", "group": "个人博客", "url": "u3", "note": "Bob"},
                 {"name": "Lab", "group": "实验室", "url": "u4", "note": ""}]
        lines = render_sources(feeds).splitlines()
        self.assertEqual(lines[:2], ["- **研究者与作者**：A、B（Bob）", "- **实验室**：Lab"])
        self.assertTrue(lines[2].startswith("- **社区**"))

    def test_parse_hf_papers_threshold(self):
        papers = [{"paper": {"id": "2610.1", "title": "Hot", "upvotes": 145, "ai_summary": "Sum",
                             "submittedOnDailyAt": "2026-10-20T00:00:00.000Z"}},
                  {"paper": {"id": "2610.2", "title": "Cold", "upvotes": 3}}]
        items = parse_hf_papers(json.dumps(papers))
        self.assertEqual([item["link"] for item in items], ["https://huggingface.co/papers/2610.1"])


class SummarizeTests(unittest.TestCase):
    def test_generate_falls_back_and_promotes_working_model(self):
        answer = {"candidates": [{"content": {"parts": [{"text": '{"items": [{"id": "a"}]}'}]}}]}
        calls = []

        def fake_call(model, *args):
            calls.append(model)
            if model == "busy":
                raise Unavailable("Gemini HTTP 503")
            return answer

        models = ["busy", "ok", "spare"]
        with mock.patch("digest.summarize._call", side_effect=fake_call):
            logged = []
            self.assertEqual(summarize._generate("s", "u", {}, "h", "key", models, logged.append), [{"id": "a"}])
            summarize._generate("s", "u", {}, "h", "key", models, logged.append)
        self.assertEqual(len(logged), 1)
        self.assertIn("fallback to ok", logged[0])
        self.assertEqual(calls, ["busy", "ok", "ok"])
        self.assertEqual(models, ["ok", "spare", "busy"])

    def test_generate_reports_all_unavailable(self):
        with mock.patch("digest.summarize._call", side_effect=Unavailable("Gemini HTTP 429")):
            with self.assertRaisesRegex(RuntimeError, "All Gemini models unavailable"):
                summarize._generate("s", "u", {}, "h", "key", ["a", "b"])

    def test_post_does_not_retry_quota_errors(self):
        error = summarize.urllib.error.HTTPError("u", 429, "quota", {}, None)
        error.read = lambda: b"quota"
        with mock.patch("digest.summarize.urllib.request.urlopen", side_effect=error) as urlopen, \
             mock.patch("digest.summarize.time.sleep") as sleep:
            with self.assertRaises(Unavailable):
                summarize._post("https://gemini.example/m", {}, "key")
        self.assertEqual((urlopen.call_count, sleep.call_count), (1, 0))


class UpdateTests(unittest.TestCase):
    def test_select_new_skips_known_old_duplicate_and_undated(self):
        undated = {**_item("https://d"), "published": None}
        fetched = [_item("https://a"), _item("https://a/"), _item("https://b"), _item("https://c", hours_ago=24 * 5), undated]
        new = select_new(fetched, {item_id("https://b")}, NOW)
        self.assertEqual([item["link"] for item in new], ["https://a"])

    def test_select_new_clamps_future_dates(self):
        new = select_new([_item("https://future", hours_ago=-24 * 10)], set(), NOW)
        self.assertEqual(new[0]["published"], NOW)

    def test_store_render_and_readme(self):
        items = select_new([_item("https://a", 3), _item("https://b", 2), _item("https://c", 1)], set(), NOW)
        summaries = {
            items[0]["id"]: {"title_zh": "重大发布 | 新模型", "summary_zh": "摘要一", "category": "模型发布", "importance": "5"},
            items[1]["id"]: {"title_zh": "一般资讯", "summary_zh": "摘要二", "category": "行业动态", "importance": "2"},
        }  # items[2] failed to summarize and is stored as pending
        with tempfile.TemporaryDirectory() as tmp:
            data, digest = Path(tmp) / "data", Path(tmp) / "digest"
            stored = store_items(data, items, summaries, NOW)
            self.assertEqual([is_pending(row) for row in stored], [False, False, True])
            self.assertEqual(len(load_items(data)), 3)
            rebuild_pages(data, digest, {"2026-10-20"})
            page = (digest / "2026" / "2026-10-20.md").read_text(encoding="utf-8")
            readme = Path(tmp) / "README.md"
            readme.write_text("<!-- latest:start -->\nold\n<!-- latest:end -->\n<!-- archive:start -->\n<!-- archive:end -->\n"
                              "<!-- sources:start -->\n<!-- sources:end -->\n",
                              encoding="utf-8")
            update_readme(readme, render_readme_sections(data, Path("digest")))
            text = readme.read_text(encoding="utf-8")
        self.assertIn("## [重大发布 \\| 新模型](https://a)", page)
        self.assertIn("从当天收集的 2 条中精选 1 条", page)
        self.assertNotIn("一般资讯", page)  # below PICK_MIN_IMPORTANCE
        self.assertNotIn("old", text)
        self.assertIn("<!-- latest:start -->\n\n| 重要度 |", text)
        self.assertIn("★★★★★", text)
        self.assertNotIn("一般资讯", text)
        self.assertIn("- [2026-10-20](digest/2026/2026-10-20.md)：1 条精选", text)

    def test_day_navigation_and_feed(self):
        later = NOW + timedelta(days=1)
        day1 = select_new([_item("https://a", 3)], set(), NOW)
        day2 = select_new([_item("https://b & c", 3 - 24)], set(), later)
        summary = {"title_zh": "新模型 <发布>", "summary_zh": "摘要", "category": "模型发布", "importance": "4"}
        with tempfile.TemporaryDirectory() as tmp:
            data, digest = Path(tmp) / "data", Path(tmp) / "digest"
            store_items(data, day1, {day1[0]["id"]: summary}, NOW)
            rebuild_pages(data, digest, {"2026-10-20"})
            self.assertNotIn("→", (digest / "2026" / "2026-10-20.md").read_text(encoding="utf-8"))
            store_items(data, day2, {day2[0]["id"]: summary}, later)
            rebuild_pages(data, digest, {"2026-10-21"})  # the earlier page gains its next link
            first = (digest / "2026" / "2026-10-20.md").read_text(encoding="utf-8")
            second = (digest / "2026" / "2026-10-21.md").read_text(encoding="utf-8")
            feed = render_feed(data)
        self.assertIn("[2026-10-21](../2026/2026-10-21.md) →", first)
        self.assertIn("← [2026-10-20](../2026/2026-10-20.md)", second)
        root = ET.fromstring(feed)
        items = root.findall("./channel/item")
        self.assertEqual([item.findtext("link") for item in items], ["https://b & c", "https://a"])
        self.assertEqual(items[0].findtext("title"), "新模型 <发布>")
        self.assertIn('<a href="https://jiande.is-a.si/ai-frontier-digest/digest/2026/2026-10-21.html">',
                      items[0].findtext("description"))

    def test_blog_bonus(self):
        rows = [{"group": "个人博客", "importance": "3"}, {"group": "个人博客", "importance": "5"},
                {"group": "个人博客", "importance": "2"}, {"group": "新闻汇总", "importance": "3"}]
        self.assertEqual([_importance(row) for row in rows], [4, 5, 2, 3])

    def test_pick_caps_per_source_and_total(self):
        rows = [{"id": f"{source}{n}", "source": source, "group": "实验室", "importance": "4",
                 "published_et": f"2026-10-20 0{n}:00"}
                for source in "ABCDEFG" for n in range(3)]
        picks = pick(rows)
        self.assertEqual(len(picks), 10)
        self.assertLessEqual(max(Counter(row["source"] for row in picks).values()), 2)

    def test_extract_text_prefers_article(self):
        page = ("<html><body><nav>Menu</nav><main>Repo chrome <article><p>Real &amp; long text.</p>"
                "<script>x()</script></article></main></body></html>")
        self.assertEqual(extract_text(page), "Real & long text.")

    def test_explain_picks_stores_explanations_and_renders_them(self):
        items = select_new([_item("https://a", 2), _item("https://b", 1)], set(), NOW)
        summaries = {item["id"]: {"title_zh": f"标题{n}", "summary_zh": f"短摘要{n}", "category": "研究",
                                  "importance": "4"} for n, item in enumerate(items)}
        with tempfile.TemporaryDirectory() as tmp:
            data, digest = Path(tmp) / "data", Path(tmp) / "digest"
            store_items(data, items, summaries, NOW)
            fake_text = {"https://a": "full text", "https://b": ""}  # b is unreadable
            with mock.patch("digest.update.fetch_text", side_effect=fake_text.get), \
                 mock.patch("digest.update.explain", side_effect=lambda readable, *_: {
                     entry["id"]: "通俗解释" for entry in readable}) as explain_mock:
                explained = explain_picks(data, "key", "model", log=lambda _: None)
                self.assertEqual([row["link"] for row in explained], ["https://a"])
                explain_picks(data, "key", "model", log=lambda _: None)  # a is not explained twice
                self.assertEqual(explain_mock.call_args.args[0], [])
            rows = {row["link"]: row for row in load_items(data)}
            self.assertEqual((rows["https://a"]["explain_zh"], rows["https://b"]["explain_zh"]), ("通俗解释", ""))
            rebuild_pages(data, digest, {"2026-10-20"})
            page = (digest / "2026" / "2026-10-20.md").read_text(encoding="utf-8")
        self.assertIn("通俗解释", page)
        self.assertNotIn("短摘要0", page)
        self.assertIn("短摘要1", page)

    def test_events_merge_coverage_and_dedupe_picks(self):
        items = select_new([_item("https://lab/a", 3), _item("https://news/a", 2), _item("https://c", 1)], set(), NOW)
        sources = ["Lab", "News", "Blog"]
        items = [{**item, "source": source, "group": "实验室"} for item, source in zip(items, sources)]
        summaries = {item["id"]: {"title_zh": item["link"], "summary_zh": "", "category": "研究", "importance": "3"}
                     for item in items}
        with tempfile.TemporaryDirectory() as tmp:
            data, digest = Path(tmp) / "data", Path(tmp) / "digest"
            store_items(data, items, summaries, NOW)
            same = [items[0]["id"], items[1]["id"]]
            with mock.patch("digest.update.group_events", return_value=[same]):
                self.assertTrue(mark_events(data, "key", "model"))
            rows = load_items(data)
            picks = pick(rows)
            rebuild_pages(data, digest, {"2026-10-20"})
            page = (digest / "2026" / "2026-10-20.md").read_text(encoding="utf-8")
        self.assertEqual([row["link"] for row in picks], ["https://lab/a", "https://c"])  # one per event
        self.assertEqual([_importance(row) for row in picks], [4, 3])  # covered by two sources
        self.assertIn("另见：[News](https://news/a)", page)

    def test_group_events_validates_ids(self):
        items = [{"id": i, "source": "S", "title_zh": "t", "summary_zh": "s"} for i in "abcd"]
        reply = [{"ids": ["a", "b", "a"]}, {"ids": ["b", "c"]}, {"ids": ["d", "zz"]}]
        with mock.patch("digest.summarize._generate", return_value=reply):
            self.assertEqual(group_events(items, "key", "model"), [["a", "b"]])
        with mock.patch("digest.summarize._generate", side_effect=RuntimeError("boom")):
            self.assertIsNone(group_events(items, "key", "model", log=lambda _: None))

    def test_pending_items_are_retried_then_published(self):
        items = select_new([_item("https://a"), _item("https://b")], set(), NOW)
        with tempfile.TemporaryDirectory() as tmp:
            data, digest = Path(tmp) / "data", Path(tmp) / "digest"
            store_items(data, items, {}, NOW)  # every Gemini model failed
            self.assertEqual(pick(load_items(data)), [])
            rebuild_pages(data, digest, {"2026-10-20"})
            page = (digest / "2026" / "2026-10-20.md").read_text(encoding="utf-8")
            self.assertIn("从当天收集的 0 条中精选 0 条", page)

            later = NOW + timedelta(days=5)
            pending = pending_items(data, later)
            self.assertEqual({item["title"] for item in pending}, {"T https://a", "T https://b"})
            summary = {"title_zh": "补上的标题", "summary_zh": "摘要", "category": "研究", "importance": "4"}
            resolved = resolve_pending(data, {items[0]["id"]: summary})
            self.assertEqual([row["link"] for row in resolved], ["https://a"])
            rows = load_items(data)
            self.assertEqual([row["link"] for row in pick(rows)], ["https://a"])
            self.assertEqual({row["detected_et"][:10] for row in rows}, {"2026-10-20"})  # stays on its day
            self.assertEqual(len(pending_items(data, later)), 1)
            self.assertEqual(pending_items(data, NOW + timedelta(days=15)), [])  # gives up after PENDING_DAYS

    def test_archive_keys_compress_by_age(self):
        days = ["2026-11-05", "2026-10-30", "2026-10-29", "2026-10-20", "2026-09-20", "2025-08-01", "2024-12-31"]
        self.assertEqual(archive_keys(days), ["2026-11-05", "2026-10-30", "2026-W44", "2026-W43", "2026-09", "2025", "2024"])
        self.assertEqual(archive_keys([]), [])

    def test_week_of_uses_iso_weeks(self):
        self.assertEqual(week_of("2026-10-26"), "2026-W44")  # Monday
        self.assertEqual(week_of("2026-11-01"), "2026-W44")  # Sunday
        self.assertEqual(week_of("2027-01-01"), "2026-W53")  # ISO year differs near New Year

    def test_rebuild_periods_writes_week_month_and_year(self):
        items = select_new([_item("https://a", 2), _item("https://b", 1)], set(), NOW)
        summaries = {item["id"]: {"title_zh": f"标题{n}", "summary_zh": "摘要", "category": "研究", "importance": "4"}
                     for n, item in enumerate(items)}
        with tempfile.TemporaryDirectory() as tmp:
            data, digest = Path(tmp) / "data", Path(tmp) / "digest"
            store_items(data, items, summaries, NOW)  # NOW is 2026-10-20, ISO week 2026-W43
            rebuild_periods(data, digest)
            week = (digest / "2026" / "2026-W43.md").read_text(encoding="utf-8")
            month = (digest / "2026" / "2026-10.md").read_text(encoding="utf-8")
            year = (digest / "2026" / "2026.md").read_text(encoding="utf-8")
        self.assertIn("# AI 前沿 2026-W43（10-19 至 10-25）", week)
        self.assertIn("标题0", week)
        self.assertIn("每天：[10-20](../2026/2026-10-20.md)", week)
        self.assertIn("- [2026-W43（10-19 至 10-25）](../2026/2026-W43.md)：2 条精选", month)
        self.assertIn("- [2026-10](../2026/2026-10.md)：1 周", year)

    def test_commit_message(self):
        rows = [{"source": "OpenAI"}, {"source": "HF Daily Papers"}, {"source": "HF Daily Papers"}]
        self.assertEqual(commit_message(rows), "digest: 3 new item(s) (HF Daily Papers ×2, OpenAI)")
        self.assertEqual(commit_message([], 4), "digest: explain 4 pick(s)")
        self.assertEqual(commit_message([], 0, 7), "digest: 7 pending")
        self.assertEqual(commit_message(rows[:1], 0, 2), "digest: 1 new item(s) (OpenAI); 2 pending")


if __name__ == "__main__":
    unittest.main()
