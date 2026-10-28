import json,subprocess,sys
from pathlib import Path
import numpy as np,faiss,pytest
from lean_retrieval.core import build,id_order_sha,quarantine,verify_index,sha

ROOT=Path(__file__).resolve().parents[1]

def fixture(d,n=300,bad=False):
    corpus=[dict(id=f'p{i}',name=f'P.{i}',namespace='P',statement=f'theorem t{i} (a : Nat) : a + {i} = {i} + a',source_commit='test') for i in range(n)]
    queries=[dict(id=f'q{i}',statement=f'goal {i}',relevant_ids=[f'p{i}'],split='test',pool_id='shared-frozen-pool') for i in range(20)]
    if bad:
        corpus+= [dict(id='p0',statement='dup',source_commit='test'),dict(id='e1',statement='  ',source_commit='test'),dict(id='e2',statement='x')]
        queries+=[dict(id='qx',statement='goal',relevant_ids=['e1'],split='test',pool_id='shared-frozen-pool'),dict(id='qy',statement='',relevant_ids=['p1'],split='test',pool_id='shared-frozen-pool')]
    for name,rows in [('corpus',corpus),('queries',queries)]:(d/f'{name}.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))

def embed(d,out):
    r=subprocess.run([sys.executable,'scripts/embed.py','--corpus',str(d/'corpus.jsonl'),'--queries',str(d/'queries.jsonl'),'--out',str(out),'--batch-size','64'],cwd=ROOT,capture_output=True,text=True,env={'PYTHONPATH':str(ROOT/'src')})
    assert r.returncode==0,r.stderr
    return json.loads((out/'manifest.json').read_text())

def test_resume_after_interrupted_encoding_is_byte_identical(tmp_path):
    fixture(tmp_path);ref=embed(tmp_path,tmp_path/'a')
    out=tmp_path/'b';embed(tmp_path,out)
    shards=sorted((out/'checkpoints').rglob('*.npy'));assert len(shards)==6  # 5 corpus + 1 query batch
    for s in shards[::2]:s.unlink()                          # simulate a crash midway
    shards[1].with_suffix('.tmp').write_bytes(b'partial')    # torn write left behind
    (out/'corpus.npy').unlink()
    got=embed(tmp_path,out)
    assert got['files']==ref['files'] and got['artifact_version']==ref['artifact_version']

def test_bad_records_are_quarantined_not_fatal(tmp_path):
    fixture(tmp_path,bad=True);m=embed(tmp_path,tmp_path/'o')
    bad={(x['kind'],x['id'],x['reason']) for x in map(json.loads,(tmp_path/'o'/'quarantine.jsonl').read_text().splitlines())}
    assert bad=={('premise','p0','duplicate_id'),('premise','e1','empty_statement'),('premise','e2','missing_source_commit'),('query','qx','gold_outside_pool'),('query','qy','empty_statement')}
    assert m['rows']==300 and m['queries']==20 and m['quarantined']=={'premises':3,'queries':2}

def test_version_changes_with_content(tmp_path):
    fixture(tmp_path);a=embed(tmp_path,tmp_path/'a')['artifact_version']
    fixture(tmp_path,n=301);assert embed(tmp_path,tmp_path/'b')['artifact_version']!=a

def test_index_checksum_and_id_order_are_enforced(tmp_path):
    r=np.random.default_rng(0);x=r.normal(size=(50,8)).astype('float32');faiss.normalize_L2(x)
    ids=[f'p{i}' for i in range(50)];path=tmp_path/'50_flat.faiss';faiss.write_index(build(x,'flat'),str(path))
    im=dict(indexes={path.name:dict(sha256=sha(path),id_order_sha256=id_order_sha(ids))})
    verify_index(path,ids,im)
    with pytest.raises(RuntimeError,match='ID order'):verify_index(path,ids[::-1],im)   # same count, wrong order
    raw=bytearray(path.read_bytes());raw[-1]^=1;path.write_bytes(bytes(raw))
    with pytest.raises(RuntimeError,match='checksum'):verify_index(path,ids,im)
