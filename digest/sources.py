"""Fetch items from blogs, lab news, Hacker News and Hugging Face Daily Papers."""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from .http import get


USER_AGENT = "Mozilla/5.0 (compatible; ai-frontier-digest; +https://github.com/jiandewu/ai-frontier-digest)"

# name -> (feed URL, group)
FEEDS = {
    "Simon Willison": ("https://simonwillison.net/atom/entries/", "个人博客"),
    "Andrej Karpathy": ("https://karpathy.bearblog.dev/feed/", "个人博客"),
    "Andrej Karpathy (blog)": ("https://karpathy.github.io/feed.xml", "个人博客"),
    "Lilian Weng": ("https://lilianweng.github.io/index.xml", "个人博客"),
    "Ahead of AI": ("https://magazine.sebastianraschka.com/feed", "个人博客"),
    "Interconnects": ("https://www.interconnects.ai/feed", "个人博客"),
    "Chip Huyen": ("https://huyenchip.com/feed.xml", "个人博客"),
    "Eugene Yan": ("https://eugeneyan.com/rss/", "个人博客"),
    "Hamel Husain": ("https://hamel.dev/index.xml", "个人博客"),
    "One Useful Thing": ("https://www.oneusefulthing.org/feed", "个人博客"),
    # *.substack.com feeds return 403 to GitHub-hosted runners; use custom domains.
    "Import AI": ("https://jack-clark.net/feed/", "个人博客"),
    "Dwarkesh Podcast": ("https://www.dwarkesh.com/feed", "个人博客"),
    "AINews": ("https://news.smol.ai/rss.xml", "新闻汇总"),
    "Latent Space": ("https://www.latent.space/feed", "新闻汇总"),
    "量子位": ("https://www.qbitai.com/feed", "新闻汇总"),
    "宝玉": ("https://baoyu.io/feed.xml", "新闻汇总"),
    "OpenAI": ("https://openai.com/news/rss.xml", "实验室"),
    "Google DeepMind": ("https://deepmind.google/blog/rss.xml", "实验室"),
    "Google Research": ("https://research.google/blog/rss/", "实验室"),
    "Hugging Face": ("https://huggingface.co/blog/feed.xml", "实验室"),
}
MAX_PER_FEED = 10
HN_URL = "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=100"
HN_MIN_POINTS = 200
HN_PATTERN = re.compile(
    r"\b(AI|AGI|LLMs?|GPT[-\w.]*|ChatGPT|Claude|Gemini|Gemma|OpenAI|Anthropic|DeepMind|DeepSeek|Qwen|Llama|"
    r"Mistral|Grok|Copilot|transformers?|neural|diffusion|machine learning|deep learning|RAG|agentic|"
    r"AI agents?|inference|fine-?tuning|embeddings?|tokens?|reasoning models?)\b", re.IGNORECASE)
HF_PAPERS_URL = "https://huggingface.co/api/daily_papers?date={date}&limit=100"
HF_MIN_UPVOTES = 30
ATOM = "{http://www.w3.org/2005/Atom}"


def _plain(text: str, limit: int) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _date(value: str):
    value = (value or "").strip()
    if not value:
        return None
    try:
        moment = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def parse_feed(text: str, source: str, group: str) -> list[dict]:
    """Parse RSS 2.0 or Atom into item dicts."""
    root = ET.fromstring(text)
    items = []
    channel = root.find("channel")
    if channel is not None:
        for node in channel.findall("item"):
            items.append({"title": node.findtext("title", ""), "link": (node.findtext("link") or "").strip(),
                          "published": _date(node.findtext("pubDate", "")),
                          "snippet": node.findtext("description", "")})
    else:
        for node in root.findall(f"{ATOM}entry"):
            link = next((el.get("href", "") for el in node.findall(f"{ATOM}link")
                         if el.get("rel", "alternate") == "alternate"), "")
            items.append({"title": node.findtext(f"{ATOM}title", ""), "link": link.strip(),
                          "published": _date(node.findtext(f"{ATOM}published") or node.findtext(f"{ATOM}updated", "")),
                          "snippet": node.findtext(f"{ATOM}summary") or node.findtext(f"{ATOM}content", "")})
    result = []
    for item in items:
        title = _plain(item["title"], 300)
        if title and item["link"]:
            result.append({**item, "title": title, "snippet": _plain(item["snippet"], 500),
                           "source": source, "group": group, "score": ""})
    return result


def parse_hn(text: str) -> list[dict]:
    items = []
    for hit in json.loads(text).get("hits", []):
        title = hit.get("title") or ""
        if (hit.get("points") or 0) < HN_MIN_POINTS or not HN_PATTERN.search(title):
            continue
        discussion = f"https://news.ycombinator.com/item?id={hit['objectID']}"
        items.append({"title": title, "link": hit.get("url") or discussion, "published": _date(hit.get("created_at", "")),
                      "snippet": f"HN {hit.get('points')} points, {hit.get('num_comments') or 0} comments: {discussion}",
                      "source": "Hacker News", "group": "社区", "score": str(hit.get("points"))})
    return items


def parse_hf_papers(text: str) -> list[dict]:
    items = []
    for entry in json.loads(text):
        paper = entry.get("paper", {})
        upvotes = paper.get("upvotes") or 0
        if upvotes < HF_MIN_UPVOTES:
            continue
        items.append({"title": _plain(paper.get("title", ""), 300), "link": f"https://huggingface.co/papers/{paper['id']}",
                      "published": _date(paper.get("submittedOnDailyAt") or paper.get("publishedAt", "")),
                      "snippet": _plain(paper.get("ai_summary") or paper.get("summary", ""), 500),
                      "source": "HF Daily Papers", "group": "论文", "score": str(upvotes)})
    return items


def collect(now: datetime, log=print) -> list[dict]:
    headers = {"User-Agent": USER_AGENT}
    items = []
    for name, (url, group) in FEEDS.items():
        try:
            fetched = parse_feed(get(url, headers), name.split(" (")[0], group)
        except Exception as exc:  # one broken feed must not stop the run
            log(f"Feed failed: {name}: {type(exc).__name__}: {str(exc)[:200]}")
            continue
        fetched.sort(key=lambda item: item["published"] or now, reverse=True)
        items += fetched[:MAX_PER_FEED]
    try:
        items += parse_hn(get(HN_URL, headers))
    except Exception as exc:
        log(f"Hacker News failed: {type(exc).__name__}: {str(exc)[:200]}")
    for days in (0, 1, 2):  # papers keep collecting upvotes for a couple of days
        date = (now - timedelta(days=days)).date().isoformat()
        try:
            items += parse_hf_papers(get(HF_PAPERS_URL.format(date=date), headers))
        except Exception as exc:
            log(f"HF papers failed for {date}: {type(exc).__name__}: {str(exc)[:200]}")
    return items
