from __future__ import annotations
import sys,time,json,statistics,importlib.util
from pathlib import Path
import numpy as np
mode=sys.argv[1];reps=int(sys.argv[2]) if len(sys.argv)>2 else 7
# fresh exported data
sys.path.insert(0,'/mnt/data/lfl_benchmark/export/BasicTerm_S_env');import BasicTerm_S
p=BasicTerm_S.mx_model.Projection;df=p.model_point_table
pt=np.ascontiguousarray(df['policy_term'].to_numpy(dtype=np.int64));sa=np.ascontiguousarray(df['sum_assured'].to_numpy(dtype=np.int64));aa=np.ascontiguousarray(df['age_at_entry'].to_numpy(dtype=np.int64))
dr=np.ascontiguousarray(p.disc_rate_ann.to_numpy(dtype=np.float64));mt=np.zeros((121,6),dtype=np.float64)
for age,row in p.mort_table.iterrows(): mt[int(age),:]=row.to_numpy(dtype=np.float64)
mt=np.ascontiguousarray(mt)
base=Path('/mnt/data/lfl_benchmark/artifacts/BasicTerm_S')/(mode)
so=next(base.glob(('fast_recursive' if mode=='r1' else 'sequential')+'*.so'))
modname='fast_recursive' if mode=='r1' else 'sequential';spec=importlib.util.spec_from_file_location(modname,so);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def run():
 if mode=='r1': return np.asarray(m.run(pt,sa,aa,dr,mt),dtype=float)
 return np.asarray(m.run(pt,sa,aa,dr,mt,1),dtype=float).reshape(-1)
first=run();times=[]
for _ in range(reps):
 t=time.perf_counter();o=run();times.append(time.perf_counter()-t)
np.save(base/'fresh_values.npy',first)
ref=np.load('/mnt/data/fast_recursive_runtime/MXCY_R0_VALUES.npy')
res={'name':'BasicTerm_S','variant':'fast_recursive_cython' if mode=='r1' else 'compact_sequential_cython','n':len(first),'reps':reps,'times_s':times,'median_s':statistics.median(times),'per_policy_us':statistics.median(times)/len(first)*1e6,'checksum':float(first.sum()),'allclose_old_mxcy_1e12':bool(np.allclose(first,ref,rtol=1e-12,atol=1e-12)),'max_abs_vs_old_mxcy':float(np.max(np.abs(first-ref)))}
print(json.dumps(res))
