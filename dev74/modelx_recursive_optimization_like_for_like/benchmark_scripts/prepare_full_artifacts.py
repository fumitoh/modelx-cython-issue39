from __future__ import annotations
import sys,os,json,time,ast,traceback
from pathlib import Path
ROOT=Path('/mnt/data/modelx_export_review/modelx_compiler_handoff_2026-09-05_v0.23.0.dev73_bounded_context_accessors')
sys.path[:0]=['/mnt/data/fast_recursive_runtime/localdeps',str(ROOT/'compiler'),str(ROOT/'third_party/src/modelx-main'),str(ROOT/'third_party/src/lifelib-main'),str(ROOT)]
import modelx as mx, numpy as np
from probe_v10_products import SPECS
from modelx_graph import RealizedTraceCompiler, StageCythonGenerator
from modelx_graph.native_batch import prepare_stage_scalar,prepare_optimized_scalar,plan_cython_backend,plan_stage_cython_backend
from modelx_graph.codegen import CythonGenerator
name=sys.argv[1]; sample=tuple(int(x) for x in sys.argv[2].split(',')); rel,helper=SPECS[name]
out=Path('/mnt/data/lfl_benchmark/artifacts')/name;out.mkdir(parents=True,exist_ok=True)
row={'model':name,'sample':sample}
m=mx.read_model(ROOT/'third_party/src/lifelib-main/lifelib/libraries'/rel);sp=m.Projection
if 'bench_net_cf' not in sp.cells:sp.new_cells('bench_net_cf',formula=helper)
keys=tuple(m.Data.model_point_table().index.tolist()); row['run_keys']=keys
try:
 t=time.perf_counter();rc=RealizedTraceCompiler.from_target(m,[sp[k].bench_net_cf.node() for k in sample]);row['trace_s']=time.perf_counter()-t;row['trace_nodes']=len(rc.trace.nodes)
 try:
  t=time.perf_counter();p=prepare_stage_scalar(rc,sample_keys=sample,run_keys=keys,validation_points=len(keys),full_run_domain_validation=True);row['stage_prepare_s']=time.perf_counter()-t; row['stage_validation']=p.python_validation; row['stage_plan']=plan_stage_cython_backend(p).__dict__
  src=StageCythonGenerator(p.stage_program).write(out/'stage_full.pyx','stage_'+name.lower()+'_full'); np.savez(out/'stage_inputs.npz',**{k:np.asarray(v) for k,v in p.bound_inputs.items()});
  prog=p.stage_program; impls=[]
  for uid,v in prog.variants.items(): impls.append({'uid':uid,'source_name':v.source_name,'role':v.role,'dtype':v.dtype,'time_param':v.time_param_source,'arg_count':len(v.function.args.args),'formula':ast.unparse(v.function),'reduction':repr(v.reduction)})
  row['stage_input_order']=list(prog.input_order);row['output_uid']=prog.output_uid;row['variants']=impls;row['iteration_domains']=[x.manifest() if hasattr(x,'manifest') else repr(x) for x in prog.iteration_domains];row['execution_blocks']=[x.manifest() if hasattr(x,'manifest') else repr(x) for x in prog.execution_blocks]
 except Exception as e: row['stage_error']=f'{type(e).__name__}: {e}';row['stage_traceback']=traceback.format_exc()[-8000:]
 try:
  t=time.perf_counter();lp=prepare_optimized_scalar(rc,sample_keys=sample,run_keys=keys,validation_points=len(keys));row['legacy_prepare_s']=time.perf_counter()-t;row['legacy_validation']=lp.python_validation;plan=plan_cython_backend(lp,emission_mode='direct_locals');row['legacy_plan']=plan.__dict__
  if plan.available:
   src=CythonGenerator(lp.optimized,emission_mode='direct_locals').emit('seq_'+name.lower()+'_full');(out/'sequential_full.pyx').write_text(src);np.savez(out/'legacy_inputs.npz',**{k:np.asarray(v) for k,v in lp.bound_inputs.items()});row['legacy_input_order']=list(lp.optimized.input_order)
 except Exception as e: row['legacy_error']=f'{type(e).__name__}: {e}';row['legacy_traceback']=traceback.format_exc()[-8000:]
except Exception as e: row['fatal']=f'{type(e).__name__}: {e}';row['fatal_traceback']=traceback.format_exc()[-8000:]
# Reference values after compiler preparation, using a separate model instance so trace state is untouched.
try:
 m2=mx.read_model(ROOT/'third_party/src/lifelib-main/lifelib/libraries'/rel); sp2=m2.Projection
 if 'bench_net_cf' not in sp2.cells: sp2.new_cells('bench_net_cf',formula=helper)
 t=time.perf_counter(); ref=np.asarray([float(sp2[k].bench_net_cf()) for k in keys],dtype=np.float64); row['live_reference_s']=time.perf_counter()-t; np.save(out/'reference.npy',ref); row['reference_checksum']=float(ref.sum()); m2.close()
except Exception as e: row['reference_error']=f'{type(e).__name__}: {e}'
(out/'prepare_full_meta.json').write_text(json.dumps(row,indent=2,default=str)); print(json.dumps({k:v for k,v in row.items() if k not in ('variants','iteration_domains','execution_blocks','stage_traceback','legacy_traceback','fatal_traceback')},default=str),flush=True)
try:m.close()
except:pass
os._exit(0)
