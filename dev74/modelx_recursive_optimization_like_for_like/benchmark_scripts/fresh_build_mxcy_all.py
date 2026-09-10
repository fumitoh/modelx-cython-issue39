from __future__ import annotations
import sys, os, json, time, traceback
from pathlib import Path
ROOT=Path('/mnt/data/modelx_export_review/modelx_compiler_handoff_2026-09-05_v0.23.0.dev73_bounded_context_accessors')
sys.path[:0]=[
 '/mnt/data/fast_recursive_runtime/localdeps',
 str(ROOT/'compiler'),str(ROOT/'third_party/src/modelx-main'),str(ROOT/'third_party/src/lifelib-main'),
 str(ROOT/'third_party/src/modelx-cython-main'),str(ROOT/'third_party/src/MonkeyType-23.3.0'),str(ROOT)]
import modelx as mx
from modelx_graph import RealizedTraceCompiler
from modelx_graph.modelx_cython_bridge import derive_modelx_cython_trace_sample, build_modelx_cython_bridge
from probe_v10_products import SPECS
OUT=Path('/mnt/data/lfl_benchmark/mxcy'); OUT.mkdir(parents=True,exist_ok=True)
LIB=ROOT/'third_party/src/lifelib-main/lifelib/libraries'
models=sys.argv[1:] or ['BasicTerm_S','Term_UK_A','WOL_UK_S','ULSG_US_S','VA_US_S']
rows=[]
for name in models:
    row={'model':name}
    print(json.dumps({'event':'start','model':name}),flush=True)
    try:
        if name=='BasicTerm_S':
            m=mx.read_model(LIB/'basiclife/BasicTerm_S'); sp=m.Projection; keys=tuple(range(1,10001)); target=sp[1].pv_net_cf.node()
            c=RealizedTraceCompiler.from_target(m,target)
            sample,meta=derive_modelx_cython_trace_sample(c,keys,max_points=96,spread_points=32,max_categories=16)
        else:
            rel,helper=SPECS[name]; m=mx.read_model(LIB/rel); sp=m.Projection
            if 'bench_net_cf' not in sp.cells: sp.new_cells('bench_net_cf',formula=helper)
            keys=tuple(m.Data.model_point_table().index.tolist()); c=RealizedTraceCompiler.from_target(m,sp[keys[0]].bench_net_cf.node()); sample=tuple((k,) for k in keys); meta={'method':'all_shipped_policies'}
        row['policy_count']=len(keys); row['sample_count']=len(sample); row['sample']=sample; row['sample_meta']=meta
        t=time.perf_counter(); p=build_modelx_cython_bridge(c,OUT/name,sample_point_keys=sample,force_rebuild=True,build_timeout_seconds=240.0); row['wall_build_s']=time.perf_counter()-t; row['status']='ok'; row['package']=p.package_name; row['root']=str(p.root); row['build_report']=p.build_report.__dict__
        # full policy execution once as build sanity
        pts=tuple((k,) for k in keys)
        t=time.perf_counter(); vals=p.execute_points(pts); row['sanity_exec_s']=time.perf_counter()-t; row['sanity_checksum']=float(vals.sum()); row['sanity_count']=int(vals.size)
    except Exception as e:
        row['status']='failed'; row['error']=f'{type(e).__name__}: {e}'; row['traceback']=traceback.format_exc()[-12000:]
    finally:
        try:m.close()
        except Exception:pass
    rows.append(row); (OUT/f'{name}_build.json').write_text(json.dumps(row,indent=2,default=str)); print(json.dumps({'event':'done','model':name,'status':row['status'],'wall_build_s':row.get('wall_build_s'),'error':row.get('error')}),flush=True)
Path('/mnt/data/lfl_benchmark/MXCY_BUILD_RESULTS.json').write_text(json.dumps(rows,indent=2,default=str))
os._exit(0)
