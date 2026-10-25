# Shared Benchmark Results (Group 3 ↔ Group 4)

## Overview
Benchmark results on shared dataset with Group 3 (LeanDojo Benchmark 4, commit 29dcec07).

## Dataset
- **Corpus**: 180,907 premises (shared with Group 3)
- **Queries**: 898 test queries (shared with Group 3)
- **Source**: LeanDojo Benchmark 4 v10 (mathlib4 commit: 29dcec074de168ac2bf835a77ef68bbe069194c5)
- **Checksum**: Matches Group 3's checksums.txt
- **Pool ID**: shared-frozen-pool
- **Eligibility**: Self-matches filtered (queries cannot retrieve themselves)

## Encoder
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Revision**: ee8519ce6a28a61c9190da0a16e199d262197a1b
- **Dimension**: 384

## Benchmark Results

### Exact Baseline (Flat)
- **ANN Recall**: 99.98%
- **Premise Recall@10**: 19.0%
- **MRR@10**: 13.3%
- **P95 Latency**: 97.7 ms
- **QPS**: 20.8
- **Index Size**: 265 MB
- **Build Time**: 0.22 s

### HNSW
| efSearch | ANN Recall | Premise Recall@10 | MRR@10 | P95 (ms) | QPS | Index Size (MB) | Build Time (s) |
|----------|------------|-------------------|--------|----------|-----|-----------------|----------------|
| 16 | 98.8% | 18.8% | 13.3% | 0.22 | 7,711 | 290 | 99.2 |
| 64 | 99.4% | 18.9% | 13.3% | 0.51 | 2,919 | 290 | 99.2 |
| 128 | 99.7% | 19.0% | 13.3% | 0.79 | 1,839 | 290 | 99.2 |

### IVFFlat
| nprobe | ANN Recall | Premise Recall@10 | MRR@10 | P95 (ms) | QPS | Index Size (MB) | Build Time (s) |
|--------|------------|-------------------|--------|----------|-----|-----------------|----------------|
| 1 | 61.0% | 13.1% | 9.7% | 0.50 | 3,147 | 267 | 1.69 |
| 8 | 91.0% | 17.2% | 12.5% | 3.24 | 473 | 267 | 1.69 |
| 32 | 98.3% | 18.6% | 13.2% | 10.23 | 134 | 267 | 1.69 |

## Comparison with Filtered Subset (4,692 premises)

| Metric | Filtered (4,692) | Shared (180,907) | Change |
|--------|------------------|------------------|--------|
| Premise Recall@10 (Flat) | 32.8% | 19.0% | -13.8% |
| MRR@10 (Flat) | 43.6% | 13.3% | -30.3% |
| P95 (Flat) | 2.16 ms | 97.7 ms | +95.5 ms |
| QPS (Flat) | 810 | 20.8 | -789.2 |

**Analysis**: The larger corpus significantly reduces retrieval quality (premise recall drops from 32.8% to 19.0%) and increases latency (from 2.16 ms to 97.7 ms). This is expected as the search space increases 38x.

## Exported Files for Group 3
- `results/raw/run_dense_flat_0.csv` - Exact baseline results
- `results/raw/run_dense_hnsw_16.csv` - HNSW efSearch=16
- `results/raw/run_dense_hnsw_64.csv` - HNSW efSearch=64
- `results/raw/run_dense_hnsw_128.csv` - HNSW efSearch=128
- `results/raw/run_dense_ivf_1.csv` - IVF nprobe=1
- `results/raw/run_dense_ivf_8.csv` - IVF nprobe=8
- `results/raw/run_dense_ivf_32.csv` - IVF nprobe=32

Each file contains:
- Columns: query_id, premise_id
- 8,980 rows (898 queries × 10 top-k results)
- No self-matches (queries cannot retrieve themselves)

## Configuration
- Config file: `configs/shared.json`
- Scales: ["full"] (180,907 premises)
- Repeats: 3
- k: 10
- Threads: 1
- Seed: 42
- Warmup: 20

## Notes
1. **Encoder limitation**: all-MiniLM-L6-v2 is a general-purpose text encoder, not fine-tuned for formal mathematics
2. **Self-match filtering**: Applied per Group 3's eligible rule (queries cannot retrieve themselves)
3. **Empty relevant_ids**: Some queries have empty relevant_ids (already filtered by Group 3's self-match removal)
4. **Namespace**: 20,870 premises (11.5%) have empty namespace field in LeanDojo data

## Files
- `results/raw/metrics.csv` - Raw benchmark metrics
- `results/raw/summary.csv` - Summary statistics
- `results/raw/metrics.run.json` - Run metadata
- `results/raw/metrics.errors.json` - Error data
- `artifacts/shared/` - Embeddings and indexes
