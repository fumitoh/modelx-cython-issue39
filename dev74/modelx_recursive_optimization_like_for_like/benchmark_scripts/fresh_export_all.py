from __future__ import annotations
import sys, shutil, time, json
from pathlib import Path
ROOT=Path('/mnt/data/modelx_export_review/modelx_compiler_handoff_2026-09-05_v0.23.0.dev73_bounded_context_accessors')
sys.path[:0]=['/mnt/data/fast_recursive_runtime/localdeps',str(ROOT/'third_party/src/modelx-main'),str(ROOT/'third_party/src/lifelib-main'),str(ROOT/'compiler'),str(ROOT/'compiler/tests')]
import modelx as mx
from probe_v10_products import SPECS
LIB=ROOT/'third_party/src/lifelib-main/lifelib/libraries'
OUT=Path('/mnt/data/lfl_benchmark/export'); OUT.mkdir(parents=True,exist_ok=True)
models=['BasicTerm_S','Term_UK_A','WOL_UK_S','ULSG_US_S','VA_US_S']
for name in models:
    if name=='BasicTerm_S':
        p=LIB/'basiclife/BasicTerm_S'
        fn=None
    else:
        rel,fn=SPECS[name];p=LIB/rel
    env=OUT/(name+'_env');dest=env/name
    if env.exists():shutil.rmtree(env)
    env.mkdir(parents=True)
    for src in p.parent.iterdir():
        if src.is_file() and src.suffix.lower() in {'.csv','.xlsx','.xls','.json','.txt'}: shutil.copy2(src,env/src.name)
    t0=time.perf_counter();m=mx.read_model(p);read_s=time.perf_counter()-t0
    try:
        if fn is not None and 'bench_net_cf' not in m.Projection.cells:m.Projection.new_cells('bench_net_cf',formula=fn)
        keys=list((m.Projection.model_point_table if name=='BasicTerm_S' else m.Data.model_point_table()).index)
        t0=time.perf_counter();m.export(dest);export_s=time.perf_counter()-t0
        row={'name':name,'read_s':read_s,'export_s':export_s,'policy_count':len(keys),'keys':[str(k) for k in keys],'dest':str(dest)}
        (OUT/(name+'_export.json')).write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
    finally:m.close()
