from __future__ import annotations
import sys as _sys; _sys.setrecursionlimit(20000)
import sys, importlib, time, gc, json, statistics, bisect
from pathlib import Path
NAME=sys.argv[1]; VARIANT=sys.argv[2]; REPS=int(sys.argv[3]) if len(sys.argv)>3 else 5
OUT=Path('/mnt/data/modelx_export_review/multi_exports2'); env=str(OUT/(NAME+'_env')); sys.path.insert(0,env)
mod=importlib.import_module(NAME+'._mx_model'); cm=importlib.import_module(NAME+'._mx_classes')
Model=getattr(mod,'_c_'+NAME); Proj=getattr(cm,'_c_Projection')
# setup immutable normalized data using a separate model instance
setup=Model(); D=setup.Data
for cn in getattr(cm,'_v_cells_names_Data'):
    try:getattr(D,cn)()
    except Exception:pass
mp=D.model_point_table(); keys=list(mp.index); rows={k:r.to_dict() for k,r in mp.iterrows()}

def patch_modelpoint():
    def _f_model_point(self): return rows[self.point_id]
    Proj._f_model_point=_f_model_point

def patch_providers():
    if NAME=='Term_UK_A':
        sf={int(k):float(v) for k,v in D.select_factor_table()['factor'].items()}; sfmax=max(sf)
        mort={tuple(k):float(v) for k,v in D.mort_table()['mort_rate'].items()}
        lapse={int(k):float(v) for k,v in D.lapse_table()['lapse_rate'].items()}; lmax=max(lapse)
        def _f_select_factor(self,t): return sf[min(self.duration(t), self.select_period)]
        def _f_mort_rate_base(self,t,life=1): return mort[(self.sex(life),self.smoker(life),self.age(t,life))]
        def _f_lapse_rate_base(self,t): return lapse[min(t,lmax)]
        Proj._f_select_factor=_f_select_factor; Proj._f_mort_rate_base=_f_mort_rate_base; Proj._f_lapse_rate_base=_f_lapse_rate_base
    elif NAME=='WOL_UK_S':
        mort={tuple(k):float(v) for k,v in D.mort_table()['mort_rate'].items()}
        lapse={tuple(k):float(v) for k,v in D.lapse_table()['lapse_rate'].items()}
        maxy={c:max(y for cc,y in lapse if cc==c) for c,_ in lapse}
        def _f_mort_rate(self,t):
            q=mort[(self.mort_basis(),self.sex(),self.smoker(),self.age(t))]
            return min(1.0,q*self.mort_loading()*self.mort_improve_factor(t))
        def _f_lapse_rate_base(self,t):
            c=self.cell(); y=min(self.policy_year(t),maxy[c]); return lapse[(c,y)]
        Proj._f_mort_rate=_f_mort_rate; Proj._f_lapse_rate_base=_f_lapse_rate_base
    elif NAME=='ULSG_US_S':
        corr={int(k):float(v) for k,v in D.corridor_factors()['corridor_factor'].items()}; cmin=min(corr); cmax=max(corr)
        coi={tuple(k):float(v) for k,v in D.coi_rates()['coi_rate_guar_ann'].items()}
        coimax={(sex,rc):max(a for s,r,a in coi if s==sex and r==rc) for sex,rc,_ in coi}
        surr={k:(float(r['sc_per_1000_init']),float(r['runoff_years'])) for k,r in D.surr_charge_table().iterrows()}
        rop={int(k):(float(r['refund_ratio']),float(r['exercise_rate'])) for k,r in D.rop_table().iterrows()}
        classfac={k:float(v) for k,v in D.class_factor_table()['factor'].items()}
        mort={int(k):float(v) for k,v in D.mort_table()['mort_rate'].items()}; mmin=min(mort); mmax=max(mort)
        lapse={int(k):float(v) for k,v in D.lapse_table()['lapse_rate_ann'].items()}; lmax=max(lapse)
        def _f_corridor_factor(self,t): return corr[min(max(self.age(t),cmin),cmax)]
        def _f_coi_rate_guar(self,t):
            sex=self.sex(); rc=self.rate_class(); a=min(self.age(t),coimax[(sex,rc)]); return coi[(sex,rc,a)]/12.0
        def _f_surr_charge_rate(self,t):
            if not self.has_surr_charge(): return 0.0
            init,yrs=surr[self.surr_charge_id()]; m=self.duration_mth(t)+1; return max(0.0,init-(init/yrs)*(m/12.0))
        def _f_rop_anniversary(self,t):
            if not self.rop_elected() or self.duration_mth(t)%12 !=0: return 0
            y=self.duration(t); return y if y in rop else 0
        def _f_rop_ratio(self,t):
            a=self.rop_anniversary(t); return 0.0 if a==0 else rop[a][0]
        def _f_rop_rate(self,t):
            a=self.rop_anniversary(t); return 0.0 if a==0 else rop[a][1]
        def _f_class_factor(self): return classfac[self.rate_class()]
        def _f_mort_rate(self,t):
            a=min(max(self.age(t),mmin),mmax); return min(1.0,mort[a]*self.class_factor()*self.mort_ae_factor*self.mort_improve_factor(t))
        def _f_lapse_rate_base(self,t): return lapse[min(self.policy_year(t),lmax)]
        Proj._f_corridor_factor=_f_corridor_factor; Proj._f_coi_rate_guar=_f_coi_rate_guar; Proj._f_surr_charge_rate=_f_surr_charge_rate
        Proj._f_rop_anniversary=_f_rop_anniversary; Proj._f_rop_ratio=_f_rop_ratio; Proj._f_rop_rate=_f_rop_rate; Proj._f_class_factor=_f_class_factor
        Proj._f_mort_rate=_f_mort_rate; Proj._f_lapse_rate_base=_f_lapse_rate_base
    elif NAME=='VA_US_S':
        ft=D.fund_table(); fund_sub={fs:list(g.index.get_level_values(1)) for fs,g in ft.groupby(level=0,sort=False)}
        alloc={tuple(k):float(v) for k,v in ft['alloc'].items()}; fexp={tuple(k):float(v) for k,v in ft['fund_expense'].items()}
        ret={}
        for (sc,i),g in D.return_scenario().groupby(level=[0,1],sort=False):
            gg=g.droplevel([0,1]).sort_index(); ret[(sc,int(i))]=(list(map(int,gg.index)),list(map(float,gg['gross_return'])))
        rate={}
        for sc,g in D.rate_scenario().groupby(level=0,sort=False):
            gg=g.droplevel(0).sort_index(); rate[sc]=(list(map(int,gg.index)),{c:list(map(float,gg[c])) for c in ['vix_sq','cmt10']})
        txn={tuple(k):(float(r['prem_amount']),float(r['wd_amount'])) for k,r in D.transaction_table().iterrows()}
        gawa={}
        for opt,g in D.gawa_pct_table().groupby(level=0,sort=False):
            gg=g.droplevel(0).sort_index(); gawa[opt]=(list(map(int,gg.index)),list(map(float,gg['gawa_pct'])))
        cdsc={}
        for sched,g in D.cdsc_table().groupby(level=0,sort=False):
            gg=g.droplevel(0).sort_index(); cdsc[sched]=(list(map(int,gg.index)),list(map(float,gg['surr_charge_rate'])))
        mort={tuple(k):float(v) for k,v in D.mort_table()['mort_rate'].items()}; mtop=max(a for a,s in mort)
        def _f_sub_ids(self): return fund_sub[self.fund_set()]
        def _f_alloc(self,i): return alloc[(self.fund_set(),i)]
        def _f_fund_expense_rate(self,i): return fexp[(self.fund_set(),i)]
        def _f_inv_return_mth(self,t,i):
            months,vals=ret[(self.scenario_id(),int(i))]; q=max(self.duration_mth(t),0); j=bisect.bisect_right(months,q)-1; return vals[j]
        def _f_scenario_rate(self,t,name):
            months,cols=rate[self.scenario_id()]; q=max(self.duration_mth(t),0); j=bisect.bisect_right(months,q)-1; return cols[name][j]
        def _f_prem_scheduled_pp(self,t):
            if t<1:return 0.0
            return txn.get((self.txn_id(),self.duration_mth(t)),(0.0,0.0))[0]
        def _f_wd_scheduled_pp(self,t):
            if t<1:return 0.0
            return txn.get((self.txn_id(),self.duration_mth(t)),(0.0,0.0))[1]
        def _f_gawa_pct_at_age(self,a):
            bands,vals=gawa[self.glwb_option()]; j=bisect.bisect_right(bands,a)-1; return 0.0 if j<0 else vals[j]
        def _f_surr_charge_rate(self,t):
            years,vals=cdsc[self.cdsc_schedule()]; y=min(self.duration(t),years[-1]); j=bisect.bisect_right(years,y)-1; return vals[j]
        def _f_mort_rate(self,t): return mort[(min(self.age(t),mtop),self.sex())]
        Proj._f_sub_ids=_f_sub_ids; Proj._f_alloc=_f_alloc; Proj._f_fund_expense_rate=_f_fund_expense_rate; Proj._f_inv_return_mth=_f_inv_return_mth
        Proj._f_scenario_rate=_f_scenario_rate; Proj._f_prem_scheduled_pp=_f_prem_scheduled_pp; Proj._f_wd_scheduled_pp=_f_wd_scheduled_pp
        Proj._f_gawa_pct_at_age=_f_gawa_pct_at_age; Proj._f_surr_charge_rate=_f_surr_charge_rate; Proj._f_mort_rate=_f_mort_rate


def merge_wrappers(exclude):
    import ast, copy
    src_path=Path(cm.__file__)
    tree=ast.parse(src_path.read_text())
    clsnode=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_c_Projection')
    funcs={n.name:n for n in clsnode.body if isinstance(n,ast.FunctionDef)}
    glb=dict(cm.__dict__)
    for name,wrap in list(funcs.items()):
        if name.startswith('_f_') or name in exclude: continue
        formula=funcs.get('_f_'+name)
        if formula is None or len(wrap.body)!=1 or not isinstance(wrap.body[0],ast.If): continue
        ifnode=wrap.body[0]
        if not ifnode.orelse or not isinstance(ifnode.orelse[-1],ast.Return): continue
        # identify generated cache updates from wrapper else branch
        first=ifnode.orelse[0]
        updates=[]
        if isinstance(first,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='val' for t in first.targets):
            other=[copy.deepcopy(t) for t in first.targets if not (isinstance(t,ast.Name) and t.id=='val')]
            if other:
                updates.append(ast.Assign(targets=other,value=ast.Name(id='val',ctx=ast.Load())))
            updates.extend(copy.deepcopy(ifnode.orelse[1:-1]))
        else:
            continue
        class Ret(ast.NodeTransformer):
            def visit_Return(self,node):
                value=copy.deepcopy(node.value) if node.value is not None else ast.Constant(None)
                return [ast.Assign(targets=[ast.Name(id='val',ctx=ast.Store())],value=value),
                        *copy.deepcopy(updates),
                        ast.Return(value=ast.Name(id='val',ctx=ast.Load()))]
        body=copy.deepcopy(formula.body)
        body=Ret().visit(ast.Module(body=body,type_ignores=[])).body
        # preserve cache-hit branch; inline formula body into miss branch
        new_if=copy.deepcopy(ifnode); new_if.orelse=body+[ast.Assign(targets=[ast.Name(id='val',ctx=ast.Store())],value=ast.Constant(None)),*copy.deepcopy(updates),ast.Return(value=ast.Name(id='val',ctx=ast.Load()))]
        newf=ast.FunctionDef(name=name,args=copy.deepcopy(wrap.args),body=[new_if],decorator_list=[],returns=None,type_comment=None)
        ast.fix_missing_locations(newf)
        ns={}; exec(compile(ast.Module(body=[newf],type_ignores=[]),str(src_path),'exec'),glb,ns)
        setattr(Proj,name,ns[name])

provider_excludes={
'Term_UK_A':{'select_factor','mort_rate_base','lapse_rate_base'},
'WOL_UK_S':{'mort_rate','lapse_rate_base'},
'ULSG_US_S':{'corridor_factor','coi_rate_guar','surr_charge_rate','rop_anniversary','rop_ratio','rop_rate','class_factor','mort_rate','lapse_rate_base'},
'VA_US_S':{'sub_ids','alloc','fund_expense_rate','inv_return_mth','scenario_rate','prem_scheduled_pp','wd_scheduled_pp','gawa_pct_at_age','surr_charge_rate','mort_rate'},
}
if VARIANT in ('providers','providers_mpdict','providers_mpdict_merged'): patch_providers()
if VARIANT in ('mpdict','providers_mpdict','providers_mpdict_merged'): patch_modelpoint()
if VARIANT=='providers_mpdict_merged': merge_wrappers(provider_excludes.get(NAME,set())|{'model_point'})
# expected baseline using separate unpatched? For patched variants, compute current package baseline from stored reference isn't available; use setup model before patch only if need. We validate patched values against live values captured by baseline in an unpatched sibling process later.
times=[]; outputs=None
for rep in range(REPS):
    m=Model(); d=m.Data
    for cn in getattr(cm,'_v_cells_names_Data'):
        try:getattr(d,cn)()
        except Exception:pass
    gc.collect(); t=time.perf_counter(); vals=[float(m.Projection[k].bench_net_cf()) for k in keys]; dt=time.perf_counter()-t
    times.append(dt); outputs=vals
print(json.dumps({'name':NAME,'variant':VARIANT,'reps':REPS,'n':len(keys),'times_s':times,'median_s':statistics.median(times),'per_policy_ms':statistics.median(times)/len(keys)*1e3,'checksum':sum(outputs),'values':outputs}),flush=True)
