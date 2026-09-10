from __future__ import annotations
import sys,os,json,time
from pathlib import Path
ROOT=Path('/mnt/data/modelx_export_review/modelx_compiler_handoff_2026-09-05_v0.23.0.dev73_bounded_context_accessors')
sys.path[:0]=['/mnt/data/fast_recursive_runtime/localdeps',str(ROOT/'compiler'),str(ROOT/'third_party/src/modelx-main'),str(ROOT/'third_party/src/lifelib-main'),str(ROOT)]
import modelx as mx
from probe_v10_products import SPECS
from modelx_graph import RealizedTraceCompiler
from modelx_graph.native_batch import prepare_stage_scalar,plan_stage_cython_backend
name=sys.argv[1]; sample=tuple(int(x) for x in sys.argv[2].split(','));rel,helper=SPECS[name]
m=mx.read_model(ROOT/'third_party/src/lifelib-main/lifelib/libraries'/rel);sp=m.Projection
if 'bench_net_cf' not in sp.cells:sp.new_cells('bench_net_cf',formula=helper)
keys=tuple(m.Data.model_point_table().index.tolist())
t=time.perf_counter();rc=RealizedTraceCompiler.from_target(m,[sp[k].bench_net_cf.node() for k in sample]);print(json.dumps({'event':'trace','seconds':time.perf_counter()-t,'sample':sample,'nodes':len(rc.trace.nodes),'run_keys':keys}),flush=True)
try:
 t=time.perf_counter();p=prepare_stage_scalar(rc,sample_keys=sample,run_keys=keys,validation_points=len(keys),full_run_domain_validation=True);plan=plan_stage_cython_backend(p);print(json.dumps({'event':'complete','seconds':time.perf_counter()-t,'point_count':p.point_count,'validation':p.python_validation,'cython_available':plan.available,'reason':plan.reason},default=str),flush=True)
except Exception as e:print(json.dumps({'event':'error','error':f'{type(e).__name__}: {e}','seconds':time.perf_counter()-t}),flush=True)
try:m.close()
except:pass
os._exit(0)
