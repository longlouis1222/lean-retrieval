# Ablation Study: Preprocessing Lean Statements

## Objective
Evaluate whether preprocessing Lean statements (Unicode → ASCII conversion) improves premise recall.

## Method

### Preprocessing Steps
1. Remove Lean annotation markers (@[to_additive], @[inline], etc.)
2. Replace Unicode math symbols with ASCII equivalents:
   - → →
   - ∀ Forall
   - ∃ Exists
   - ∈ in
   - ∉ notin
   - ⊢ turnstile
   - λ lam
   - ≤ le
   - ≥ ge
   - ∧ and
   - ∨ or
   - ¬ not
3. Remove extra whitespace

### Experimental Setup
- Same encoder: all-MiniLM-L6-v2 (revision: ee8519ce6a28a61c9190da0a16e199d262197a1b)
- Same corpus: 4,692 premises (filtered)
- Same queries: 1,196
- Same config: 21 measurements (Flat, HNSW efSearch=16/64/128, IVF nprobe=1/4/16)

## Results

| Index | Parameter | Premise Recall (Original) | Premise Recall (Preprocessed) | Change |
|-------|-----------|---------------------------|--------------------------------|--------|
| Flat | - | 32.8% | 32.5% | -0.3% |
| HNSW | efSearch=16 | 30.9% | 30.7% | -0.2% |
| HNSW | efSearch=64 | 32.4% | 32.2% | -0.2% |
| HNSW | efSearch=128 | 32.6% | 32.5% | -0.1% |
| IVF | nprobe=1 | 14.5% | 14.2% | -0.3% |
| IVF | nprobe=4 | 22.5% | 23.2% | +0.7% |
| IVF | nprobe=16 | 28.2% | 28.9% | +0.7% |

## Analysis

### Key Findings
1. **No significant improvement**: Preprocessing does not meaningfully improve premise recall
2. **Slight degradation**: Most configurations show a small decrease in recall
3. **Minor gains**: IVF with higher nprobe shows slight improvement (+0.7%)

### Possible Explanations
1. **Unicode symbols carry semantic meaning**: Mathematical symbols like ∀, ∃, ∈ have precise meanings that may be lost in ASCII conversion
2. **Simple preprocessing insufficient**: Basic symbol replacement does not capture the complexity of Lean's type system
3. **Encoder limitation**: all-MiniLM-L6-v2 is trained on general text, not formal mathematics, so preprocessing does not help

## Conclusion
Preprocessing Lean statements (Unicode → ASCII) is not an effective strategy for improving retrieval quality with a general-purpose encoder. The approach fails to capture the semantic nuance of formal mathematical notation.

## Recommendations
1. **Preserve Unicode**: Keep original Unicode symbols in Lean statements
2. **Better encoder**: Use an encoder specifically trained on formal mathematics or code
3. **Advanced preprocessing**: Consider AST-based preprocessing or symbol-aware tokenization
4. **Fine-tuning**: Fine-tune the encoder on Lean data to understand formal math better

## Files
- `scripts/preprocess_lean.py` - Preprocessing script
- `data/corpus_filtered_preprocessed.jsonl` - Preprocessed corpus
- `data/queries_preprocessed.jsonl` - Preprocessed queries
- `artifacts/real_preprocessed/` - Embeddings of preprocessed data
- `results/raw/metrics_preprocessed.csv` - Benchmark results
- `results/raw/summary_preprocessed.csv` - Summary statistics
