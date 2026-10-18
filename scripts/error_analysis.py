#!/usr/bin/env python3
"""
Analyze retrieval errors from benchmark results.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict


def analyze_errors(errors_path: Path):
    """Analyze error patterns from metrics errors JSON."""
    with open(errors_path) as f:
        errors = json.load(f)

    # Count errors by namespace
    namespace_errors = Counter()
    error_types = Counter()

    for error in errors:
        namespace = error.get("namespace", "unknown")
        error_type = error.get("error_type", "unknown")
        namespace_errors[namespace] += 1
        error_types[error_type] += 1

    print("Error Types:")
    for error_type, count in error_types.most_common():
        print(f"  {error_type}: {count} ({count/len(errors)*100:.1f}%)")

    print("\nTop Namespaces with Errors:")
    for namespace, count in namespace_errors.most_common(10):
        print(f"  {namespace}: {count}")

    return {
        "error_types": dict(error_types),
        "namespace_errors": dict(namespace_errors),
    }


if __name__ == "__main__":
    errors_path = Path("results/raw/metrics_filtered.errors.json")
    if errors_path.exists():
        results = analyze_errors(errors_path)
        output_path = Path("results/raw/error_analysis.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved analysis to {output_path}")
    else:
        print(f"Error file not found: {errors_path}")
