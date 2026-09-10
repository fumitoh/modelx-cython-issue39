from __future__ import annotations
import argparse, importlib, json, math, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET={'BasicTerm_S':'pv_net_cf','Term_UK_A':'bench_net_cf','WOL_UK_S':'bench_net_cf','ULSG_US_S':'bench_net_cf','VA_US_S':'bench_net_cf'}
def main():
    sys.setrecursionlimit(20000)
    ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--limit',type=int,default=None);ns=ap.parse_args();model=ns.model;target=TARGET[model]
    sys.path.insert(0,str(ROOT/'generated_exports'/model));sys.path.insert(0,str(ROOT/'fast_recursive_cython_object'))
    mm=importlib.import_module(model+'._mx_model');m=getattr(mm,'_c_'+model)();fr=importlib.import_module('frcy_'+model);rt=fr.FastRecursiveRuntime()
    keys=list(m.Projection.model_point_table.index) if model=='BasicTerm_S' else list(m.Data.model_point_table().index)
    if ns.limit is not None:keys=keys[:ns.limit]
    exp=[]
    for k in keys:
        ctx=m.Projection[k];exp.append(float(getattr(ctx,target)()))
        try:del m.Projection[k]
        except Exception:pass
    t=time.perf_counter();got=[]
    for k in keys:
        ctx=m.Projection[k];got.append(float(fr.evaluate(rt,ctx)))
        try:del m.Projection[k]
        except Exception:pass
    elapsed=time.perf_counter()-t
    ok=all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(exp,got));row={'model':model,'policies':len(keys),'cython_object_s':elapsed,'max_abs_error':max((abs(a-b) for a,b in zip(exp,got)),default=0.0),'allclose_1e12':ok,'checksum':sum(got)};print(json.dumps(row));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
