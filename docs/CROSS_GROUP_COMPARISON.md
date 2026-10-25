# Cross-Group Comparison (Nhóm 3 ↔ Nhóm 4)

## Điều kiện so sánh liên nhóm

### ✅ Đã thống nhất:
1. **Snapshot chung**: LeanDojo Benchmark 4, mathlib commit 29dcec074de168ac2bf835a77ef68bbe069194c5
2. **Data version**: leandojo-benchmark-4@29dcec07+split-v1.0
3. **Corpus checksum**: c9157bd1381ca4147aa931f14b9985ac9bfe5cbfe892a982a24a133ff4221efd
4. **Queries checksum**: c2b764fafe981755ae7ca2614912498f0559317ea5427bcb7a7150cb45166004
5. **Pool ID**: shared-frozen-pool
6. **Quy tắc eligible premise**: Corpus trừ chính định lý truy vấn (self-match filtering)
7. **k**: 10 (top-10)

### ✅ Đã implement:
1. **Ánh xạ query ID sang theorem ID**: Đã có trong data contract (query.id)
2. **Lọc self-match trước khi cắt top-k**:
   - Exact baseline: ✅ (validate() check q['id'] not in pool)
   - ANN: ✅ (export_results.py filter premise_id == query_id)
   - API: ✅ (/search endpoint filter nếu query_id được cung cấp)
3. **Bộ kiểm tra dữ liệu compatible với tập liên nhóm**:
   - Đã remove check statement duplicate
   - Chỉ check ID không trong corpus (theo rule corpus trừ chính định lý)
4. **Format chuẩn export**: query_id, premise_id, rank, score, run_id

## Kết quả Dense (Nhóm 4)

### Files exported:
- `results/raw/run_dense_flat_0.csv` - Exact baseline
- `results/raw/run_dense_hnsw_16.csv` - HNSW efSearch=16
- `results/raw/run_dense_hnsw_64.csv` - HNSW efSearch=64
- `results/raw/run_dense_hnsw_128.csv` - HNSW efSearch=128
- `results/raw/run_dense_ivf_1.csv` - IVF nprobe=1
- `results/raw/run_dense_ivf_8.csv` - IVF nprobe=8
- `results/raw/run_dense_ivf_32.csv` - IVF nprobe=32

### Format:
```csv
query_id,premise_id,rank,score,run_id
QAddCircle.norm_coe_eq_abs_iff,AddCircle.norm_coe_eq_abs_iff,1,1.000000238418579,flat_0
QAddCircle.norm_coe_eq_abs_iff,AddCircle.norm_eq',2,0.8595499396324158,flat_0
...
```

### Statistics:
- Total rows: 8,980 (898 queries × 10 top-k)
- Self-matches: 0 (đã lọc)
- Corpus size: 180,907 premises
- Queries: 898 test queries

## API Endpoint

### POST /search
Request:
```json
{
  "query": "goal (x y : Nat) : add x y = add x y",
  "k": 10,
  "query_id": "QAddCircle.norm_coe_eq_abs_iff"  // Optional, for self-match filtering
}
```

Response:
```json
{
  "query": "goal (x y : Nat) : add x y = add x y",
  "query_id": "QAddCircle.norm_coe_eq_abs_iff",
  "elapsed_ms": 1.23,
  "demo": false,
  "results": [
    {
      "rank": 1,
      "id": "AddCircle.norm_coe_eq_abs_iff",
      "name": "...",
      "statement": "...",
      "namespace": "...",
      "source_commit": "...",
      "score": 1.0
    },
    ...
  ]
}
```

**Note**: Nếu `query_id` được cung cấp, các kết quả có `id == query_id` sẽ bị lọc (self-match filtering).

## Cần Nhóm 3 Cung Cấp

Để hoàn thành bảng so sánh sparse/dense/hybrid, cần Nhóm 3 cung cấp:

1. **Sparse results**: run_sparse_*.csv với format:
   - query_id, premise_id, rank, score, run_id
   - Same corpus và queries checksum

2. **Hybrid results**: run_hybrid_*.csv với format:
   - query_id, premise_id, rank, score, run_id
   - Same corpus và queries checksum

3. **Metadata**:
   - Sparse/hybrid index configuration
   - Build time, index size, latency metrics

## Bảng So Sánh (Chờ Nhóm 3)

| Method | ANN Recall | Premise Recall@10 | MRR@10 | P95 (ms) | QPS | Index Size (MB) |
|--------|------------|-------------------|--------|----------|-----|-----------------|
| Dense (Flat) | 99.98% | 19.0% | 13.3% | 97.7 | 20.8 | 265 |
| Dense (HNSW-64) | 99.4% | 18.9% | 13.3% | 0.51 | 2,919 | 290 |
| Dense (IVF-8) | 91.0% | 17.2% | 12.5% | 3.24 | 473 | 267 |
| Sparse | TBD | TBD | TBD | TBD | TBD | TBD |
| Hybrid | TBD | TBD | TBD | TBD | TBD | TBD |

## Notes

1. **Quy tắc corpus trừ chính định lý**: Đây là quy ước của benchmark, không mô tả đầy đủ khả năng sử dụng tiền đề theo import và vị trí khai báo trong từng tệp Lean.

2. **Eligibility rule**: Đã áp dụng trong cả exact, ANN và API:
   - Query không thể truy hồi chính nó
   - Pool là toàn bộ corpus trừ query đó
   - Frozen trước mọi run

3. **Tính so sánh**: Chỉ so sánh được khi có sparse/hybrid results từ Nhóm 3 trên cùng snapshot, corpus, queries, nhãn, quy tắc eligible và giá trị k.

## Files
- `scripts/export_results.py` - Export script với format chuẩn
- `src/lean_retrieval/service.py` - API với self-match filtering
- `src/lean_retrieval/core.py` - Validation compatible với cross-group dataset
