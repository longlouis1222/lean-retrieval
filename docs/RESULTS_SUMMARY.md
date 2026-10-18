# Results Summary

## Overview
This document summarizes the experimental results for the Lean premise retrieval system using the filtered subset of LeanDojo Benchmark 4.

## Dataset
- **Corpus**: 4,692 premises (filtered from 180,973 total premises)
- **Queries**: 1,196 test queries
- **Source**: LeanDojo Benchmark 4 v10 (mathlib4 commit: 29dcec074de168ac2bf835a77ef68bbe069194c5)

## Encoder
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Revision**: ee8519ce6a28a61c9190da0a16e199d262197a1b
- **Dimension**: 384

## Benchmark Results

### Exact Baseline (Flat)
- **ANN Recall**: 100%
- **Premise Recall@10**: 32.8%
- **MRR@10**: 43.6%
- **P95 Latency**: 2.16 ms
- **QPS**: 810
- **Index Size**: 7.2 MB

### HNSW
| efSearch | ANN Recall | Premise Recall@10 | MRR@10 | P95 (ms) | QPS | Index Size (MB) |
|----------|------------|-------------------|--------|----------|-----|-----------------|
| 16 | 93.8% | 30.9% | 42.0% | 0.33 | 3941 | 7.5 |
| 64 | 98.9% | 32.4% | 43.1% | 1.21 | 1852 | 7.5 |
| 128 | 99.7% | 32.6% | 43.4% | 2.10 | 1045 | 7.5 |

### IVFFlat
| nprobe | ANN Recall | Premise Recall@10 | MRR@10 | P95 (ms) | QPS | Index Size (MB) |
|--------|------------|-------------------|--------|----------|-----|-----------------|
| 1 | 38.8% | 14.5% | 22.0% | 0.12 | 12450 | 7.1 |
| 4 | 66.7% | 22.5% | 33.2% | 0.22 | 8210 | 7.1 |
| 16 | 88.0% | 28.2% | 40.0% | 0.56 | 3219 | 7.1 |

## Load Test Results

| Clients | QPS | P95 (ms) |
|---------|-----|----------|
| 1 | 76 | 13.2 |
| 10 | 45 | 220.5 |
| 50 | 32 | 1560.0 |

## Error Analysis

- **Queries with errors**: 805/1,196 (67.3%)
- **Total error entries**: 10,077

### Error Categories
- **Unseen namespace**: 89.2%
- **Symbol ambiguity**: 10.8%

### Top Error Namespaces
1. Mathlib.Algebra.Order.Field.Basic
2. Mathlib.AlgebraicGeometry.EllipticCurve.Jacobian
3. Mathlib.Algebra.BigOperators.Group.Finset
4. Mathlib.AlgebraicGeometry.EllipticCurve.Weierstrass
5. Mathlib.Algebra.Lie.Nilpotent

## Limitations

1. **Encoder**: all-MiniLM-L6-v2 is a general-purpose text encoder, not fine-tuned for formal mathematics or Lean theorem proving
2. **Scale**: Results are on a filtered subset (4,692 premises), not the full corpus (180,973 premises)
3. **Error rate**: 67.3% of queries have retrieval errors, indicating room for improvement
4. **Preprocessing**: Ablation study showed that Unicode → ASCII preprocessing did not improve retrieval quality

## Files
- `results/raw/metrics_filtered.csv` - Raw metrics
- `results/raw/summary_filtered.csv` - Summary statistics
- `results/figures/pareto_filtered_4692.png` - Pareto plot
