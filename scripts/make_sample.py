"""Original synthetic fixtures, no external corpus or proof claims."""
import json
from pathlib import Path
p = Path('data_sample'); p.mkdir(exist_ok=True)
ops = ['add', 'mul', 'sub', 'div', 'pow', 'mod', 'le', 'lt']
corpus = []
for i in range(1200):
    op = ops[i % len(ops)]
    corpus.append(dict(id=f'p{i}', name=f'Demo.{op}_{i}', namespace=f'Demo.{op}',
        statement=f'theorem premise_{i} (a b : Nat) : {op} a b = {op} a b -- property {i}',
        source_commit='synthetic-v1'))
queries = [dict(id=f'q{i}', statement=f'goal (x y : Nat) : {ops[i%8]} x y = {ops[i%8]} x y -- property {i}',
                relevant_ids=[f'p{i}'], split='test', pool_id='shared-frozen-pool') for i in range(80)]
for name, data in [('corpus',corpus), ('queries',queries)]:
    (p/f'{name}.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in data))
