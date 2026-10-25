#!/usr/bin/env python3
"""
Export benchmark results to format required by group 3.
Output: run_dense_*.csv with columns query_id, premise_id
"""

import json
import csv
from pathlib import Path
import numpy as np
import faiss
from lean_retrieval.core import build


def export_retrieval_results(artifacts_path, config_path, output_prefix):
    """Export retrieval results for each index configuration."""
    artifacts = Path(artifacts_path)
    with open(config_path, encoding='utf-8') as f:
        config = json.load(f)

    # Load data
    x = np.load(artifacts / 'corpus.npy', mmap_mode='r')
    q = np.load(artifacts / 'queries.npy')
    meta = json.loads((artifacts / 'corpus.json').read_text(encoding='utf-8'))
    queries = json.loads((artifacts / 'queries.json').read_text(encoding='utf-8'))

    ids = [p['id'] for p in meta]
    n = len(x)
    k = config['k']

    # Get fixed premises (qrels)
    required = {p for z in queries for p in z['relevant_ids']}
    lookup = {p['id']: i for i, p in enumerate(meta)}
    fixed = sorted(lookup[z] for z in required)
    rest = [i for i in range(len(x)) if i not in set(fixed)]
    selected = sorted(fixed + rest[:n - len(fixed)])
    xx = np.ascontiguousarray(x[selected])
    selected_ids = [ids[i] for i in selected]

    # Build exact index for truth
    exact = build(xx, 'flat')
    _, truth = exact.search(q, k)

    # Export for each configuration
    for kind in ['flat', 'hnsw', 'ivf']:
        if kind == 'hnsw':
            params = config['hnsw']['efSearch']
        elif kind == 'ivf':
            params = config['ivf']['nprobe']
        else:
            params = [0]

        for param in params:
            # Build index
            idx = build(xx, kind, config['seed'])
            if kind == 'hnsw':
                idx.hnsw.efSearch = max(k, param)
            elif kind == 'ivf':
                idx.nprobe = min(param, idx.nlist)

            # Search
            _, results = idx.search(q, k)

            # Export to CSV (top-k results per query)
            output_file = Path('results/raw') / f'{output_prefix}_{kind}_{param}.csv'
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['query_id', 'premise_id'])
                for i, row in enumerate(results):
                    query_id = queries[i]['id']
                    for j in row[:k]:  # Top-k
                        if j >= 0:
                            premise_id = selected_ids[j]
                            writer.writerow([query_id, premise_id])

            print(f'Exported {output_file}')


if __name__ == '__main__':
    export_retrieval_results(
        artifacts_path='artifacts/shared',
        config_path='configs/shared.json',
        output_prefix='run_dense'
    )
