# Error Analysis

## Overview
This document analyzes retrieval errors from the filtered benchmark results.

## Error Statistics

### Overall
- **Total queries**: 1,196
- **Queries with errors**: 805 (67.3%)
- **Total error entries**: 10,077

### Error Categories
| Category | Count | Percentage |
|----------|-------|------------|
| Unseen namespace | 8,994 | 89.2% |
| Symbol ambiguity | 1,083 | 10.8% |

## Top Error Namespaces

| Namespace | Error Count |
|-----------|-------------|
| Mathlib.Algebra.Order.Field.Basic | 1,245 |
| Mathlib.AlgebraicGeometry.EllipticCurve.Jacobian | 892 |
| Mathlib.Algebra.BigOperators.Group.Finset | 756 |
| Mathlib.AlgebraicGeometry.EllipticCurve.Weierstrass | 698 |
| Mathlib.Algebra.Lie.Nilpotent | 543 |

## Analysis

### Unseen Namespace (89.2%)
The majority of errors are due to queries requiring premises from namespaces that are not well-represented in the training data or the filtered corpus. This suggests:

1. The filtered corpus may not include all necessary namespaces
2. The encoder may not generalize well to unseen mathematical domains
3. Lean's hierarchical namespace structure creates domain-specific vocabulary

### Symbol Ambiguity (10.8%)
Symbol ambiguity errors occur when:
- The same symbol has different meanings in different contexts
- Unicode symbols are not properly normalized
- Type-dependent symbols are not disambiguated

## Limitations

1. **Heuristic classification**: Error categories are based on available metadata, not verified semantic analysis
2. **Namespace bias**: High error rates in algebraic geometry suggest domain-specific challenges
3. **Encoder limitations**: General-purpose text encoder may not capture formal math semantics

## Recommendations

1. **Expand corpus**: Include more diverse namespaces in the filtered subset
2. **Domain-specific encoder**: Use or fine-tune an encoder trained on formal mathematics
3. **Symbol normalization**: Improve preprocessing to handle symbol disambiguation
4. **Context-aware retrieval**: Incorporate namespace hierarchy into retrieval

## Files
- `results/raw/error_analysis.json` - Detailed error analysis
- `results/raw/metrics_filtered.errors.json` - Raw error data
