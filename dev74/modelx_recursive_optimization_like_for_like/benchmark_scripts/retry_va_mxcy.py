from __future__ import annotations
import sys,json,time,traceback,os
from pathlib import Path
ROOT=Path('/mnt/data/modelx_export_review/modelx_compiler_handoff_2026-09-05_v0.23.0.dev73_bounded_context_accessors')
sys.path[:0]=['/mnt/data/fast_recursive_runtime/localdeps',str(ROOT/'compiler'),str(ROOT/'third_party/src/modelx-main'),str(ROOT/'third_party/src/lifelib-main'),str(ROOT/'third_party/src/modelx-cython-main'),str(ROOT/'third_party/src/MonkeyType-23.3.0'),str(ROOT)]
import modelx as mx
from probe_v10_products import SPECS
from modelx_graph import RealizedTraceCompiler
import modelx_graph.modelx_cython_bridge as b
old=b._sample_source
def patched(export_package,target):
    return 'import sys\nsys.setrecursionlimit(50000)\n'+old(export_package,target)
b._sample_source=patched
name='VA_US_S'; rel,helper=SPECS[name]; m=mx.read_model(ROOT/'third_party/src/lifelib-main/lifelib/libraries'/rel); sp=m.Projection
if 'bench_net_cf' not in sp.cells:sp.new_cells('bench_net_cf',formula=helper)
keys=tuple(m.Data.model_point_table().index.tolist()); c=RealizedTraceCompiler.from_target(m,sp[keys[0]].bench_net_cf.node())
row={'model':name,'keys':keys,'sample':keys,'recursionlimit':50000}
try:
 t=time.perf_counter(); p=b.build_modelx_cython_bridge(c,'/mnt/data/lfl_benchmark/mxcy/VA_US_S_retry',sample_point_keys=tuple((k,) for k in keys),force_rebuild=True,build_timeout_seconds=300.0);row['status']='ok';row['wall_build_s']=time.perf_counter()-t;row['package']=p.package_name;row['root']=str(p.root);row['build_report']=p.build_report.__dict__;t=time.perf_counter();v=p.execute_points(tuple((k,) for k in keys));row['sanity_exec_s']=time.perf_counter()-t;row['values']=v.tolist();row['checksum']=float(v.sum())
except Exception as e:row['status']='failed';row['error']=f'{type(e).__name__}: {e}';row['traceback']=traceback.format_exc()[-12000:]
Path('/mnt/data/lfl_benchmark/mxcy/VA_US_S_retry_build.json').write_text(json.dumps(row,indent=2,default=str));print(json.dumps({'status':row['status'],'wall_build_s':row.get('wall_build_s'),'error':row.get('error')},default=str),flush=True)
try:m.close()
except:pass
os._exit(0)
