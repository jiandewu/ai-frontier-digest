import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digest import podcast  # noqa: E402
from digest.update import NEW_YORK, item_id  # noqa: E402

NOW = datetime(2026, 11, 9, 8, 0, tzinfo=NEW_YORK)

VTT = """WEBVTT

00:00:01.760 --> 00:00:35.760
<v Narrator>Welcome to the show.

00:00:35.760 --> 00:00:37.440
Now onto the show.

00:00:41.280 --> 00:01:11.920
<v Chris>Hello &amp; welcome.
"""

FEED = """<?xml version="1.0"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:podcast="https://podcastindex.org/namespace/1.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
<channel><title>Show</title>
<item><title>With transcript</title><link>https://x/1</link><pubDate>Thu, 05 Nov 2026 12:00:00 GMT</pubDate>
  <enclosure url="https://x/1.mp3" type="audio/mpeg"/><itunes:duration>2873</itunes:duration>
  <podcast:transcript url="https://x/1.vtt" type="text/vtt" rel="captions"/></item>
<item><title>Text in content</title><link>https://x/2</link><pubDate>Wed, 04 Nov 2026 12:00:00 GMT</pubDate>
  <enclosure url="https://x/2.mp3" type="audio/mpeg"/><itunes:duration>1:02:03</itunes:duration>
  <content:encoded><![CDATA[<p>Transcript</p><p>word word</p>]]></content:encoded></item>
<item><title>Essay without audio</title><link>https://x/3</link><pubDate>Wed, 04 Nov 2026 12:00:00 GMT</pubDate></item>
</channel></rss>"""


def _episode(link, days_ago=1, **extra):
    return {"source": "Show", "title": f"T {link}", "link": link, "published": NOW - timedelta(days=days_ago),
            "minutes": "48", "transcript_url": "", "transcript_type": "", "content": "", **extra}


def _row(day, link, added="2026-11-09 08:00"):
    return {"id": item_id(link), "source": "Show", "title": "Original", "title_zh": "标题", "link": link,
            "published_et": day, "minutes": "48", "words": "9000", "intro_zh": "导读正文 <b>",
            "points_zh": "要点一\n要点二", "why_zh": "适合谁", "added_et": added}


class PodcastTests(unittest.TestCase):
    def test_feeds_csv_is_valid(self):
        for feed in podcast.load_feeds(podcast.FEEDS_CSV):
            self.assertTrue(feed["name"] and feed["group"] and feed["url"].startswith("https://"), feed)

    def test_caption_text_keeps_speakers_and_drops_timing(self):
        self.assertEqual(podcast.caption_text(VTT),
                         "Narrator: Welcome to the show. Now onto the show. Chris: Hello & welcome.")
        srt = "1\n00:00:01,000 --> 00:00:02,000\nHi there\n\n2\n00:00:03,000 --> 00:00:04,000\nBye"
        self.assertEqual(podcast.transcript_text(srt, "application/x-subrip"), "Hi there Bye")
        self.assertEqual(podcast.transcript_text('{"segments": [{"speaker": "A", "body": "hi"}]}',
                                                 "application/json"), "A: hi")

    def test_parse_episodes_needs_audio_and_reads_transcript_sources(self):
        episodes = podcast.parse_episodes(FEED, "Show")
        self.assertEqual([e["link"] for e in episodes], ["https://x/1", "https://x/2"])
        self.assertEqual((episodes[0]["minutes"], episodes[0]["transcript_url"]), ("48", "https://x/1.vtt"))
        self.assertEqual((episodes[1]["minutes"], episodes[1]["transcript_url"]), ("62", ""))
        self.assertIn("word word", episodes[1]["content"])

    def test_fetch_transcript_requires_enough_words(self):
        long_text = "<p>" + "word " * podcast.MIN_WORDS + "</p>"
        self.assertTrue(podcast.fetch_transcript(_episode("https://x/a", content=long_text)))
        self.assertEqual(podcast.fetch_transcript(_episode("https://x/b", content="<p>show notes</p>")), "")
        vtt = _episode("https://x/c", transcript_url="https://x/c.vtt", transcript_type="text/vtt")
        self.assertEqual(podcast.fetch_transcript(vtt, fetch=lambda url: VTT), "")  # too short

    def test_candidates_skip_done_old_and_undated_newest_first(self):
        episodes = [_episode("https://x/a", 3), _episode("https://x/b", 1), _episode("https://x/a", 3),
                    _episode("https://x/old", podcast.LOOKBACK_DAYS + 1), _episode("https://x/done", 1),
                    {**_episode("https://x/undated"), "published": None}]
        result = podcast.candidates(episodes, {item_id("https://x/done")}, NOW)
        self.assertEqual([e["link"] for e in result], ["https://x/b", "https://x/a"])

    def test_run_caps_episodes_and_skips_missing_transcripts(self):
        text = "<p>" + "word " * podcast.MIN_WORDS + "</p>"
        episodes = [_episode("https://x/none", 0), *[_episode(f"https://x/{i}", i + 1, content=text) for i in range(3)]]
        fields = {"title_zh": "中文", "intro_zh": "导读", "points_zh": "一", "why_zh": "谁"}
        with mock.patch.object(podcast, "introduce", return_value=fields) as introduce:
            added = podcast.run([], episodes, "key", ["m"], NOW, log=lambda *_: None)
        self.assertEqual([row["link"] for row in added], ["https://x/0", "https://x/1"])
        self.assertEqual(introduce.call_count, podcast.MAX_PER_RUN)
        self.assertEqual(added[0]["added_et"], "2026-11-09 08:00")

    def test_introduce_drops_empty_points_and_needs_an_intro(self):
        reply = [{"titleZh": "中文", "introZh": "导读", "points": ["一", " ", "二"], "whyZh": "谁"}]
        with mock.patch.object(podcast, "_generate", return_value=reply):
            fields = podcast.introduce(_episode("https://x/a"), "text", "key", ["m"])
        self.assertEqual(fields["points_zh"], "一\n二")
        with mock.patch.object(podcast, "_generate", return_value=[{"introZh": ""}]):
            self.assertIsNone(podcast.introduce(_episode("https://x/a"), "text", "key", ["m"]))

    def test_write_site_pages_index_and_feed(self):
        rows = podcast._sorted([_row("2026-11-04", "https://x/1", "2026-11-05 08:00"),
                                _row("2026-11-05", "https://x/2", "2026-11-06 08:00")])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "index.md").write_text((podcast.ROOT / "podcast" / "index.md").read_text(encoding="utf-8"),
                                          encoding="utf-8")
            podcast.write_site(rows, out)
            page = (out / podcast._page(rows[0])).read_text(encoding="utf-8")
            self.assertIn("- 要点一", page)
            self.assertIn("约 48 分钟", page)
            index = (out / "index.md").read_text(encoding="utf-8")
            self.assertIn(podcast._page(rows[0]), index)
            channel = ET.fromstring((out / "feed.xml").read_text(encoding="utf-8")).find("channel")
            self.assertEqual(len(channel.findall("item")), 2)
            self.assertIn("06 Nov 2026", channel.findtext("lastBuildDate"))
            self.assertIn("导读正文 &lt;b&gt;", channel.find("item").findtext("description"))


if __name__ == "__main__":
    unittest.main()
