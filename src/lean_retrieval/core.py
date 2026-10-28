import hashlib
import json
import re
from pathlib import Path
import numpy as np
import faiss


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(x) for x in f if x.strip()]


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')


class Encoder:
    def __init__(self, spec):
        self.spec = spec
        if spec['backend'] == 'sentence-transformers':
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(spec['model'], revision=spec['revision'], device='cpu')
            self.model.max_seq_length = spec['max_seq_length']

    def encode(self, texts):
        if self.spec['backend'] == 'sentence-transformers':
            return self.model.encode(texts, batch_size=self.spec['batch_size'], normalize_embeddings=True).astype('float32')
        # Offline deterministic smoke encoder, NOT a pretrained dense model.
        a = np.zeros((len(texts), self.spec['dimension']), dtype='float32')
        for i, text in enumerate(texts):
            for token in re.findall(r'\w+|[^\w\s]', text):
                digest = hashlib.sha256(token.encode()).digest()
                a[i, int.from_bytes(digest[:4], 'little') % a.shape[1]] += 1 if digest[4] % 2 else -1
        faiss.normalize_L2(a)
        return a


def id_order_sha(ids):
    # Binds vector row i to premise ID i; any reorder/insert/delete changes the hash.
    return hashlib.sha256('\n'.join(ids).encode('utf-8')).hexdigest()


def quarantine(corpus, queries):
    """Split invalid records out instead of aborting the whole batch."""
    good_c, good_q, bad, seen = [], [], [], set()
    for p in corpus:
        reason = ('missing_id' if not p.get('id') else 'duplicate_id' if p['id'] in seen else
                  'empty_statement' if not str(p.get('statement') or '').strip() else
                  'missing_source_commit' if not p.get('source_commit') else None)
        if reason: bad.append(dict(kind='premise', id=p.get('id'), reason=reason, record=p))
        else: good_c.append(p); seen.add(p['id'])
    qseen = set()
    for q in queries:
        reason = ('missing_id' if not q.get('id') else 'duplicate_id' if q['id'] in qseen else
                  'empty_statement' if not str(q.get('statement') or '').strip() else
                  'wrong_split_or_pool' if q.get('split') != 'test' or q.get('pool_id') != 'shared-frozen-pool' else
                  'self_in_pool' if q['id'] in seen else
                  'gold_outside_pool' if not set(q.get('relevant_ids') or []) <= seen else None)
        if reason: bad.append(dict(kind='query', id=q.get('id'), reason=reason, record=q))
        else: good_q.append(q); qseen.add(q['id'])
    return good_c, good_q, bad


def verify_index(path, ids, index_manifest):
    """Reject an index whose bytes or row->ID order differ from what was benchmarked."""
    entry = index_manifest.get('indexes', {}).get(Path(path).name)
    if entry is None: raise RuntimeError(f'Index not registered in index_manifest: {Path(path).name}')
    if sha(path) != entry['sha256']: raise RuntimeError('Index checksum mismatch')
    if id_order_sha(ids) != entry['id_order_sha256']: raise RuntimeError('Index ID order mismatch')
    return entry


def validate(corpus, queries):
    ids = [x['id'] for x in corpus]
    assert len(ids) == len(set(ids)) and ids, 'Corpus IDs must be unique and nonempty'
    qids = [q['id'] for q in queries]
    assert len(qids) == len(set(qids)) and qids, 'Query IDs must be unique and nonempty'
    pool = set(ids)
    for p in corpus:
        if not p.get('statement') or not p['statement'].strip():
            print(f'Warning: Empty statement for premise {p.get("id", "unknown")}')
        assert p['source_commit']
        # Namespace may be empty for some premises in LeanDojo
    for q in queries:
        assert q['split'] == 'test' and q['statement'].strip()
        # relevant_ids may be empty for filtered queries (self-match removed)
        if q['relevant_ids']:
            assert set(q['relevant_ids']) <= pool
        assert q['id'] not in pool, 'Self retrieval / theorem leakage'
        # Query statement may appear in corpus, but self-match will be filtered during retrieval
        # This implementation requires ONE frozen, already eligibility-filtered pool.
        assert q['pool_id'] == 'shared-frozen-pool'


def build(x, kind, seed=42):
    d = x.shape[1]
    if kind == 'flat':
        idx = faiss.IndexFlatIP(d)
    elif kind == 'hnsw':
        idx = faiss.IndexHNSWFlat(d, 16, faiss.METRIC_INNER_PRODUCT)
        idx.hnsw.efConstruction = 100
    elif kind == 'ivf':
        nlist = max(1, min(128, len(x) // 40))
        idx = faiss.IndexIVFFlat(faiss.IndexFlatIP(d), d, nlist, faiss.METRIC_INNER_PRODUCT)
        idx.cp.seed = seed
        idx.train(np.ascontiguousarray(x))
    else:
        raise ValueError(kind)
    idx.add(np.ascontiguousarray(x))
    return idx


def quality(rows, relevant, ids, exact):
    recalls, rr, ann = [], [], []
    for i, row in enumerate(rows):
        found = [ids[j] for j in row if j >= 0]
        gold = set(relevant[i])
        if gold:
            recalls.append(len(gold.intersection(found)) / len(gold))
            rr.append(next((1 / rank for rank, p in enumerate(found, 1) if p in gold), 0))
        else:
            # Query with no relevant_ids (filtered by self-match removal)
            recalls.append(0.0)
            rr.append(0.0)
        target = set(int(j) for j in exact[i] if j >= 0)
        if target:
            ann.append(len(target.intersection(int(j) for j in row if j >= 0)) / len(target))
        else:
            ann.append(0.0)
    return float(np.mean(recalls)), float(np.mean(rr)), float(np.mean(ann))
