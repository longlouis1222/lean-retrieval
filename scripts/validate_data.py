#!/usr/bin/env python3
"""
Validate corpus and queries against the data contract.
"""

import json
import hashlib
from pathlib import Path
from lean_retrieval.core import validate


def compute_checksum(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_corpus(corpus_path: Path):
    """Validate corpus JSONL."""
    print(f"Validating corpus: {corpus_path}")
    records = []
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    print(f"  Total records: {len(records)}")

    # Check uniqueness
    ids = [r["id"] for r in records]
    unique_ids = set(ids)
    print(f"  Unique IDs: {len(unique_ids)}")
    if len(ids) != len(unique_ids):
        print("  [ERROR] Duplicate IDs found!")
        return False

    # Check required fields
    required_fields = ["id", "name", "statement", "namespace", "source_commit"]
    for field in required_fields:
        missing = sum(1 for r in records if field not in r)
        if missing > 0:
            print(f"  [ERROR] {missing} records missing field: {field}")
            return False

    print("  [OK] Corpus validation passed")
    return True


def validate_queries(queries_path: Path):
    """Validate queries JSONL."""
    print(f"Validating queries: {queries_path}")
    records = []
    with open(queries_path, encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    print(f"  Total records: {len(records)}")

    # Check uniqueness
    ids = [r["id"] for r in records]
    unique_ids = set(ids)
    print(f"  Unique IDs: {len(unique_ids)}")
    if len(ids) != len(unique_ids):
        print("  [ERROR] Duplicate IDs found!")
        return False

    # Check required fields
    required_fields = ["id", "statement", "relevant_ids", "split", "pool_id"]
    for field in required_fields:
        missing = sum(1 for r in records if field not in r)
        if missing > 0:
            print(f"  [ERROR] {missing} records missing field: {field}")
            return False

    print("  [OK] Queries validation passed")
    return True


if __name__ == "__main__":
    base_dir = Path("data")
    corpus_valid = validate_corpus(base_dir / "corpus.jsonl")
    queries_valid = validate_queries(base_dir / "queries.jsonl")

    if corpus_valid and queries_valid:
        print("\n[OK] All validation passed!")
    else:
        print("\n[ERROR] Validation failed!")
