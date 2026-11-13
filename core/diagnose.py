import config

def _p(ok, msg):
    print(("[OK]  " if ok else "[LỖI] ") + msg)
    return ok

def run_checks() -> bool:
    good = True
    try:
        import requests
        _p(True, "requests")
    except ImportError:
        return _p(False, "thiếu requests -> python -m pip install requests")
    have_traf = True
    try:
        import trafilatura  # noqa
        _p(True, "trafilatura")
    except ImportError:
        have_traf = good = _p(False, "thiếu trafilatura -> python -m pip install trafilatura")

    url = None
    try:
        from core.searcher import _client
        res = _client().text("xe điện", region=config.REGION, max_results=3)
        if res:
            url = res[0].get("href") or res[0].get("url")
            _p(True, f"ddgs: {len(res)} kết quả (vùng {config.REGION})")
        else:
            good = _p(False, "ddgs chạy nhưng 0 kết quả: có thể bị giới hạn tần suất, đợi vài phút rồi thử lại")
    except ImportError:
        good = _p(False, "thiếu ddgs -> python -m pip install ddgs")
    except Exception as e:
        good = _p(False, f"ddgs lỗi: {e!r} (kiểm tra mạng, hoặc bị giới hạn tần suất)")

    if have_traf:
        test_url = url or "https://vnexpress.net"
        try:
            from core.extractor import extract_html
            h = requests.get(test_url, timeout=config.TIMEOUT,
                             headers={"User-Agent": "Mozilla/5.0"}).text
            n = len(extract_html(h).get("text", ""))
            if n >= config.MIN_PAGE_CHARS:
                _p(True, f"tải và trích {test_url}: {n} ký tự")
            else:
                good = _p(False, f"tải được {test_url} nhưng chỉ trích {n} ký tự "
                                 "(trang cần JavaScript hoặc chặn bot)")
        except Exception as e:
            good = _p(False, f"không tải được {test_url}: {e!r}")
    return good
