import logging
import json
import os
import config
from . import query_expander, report
from .preprocess import normalize, split_sentences, tokenize, is_standalone
from .retriever import BM25
from .vectorizer import Tfidf, cosine
from .selector import mmr

log = logging.getLogger("research")

def _fail(msg, queries=(), urls=()):
    return {"ok": False, "report": msg, "queries": list(queries), "urls": list(urls)}

def _process_and_select(queries: list[str], docs: list[dict], num_sentences: int) -> list[tuple]:
    """Hàm nội bộ xử lý phân đoạn, BM25, TF-IDF và MMR trên một tập tài liệu cụ thể."""
    sents, chunks = [], []
    n = getattr(config, 'CHUNK_SENTS', 1)
    
    # 1. Phân đoạn văn bản
    for d, doc in enumerate(docs):
        ss = split_sentences(normalize(doc["text"]))
        sents.append(ss)
        for i in range(0, max(len(ss) - 1, 1), max(n - 1, 1)):
            chunks.append((d, i, min(i + n, len(ss))))
            
    if not chunks:
        return []

    # 2. Truy xuất thô bằng BM25
    ctoks = [tokenize(" ".join(sents[d][i:j])) for d, i, j in chunks]
    bm = BM25(ctoks, config.K1, config.B)
    
    # Tính điểm BM25 cao nhất trên tất cả các truy vấn nhánh hiện tại
    per_q = [bm.score(tokenize(q)) for q in queries]
    cscore = [max(col) for col in zip(*per_q)]          
    
    top_k_chunks = getattr(config, 'TOP_CHUNKS', 50)
    top = sorted(range(len(chunks)), key=lambda i: -cscore[i])[: top_k_chunks]
    mx = max(cscore[i] for i in top) or 1.0

    cand, seen = [], set()
    for i in top:
        d, i0, i1 = chunks[i]
        for k in range(i0, i1):
            s = sents[d][k]
            if (config.MIN_LEN <= len(s) <= config.MAX_LEN and is_standalone(s) and s not in seen):
                seen.add(s)
                cand.append((d, k, s, cscore[i] / mx))
                
    if not cand:
        return []

    # 3. TF-IDF + Cosine chấm độ liên quan
    combined_query = " ".join(queries) # Ghép truy vấn để tạo ngữ cảnh vector rộng
    toks = [tokenize(s, bigrams=True) for _, _, s, _ in cand]
    qtok = tokenize(combined_query, bigrams=True)
    
    tf = Tfidf().fit(toks + [qtok])
    vecs, qv = [tf.vec(t) for t in toks], tf.vec(qtok)
    
    w = config.W_BM25
    rel = [(1 - w) * cosine(v, qv) + w * cand[i][3] for i, v in enumerate(vecs)]
    
    # 4. Chọn lọc câu bằng MMR
    chosen = mmr(rel, vecs, num_sentences, config.LAMBDA)
    return [(cand[i][0], cand[i][1], cand[i][2]) for i in chosen]


def run(question: str, search_fn=None, extract_fn=None) -> dict:
    """search_fn / extract_fn cho phép thay thế khi test không cần mạng."""
    if search_fn is None:
        from .searcher import search as search_fn
    if extract_fn is None:
        from .extractor import extract_all as extract_fn

    # Nạp tham số rẽ nhánh (Dùng getattr để tránh lỗi nếu config.py chưa cập nhật)
    K = config.DEEP_SEARCH_K       # Số vòng lặp Deep Search tối đa
    M = config.BRANCHING_M       # Số câu rẽ nhánh mỗi vòng
    F = config.FINAL_F_SENTS  # Số câu chắt lọc cuối cùng
    DATA_FILE = "betagay.json"

    # Khởi tạo file lưu trữ toàn cục
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

    # 1. Mở rộng truy vấn gốc cho vòng đầu tiên
    initial_queries = query_expander.expand(question, config.N_SUBQUERIES)
    current_queries = initial_queries
    all_urls = []
    
    log.info("[*] BẮT ĐẦU RẼ NHÁNH (K=%d, M=%d, F=%d)", K, M, F)

    for iteration in range(1, K + 1):
        log.info("\n--- VÒNG %d/%d: %d truy vấn nhánh ---", iteration, K, len(current_queries))
        
        # Tìm kiếm và thu thập URL
        items = search_fn(current_queries)
        if items:
            all_urls.extend(items)
            
        # Cào dữ liệu web
        docs = extract_fn(items)
        log.info("[+] Trích được %d trang ở vòng %d", len(docs), iteration)
        
        if docs:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved_docs = json.load(f)
            saved_docs.extend(docs)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(saved_docs, f, ensure_ascii=False, indent=2)

        if iteration == K:
            break  # Vòng cuối cùng, dừng rẽ nhánh để chuẩn bị hội tụ

        if not docs:
            log.warning("Không có tài liệu mới, dừng rẽ nhánh sớm.")
            break

        # Chấm điểm để tìm M nhánh rẽ cho vòng kế tiếp
        log.info("[-] Đang trích xuất %d câu mồi cho vòng sau...", M)
        branch_picked = _process_and_select(current_queries, docs, num_sentences=M)
        
        if branch_picked:
            current_queries = [s for _, _, s in branch_picked]
            log.info("[-] Các nhánh tiếp theo: %s", current_queries)
        else:
            log.warning("Không trích được câu nhánh, dừng rẽ nhánh sớm.")
            break

    log.info("\n[*] ĐÃ HOÀN TẤT %d VÒNG. BẮT ĐẦU CHẮT LỌC %d CÂU TỪ DATA FILE...", K, F)
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_docs = json.load(f)

    if not all_docs:
        return _fail("Không trích được nội dung trang nào qua toàn bộ các vòng lặp.", initial_queries, all_urls)

    # Ép MMR xuất ra chính xác F câu đa dạng nhất dựa trên truy vấn gốc
    final_picked = _process_and_select(initial_queries, all_docs, num_sentences=F)
    
    if not final_picked:
        return _fail("Không có câu nào đạt yêu cầu độ dài sau khi tổng hợp.", initial_queries, all_urls)

    log.info("[✓] Đã chọn %d câu đắt giá nhất từ %d tài liệu nguồn.", len(final_picked), len(all_docs))
    print("PICKED: ", final_picked)
    
    return {
        "ok": True, 
        "report": report.build(question, final_picked, all_docs),
        "queries": initial_queries, 
        "urls": all_urls, 
        "n_docs": len(all_docs)
    }
