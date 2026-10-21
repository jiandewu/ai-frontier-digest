import json
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
from digest.summarize import group_events  # noqa: E402
from digest.update import (NEW_YORK, mark_events, _importance, commit_message, explain_picks, item_id, load_items, rebuild_pages,  # noqa: E402
                           pick, render_readme_sections, render_sources, select_new, store_items, update_readme)


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


class UpdateTests(unittest.TestCase):
    def test_select_new_skips_known_old_duplicate_and_undated(self):
        undated = {**_item("https://d"), "published": None}
        fetched = [_item("https://a"), _item("https://a/"), _item("https://b"), _item("https://c", hours_ago=24 * 5), undated]
        new = select_new(fetched, {item_id("https://b")}, NOW)
        self.assertEqual([item["link"] for item in new], ["https://a"])

    def test_store_render_and_readme(self):
        items = select_new([_item("https://a", 3), _item("https://b", 2), _item("https://c", 1)], set(), NOW)
        summaries = {
            items[0]["id"]: {"title_zh": "重大发布 | 新模型", "summary_zh": "摘要一", "category": "模型发布", "importance": "5"},
            items[1]["id"]: {"title_zh": "一般资讯", "summary_zh": "摘要二", "category": "行业动态", "importance": "2"},
        }  # items[2] failed to summarize and must be retried later
        with tempfile.TemporaryDirectory() as tmp:
            data, digest = Path(tmp) / "data", Path(tmp) / "digest"
            stored = store_items(data, items, summaries, NOW)
            self.assertEqual(len(stored), 2)
            self.assertEqual(len(load_items(data)), 2)
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
        self.assertIn("★★★★★", text)
        self.assertNotIn("一般资讯", text)
        self.assertIn("- [2026-10-20](digest/2026/2026-10-20.md)：1 条精选", text)

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

    def test_commit_message(self):
        rows = [{"source": "OpenAI"}, {"source": "HF Daily Papers"}, {"source": "HF Daily Papers"}]
        self.assertEqual(commit_message(rows), "digest: 3 new item(s) (HF Daily Papers ×2, OpenAI)")
        self.assertEqual(commit_message([], 4), "digest: explain 4 pick(s)")


if __name__ == "__main__":
    unittest.main()
