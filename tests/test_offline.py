"""Chạy: python tests/test_offline.py  (không cần mạng, ddgs hay Trafilatura)"""
import sys; sys.path.insert(0, ".")
from core import pipeline
from core.preprocess import normalize, split_sentences, is_standalone

T1 = ("Trạm sạc xe điện tại Việt Nam tăng nhanh trong năm 2025. Theo TS. Nguyễn Văn A, "
      "số lượng cổng sạc đã vượt 150.000 cổng trên toàn quốc. Lưới điện chịu áp lực lớn vào giờ cao điểm buổi tối. ") * 4
T2 = ("Xe điện làm tăng phụ tải của lưới điện quốc gia vào giờ cao điểm. Giải pháp sạc thông minh giúp "
      "dịch chuyển nhu cầu sang ban đêm và giảm áp lực lên lưới. Trạm sạc xe điện tại Việt Nam tăng nhanh trong năm 2025. ") * 4
fake_s = lambda qs: [{"url": "http://a.vn/1", "title": "A"}, {"url": "http://b.vn/2", "title": "B"}]
fake_e = lambda it: [{"url": "http://a.vn/1", "title": "A", "text": T1, "date": "2025-05-01", "domain": "a.vn"},
                     {"url": "http://b.vn/2", "title": "B", "text": T2, "date": "", "domain": "b.vn"}]

assert split_sentences(normalize("Theo TS. Lê Văn B, giá là 3.5 triệu. Điều này đúng.")) == \
    ["Theo TS. Lê Văn B, giá là 3.5 triệu.", "Điều này đúng."]
assert not is_standalone("Tuy nhiên, giá vẫn cao.")
res = pipeline.run("tác động của xe điện đến lưới điện Việt Nam", search_fn=fake_s, extract_fn=fake_e)
assert res["ok"] and "## Tài liệu tham khảo" in res["report"]
assert not pipeline.run("x", search_fn=lambda q: [], extract_fn=fake_e)["ok"]
print(res["report"]); print("PASS")
