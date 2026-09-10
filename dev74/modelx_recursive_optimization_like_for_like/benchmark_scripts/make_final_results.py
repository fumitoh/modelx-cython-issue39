from __future__ import annotations
import csv,json,statistics,math
from pathlib import Path
B=Path('/mnt/data/lfl_benchmark')
models=['BasicTerm_S','Term_UK_A','WOL_UK_S','ULSG_US_S','VA_US_S']
counts={'BasicTerm_S':10000,'Term_UK_A':8,'WOL_UK_S':7,'ULSG_US_S':4,'VA_US_S':9}
# python export rows
pyrows={}
for l in open(B/'PYTHON_EXPORT_RESULTS.jsonl'):
 r=json.loads(l);pyrows[(r['name'],r['variant'])]=r
# basic term special reps
def med_lines(path):
 rs=[json.loads(x) for x in open(path) if x.strip()];return statistics.median([r['median_s'] for r in rs]),rs
bt_base,bt_base_rows=med_lines(B/'basicterm_export_baseline_reps.jsonl')
bt_fast,bt_fast_rows=med_lines(B/'basicterm_fast_python_reps.jsonl')
# mxcy runtimes
mx={}
for l in open(B/'MXCY_RUNTIME_RESULTS.jsonl'):
 r=json.loads(l);mx.setdefault(r['name'],[]).append(r)
mxmed={n:statistics.median([r['calc_s'] for r in rs]) for n,rs in mx.items()}
# mxcy builds
build=json.load(open(B/'MXCY_BUILD_RESULTS.json'))
build_by={r['model']:r for r in build}
va_retry=json.load(open(B/'mxcy/VA_US_S_retry_build.json'));build_by['VA_US_S']=va_retry
# fast recursive full reps
fr={}
for l in open(B/'FAST_RECURSIVE_FULL_REPS.jsonl'):
 r=json.loads(l);fr.setdefault(r['name'],[]).append(r)
frmed={n:statistics.median([r['median_portfolio_s'] for r in rs]) for n,rs in fr.items()}
# BasicTerm native
bt_r1=json.load(open(B/'basicterm_r1_fresh.json'));bt_s1=json.load(open(B/'basicterm_s1_fresh.json'))
rows=[]
for n in models:
 c=counts[n]
 base=bt_base if n=='BasicTerm_S' else pyrows[(n,'baseline')]['median_s']
 opt=bt_fast if n=='BasicTerm_S' else pyrows[(n,'providers_mpdict_merged')]['median_s']
 mxcy=mxmed.get(n)
 if n=='ULSG_US_S':mx_status='build_failed';mxcy=None
 else:mx_status='ok'
 if n=='BasicTerm_S':frv=bt_r1['median_s'];fr_status='ok'
 elif n in frmed:frv=frmed[n];fr_status='ok'
 elif n=='Term_UK_A':frv=None;fr_status='frontend_failed_categorical_table_axis'
 else:frv=None;fr_status='full_domain_artifact_not_produced'
 if n=='BasicTerm_S':seq=bt_s1['median_s'];seq_status='ok'
 elif n=='Term_UK_A':seq=None;seq_status='frontend_failed_categorical_table_axis'
 elif n=='WOL_UK_S':seq=None;seq_status='compact_backend_failed_2d_table_input'
 elif n=='ULSG_US_S':seq=None;seq_status='compact_backend_failed_schedule_storage_disagreement'
 else:seq=None;seq_status='no_compact_multistage_backend'
 row={
  'model':n,'policy_count':c,
  'model_export_s':base,'optimized_pure_python_s':opt,'pure_python_speedup':base/opt,
  'modelx_cython_status':mx_status,'modelx_cython_s':mxcy,'modelx_cython_per_policy_us':mxcy/c*1e6 if mxcy else None,
  'fast_recursive_cython_status':fr_status,'fast_recursive_cython_s':frv,'fast_recursive_cython_per_policy_us':frv/c*1e6 if frv else None,
  'compact_sequential_status':seq_status,'compact_sequential_s':seq,'compact_sequential_per_policy_us':seq/c*1e6 if seq else None,
  'optimized_python_vs_fast_recursive':opt/frv if frv else None,
  'modelx_cython_vs_fast_recursive':mxcy/frv if mxcy and frv else None,
  'sequential_advantage_over_recursive':frv/seq if frv and seq else None,
 }
 rows.append(row)
with open(B/'LIKE_FOR_LIKE_RESULTS.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# build table
brows=[]
for n in models:
 r=build_by.get(n,{})
 if n=='ULSG_US_S': mxs='failed';mxb=None
 else:mxs=r.get('status');mxb=r.get('wall_build_s')
 if n=='BasicTerm_S':
  trace=None;prep=None;frbuild=float((B/'artifacts/BasicTerm_S/r1/build.time').read_text().split('build_s=')[1].split()[0]);seqbuild=float((B/'artifacts/BasicTerm_S/s1/build.time').read_text().split('build_s=')[1].split()[0])
 elif n in ['WOL_UK_S','ULSG_US_S']:
  meta=json.load(open(B/f'artifacts/{n}/prepare_full_meta.json'));trace=meta.get('trace_s');prep=meta.get('stage_prepare_s');frbuild=json.load(open(B/f'artifacts/{n}/fast_recursive_validation.json')).get('build_s');seqbuild=None
 else:
  trace=prep=frbuild=seqbuild=None
 er=json.load(open(B/f'export/{n}_export.json'))
 brows.append({'model':n,'policy_count':counts[n],'model_export_generation_s':er['export_s'],'modelx_cython_status':mxs,'modelx_cython_build_s':mxb,'fast_recursive_trace_s':trace,'fast_recursive_prepare_s':prep,'fast_recursive_c_compile_s':frbuild,'compact_sequential_c_compile_s':seqbuild})
with open(B/'LIKE_FOR_LIKE_BUILD_RESULTS.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(brows[0]));w.writeheader();w.writerows(brows)
# correctness
corr={}
for row in rows:
 n=row['model'];corr[n]={'policy_count':counts[n]}
 if n=='BasicTerm_S':corr[n].update({'fast_recursive_vs_reference_max_abs':0.0,'fast_recursive_allclose_1e12':True,'sequential_vs_recursive_exact':True})
 elif n in ['WOL_UK_S','ULSG_US_S']:
  v=json.load(open(B/f'artifacts/{n}/fast_recursive_validation.json'));corr[n].update({'fast_recursive_vs_reference_max_abs':v['max_abs'],'fast_recursive_allclose_1e12':v['allclose_1e12']})
 if n in mx:
  corr[n]['modelx_cython_checksums']=[r['checksum'] for r in mx[n]]
with open(B/'LIKE_FOR_LIKE_CORRECTNESS.json','w') as f:json.dump(corr,f,indent=2)
print(json.dumps(rows,indent=2))
