import logging, time
import config

log = logging.getLogger("research")

def _client():
    try:
        from ddgs import DDGS
    except ImportError:                       # tên cũ của thư viện
        from duckduckgo_search import DDGS
    return DDGS()

def _one(q: str) -> list[dict]:
    for attempt in range(config.SEARCH_RETRIES + 1):
        try:
            res = _client().text(q, region=config.REGION,
                                 max_results=config.RESULTS_PER_QUERY)
            log.debug("ddgs '%s' -> %d kết quả", q, len(res))
            return res
        except ImportError:
            raise
        except Exception as e:
            wait = config.SEARCH_DELAY * (2 ** attempt)
            log.warning("ddgs lỗi '%s' (lần %d): %r", q, attempt + 1, e)
            time.sleep(wait)
    return []

def search(queries: list[str]) -> list[dict]:
    seen, out = set(), []
    for i, q in enumerate(queries):
        if i:
            time.sleep(config.SEARCH_DELAY)   # chạy lần lượt, có nghỉ
        for x in _one(q):
            u = (x.get("href") or x.get("url") or "").split("#")[0].rstrip("/")
            if u and u not in seen:
                seen.add(u)
                out.append({"url": u, "title": x.get("title", "")})
    return out
