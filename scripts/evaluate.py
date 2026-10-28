import argparse,csv,json,time,platform,subprocess,sys,threading
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,faiss,psutil
from lean_retrieval.core import build,quality,sha,write_json,id_order_sha
p=argparse.ArgumentParser();p.add_argument('--artifacts',default='artifacts/demo');p.add_argument('--config',default='configs/demo.json');p.add_argument('--output',default='results/raw/metrics.csv');a=p.parse_args()
b=Path(a.artifacts); c=json.loads(Path(a.config).read_text(encoding='utf-8'));m=json.loads((b/'manifest.json').read_text(encoding='utf-8'))
for f,h in m['files'].items(): assert sha(b/f)==h, f'Checksum mismatch: {f}'
x=np.load(b/'corpus.npy',mmap_mode='r');q=np.load(b/'queries.npy');meta=json.loads((b/'corpus.json').read_text(encoding='utf-8'));queries=json.loads((b/'queries.json').read_text(encoding='utf-8'))
# Accept both the flat config (demo/full) and the nested one (shared).
c.setdefault('hnsw',{'efSearch':c.get('efSearch',[16,64,128])});c.setdefault('ivf',{'nprobe':c.get('nprobe',[1,4,16])})
faiss.omp_set_num_threads(c['threads']);indexes={};rng=np.random.default_rng(c['seed']); rows=[]; errors=[]
try: commit=subprocess.check_output(['git','rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
except Exception: commit='uncommitted-release'
run=dict(timestamp=datetime.now(timezone.utc).isoformat(),machine=platform.platform(),cpu=platform.processor(),python=sys.version,numpy=np.__version__,faiss=faiss.__version__,seed=c['seed'],config=c,manifest_sha256=sha(b/'manifest.json'),commit=commit,demo=m['demo'],timeout='none; offline benchmark',status='running')
for requested in c['scales']:
    n=len(x) if requested=='full' else int(requested)
    if n>len(x): raise ValueError(f'Requested {n}, only {len(x)} vectors; do not silently relabel scale')
    # Nested deterministic subsets retain every labelled premise, avoiding changing denominator.
    required={p for z in queries for p in z['relevant_ids']}; lookup={p['id']:i for i,p in enumerate(meta)}
    fixed=sorted(lookup[z] for z in required)
    if len(fixed)>n: raise ValueError('Scale too small to retain qrels; provide separate fixed scale benchmark')
    rest=[i for i in range(len(x)) if i not in set(fixed)]; selected=sorted(fixed+rest[:n-len(fixed)])
    xx=np.ascontiguousarray(x[selected]); ids=[meta[i]['id'] for i in selected];k=min(c['k'],n)
    exact=build(xx,'flat');_,truth=exact.search(q,k)
    for kind in ['flat','hnsw','ivf']:
        for repeat in range(c['repeats']):
            peak=[0]; stop=threading.Event()
            def rss():
                try: return psutil.Process().memory_info().rss
                except (psutil.Error, OSError): return 0
            peak[0]=rss()
            def sample():
                while not stop.wait(.005): peak[0]=max(peak[0],rss())
            monitor=threading.Thread(target=sample,daemon=True);monitor.start()
            t=time.perf_counter();idx=build(xx,kind,c['seed']);build_s=time.perf_counter()-t
            path=b/f'{n}_{kind}.faiss';faiss.write_index(idx,str(path))
            indexes[path.name]=dict(sha256=sha(path),kind=kind,ntotal=idx.ntotal,id_order_sha256=id_order_sha(ids),build_seed=c['seed'])
            params=c['hnsw']['efSearch'] if kind=='hnsw' else c['ivf']['nprobe'] if kind=='ivf' else [0]
            for value in params:
                if kind=='hnsw':idx.hnsw.efSearch=max(k,value)
                if kind=='ivf':idx.nprobe=min(value,idx.nlist)
                idx.search(q[:c['warmup']],k)
                lat=[];found=np.empty((len(q),k),dtype='int64'); order=rng.permutation(len(q));start=time.perf_counter()
                for i in order:
                    t=time.perf_counter();_,r=idx.search(q[i:i+1],k);lat.append((time.perf_counter()-t)*1000);found[i]=r[0]
                elapsed=time.perf_counter()-start
                recall,mrr,ann=quality(found,[z['relevant_ids'] for z in queries],ids,truth)
                rows.append(dict(scale=n,index=kind,parameter=value,effective_parameter=(idx.nprobe if kind=='ivf' else idx.hnsw.efSearch if kind=='hnsw' else 0),repeat=repeat,k=k,premise_recall=recall,mrr=mrr,ann_recall=ann,p50_ms=float(np.percentile(lat,50)),p95_ms=float(np.percentile(lat,95)),qps=len(q)/elapsed,build_s=build_s,index_bytes=path.stat().st_size,process_peak_rss_bytes=peak[0] or None,demo=m['demo']))
                for i,r in enumerate(found):
                    if not set(queries[i]['relevant_ids']).intersection(ids[j] for j in r if j>=0):errors.append(dict(scale=n,index=kind,parameter=value,repeat=repeat,query_id=queries[i]['id'],retrieved=[ids[j] for j in r if j>=0],namespace=meta[selected[int(truth[i,0])]]['namespace']))
            stop.set();monitor.join();del idx
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
write_json(b/'index_manifest.json',dict(manifest_sha256=run['manifest_sha256'],artifact_version=m.get('artifact_version'),indexes=indexes))
run['status']='ok';write_json(out.with_suffix('.run.json'),run);write_json(out.with_suffix('.errors.json'),errors)
print(f'{len(rows)} measurements -> {out}')
