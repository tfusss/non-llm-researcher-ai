REGION = "vn-vi"          # vùng/ngôn ngữ tìm kiếm của DuckDuckGo
SEARCH_DELAY = 1.0        # giây nghỉ giữa các truy vấn (tránh bị giới hạn tần suất)
SEARCH_RETRIES = 2        # số lần thử lại khi lỗi
N_SUBQUERIES = 4          # số truy vấn phụ (ngoài câu hỏi gốc)
RESULTS_PER_QUERY = 5     # số URL mỗi truy vấn
TIMEOUT = 10              # giây cho mỗi request
WORKERS = 8               # số luồng song song
MIN_PAGE_CHARS = 300      # trang ngắn hơn bị bỏ
CHUNK_SENTS = 4           # số câu mỗi đoạn (chồng 1 câu)
TOP_CHUNKS = 15           # số đoạn giữ lại sau BM25
K1, B = 1.5, 0.75         # tham số BM25
LAMBDA = 0.7              # MMR: 1 = ưu tiên liên quan, 0 = ưu tiên đa dạng
W_BM25 = 0.5              # trọng số điểm BM25 của đoạn trong độ liên quan (phần còn lại là cosine)
MAX_SENTS = 12            # số câu tối đa trong báo cáo
MIN_LEN, MAX_LEN = 40, 400  # độ dài câu hợp lệ (ký tự)
# Ví dụ cấu hình thêm
DEEP_SEARCH_K = 3   # Số vòng lặp tối đa
BRANCHING_M = 2     # Số câu MMR mồi (từ vòng trước) làm truy vấn cho vòng sau
FINAL_F_SENTS = 15  # Số lượng câu đắt giá nhất xuất ra ở bước cuối
SUMMARY_LENGTH = 200     # Số từ mong muốn trong đoạn tóm tắt