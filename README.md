# Nhóm 4 — Lean Premise Retrieval: Dense / ANN
Bộ mã khởi đầu theo hướng dẫn INT4418, trang 12–14. Câu hỏi: ANN đánh đổi
Recall@10, P95 và chi phí index thế nào khi số premise và tải tăng?

**Trạng thái:** demo tổng hợp chạy được; chưa có split LeanDojo chung nhóm 3,
chưa tải pretrained encoder, chưa có kết quả thực nghiệm Lean thật.

## Tám đầu ra
| Đầu ra | File / thư mục |
|---|---|
| Embedding pipeline | scripts/embed.py; scripts/spark_embed.py |
| Vector manifest | artifacts/demo/manifest.json |
| Exact baseline | src/lean_retrieval/core.py: IndexFlatIP |
| ANN indexes | artifacts/demo/*_hnsw.faiss, *_ivf.faiss |
| Search service | src/lean_retrieval/service.py |
| Pareto plots | results/figures/pareto_*.png |
| Evaluation | scripts/evaluate.py, plot.py, load_test.py |
| README/demo | README.md; docs/DEMO.md |

## Chạy trên Mac / Linux (khuyến nghị Python 3.11 hoặc 3.12)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install --no-deps -e .
bash scripts/demo.sh
python -m uvicorn lean_retrieval.service:app --host 127.0.0.1 --port 8000
```
Mở http://127.0.0.1:8000/docs. Terminal thứ hai:
```bash
source .venv/bin/activate
python scripts/load_test.py
curl -X POST http://127.0.0.1:8000/search -H 'Content-Type: application/json' -d '{"query":"goal (x y : Nat) : add x y = add x y -- property 0","k":10}'
```
Demo kèm 1.200 vectors, 80 queries; scale 100/400/1200; 63 hàng metric.
Số demo chỉ xác minh đường dữ liệu, KHÔNG thay yêu cầu 10K/100K/full.
requirements.txt là khoảng version để cài; requirements-tested.txt ghi version đã
chạy ở môi trường phát triển, không phải lock đa nền tảng đầy đủ.

## Chạy benchmark thật
Chuẩn bị corpus.jsonl/queries.jsonl theo docs/DATA_CONTRACT.md, ghi nguồn/license.
Không có adapter tự động đoán schema LeanDojo trong bản này.
```bash
python -m pip install sentence-transformers
python scripts/embed.py --corpus data/corpus.jsonl --queries data/queries.jsonl --out artifacts/real --model sentence-transformers/all-MiniLM-L6-v2 --revision MODEL_COMMIT_SHA
python scripts/evaluate.py --artifacts artifacts/real --config configs/full.json
python scripts/plot.py
ARTIFACTS=artifacts/real INDEX=FULL_N_hnsw.faiss python -m uvicorn lean_retrieval.service:app
```
Thay MODEL_COMMIT_SHA bằng SHA thật (không dùng main); model trên là ví dụ để
thử, chưa được chứng minh phù hợp Lean. Thay FULL_N bằng số corpus thật.
Chỉ serve index full vì metadata theo toàn bộ corpus. Khi thay artifacts phải
restart service để cache không giữ encoder cũ. /health công bố demo flag.

## Pipeline
Corpus/query JSONL → validate → encode batch/checkpoint → normalized NPY +
manifest → Flat/HNSW/IVF → sweep/evaluate → raw CSV + errors + run metadata →
median/min/max + Pareto → FastAPI → load test.
Spark mở rộng batch output Parquet; xem limitations trước khi tích hợp.

## Đọc kết quả
premise_recall: dependency retrieval; mrr: reciprocal rank đầu tiên trong top-k;
ann_recall: overlap với exact trên cùng vector. P95 chỉ search, không encode.
QPS load HTTP nằm riêng load.csv. Build time gồm train+add; index bytes từ file.
process_peak_rss_bytes=null nếu môi trường không cho đọc process memory.
Thay configs và artifacts tạo thí nghiệm mới; lưu mỗi run ra tên CSV khác và
chỉnh đường đọc plot.py tương ứng để không ghi đè kết quả cần giữ.

## Kiểm chứng & bàn giao
`python -m pytest -q`: exact vs NumPy, IVF exhaustive, metrics/sentinel, encoder.
Xem docs/VALIDATION.md cho kết quả thực chạy. Báo cáo 8–12 trang, slides và
kết quả Lean thật cần hoàn thành sau khi nhóm chốt dữ liệu/encoder.
Tài liệu còn lại: data card, system card, experiments, AI-use và contributions.
Nguồn kỹ thuật: https://faiss.ai/ ; https://www.sbert.net/docs/ ;
https://leandojo.org/leandojo.html ; https://github.com/leanprover-community/mathlib4 .
