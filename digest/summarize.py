"""Chinese titles, summaries, categories and importance via Gemini."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
CATEGORIES = ("模型发布", "研究", "工程实践", "产品与应用", "行业动态", "政策与安全", "观点与访谈")
BATCH_SIZE = 15

SYSTEM_PROMPT = (
    "你是 AI 科普编辑，读者对 AI 感兴趣、有理工科背景，但不一定是相关细分领域的专家。"
    "为每条英文或中文条目给出：简洁准确、通俗易懂的中文标题 titleZh；"
    "一到两句中文摘要 summaryZh，用通俗语言说明讲了什么、为什么值得关注，必要的专业术语首次出现时用几个字解释；"
    "类别 category；重要度 importance，综合影响面和科普价值打分（5=人人都该知道的重大发布或突破，"
    "4=影响面广、普通读者能看懂并有收获，3=有意思但偏专业或影响有限，2=细分领域的专业内容或一般资讯，"
    "1=与 AI 关系不大、广告或水文）。只有少数条目应得到 4 分以上。"
    "只依据条目给出的标题和摘要，不得编造数字、结论或作者观点；专有名词（模型名、公司名、人名）保留英文原文。"
)


def response_schema(ids: list[str]) -> dict:
    return {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "maxItems": len(ids),
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "enum": ids},
                        "titleZh": {"type": "string"},
                        "summaryZh": {"type": "string"},
                        "category": {"type": "string", "enum": list(CATEGORIES)},
                        "importance": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    "required": ["id", "titleZh", "summaryZh", "category", "importance"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    }


def _post(url: str, payload: dict, api_key: str, attempts: int = 4) -> dict:
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=180) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise RuntimeError(f"Gemini HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:300]}") from None
        except (urllib.error.URLError, TimeoutError):  # read timeouts are not URLError
            if attempt == attempts - 1:
                raise
        time.sleep((5, 15, 30)[min(attempt, 2)])
    raise RuntimeError("unreachable")


def summarize_batch(items: list[dict], api_key: str, model: str) -> dict[str, dict]:
    candidates = [{"id": item["id"], "source": item["source"], "title": item["title"], "snippet": item["snippet"]}
                  for item in items]
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": json.dumps(candidates, ensure_ascii=False)}]}],
        "generationConfig": {
            "maxOutputTokens": 16000,
            "responseMimeType": "application/json",
            "responseJsonSchema": response_schema([item["id"] for item in items]),
        },
    }
    url = GEMINI_ENDPOINT.format(model=model)
    try:
        body = _post(url, payload, api_key)
    except RuntimeError as exc:
        if not str(exc).startswith("Gemini HTTP 400"):
            raise
        # Gemini sometimes rejects the enum-heavy schema; fall back to plain JSON mode.
        # Ids and fields are still validated below.
        del payload["generationConfig"]["responseJsonSchema"]
        payload["contents"][0]["parts"][0]["text"] = (
            "按 JSON 返回 {\"items\": [{\"id\", \"titleZh\", \"summaryZh\", \"category\", \"importance\"}]}，"
            f"category 只能是 {'、'.join(CATEGORIES)}，importance 为 1-5 的整数。\n"
            + payload["contents"][0]["parts"][0]["text"])
        body = _post(url, payload, api_key)
    parts = body.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts if not part.get("thought"))
    if not text:
        raise RuntimeError(f"Gemini returned no text; finishReason={body.get('candidates', [{}])[0].get('finishReason')}")
    known, result = {item["id"] for item in items}, {}
    for entry in json.loads(text).get("items", []):
        importance = entry.get("importance")
        if str(entry.get("id")) not in known:
            continue
        result[str(entry.get("id"))] = {
            "title_zh": str(entry.get("titleZh", "")).strip(),
            "summary_zh": str(entry.get("summaryZh", "")).strip(),
            "category": entry.get("category") if entry.get("category") in CATEGORIES else "行业动态",
            "importance": str(importance) if isinstance(importance, int) and 1 <= importance <= 5 else "2",
        }
    return result


def summarize(items: list[dict], api_key: str, model: str, log=print) -> dict[str, dict]:
    """Summaries keyed by item id; items whose batch failed are left out so a later run retries them."""
    result = {}
    for start in range(0, len(items), BATCH_SIZE):
        batch = items[start:start + BATCH_SIZE]
        try:
            result.update(summarize_batch(batch, api_key, model))
        except Exception as exc:
            log(f"Gemini failed for {len(batch)} item(s): {type(exc).__name__}: {str(exc)[:300]}")
    return result
