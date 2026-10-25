import os,json,time,threading
from pathlib import Path
from contextlib import asynccontextmanager
from functools import lru_cache
import numpy as np, faiss
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from .core import Encoder,sha

class Request(BaseModel):
    query: str=Field(min_length=1,max_length=10000)
    k: int=Field(default=10,ge=1,le=100)
    query_id: str=Field(default='',description='Optional query ID for self-match filtering (for benchmark evaluation)')

@asynccontextmanager
async def lifespan(app):
    b=Path(os.getenv('ARTIFACTS','artifacts/demo'));m=json.loads((b/'manifest.json').read_text())
    for name,h in m['files'].items():
        if sha(b/name)!=h:raise RuntimeError('Artifact checksum mismatch')
    app.state.encoder=Encoder(m['encoder']);app.state.meta=json.loads((b/'corpus.json').read_text());app.state.manifest=m
    path=b/os.getenv('INDEX','1200_hnsw.faiss');app.state.index=faiss.read_index(str(path))
    # API requires full ordered pool. Subset benchmark indexes cannot be served accidentally.
    if app.state.index.ntotal!=len(app.state.meta):raise RuntimeError('Use a full-pool index for serving')
    faiss.omp_set_num_threads(int(os.getenv('FAISS_THREADS','1')))
    if hasattr(app.state.index,'hnsw'):app.state.index.hnsw.efSearch=128
    if hasattr(app.state.index,'nprobe'):app.state.index.nprobe=min(16,app.state.index.nlist)
    app.state.lock=threading.Lock()
    app.state.index.search(app.state.encoder.encode(['Nat add zero']),1)
    yield

app=FastAPI(title='Group 4 Lean premise retrieval',lifespan=lifespan)
@app.get('/health')
def health():return dict(status='ok',vectors=app.state.index.ntotal,demo=app.state.manifest['demo'])
@lru_cache(maxsize=512)
def encoded(text):return app.state.encoder.encode([text])
@app.post('/search')
def search(r:Request):
    if not r.query.strip():raise HTTPException(422,'Query must not be whitespace')
    t=time.perf_counter()
    with app.state.lock:
        q=encoded(r.query);scores,ids=app.state.index.search(np.ascontiguousarray(q),min(r.k,app.state.index.ntotal))
    # Filter self-matches if query_id is provided (for benchmark evaluation)
    filtered_results=[]
    for rank,(s,i) in enumerate(zip(scores[0],ids[0]),1):
        if i>=0:
            premise=app.state.meta[int(i)]
            # Filter self-match: corpus trừ chính định lý truy vấn
            if r.query_id and premise['id']==r.query_id:
                continue
            filtered_results.append(dict(rank=rank,**premise,score=float(s)))
    return dict(query=r.query,query_id=r.query_id,elapsed_ms=(time.perf_counter()-t)*1000,demo=app.state.manifest['demo'],results=filtered_results[:r.k])
