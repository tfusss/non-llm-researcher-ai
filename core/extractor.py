import json, logging
import requests
import trafilatura
from concurrent.futures import ThreadPoolExecutor
import config

log = logging.getLogger("research")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}

def extract_html(html: str) -> dict:
    raw = trafilatura.extract(html, output_format="json", with_metadata=True,
                              include_comments=False, include_tables=False)
    return json.loads(raw) if raw else {}

def _fetch(item: dict):
    try:
        r = requests.get(item["url"], headers=UA, timeout=config.TIMEOUT)
        r.raise_for_status()
        d = extract_html(r.text)
        text = d.get("text") or ""
        if len(text) < config.MIN_PAGE_CHARS:
            log.debug("Bỏ qua (nội dung quá ngắn): %s", item["url"])
            return None
        return {"url": item["url"], "title": d.get("title") or item["title"],
                "text": text, "date": d.get("date") or "",
                "domain": d.get("hostname") or ""}
    except Exception as e:
        log.warning("Bỏ qua %s: %r", item["url"], e)
        return None

def extract_all(items: list[dict]) -> list[dict]:
    with ThreadPoolExecutor(config.WORKERS) as ex:
        return [d for d in ex.map(_fetch, items) if d]
