"""Small urllib GET helper with retries."""

from __future__ import annotations

import gzip
import time
import urllib.error
import urllib.request


def get(url: str, headers: dict | None = None, timeout: int = 30, attempts: int = 3) -> str:
    headers = {"Accept-Encoding": "gzip", **(headers or {})}
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as response:
                body = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return body.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
        except (urllib.error.URLError, TimeoutError):  # read timeouts are not URLError
            if attempt == attempts - 1:
                raise
        time.sleep((2, 5, 10)[min(attempt, 2)])
    raise RuntimeError("unreachable")
