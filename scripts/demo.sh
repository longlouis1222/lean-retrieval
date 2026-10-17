#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=src
python scripts/make_sample.py
python scripts/embed.py
python scripts/evaluate.py
python scripts/plot.py
python -m pytest -q
