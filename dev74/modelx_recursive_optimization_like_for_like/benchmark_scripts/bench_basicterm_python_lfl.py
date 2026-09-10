from __future__ import annotations
import sys,time,json,gc,statistics,importlib
from pathlib import Path
MODE=sys.argv[1];REPS=int(sys.argv[2]) if len(sys.argv)>2 else 3
ENV=Path('/mnt/data/lfl_benchmark/export/BasicTerm_S_env');sys.path.insert(0,str(ENV));sys.path.insert(0,'/mnt/data/modelx_export_review')
mod=importlib.import_module('BasicTerm_S');p=mod.mx_model.Projection
keys=list(p.model_point_table.index)
if MODE=='baseline':
    times=[];vals=None
    for r in range(REPS):
        p._mx_itemspaces.clear();gc.collect();t=time.perf_counter();o=[]
        for k in keys:
            o.append(float(p[k].pv_net_cf()));del p[k]
        times.append(time.perf_counter()-t);vals=o
    print(json.dumps({'name':'BasicTerm_S','variant':'baseline','n':len(keys),'times_s':times,'median_s':statistics.median(times),'per_policy_us':statistics.median(times)/len(keys)*1e6,'checksum':float(sum(vals)),'values_head':vals[:5],'values_tail':vals[-5:]}))
elif MODE=='fast':
    from fast_recursive_basicterm_python import FastRecursiveBasicTerm
    df=p.model_point_table
    pts=[int(x) for x in df['policy_term'].tolist()];sas=[int(x) for x in df['sum_assured'].tolist()];aas=[int(x) for x in df['age_at_entry'].tolist()]
    disc=[float(x) for x in p.disc_rate_ann.tolist()]
    mt=[[0.0]*6 for _ in range(121)]
    for age,row in p.mort_table.iterrows():
        for j,col in enumerate(p.mort_table.columns):mt[int(age)][j]=float(row[col])
    times=[];vals=None
    for r in range(REPS):
        rt=FastRecursiveBasicTerm(disc,mt);gc.collect();t=time.perf_counter();o=[]
        for pt,sa,aa in zip(pts,sas,aas):rt.bind(pt,sa,aa);o.append(float(rt.pv_net_cf()))
        times.append(time.perf_counter()-t);vals=o
    print(json.dumps({'name':'BasicTerm_S','variant':'fast_recursive_python','n':len(pts),'times_s':times,'median_s':statistics.median(times),'per_policy_us':statistics.median(times)/len(pts)*1e6,'checksum':float(sum(vals)),'values_head':vals[:5],'values_tail':vals[-5:]}))
else:raise SystemExit(MODE)
