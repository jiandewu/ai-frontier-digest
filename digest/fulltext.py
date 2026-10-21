"""Readable text of an article page, for the full-text explanation of daily picks."""

from __future__ import annotations

import html
import json
import re

from .http import get
from .sources import USER_AGENT


MAX_CHARS = 8000
MIN_CHARS = 500  # shorter usually means a paywall, a JS-only page or a bot wall
_DROP = re.compile(r"<(script|style|noscript|svg|template|nav|header|footer|aside|form)\b.*?</\1\s*>", re.S | re.I)
_ARTICLE = re.compile(r"<article\b.*?</article\s*>", re.S | re.I)
_MAIN = re.compile(r"<main\b.*?</main\s*>", re.S | re.I)
_BODY = re.compile(r"<body\b.*?</body\s*>", re.S | re.I)
_HF_PAPER = re.compile(r"^https://huggingface\.co/papers/([^/?#]+)")


def extract_text(page: str) -> str:
    """Text of the longest <article> block, else <main>, else <body>; tags stripped."""
    page = _DROP.sub(" ", re.sub(r"<!--.*?-->", " ", page, flags=re.S))
    blocks = _ARTICLE.findall(page) or _MAIN.findall(page) or _BODY.findall(page) or [page]
    text = html.unescape(re.sub(r"<[^>]+>", " ", max(blocks, key=len)))
    return re.sub(r"\s+", " ", text).strip()[:MAX_CHARS]


def fetch_text(url: str) -> str:
    """Article text, or "" when the page cannot be read well enough to explain."""
    headers = {"User-Agent": USER_AGENT}
    paper = _HF_PAPER.match(url)
    try:
        if paper:  # the paper page is mostly embedded JSON; the API has the abstract
            return json.loads(get(f"https://huggingface.co/api/papers/{paper.group(1)}", headers)).get("summary", "")
        text = extract_text(get(url, headers, timeout=20, attempts=2))
    except Exception:
        return ""
    return text if len(text) >= MIN_CHARS else ""
