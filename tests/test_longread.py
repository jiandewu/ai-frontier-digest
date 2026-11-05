import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digest import longread  # noqa: E402
from digest.update import NEW_YORK, item_id  # noqa: E402

NOW = datetime(2026, 11, 5, 8, 0, tzinfo=NEW_YORK)


def _item(link, days_ago=1, source="Aeon"):
    return {"title": f"T {link}", "link": link, "published": NOW - timedelta(days=days_ago), "snippet": "s",
            "source": source, "group": "长文刊物", "score": ""}


def _row(day, title="标题"):
    return {"date": day, "id": item_id(f"https://x/{day}"), "source": "Noema", "title": "Original",
            "title_zh": title, "link": f"https://x/{day}", "published_et": day, "intro_zh": "导读正文",
            "why_zh": "值得一读"}


class LongReadTests(unittest.TestCase):
    def test_feeds_csv_is_valid(self):
        for feed in longread.load_feeds(longread.FEEDS_CSV):
            self.assertTrue(feed["name"] and feed["group"] and feed["url"].startswith("https://"), feed)

    def test_candidates_skip_picked_old_undated_and_videos(self):
        undated = {**_item("https://x/undated"), "published": None}
        items = [_item("https://x/a"), _item("https://x/a"), _item("https://x/old", 11), undated,
                 _item("https://aeon.co/videos/v"), _item("https://x/picked")]
        result = longread.candidates(items, {item_id("https://x/picked")}, NOW)
        self.assertEqual([item["link"] for item in result], ["https://x/a"])

    def test_rank_keeps_known_ids_in_order(self):
        items = longread.candidates([_item("https://x/a"), _item("https://x/b")], set(), NOW)
        answer = [{"id": items[1]["id"]}, {"id": "nope"}, {"id": items[1]["id"]}, {"id": items[0]["id"]}]
        with mock.patch("digest.longread._generate", return_value=answer):
            ranked = longread.rank(items, "key", ["m"])
        self.assertEqual([item["link"] for item in ranked], ["https://x/b", "https://x/a"])

    def test_choose_skips_short_pages(self):
        items = longread.candidates([_item("https://x/short"), _item("https://x/long")], set(), NOW)
        texts = {"https://x/short": "x" * 100, "https://x/long": "y" * longread.MIN_CHARS}
        intro = {"titleZh": "中文标题", "introZh": "导读", "whyZh": "因为"}
        with mock.patch("digest.longread._generate", side_effect=[[{"id": item["id"]} for item in items], [intro]]), \
             mock.patch("digest.longread.fetch_text", side_effect=lambda url, limit: texts[url]):
            row = longread.choose(items, "2026-11-05", "key", ["m"], lambda _: None)
        self.assertEqual((row["link"], row["title_zh"], row["published_et"]), ("https://x/long", "中文标题", "2026-11-04"))

    def test_write_site_pages_index_feed_and_latest(self):
        rows = [_row("2026-11-05", "今天 | 这篇"), _row("2026-11-04", "昨天")]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "index.md").write_text("<!-- latest:start -->\n<!-- latest:end -->\n<!-- archive:start -->\n"
                                          "<!-- archive:end -->\n<!-- sources:start -->\n<!-- sources:end -->\n",
                                          encoding="utf-8")
            longread.write_site(rows, out)
            today = (out / "2026" / "2026-11-05.md").read_text(encoding="utf-8")
            earlier = (out / "2026" / "2026-11-04.md").read_text(encoding="utf-8")
            index = (out / "index.md").read_text(encoding="utf-8")
            feed = ET.fromstring((out / "feed.xml").read_text(encoding="utf-8"))
            latest = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        self.assertTrue(today.startswith("# 今天 | 这篇"))
        self.assertIn("← [2026-11-04](../2026/2026-11-04.md)", today)
        self.assertIn("[2026-11-05](../2026/2026-11-05.md) →", earlier)
        self.assertIn("### [今天 \\| 这篇](2026/2026-11-05.md)", index)
        self.assertIn("- 2026-11-04：[昨天](2026/2026-11-04.md)（Noema）", index)
        self.assertIn("**长文刊物**：Aeon", index)
        self.assertEqual(feed.find("./channel/item/link").text,
                         "https://jiande.is-a.si/ai-frontier-digest/longread/2026/2026-11-05.html")
        self.assertEqual((latest["title"], latest["page"]), ("今天 | 这篇", "2026/2026-11-05.html"))

    def test_main_does_nothing_when_today_is_picked(self):
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch("digest.longread.datetime") as fake_datetime, \
             mock.patch("digest.longread.collect") as collect:
            fake_datetime.now.return_value = NOW
            longread.save_picks(Path(tmp) / "data" / "picks.csv", [_row("2026-11-05")])
            self.assertEqual(longread.main(["--out", tmp, "--message-file", ""]), 0)
        collect.assert_not_called()


class RedoTests(unittest.TestCase):
    def test_redo_rewrites_the_same_article(self):
        intro = {"titleZh": "新标题", "introZh": "新导读", "whyZh": "新理由"}
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.dict("os.environ", {"GEMINI_API_KEY": "key"}), \
             mock.patch("digest.longread.datetime") as fake_datetime, \
             mock.patch("digest.longread.collect") as collect, \
             mock.patch("digest.longread.fetch_text", return_value="y" * longread.MIN_CHARS), \
             mock.patch("digest.longread._generate", return_value=[intro]):
            fake_datetime.now.return_value = NOW
            fake_datetime.strptime = datetime.strptime
            out = Path(tmp)
            (out / "index.md").write_text("<!-- latest:start -->\n<!-- latest:end -->\n<!-- archive:start -->\n"
                                          "<!-- archive:end -->\n<!-- sources:start -->\n<!-- sources:end -->\n",
                                          encoding="utf-8")
            longread.save_picks(out / "data" / "picks.csv", [_row("2026-11-05", "旧标题"), _row("2026-11-04")])
            longread.main(["--out", tmp, "--message-file", "", "--redo"])
            rows = longread.load_picks(out / "data" / "picks.csv")
        collect.assert_not_called()
        self.assertEqual([(row["date"], row["title_zh"]) for row in rows], [("2026-11-05", "新标题"), ("2026-11-04", "标题")])
        self.assertEqual((rows[0]["link"], rows[0]["published_et"]), ("https://x/2026-11-05", "2026-11-05"))


if __name__ == "__main__":
    unittest.main()
