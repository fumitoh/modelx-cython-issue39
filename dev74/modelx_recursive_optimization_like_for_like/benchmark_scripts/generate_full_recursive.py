from __future__ import annotations
import ast,json,sys,types,re
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/modelx_export_review/modelx_compiler_handoff_2026-09-05_v0.23.0.dev73_bounded_context_accessors')
sys.path[:0]=['/mnt/data/fast_recursive_runtime/localdeps',str(ROOT/'compiler')]
from modelx_graph.codegen import CythonGenerator
from modelx_graph.codegen_common import CodegenError
name=sys.argv[1]; d=Path('/mnt/data/lfl_benchmark/artifacts')/name
meta=json.load(open(d/'prepare_full_meta.json')); src=(d/'stage_full.pyx').read_text(); inputs={k:np.asarray(v) for k,v in np.load(d/'stage_inputs.npz',allow_pickle=False).items()}
start=src.index('def _impl_'); end=src.find('class _StageKernel',start); mod=ast.parse(src[start:end]); funcs={f.name:f for f in mod.body if isinstance(f,ast.FunctionDef)}
class CV: pass
v={}
for row in meta['variants']:
 cv=CV();cv.dtype=row['dtype'];cv.role=row['role'];cv.source_fullname=row.get('source_name',row['uid']);cv.function=funcs.get('_impl_'+row['uid']);cv.reduction=None;v[row['uid']]=cv
outuid=meta['output_uid']
# Reconstruct output reduction helpers if emitted.
if '_red_init_'+outuid in funcs:
 ri=funcs['_red_init_'+outuid];rf=funcs['_red_filter_'+outuid];rb=funcs['_red_body_'+outuid];red=types.SimpleNamespace();red.init=next(x.value for x in ri.body if isinstance(x,ast.Return));red.body_expr=next(x.value for x in rb.body if isinstance(x,ast.Return));fexpr=next(x.value for x in rf.body if isinstance(x,ast.Return));red.filters=() if isinstance(fexpr,ast.Constant) and fexpr.value is True else (fexpr,)
 # find iteration domain whose reductions include output if manifest carries it; fallback last domain
 domains=meta['iteration_domains']; dom=domains[-1]; red.range_args=tuple(ast.parse(x,mode='eval').body for x in dom['range_arg_sources']);red.target='_acc';red.loop_var='t';v[outuid].reduction=red;v[outuid].function=None
class IS: pass
specs=[]
for k,a in inputs.items():
 q=IS();q.key=k;q.dtype='bool' if a.dtype==np.bool_ else ('int64' if np.issubdtype(a.dtype,np.integer) else 'float64');q.ndim=int(a.ndim);q.scope='point' if k.startswith('p_') else 'global';q.shape=tuple(a.shape);specs.append(q)
input_specs={x.key:x for x in specs}

def mv_type(ctype,ndim):
 if ndim==0:return ctype
 if ndim==1:return f'{ctype}[::1]'
 return f"{ctype}[" + ', '.join([':']*(ndim-1)+['::1']) + ']'
class Emitter(CythonGenerator):
 def __init__(self):
  self.v=v;self.input_specs=input_specs;self.m=type('M',(),{'space':type('S',(),{'refs':{}})()})()
 def _cell_call(self,uid,args,ctx):
  i=ctx['point_index']
  if len(args)==0:return f'r_{uid}({i})'
  if len(args)==1:return f'r_{uid}({i}, <long>({self.expr(args[0],ctx)}))'
  raise CodegenError(f'{uid}: recursive prototype only supports zero/time argument variants')
 def _input_expr(self,n,args,ctx):
  if not args or not isinstance(args[0],ast.Constant):raise CodegenError(n)
  key=args[0].value; spec=self.input_specs[key]; i=ctx['point_index']
  if n=='point_input': return self._cast_read(f'{key}[{i}]',spec.dtype)
  if n=='global_input': return self._cast_read(key,spec.dtype)
  if n in ('array_input','table_input'):
   idx=[self.expr(x,ctx) for x in args[1:]]
   if len(idx)!=spec.ndim: raise CodegenError(f'{n} {key} expected {spec.ndim} indices, got {len(idx)}')
   ix=', '.join(f'<Py_ssize_t>({x})' for x in idx)
   return self._cast_read(f'{key}[{ix}]',spec.dtype)
  raise CodegenError(n)
 def expr(self,n,ctx):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name):
   if n.func.id=='__exact_axis_code__' and len(n.args)==4:
    val,start,step,size=[super(Emitter,self).expr(x,ctx) for x in n.args]
    return f'(<long>((({val}) - ({start})) / ({step})))'
   if n.func.id=='__guard_fail__': return 'NAN'
   if n.func.id=='round' and len(n.args)==2:
    x=self.expr(n.args[0],ctx); nd=self.expr(n.args[1],ctx)
    return f'_round_ndigits(<double>({x}), <long>({nd}))'
  return super().expr(n,ctx)
E=Emitter()
allnodes=[]
for cv in v.values():
 if cv.function:allnodes.extend(ast.walk(cv.function))
 if cv.reduction:
  for q in (cv.reduction.init,cv.reduction.body_expr,*cv.reduction.range_args,*cv.reduction.filters):allnodes.extend(ast.walk(q))
for attr,call in [('has_step_lookup_intrinsic','__step_lookup_1d__'),('has_interval_lookup_intrinsic','__interval_lookup_1d__'),('has_interp_lookup_intrinsic','__interp_lookup_1d__'),('has_missing_intrinsic','__is_missing__'),('has_isinf_intrinsic','__is_inf__'),('has_erf_intrinsic','__erf__')]:setattr(E,attr,any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==call for n in allnodes))
E.has_infinity_constant=False
lines=['# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False','from libc.math cimport pow, fabs, rint, exp, log, sqrt, sin, cos, floor, ceil, isnan, isinf, erf, NAN','from libc.stdlib cimport malloc, calloc, free','cimport numpy as cnp','import numpy as np','','cdef inline double _round_ndigits(double x, long n) noexcept nogil:','    cdef double scale','    if n >= 0:','        scale = pow(10.0, <double>n)','        return rint(x * scale) / scale','    scale = pow(10.0, <double>(-n))','    return rint(x / scale) * scale','', 'cdef Py_ssize_t CACHE_WIDTH = 4096','cdef Py_ssize_t CACHE_OFFSET = 1024',f'cdef Py_ssize_t CACHE_ROWS = {len(v)}','cdef double* _cache = NULL','cdef unsigned int* _valid = NULL','cdef unsigned int _epoch = 1','cdef Py_ssize_t _n = 0','']
for s in specs: lines.append(f'cdef {mv_type(E.ctype(s.dtype),s.ndim)} {s.key}')
lines.append('')
if E.has_step_lookup_intrinsic: lines+=E._step_lookup_helper_lines()+['']
if E.has_interval_lookup_intrinsic: lines+=E._interval_lookup_helper_lines()+['']
if E.has_interp_lookup_intrinsic: lines+=E._interp_lookup_helper_lines()+['']
lines.append('cpdef init_inputs(dict d):');lines.append('    global _cache, _valid, _epoch, _n, '+', '.join(s.key for s in specs))
point_specs=[s for s in specs if s.scope=='point']
if not point_specs: raise RuntimeError('expected point inputs')
for s in specs:
 k=s.key
 if s.ndim==0: lines.append(f"    {k} = {'int' if s.dtype!='float64' else 'float'}(np.asarray(d[{k!r}]).reshape(()))")
 else:
  npdt='np.int64' if s.dtype=='int64' else ('np.bool_' if s.dtype=='bool' else 'np.float64')
  lines.append(f"    {k} = np.ascontiguousarray(d[{k!r}], dtype={npdt})")
lines.append(f'    _n = {point_specs[0].key}.shape[0]')
for s in point_specs[1:]:lines+= [f'    if {s.key}.shape[0] != _n:',f"        raise ValueError('point input length mismatch: {s.key}')"]
lines+=['    if _cache == NULL:','        _cache = <double*>malloc(CACHE_ROWS * CACHE_WIDTH * sizeof(double))','        _valid = <unsigned int*>calloc(CACHE_ROWS * CACHE_WIDTH, sizeof(unsigned int))','        if _cache == NULL or _valid == NULL: raise MemoryError()','    _epoch = 1','    return None','']

def emit_fn(uid,cv):
 fn=cv.function
 if fn is None:return []
 argc=len(fn.args.args);ct=E.ctype(cv.dtype);sig='Py_ssize_t i' if argc==0 else 'Py_ssize_t i, long t';lt=E._local_types(fn);ls=[f'cdef inline {ct} calc_{uid}({sig}) noexcept nogil:']
 for n,t in sorted(lt.items()):ls.append(f"    cdef {t} l_{n} = {'0.0' if t=='double' else '0'}")
 has_any=any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='any' for n in ast.walk(fn))
 if has_any:ls.append('    cdef long _gen_i = 0')
 ctx={'locals':{n:'l_'+n for n in lt},'loop_var':'t','loop_var_c':'t','point_index':'i'}
 def st(x,ind):
  if isinstance(x,ast.Assign) and len(x.targets)==1 and isinstance(x.targets[0],ast.Name):ls.append(f'{ind}l_{x.targets[0].id} = {E.expr(x.value,ctx)}');return
  if isinstance(x,ast.AnnAssign) and isinstance(x.target,ast.Name):ls.append(f'{ind}l_{x.target.id} = {E.expr(x.value,ctx)}');return
  if isinstance(x,ast.Return):
   vv=x.value
   if isinstance(vv,ast.Call) and isinstance(vv.func,ast.Name) and vv.func.id=='any' and len(vv.args)==1 and isinstance(vv.args[0],ast.GeneratorExp):
    ge=vv.args[0];comp=ge.generators[0];it=comp.iter
    if len(ge.generators)!=1 or comp.ifs or not isinstance(comp.target,ast.Name) or not(isinstance(it,ast.Call) and isinstance(it.func,ast.Name) and it.func.id=='range'):raise RuntimeError('unsupported any generator')
    aa=list(it.args);startx=ast.Constant(0) if len(aa)==1 else aa[0];stopx=aa[0] if len(aa)==1 else aa[1];stepx=ast.Constant(1) if len(aa)<3 else aa[2]
    ls.append(f'{ind}_gen_i = <long>({E.expr(startx,ctx)})'); stopc=E.expr(stopx,ctx);stepc=E.expr(stepx,ctx);old=ctx['locals'].get(comp.target.id);ctx['locals'][comp.target.id]='_gen_i';elt=E.expr(ge.elt,ctx);ctx['locals'].pop(comp.target.id,None) if old is None else ctx['locals'].__setitem__(comp.target.id,old);ls.append(f'{ind}while (_gen_i < <long>({stopc})):' );ls.append(f'{ind}    if {elt}: return <{ct}>1');ls.append(f'{ind}    _gen_i += <long>({stepc})');ls.append(f'{ind}return <{ct}>0');return
   ls.append(f'{ind}return <{ct}>({E.expr(vv,ctx)})');return
  if isinstance(x,ast.If):
   ls.append(f'{ind}if {E.expr(x.test,ctx)}:');
   for q in x.body:st(q,ind+'    ')
   if x.orelse:
    ls.append(f'{ind}else:');
    for q in x.orelse:st(q,ind+'    ')
   return
  if isinstance(x,ast.Expr) and isinstance(x.value,ast.Constant) and isinstance(x.value.value,str):return
  if isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Name) and x.value.func.id=='__guard_fail__':
   ls.append(f'{ind}return <{ct}>({"NAN" if ct=="double" else "0"})'); return
  raise RuntimeError(ast.dump(x,include_attributes=False))
 for x in fn.body:st(x,'    ')
 ls+=['    return <'+ct+'>0',''];return ls

def emit_red(uid,cv):
 rr=cv.reduction;ct=E.ctype(cv.dtype);ctx={'locals':{rr.target:'acc'},'loop_var':'t','loop_var_c':'t','point_index':'i'};a=[E.expr(x,ctx) for x in rr.range_args];step='1' if len(a)==2 else a[2]
 ls=[f'cdef inline {ct} calc_{uid}(Py_ssize_t i) noexcept nogil:',f'    cdef {ct} acc = <{ct}>({E.expr(rr.init,ctx)})',f'    cdef long t = <long>({a[0]})',f'    cdef long stop = <long>({a[1]})',f'    cdef long step = <long>({step})','    while (t < stop if step > 0 else t > stop):'];ind='        '
 if rr.filters:ls.append('        if '+' and '.join(E.expr(x,ctx) for x in rr.filters)+':');ind='            '
 ls.append(f'{ind}acc = <{ct}>(acc + ({E.expr(rr.body_expr,ctx)}))');ls+=['        t += step','    return acc',''];return ls
for uid in sorted(v): lines += emit_red(uid,v[uid]) if v[uid].reduction else emit_fn(uid,v[uid])
rows={u:i for i,u in enumerate(sorted(v))}
for uid in sorted(v):
 cv=v[uid];argc=0 if cv.reduction else len(cv.function.args.args);ct=E.ctype(cv.dtype);row=rows[uid]
 if argc==0: lines += [f'cdef inline {ct} r_{uid}(Py_ssize_t i) noexcept nogil:',f'    cdef Py_ssize_t idx = {row} * CACHE_WIDTH + CACHE_OFFSET',f'    cdef {ct} val','    if _valid[idx] == _epoch: return <'+ct+'>_cache[idx]',f'    val = calc_{uid}(i)','    _cache[idx] = <double>val','    _valid[idx] = _epoch','    return val','']
 else: lines += [f'cdef inline {ct} r_{uid}(Py_ssize_t i, long t) noexcept nogil:',f'    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET',f'    cdef Py_ssize_t idx = {row} * CACHE_WIDTH + pos',f'    cdef {ct} val','    if pos < 0 or pos >= CACHE_WIDTH: return <'+ct+'>NAN','    if _valid[idx] == _epoch: return <'+ct+'>_cache[idx]',f'    val = calc_{uid}(i, t)','    _cache[idx] = <double>val','    _valid[idx] = _epoch','    return val','']
lines += ['cdef inline double _eval_one(Py_ssize_t i) noexcept nogil:','    global _epoch','    _epoch += 1',f'    return <double>r_{outuid}(i)','','cpdef cnp.ndarray run_all():','    cdef cnp.ndarray arr = np.empty(_n, dtype=np.float64)','    cdef double[::1] out = arr','    cdef Py_ssize_t i','    with nogil:','        for i in range(_n): out[i] = _eval_one(i)','    return arr','','cpdef double bench(long reps):','    cdef long j','    cdef Py_ssize_t i','    cdef double acc = 0.0','    with nogil:','        for j in range(reps):','            for i in range(_n): acc += _eval_one(i)','    return acc','']
out=d/'fast_recursive_full.pyx';out.write_text('\n'.join(lines));print(json.dumps({'model':name,'variants':len(v),'inputs':len(specs),'source_bytes':out.stat().st_size,'point_count':len(inputs[point_specs[0].key]),'output_uid':outuid}),flush=True)
