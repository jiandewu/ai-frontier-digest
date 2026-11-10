import json
import unittest
from pathlib import Path
from unittest import mock

from digest import numbers

LISTING = """<h3>Showing new listings for Friday, 6 November 2026</h3>
<h3>New submissions (showing 75 of 75 entries)</h3>"""

MARKET_PAGE = """# 美股要闻 2026-11-05

> 模型：x

## 今日主线

主线。

<a id="news-1"></a>

## 1. 科技股创2020年以来最差单日表现

- 来源：[MarketWatch](https://example.com/a) · 11-05 17:48 ET
- 原标题：Tech stocks log worst day since 2020
- 摘要：标普500单日市值蒸发约2.9万亿美元创下历史纪录。
- 为何重要：单日市值损失规模创历史记录。
- 市场影响（利空）：重创科技股。

<a id="news-2"></a>

## 2. 美联储官员称仍有加息可能

- 摘要：步伐将保持渐进。
"""


class NumbersTests(unittest.TestCase):
    def test_grounded(self):
        self.assertTrue(numbers.grounded("2.9万亿美元", "市值蒸发约2.9万亿美元"))
        self.assertTrue(numbers.grounded("189,000 人", "录得189000人"))
        self.assertFalse(numbers.grounded("3万亿美元", "市值蒸发约2.9万亿美元"))
        self.assertFalse(numbers.grounded("创纪录", "创纪录"))

    def test_fred_tile_skips_missing_values(self):
        tile = numbers.fred_tile("SP500", "observation_date,SP500\n2026-11-03,7568.92\n2026-11-04,7688.62\n"
                                          "2026-11-05,.\n")
        self.assertEqual((tile["date"], tile["value"], tile["previous"]), ("2026-11-04", 7688.62, 7568.92))
        self.assertIsNone(numbers.fred_tile("SP500", "observation_date,SP500\n2026-11-05,.\n"))

    def test_yahoo_tile_skips_missing_closes(self):
        chart = {"chart": {"result": [{"meta": {"exchangeTimezoneName": "America/New_York"},
                                        "timestamp": [1794114000, 1794200400, 1794286800],
                                        "indicators": {"quote": [{"close": [4074.9, 4114.5, None]}]}}]}}
        tile = numbers.yahoo_tile("gold", json.dumps(chart))
        self.assertEqual((tile["date"], tile["value"], tile["previous"]), ("2026-11-09", 4114.5, 4074.9))
        chart["chart"]["result"][0]["indicators"]["quote"][0]["close"] = [None, None, None]
        self.assertIsNone(numbers.yahoo_tile("gold", json.dumps(chart)))

    def test_arxiv_listing_and_previous_day(self):
        self.assertEqual(numbers.parse_listing(LISTING), ("2026-11-06", 75))
        self.assertIsNone(numbers.parse_listing("<html>maintenance</html>"))
        listings = {category: ("2026-11-06", 10) for category in numbers.ARXIV_CATEGORIES}
        old = {"id": "arxiv", "date": "2026-11-05", "value": 30, "previous": 20}
        tile = numbers.arxiv_tile(listings, old)
        self.assertEqual((tile["value"], tile["previous"]), (40, 30))
        # Same listing day again: the previous value stays.
        self.assertEqual(numbers.arxiv_tile(listings, tile)["previous"], 30)
        # A missing category or mixed days give no tile.
        self.assertIsNone(numbers.arxiv_tile(dict(list(listings.items())[:3]), old))

    def test_market_items(self):
        items = numbers.market_items(MARKET_PAGE)
        self.assertEqual([item["id"] for item in items], ["market-2026-11-05-1", "market-2026-11-05-2"])
        self.assertIn("2.9万亿美元", items[0]["text"])
        self.assertNotIn("重创科技股", items[0]["text"])
        self.assertTrue(items[0]["link"].endswith("news/2026/2026-11-05.html#news-1"))

    def test_news_numbers_keeps_one_grounded_number_per_section(self):
        items = numbers.market_items(MARKET_PAGE) + [
            {"id": "ai-1", "section": "ai", "title": "新模型", "text": "参数量达到 4000 亿。", "link": "https://a"}]
        reply = [{"id": "market-2026-11-05-1", "number": "3万亿美元", "label": "编造的数"},
                 {"id": "market-2026-11-05-1", "number": "2.9万亿美元", "label": "标普 500 单日蒸发市值"},
                 {"id": "market-2026-11-05-2", "number": "2.9万亿美元", "label": "同板块第二个"},
                 {"id": "ai-1", "number": "4000 亿", "label": "新模型参数量"}]
        with mock.patch.object(numbers, "_generate", return_value=reply):
            news = numbers.news_numbers(items, "key", ["m"], log=lambda *_: None)
        self.assertEqual([(n["section"], n["number"]) for n in news], [("AI", "4000 亿"), ("美股", "2.9万亿美元")])

    def test_build_keeps_old_values_on_failure_and_skips_gemini_when_inputs_unchanged(self):
        old = {"tiles": [{"id": "SP500", "value": 1}], "news": [{"number": "1"}], "newsKey": ""}

        def fetch(url):
            raise OSError("offline")

        with mock.patch.object(numbers, "digest_items", return_value=[]), \
                mock.patch.object(numbers, "news_numbers") as news_numbers:
            new = numbers.build(old, fetch=fetch, api_key="key", log=lambda *_: None)
        news_numbers.assert_not_called()
        self.assertEqual(new["tiles"], [{"id": "SP500", "value": 1}])
        self.assertEqual(new["news"], [{"number": "1"}])
        json.dumps(new)


if __name__ == "__main__":
    unittest.main()
