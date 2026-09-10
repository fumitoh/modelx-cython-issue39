from __future__ import annotations
import sys,importlib,time,json,gc,resource
from pathlib import Path
name=sys.argv[1]
roots={
'BasicTerm_S':Path('/mnt/data/lfl_benchmark/mxcy/BasicTerm_S'),
'Term_UK_A':Path('/mnt/data/lfl_benchmark/mxcy/Term_UK_A'),
'WOL_UK_S':Path('/mnt/data/lfl_benchmark/mxcy/WOL_UK_S'),
'VA_US_S':Path('/mnt/data/lfl_benchmark/mxcy/VA_US_S_retry'),
}
root=roots[name];pkg=next(p.name for p in root.iterdir() if p.is_dir() and p.name.endswith('_cy'))
sys.path.insert(0,str(root));mm=importlib.import_module(pkg+'._mx_model');Model=getattr(mm,'_c_'+name)
tprep=time.perf_counter();m=Model()
if name=='BasicTerm_S':
    keys=list(m.Projection.model_point_table.index);cell='pv_net_cf'
else:
    D=m.Data
    # mirror pure-Python benchmark: prepare all zero-arg Data cells outside valuation timer
    cm=importlib.import_module(pkg+'._mx_classes')
    for cn in getattr(cm,'_v_cells_names_Data'):
        try:getattr(D,cn)()
        except Exception:pass
    keys=list(D.model_point_table().index);cell='bench_net_cf'
prep_s=time.perf_counter()-tprep
gc.collect();t=time.perf_counter();vals=[]
for k in keys: vals.append(float(getattr(m.Projection[k],cell)()))
calc_s=time.perf_counter()-t
print(json.dumps({'name':name,'variant':'current_modelx_cython','n':len(keys),'prep_s':prep_s,'calc_s':calc_s,'per_policy_us':calc_s/len(keys)*1e6,'checksum':float(sum(vals)),'values':vals if len(vals)<=20 else None,'values_head':vals[:5],'values_tail':vals[-5:],'rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'package':pkg}))
