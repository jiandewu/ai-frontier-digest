import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digest.sources import parse_feed, parse_hf_papers, parse_hn  # noqa: E402
from digest.update import (NEW_YORK, commit_message, item_id, load_items, rebuild_pages,  # noqa: E402
                           render_readme_sections, select_new, store_items, update_readme)


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

    def test_parse_hf_papers_threshold(self):
        papers = [{"paper": {"id": "2610.1", "title": "Hot", "upvotes": 45, "ai_summary": "Sum",
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
            readme.write_text("<!-- latest:start -->\nold\n<!-- latest:end -->\n<!-- archive:start -->\n<!-- archive:end -->\n",
                              encoding="utf-8")
            update_readme(readme, render_readme_sections(data, Path("digest")))
            text = readme.read_text(encoding="utf-8")
        self.assertIn("### [重大发布 \\| 新模型](https://a)", page)
        self.assertIn("## 其他", page)
        self.assertLess(page.index("重大发布"), page.index("一般资讯"))
        self.assertNotIn("old", text)
        self.assertIn("★★★★★", text)
        self.assertNotIn("一般资讯", text)
        self.assertIn("- [2026-10-20](digest/2026/2026-10-20.md)：2 条", text)

    def test_commit_message(self):
        rows = [{"source": "OpenAI"}, {"source": "HF Daily Papers"}, {"source": "HF Daily Papers"}]
        self.assertEqual(commit_message(rows), "digest: 3 new item(s) (HF Daily Papers ×2, OpenAI)")


if __name__ == "__main__":
    unittest.main()
