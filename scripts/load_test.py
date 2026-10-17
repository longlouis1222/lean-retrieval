import argparse,asyncio,time,json,csv
import httpx,numpy as np
from lean_retrieval.core import read_jsonl
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8000');p.add_argument('--requests',type=int,default=200);p.add_argument('--timeout',type=float,default=30);a=p.parse_args()
queries=read_jsonl('data_sample/queries.jsonl')
async def run(clients,repeat):
    sem=asyncio.Semaphore(clients);lat=[];errors=[]
    async with httpx.AsyncClient(timeout=a.timeout,trust_env=False) as client:
        (await client.get(a.url+'/health')).raise_for_status()
        async def one(i):
            async with sem:
                t=time.perf_counter()
                try:
                    r=await client.post(a.url+'/search',json={'query':queries[i%len(queries)]['statement'],'k':10});r.raise_for_status();lat.append((time.perf_counter()-t)*1000)
                except Exception as e:errors.append(type(e).__name__)
        start=time.perf_counter();await asyncio.gather(*(one(i) for i in range(a.requests)));elapsed=time.perf_counter()-start
    return dict(clients=clients,repeat=repeat,requests=a.requests,success=len(lat),errors=len(errors),error_types=json.dumps(errors),qps=len(lat)/elapsed,p50_ms=float(np.percentile(lat,50)) if lat else None,p95_ms=float(np.percentile(lat,95)) if lat else None,timeout=a.timeout,cache='mixed warm after first pass')
async def main():
    rows=[]
    for clients in [1,10,50]:
        for repeat in range(3):rows.append(await run(clients,repeat))
    with open('results/raw/load.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
asyncio.run(main())
