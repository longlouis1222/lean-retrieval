#!/usr/bin/env python3
"""
Preprocess Lean statements by converting Unicode symbols to ASCII.
"""

import json
import re
from pathlib import Path


# Unicode to ASCII mappings for Lean symbols
SYMBOL_MAP = {
    "→": "->",
    "∀": "forall",
    "∃": "exists",
    "∈": "in",
    "∉": "notin",
    "⊢": "⊢",
    "λ": "fun",
    "≤": "<=",
    "≥": ">=",
    "∧": "/\\",
    "∨": "\\/",
    "¬": "not",
    "≠": "!=",
    "≈": "~",
    "×": "*",
    "∪": "union",
    "∩": "inter",
    "⊆": "subset",
    "⊂": "ssubset",
    "∞": "inf",
    "∂": "partial",
    "∇": "nabla",
    "∫": "integral",
    "∑": "sum",
    "∏": "prod",
}


def preprocess_statement(statement: str) -> str:
    """Preprocess a Lean statement by replacing Unicode symbols."""
    # Remove Lean annotation markers
    statement = re.sub(r'@\[[^\]]+\]', '', statement)

    # Replace Unicode symbols
    for unicode_char, ascii_replacement in SYMBOL_MAP.items():
        statement = statement.replace(unicode_char, ascii_replacement)

    # Normalize whitespace
    statement = re.sub(r'\s+', ' ', statement).strip()

    return statement


def preprocess_jsonl(input_path: Path, output_path: Path):
    """Preprocess a JSONL file."""
    print(f"Preprocessing {input_path}...")
    with open(input_path, encoding="utf-8") as f_in:
        with open(output_path, "w", encoding="utf-8") as f_out:
            for line in f_in:
                record = json.loads(line)
                if "statement" in record:
                    record["statement"] = preprocess_statement(record["statement"])
                f_out.write(json.dumps(record) + "\n")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    base_dir = Path("data")
    preprocess_jsonl(
        base_dir / "corpus_filtered.jsonl",
        base_dir / "corpus_filtered_preprocessed.jsonl",
    )
    preprocess_jsonl(
        base_dir / "queries.jsonl",
        base_dir / "queries_preprocessed.jsonl",
    )
