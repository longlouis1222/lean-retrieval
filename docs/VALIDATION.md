# Validation thực chạy
- Python 3.12, CPU Linux; version trực tiếp trong requirements-tested.txt.
- Embedding offline tổng hợp: 1.200 premise, 80 query; checksum manifest sinh thật.
- Flat/HNSW/IVF: 3 scale (100/400/1200), 3 repeats, tổng 63 hàng CSV.
- Plot script sinh 3 PNG và summary median/min/max, Pareto 3 mục tiêu.
- pytest: 3 passed (exact vs NumPy, IVF exhaustive, sentinel metrics, hash stability).
- HTTP /health trả ok với 1.200 vectors, demo=true; /search trả 10 kết quả.
- HTTP load: 1/10/50 clients x 3 repeats x 60 requests = 540 requests; xem load.csv.
- RAM process không khả dụng trong môi trường này, ghi null; không suy diễn từ index bytes.
- Chưa chạy: SentenceTransformer thật, Spark cluster, Docker build, dữ liệu LeanDojo,
  10K/100K/full, benchmark chung nhóm 3, encoder ablation và Lean proof evaluation.

Những kết quả này chỉ xác minh demo. Không được dùng làm kết luận chất lượng
hoặc scalability của hệ thống trên toán học hình thức thực tế.
