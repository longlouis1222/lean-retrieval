# Nhóm 4 - Dense Retrieval Results for Cross-Group Comparison

## Contents
- `run_dense_flat_0.csv` - Exact baseline results
- `run_dense_hnsw_16.csv` - HNSW efSearch=16
- `run_dense_hnsw_64.csv` - HNSW efSearch=64
- `run_dense_hnsw_128.csv` - HNSW efSearch=128
- `run_dense_ivf_1.csv` - IVF nprobe=1
- `run_dense_ivf_8.csv` - IVF nprobe=8
- `run_dense_ivf_32.csv` - IVF nprobe=32

## Format
Each CSV file contains:
- Columns: query_id, premise_id, rank, score, run_id
- 8,980 rows (898 queries × 10 top-k results)
- No self-matches (filtered per eligible rule: corpus trừ chính định lý truy vấn)

## Dataset Information
- **Source**: LeanDojo Benchmark 4 v10
- **Mathlib commit**: 29dcec074de168ac2bf835a77ef68bbe069194c5
- **Data version**: leandojo-benchmark-4@29dcec07+split-v1.0
- **Corpus checksum**: c9157bd1381ca4147aa931f14b9985ac9bfe5cbfe892a982a24a133ff4221efd
- **Queries checksum**: c2b764fafe981755ae7ca2614912498f0559317ea5427bcb7a7150cb45166004
- **Pool ID**: shared-frozen-pool
- **Corpus size**: 180,907 premises
- **Queries**: 898 test queries

## Encoder
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Revision**: ee8519ce6a28a61c9190da0a16e199d262197a1b
- **Dimension**: 384

## Benchmark Configuration
- **k**: 10 (top-10)
- **Seed**: 42
- **Threads**: 1
- **Repeats**: 3
- **Warmup**: 20

## Summary Results
| Method | ANN Recall | Premise Recall@10 | MRR@10 | P95 (ms) | QPS | Index Size (MB) |
|--------|------------|-------------------|--------|----------|-----|-----------------|
| Dense (Flat) | 99.98% | 19.0% | 13.3% | 97.7 | 20.8 | 265 |
| Dense (HNSW-64) | 99.4% | 18.9% | 13.3% | 0.51 | 2,919 | 290 |
| Dense (IVF-8) | 91.0% | 17.2% | 12.5% | 3.24 | 473 | 267 |

## Request to Group 3
Please provide:
1. **Sparse results**: run_sparse_*.csv with format (query_id, premise_id, rank, score, run_id)
2. **Hybrid results**: run_hybrid_*.csv with format (query_id, premise_id, rank, score, run_id)
3. **Metadata**: Index configuration, build time, index size, latency metrics

Format should match our dense results for cross-group comparison.

## Contact
Nhóm 4 - Big Data Course
GitHub: https://github.com/longlouis1222/lean-retrieval
