import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from lean_retrieval.core import Encoder, read_jsonl, validate, write_json, sha, quarantine, id_order_sha
p=argparse.ArgumentParser(); p.add_argument('--corpus',default='data_sample/corpus.jsonl'); p.add_argument('--queries',default='data_sample/queries.jsonl'); p.add_argument('--out',default='artifacts/demo'); p.add_argument('--model'); p.add_argument('--revision'); p.add_argument('--batch-size',type=int,default=64); a=p.parse_args()
if a.model and not a.revision: p.error('Real model requires immutable --revision commit SHA')
c,q,bad=quarantine(read_jsonl(a.corpus),read_jsonl(a.queries)); validate(c,q)
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
# Bad records are isolated with a reason, not silently dropped and not fatal to the batch.
(out/'quarantine.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in bad),encoding='utf-8')
if bad: print(f'Quarantined {len(bad)} records -> {out/"quarantine.jsonl"}')
spec=dict(backend='sentence-transformers' if a.model else 'hash-smoke',model=a.model or 'sha256-token-hash',revision=a.revision or 'v1',dimension=256,batch_size=a.batch_size,max_seq_length=256,pooling='model-defined; see model_config' if a.model else 'signed token sum',normalize=True)
e=Encoder(spec)
for name, rows in [('corpus',c),('queries',q)]:
    # Batch shards are restartable and bound to both input checksum and encoder configuration.
    fingerprint=hashlib.sha256((sha(getattr(a,name))+json.dumps(spec,sort_keys=True)).encode()).hexdigest()
    shard_dir=out/'checkpoints'/fingerprint; shard_dir.mkdir(parents=True,exist_ok=True)
    shards=[]
    for start in range(0,len(rows),a.batch_size):
        target=shard_dir/f'{start}.npy'
        if not target.exists():
            arr=e.encode([r['statement'] for r in rows[start:start+a.batch_size]])
            tmp=target.with_suffix('.tmp')
            with tmp.open('wb') as f: np.save(f,arr)
            tmp.replace(target)
        shards.append(np.load(target))
    arr=np.concatenate(shards); assert np.isfinite(arr).all() and np.all(np.linalg.norm(arr,axis=1)>0)
    np.save(out/f'{name}.npy',arr)
    write_json(out/f'{name}.json',rows)
if a.model:
    # SentenceTransformer doesn't have get_config_dict, use config from object
    model_config = {
        'model_name': a.model,
        'revision': a.revision,
        'max_seq_length': e.model.max_seq_length if hasattr(e.model, 'max_seq_length') else 256,
        'dimension': e.model.get_sentence_embedding_dimension()
    }
    write_json(out/'model_config.json', model_config)
spec['dimension']=arr.shape[1]
files=['corpus.npy','queries.npy','corpus.json','queries.json','quarantine.jsonl']
try: commit=subprocess.check_output(['git','rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
except Exception: commit='uncommitted-release'
checksums={f:sha(out/f) for f in files}
# Published version = content address of inputs + encoder + outputs; same bytes -> same version.
version=hashlib.sha256(json.dumps([checksums,spec],sort_keys=True).encode()).hexdigest()[:12]
write_json(out/'manifest.json',dict(schema_version='1.1',artifact_version=version,code_commit=commit,id_order_sha256=id_order_sha([r['id'] for r in c]),quarantined=dict(premises=sum(x['kind']=='premise' for x in bad),queries=sum(x['kind']=='query' for x in bad)),demo=not bool(a.model),encoder=spec,dtype='float32',metric='cosine via normalized inner product',source={k:sha(getattr(a,k)) for k in ['corpus','queries']},files=checksums,rows=len(c),queries=len(q),eligibility='one frozen pool; producer must ensure all premises available before all test queries'))
print(out/'manifest.json',version)
