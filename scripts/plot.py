import csv
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=list(csv.DictReader(open('results/raw/metrics.csv')));groups=defaultdict(list)
for r in rows:groups[(int(r['scale']),r['index'],int(r['parameter']))].append(r)
summary=[]
for key,rs in groups.items():
    s=dict(scale=key[0],index=key[1],parameter=key[2])
    for metric in ['ann_recall','premise_recall','mrr','p95_ms','qps','index_bytes','build_s','process_peak_rss_bytes']:
        v=[float(r[metric]) if r[metric] else float('nan') for r in rs];s[metric]=float(np.median(v));s[metric+'_min']=min(v);s[metric+'_max']=max(v)
    summary.append(s)
for n in sorted({s['scale'] for s in summary}):
    ss=[s for s in summary if s['scale']==n]
    for s in ss:
        s['pareto3d']=not any(t['ann_recall']>=s['ann_recall'] and t['p95_ms']<=s['p95_ms'] and t['index_bytes']<=s['index_bytes'] and (t['ann_recall']>s['ann_recall'] or t['p95_ms']<s['p95_ms'] or t['index_bytes']<s['index_bytes']) for t in ss)
    fig,ax=plt.subplots(figsize=(9,5))
    for s in ss:
        ax.scatter(s['p95_ms'],s['ann_recall'],s=30+100*s['index_bytes']/max(z['index_bytes'] for z in ss),marker='*' if s['pareto3d'] else 'o',label=f"{s['index']} {s['parameter']} ({s['index_bytes']/1024:.0f} KiB)")
    ax.set(xlabel='P95 search latency (ms); median of repeats',ylabel='ANN recall@10 versus exact',title=f"{'SYNTHETIC SMOKE TEST — ' if rows[0]['demo']=='True' else ''}N={n}\nSize = serialized index bytes; star = 3-objective Pareto")
    ax.legend(fontsize=7);ax.grid(alpha=.2);fig.tight_layout();Path('results/figures').mkdir(exist_ok=True,parents=True);fig.savefig(f'results/figures/pareto_{n}.png',dpi=150);plt.close(fig)
with open('results/raw/summary.csv','w') as f:
    w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
