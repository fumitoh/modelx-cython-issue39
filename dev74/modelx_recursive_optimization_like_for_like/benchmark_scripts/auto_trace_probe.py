from __future__ import annotations
import sys,os,json,time
from pathlib import Path
ROOT=Path('/mnt/data/modelx_export_review/modelx_compiler_handoff_2026-09-05_v0.23.0.dev73_bounded_context_accessors')
sys.path[:0]=['/mnt/data/fast_recursive_runtime/localdeps',str(ROOT/'compiler'),str(ROOT/'third_party/src/modelx-main'),str(ROOT/'third_party/src/lifelib-main'),str(ROOT)]
import modelx as mx
from probe_v10_products import SPECS
from modelx_graph import RealizedTraceCompiler
from modelx_graph.native_batch import prepare_stage_scalar_auto_trace, plan_stage_cython_backend
name=sys.argv[1]; rel,helper=SPECS[name]; m=mx.read_model(ROOT/'third_party/src/lifelib-main/lifelib/libraries'/rel);sp=m.Projection
if 'bench_net_cf' not in sp.cells:sp.new_cells('bench_net_cf',formula=helper)
keys=tuple(m.Data.model_point_table().index.tolist()); first=keys[0]
t=time.perf_counter(); rc=RealizedTraceCompiler.from_target(m,sp[first].bench_net_cf.node()); print(json.dumps({'event':'initial_trace','seconds':time.perf_counter()-t,'key':first,'nodes':len(rc.trace.nodes),'run_keys':keys}),flush=True)
try:
 t=time.perf_counter(); clo=prepare_stage_scalar_auto_trace(rc,run_keys=keys,validation_points=len(keys),expansion_batch=2,max_rounds=8,max_sample_keys=len(keys)); dt=time.perf_counter()-t
 p=clo.preparation; plan=plan_stage_cython_backend(p)
 print(json.dumps({'event':'complete','seconds':dt,'samples':p.samples,'rounds':[r.__dict__ for r in clo.rounds],'proof':clo.coverage_proof.__dict__,'point_count':p.point_count,'cython_available':plan.available,'reason':plan.reason},default=str),flush=True)
except Exception as e:
 print(json.dumps({'event':'error','error':f'{type(e).__name__}: {e}','seconds':time.perf_counter()-t},default=str),flush=True)
try:m.close()
except:pass
os._exit(0)
