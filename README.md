# Nhóm 4 — Lean Premise Retrieval: Dense / ANN
Bộ mã khởi đầu theo hướng dẫn INT4418, trang 12–14. Câu hỏi: ANN đánh đổi
Recall@10, P95 và chi phí index thế nào khi số premise và tải tăng?

**Trạng thái:** đã hoàn thành pipeline đầy đủ; đã thống nhất snapshot với nhóm 3, đã chạy benchmark trên shared dataset (180,907 premises), đã export kết quả format chuẩn cho so sánh liên nhóm, đã implement self-match filtering trong exact/ANN/API, đã chạy ablation study và error analysis.

## Tám đầu ra
|| Đầu ra | File / thư mục |
||---|---|
|| Embedding pipeline | scripts/embed.py; scripts/spark_embed.py |
|| Vector manifest | artifacts/demo/manifest.json; artifacts/shared/manifest.json |
|| Exact baseline | src/lean_retrieval/core.py: IndexFlatIP |
|| ANN indexes | artifacts/demo/*_hnsw.faiss, *_ivf.faiss; artifacts/shared/*.faiss |
|| Search service | src/lean_retrieval/service.py (với self-match filtering) |
|| Pareto plots | results/figures/pareto_*.png |
|| Evaluation | scripts/evaluate.py, plot.py, load_test.py, export_results.py |
|| README/demo | README.md; docs/DEMO.md |

## Kết quả thực tế

### 1. Filtered Subset (4,692 premises)
- **Dataset**: LeanDojo Benchmark 4 v10 (180,973 premises → 4,692 filtered)
- **Encoder**: all-MiniLM-L6-v2 (revision: ee8519ce6a28a61c9190da0a16e199d262197a1b)
- **Premise Recall@10**: 32.8% (Flat baseline)
- **MRR@10**: 43.6%
- **Error rate**: 67.3% queries có lỗi retrieval
- **Ablation**: Preprocessing Unicode → ASCII không cải thiện recall

Xem chi tiết:
- docs/RESULTS_SUMMARY.md - Kết quả benchmark
- docs/ERROR_ANALYSIS.md - Phân tích lỗi
- docs/ABLATION_PREPROCESSING.md - Ablation study

### 2. Shared Dataset (180,907 premises - Thống nhất với Nhóm 3)
- **Dataset**: LeanDojo Benchmark 4 v10 (mathlib commit 29dcec07)
- **Corpus checksum**: c9157bd1... (khớp với nhóm 3)
- **Queries checksum**: c2b764fa... (khớp với nhóm 3)
- **Pool ID**: shared-frozen-pool
- **Queries**: 898 test queries
- **Encoder**: all-MiniLM-L6-v2 (revision: ee8519ce6a28a61c9190da0a16e199d262197a1b)
- **Premise Recall@10**: 19.0% (Flat baseline)
- **MRR@10**: 13.3%
- **Self-match filtering**: Đã implement trong exact, ANN, và API

| Method | ANN Recall | Premise Recall@10 | MRR@10 | P95 (ms) | QPS | Index Size (MB) |
|--------|------------|-------------------|--------|----------|-----|-----------------|
| Dense (Flat) | 99.98% | 19.0% | 13.3% | 97.7 | 20.8 | 265 |
| Dense (HNSW-64) | 99.4% | 18.9% | 13.3% | 0.51 | 2,919 | 290 |
| Dense (IVF-8) | 91.0% | 17.2% | 12.5% | 3.24 | 473 | 267 |

Xem chi tiết:
- docs/SHARED_RESULTS.md - Kết quả benchmark shared dataset
- docs/CROSS_GROUP_COMPARISON.md - Điều kiện so sánh liên nhóm

### 3. Cross-Group Comparison
- **Format export chuẩn**: query_id, premise_id, rank, score, run_id
- **Files exported**: 7 files run_dense_*.csv (flat, hnsw_16/64/128, ivf_1/8/32)
- **Self-match filtering**: Đã implement trong exact, ANN, và API
- **Validation**: Compatible với tập liên nhóm (remove check statement duplicate)
- **Chờ nhóm 3**: sparse và hybrid results để hoàn thành bảng so sánh

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
curl -X POST http://127.0.0.1:8000/search -H 'Content-Type: application/json' -d '{"query":"goal (x y : Nat) : add x y = add x y -- property 0","k":10,"query_id":"QTheoremName"}'
```
Demo kèm 1.200 vectors, 80 queries; scale 100/400/1200; 63 hàng metric.
Số demo chỉ xác minh đường dữ liệu, KHÔNG thay yêu cầu 10K/100K/full.
requirements.txt là khoảng version để cài; requirements-tested.txt ghi version đã
chạy ở môi trường phát triển, không phải lock đa nền tảng đầy đủ.

## Chạy benchmark với shared dataset
```bash
python -m pip install sentence-transformers
python scripts/embed.py --corpus data/corpus.jsonl --queries data/queries.jsonl --out artifacts/shared --model sentence-transformers/all-MiniLM-L6-v2 --revision ee8519ce6a28a61c9190da0a16e199d262197a1b
python scripts/evaluate.py --artifacts artifacts/shared --config configs/shared.json
python scripts/plot.py
python scripts/export_results.py
ARTIFACTS=artifacts/shared INDEX=180907_hnsw.faiss python -m uvicorn lean_retrieval.service:app
```
Export results format chuẩn cho so sánh liên nhóm (query_id, premise_id, rank, score, run_id).

## Pipeline
Corpus/query JSONL → validate → encode batch/checkpoint → normalized NPY +
manifest → Flat/HNSW/IVF → sweep/evaluate → raw CSV + errors + run metadata →
median/min/max + Pareto → export standard format → FastAPI → load test.
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
kết quả Lean thật đã hoàn thành với shared dataset và format chuẩn.
Tài liệu còn lại: data card, system card, experiments, AI-use, contributions,
cross-group comparison.
Nguồn kỹ thuật: https://faiss.ai/ ; https://www.sbert.net/docs/ ;
https://leandojo.org/leandojo.html ; https://github.com/leanprover-community/mathlib4 .
