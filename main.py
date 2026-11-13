"""Chạy: python main.py "câu hỏi"  |  python main.py --check"""
import argparse, logging, re, sys, pathlib, unicodedata
import config
import slm

def slug(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "bao-cao"

def main():
    ap = argparse.ArgumentParser(description="AI Research không dùng LLM")
    ap.add_argument("question", nargs="?", help="câu hỏi hoặc chủ đề")
    ap.add_argument("--check", action="store_true", help="kiểm tra môi trường, ddgs, Trafilatura")
    ap.add_argument("-o", "--out", help="đường dẫn file .md (mặc định outputs/<tên>.md)")
    ap.add_argument("--region", help=f"vùng tìm kiếm (mặc định {config.REGION})")
    ap.add_argument("--urls", type=int, help="số URL mỗi truy vấn")
    ap.add_argument("--sents", type=int, help="số câu tối đa trong báo cáo")
    ap.add_argument("--lam", type=float, help="λ của MMR, 0..1")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()

    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(message)s", stream=sys.stderr)
    if a.region: config.REGION = a.region
    if a.urls: config.RESULTS_PER_QUERY = a.urls
    if a.sents: config.MAX_SENTS = a.sents
    if a.lam is not None: config.LAMBDA = a.lam

    if a.check:
        from core.diagnose import run_checks
        sys.exit(0 if run_checks() else 1)

    q = (a.question or input("Câu hỏi: ")).strip()
    if not q:
        sys.exit("Chưa nhập câu hỏi.")
    from core import pipeline
    try:
        res = pipeline.run(q)
    except ImportError as e:
        sys.exit(f"Thiếu thư viện ({e}). Chạy: python -m pip install -r requirements.txt")
    print(res["report"])
    if res["ok"]:
        out = pathlib.Path(a.out) if a.out else pathlib.Path("outputs") / f"{slug(q)}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(res["report"], encoding="utf-8")
        print(f"\nĐã lưu: {out}", file=sys.stderr)

        slm.summarize_local_file(out.name, summary_length=config.SUMMARY_LENGTH)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
