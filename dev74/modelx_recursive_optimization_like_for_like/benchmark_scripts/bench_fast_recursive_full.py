from __future__ import annotations
import sys,time,json,statistics,importlib.util
from pathlib import Path
import numpy as np
name=sys.argv[1];calls=int(sys.argv[2]) if len(sys.argv)>2 else 1000
d=Path('/mnt/data/lfl_benchmark/artifacts')/name;b=d/'fast_recursive_build';so=next(b.glob('fast_recursive_full*.so'))
spec=importlib.util.spec_from_file_location('fast_recursive_full',so);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
z=np.load(d/'stage_inputs.npz',allow_pickle=False);m.init_inputs({k:z[k] for k in z.files});ref=np.load(d/'reference.npy')
# warm and verify
first=np.asarray(m.run_all(),dtype=float);assert np.allclose(first,ref,rtol=1e-12,atol=1e-12),(first,ref)
times=[]
for _ in range(calls):
 t=time.perf_counter_ns();o=m.run_all();times.append((time.perf_counter_ns()-t)/1e9)
print(json.dumps({'name':name,'variant':'fast_recursive_cython_full_domain','n':len(ref),'calls':calls,'median_portfolio_s':statistics.median(times),'mean_portfolio_s':statistics.mean(times),'p10_s':sorted(times)[int(calls*.1)],'p90_s':sorted(times)[int(calls*.9)],'per_policy_us':statistics.median(times)/len(ref)*1e6,'checksum':float(first.sum()),'values':first.tolist(),'allclose_1e12':True}))
