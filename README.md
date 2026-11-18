# Non-LLM AI Web Research
> Mô hình AI Research tự động tìm kiếm, trích xuất và tổng hợp thông tin trang web không sử dụng LLM.

Hệ thống thu thập dữ liệu thời gian thực từ công cụ tìm kiếm DuckDuckGo và bóc tách nội dung văn bản sạch từ các trang web bằng thư viện Trafilatura.

Thư mục **core** chứa toàn bộ pipeline truy xuất thông tin và tóm tắt trích xuất (Extractive Summarization). File **slm.py** được tích hợp thêm nếu bạn muốn sử dụng mô hình ngôn ngữ nhỏ `qwen2.5:1.5b` qua Ollama để biên tập lại kết quả thành văn bản hoàn chỉnh và tự động ghi vào file **output.txt**.

### Performance
Độ liên quan và chất lượng bản tóm tắt được tính toán bằng trọng số thống kê **TF-IDF** kết hợp với độ đo tương đồng **Cosine Similarity** và thuật toán **Maximal Marginal Relevance (MMR)** để khử trùng lặp đa văn bản. Kiến trúc hệ thống bao gồm 8 giai đoạn xử lý tuần tự từ mở rộng truy vấn (`query_expander.py`), tìm kiếm (`searcher.py`), bóc tách DOM (`extractor.py`), tiền xử lý (`preprocess.py`), vector hóa (`vectorizer.py`), truy xuất (`retriever.py`), chọn câu (`selector.py`) đến kết xuất báo cáo (`report.py`). Toàn bộ quá trình đánh giá và kiểm thử ngoại tuyến được thực hiện thông qua **test_offline.py** và công cụ chẩn đoán **diagnose.py** chạy hoàn toàn trên CPU với 0% ảo giác (Zero Hallucination).

## Requirements
- Python 3.11
- ddgs
- requests
- trafilatura
- Ollama (`qwen2.5:1.5b`)

```
pip install ddgs
pip install requests
pip install trafilatura
ollama pull qwen2.5:1.5b
```

## Installation 
- Clone the repo
- Chạy trực tiếp file **main.py** để thực thi pipeline tổng hợp trang web không dùng LLM.
- Để chạy chế độ tóm tắt thành văn bản qua Ollama (`qwen2.5:1.5b`) và xuất kết quả ra file **output.txt**, mở terminal tại thư mục dự án và chạy:
```
python main.py
python slm.py
```

## References
1. [The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf) </br>
2. [Trafilatura: A Web Scraping Library and Command-Line Tool for Text Discovery and Extraction](https://aclanthology.org/2021.acl-demo.15.pdf)

---


