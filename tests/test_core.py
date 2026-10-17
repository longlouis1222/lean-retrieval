import numpy as np
from lean_retrieval.core import build,quality,Encoder,validate

def test_exact_matches_numpy_and_ivf_exhaustive():
    r=np.random.default_rng(42);x=r.normal(size=(200,16)).astype('float32');x/=np.linalg.norm(x,axis=1,keepdims=True);q=x[:4]
    expected=np.argsort(-(q@x.T),axis=1)[:,:10]
    _,actual=build(x,'flat').search(q,10);assert np.array_equal(expected,actual)
    idx=build(x,'ivf');idx.nprobe=idx.nlist;_,actual=idx.search(q,10);assert np.array_equal(expected,actual)

def test_metrics_ignore_missing_ids():
    recall,mrr,ann=quality(np.array([[1,-1]]),[['b']],['a','b'],np.array([[1,0]]))
    assert (recall,mrr,ann)==(1,1,.5)

def test_hash_determinism():
    e=Encoder(dict(backend='hash-smoke',dimension=32));a=e.encode(['Nat.add a 0'])
    assert np.allclose(a,e.encode(['Nat.add a 0'])) and np.isclose(np.linalg.norm(a),1)
