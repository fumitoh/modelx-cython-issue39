from __future__ import annotations
import math
MAX_T=241
N_TIME=16
N_SCALAR=17
# time IDs
AGE=0; CLAIM_PP=1; CLAIMS=2; COMMISSIONS=3; DURATION=4; EXPENSES=5; INFLATION_FACTOR=6; LAPSE_RATE=7; MORT_RATE=8; MORT_RATE_MTH=9; NET_CF=10; POLS_DEATH=11; POLS_IF=12; POLS_LAPSE=13; POLS_MATURITY=14; PREMIUMS=15
# scalar IDs
AGE_AT_ENTRY=0; EXPENSE_ACQ=1; EXPENSE_MAINT=2; INFLATION_RATE=3; LOADING_PREM=4; NET_PREMIUM_PP=5; POLICY_TERM=6; POLS_IF_INIT=7; PREMIUM_PP=8; PROJ_LEN=9; PV_CLAIMS=10; PV_COMMISSIONS=11; PV_EXPENSES=12; PV_NET_CF=13; PV_POLS_IF=14; PV_PREMIUMS=15; SUM_ASSURED=16

class FastRecursiveBasicTerm:
    __slots__=('generation','policy_term_v','sum_assured_v','age_at_entry_v','disc_factor','mort_flat','tv','tg','sv','sg')
    def __init__(self, disc_rate_ann, mort_table):
        self.generation=0
        self.policy_term_v=0; self.sum_assured_v=0; self.age_at_entry_v=0
        # exact same mathematical definition, prepared once because it is policy-independent
        self.disc_factor=[0.0]*MAX_T
        for t in range(MAX_T):
            mth=(1.0+float(disc_rate_ann[t//12]))**(1.0/12.0)-1.0
            self.disc_factor[t]=(1.0+mth)**(-t)
        # prepare numeric table as a flat Python list to avoid pandas/NumPy indexing in hot formulas
        self.mort_flat=[float(x) for row in mort_table for x in row]
        self.tv=[0.0]*(N_TIME*MAX_T)
        self.tg=[0]*(N_TIME*MAX_T)
        self.sv=[0.0]*N_SCALAR
        self.sg=[0]*N_SCALAR
    def bind(self, policy_term, sum_assured, age_at_entry):
        self.generation += 1
        self.policy_term_v=int(policy_term); self.sum_assured_v=int(sum_assured); self.age_at_entry_v=int(age_at_entry)
    # generic exporter-style helpers are deliberately NOT used below; each Cell has its own direct method.
    def age(self,t):
        i=AGE*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=self.age_at_entry()+self.duration(t); self.tv[i]=v; self.tg[i]=g; return v
    def claim_pp(self,t):
        i=CLAIM_PP*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=self.sum_assured(); self.tv[i]=v; self.tg[i]=g; return v
    def claims(self,t):
        i=CLAIMS*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=self.claim_pp(t)*self.pols_death(t); self.tv[i]=v; self.tg[i]=g; return v
    def commissions(self,t):
        i=COMMISSIONS*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=self.premiums(t) if self.duration(t)==0 else 0.0; self.tv[i]=v; self.tg[i]=g; return v
    def duration(self,t):
        i=DURATION*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=t//12; self.tv[i]=v; self.tg[i]=g; return v
    def expenses(self,t):
        i=EXPENSES*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        maint=self.pols_if(t)*self.expense_maint()/12.0*self.inflation_factor(t)
        v=self.expense_acq()+maint if t==0 else maint
        self.tv[i]=v; self.tg[i]=g; return v
    def inflation_factor(self,t):
        i=INFLATION_FACTOR*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=(1.0+self.inflation_rate())**(t/12.0); self.tv[i]=v; self.tg[i]=g; return v
    def lapse_rate(self,t):
        i=LAPSE_RATE*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=max(0.1-0.02*self.duration(t),0.02); self.tv[i]=v; self.tg[i]=g; return v
    def mort_rate(self,t):
        i=MORT_RATE*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        d=max(min(5,self.duration(t)),0); a=int(self.age(t)); v=self.mort_flat[a*6+d]
        self.tv[i]=v; self.tg[i]=g; return v
    def mort_rate_mth(self,t):
        i=MORT_RATE_MTH*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=1.0-(1.0-self.mort_rate(t))**(1.0/12.0); self.tv[i]=v; self.tg[i]=g; return v
    def net_cf(self,t):
        i=NET_CF*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=self.premiums(t)-self.claims(t)-self.expenses(t)-self.commissions(t); self.tv[i]=v; self.tg[i]=g; return v
    def pols_death(self,t):
        i=POLS_DEATH*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=self.pols_if(t)*self.mort_rate_mth(t); self.tv[i]=v; self.tg[i]=g; return v
    def pols_if(self,t):
        i=POLS_IF*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        if t==0:v=self.pols_if_init()
        elif t>self.policy_term()*12:v=0.0
        else:v=self.pols_if(t-1)-self.pols_lapse(t-1)-self.pols_death(t-1)-self.pols_maturity(t)
        self.tv[i]=v; self.tg[i]=g; return v
    def pols_lapse(self,t):
        i=POLS_LAPSE*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=(self.pols_if(t)-self.pols_death(t))*(1.0-(1.0-self.lapse_rate(t))**(1.0/12.0))
        self.tv[i]=v; self.tg[i]=g; return v
    def pols_maturity(self,t):
        i=POLS_MATURITY*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        if t==self.policy_term()*12:v=self.pols_if(t-1)-self.pols_lapse(t-1)-self.pols_death(t-1)
        else:v=0.0
        self.tv[i]=v; self.tg[i]=g; return v
    def premiums(self,t):
        i=PREMIUMS*MAX_T+t; g=self.generation
        if self.tg[i]==g:return self.tv[i]
        v=self.premium_pp()*self.pols_if(t); self.tv[i]=v; self.tg[i]=g; return v
    # scalar Cells
    def _scalar_get(self, cell):
        # not used by formula methods; only a placeholder for diagnostics
        return self.sv[cell] if self.sg[cell]==self.generation else None
    def age_at_entry(self):
        c=AGE_AT_ENTRY; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=float(self.age_at_entry_v); self.sv[c]=v; self.sg[c]=g; return v
    def expense_acq(self):
        c=EXPENSE_ACQ; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=300.0; self.sv[c]=v; self.sg[c]=g; return v
    def expense_maint(self):
        c=EXPENSE_MAINT; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=60.0; self.sv[c]=v; self.sg[c]=g; return v
    def inflation_rate(self):
        c=INFLATION_RATE; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=0.01; self.sv[c]=v; self.sg[c]=g; return v
    def loading_prem(self):
        c=LOADING_PREM; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=0.5; self.sv[c]=v; self.sg[c]=g; return v
    def net_premium_pp(self):
        c=NET_PREMIUM_PP; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=self.pv_claims()/self.pv_pols_if(); self.sv[c]=v; self.sg[c]=g; return v
    def policy_term(self):
        c=POLICY_TERM; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=float(self.policy_term_v); self.sv[c]=v; self.sg[c]=g; return v
    def pols_if_init(self):
        c=POLS_IF_INIT; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=1.0; self.sv[c]=v; self.sg[c]=g; return v
    def premium_pp(self):
        c=PREMIUM_PP; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=round((1.0+self.loading_prem())*self.net_premium_pp(),2); self.sv[c]=v; self.sg[c]=g; return v
    def proj_len(self):
        c=PROJ_LEN; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=float(12*self.policy_term_v+1); self.sv[c]=v; self.sg[c]=g; return v
    def sum_assured(self):
        c=SUM_ASSURED; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=float(self.sum_assured_v); self.sv[c]=v; self.sg[c]=g; return v
    def pv_claims(self):
        c=PV_CLAIMS; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        n=int(self.proj_len()); df=self.disc_factor; acc=0.0
        for t in range(n):acc += self.claims(t)*df[t]
        self.sv[c]=acc; self.sg[c]=g; return acc
    def pv_commissions(self):
        c=PV_COMMISSIONS; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        n=int(self.proj_len()); df=self.disc_factor; acc=0.0
        for t in range(n):acc += self.commissions(t)*df[t]
        self.sv[c]=acc; self.sg[c]=g; return acc
    def pv_expenses(self):
        c=PV_EXPENSES; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        n=int(self.proj_len()); df=self.disc_factor; acc=0.0
        for t in range(n):acc += self.expenses(t)*df[t]
        self.sv[c]=acc; self.sg[c]=g; return acc
    def pv_pols_if(self):
        c=PV_POLS_IF; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        n=int(self.proj_len()); df=self.disc_factor; acc=0.0
        for t in range(n):acc += self.pols_if(t)*df[t]
        self.sv[c]=acc; self.sg[c]=g; return acc
    def pv_premiums(self):
        c=PV_PREMIUMS; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        n=int(self.proj_len()); df=self.disc_factor; acc=0.0
        for t in range(n):acc += self.premiums(t)*df[t]
        self.sv[c]=acc; self.sg[c]=g; return acc
    def pv_net_cf(self):
        c=PV_NET_CF; g=self.generation
        if self.sg[c]==g:return self.sv[c]
        v=self.pv_premiums()-self.pv_claims()-self.pv_expenses()-self.pv_commissions()
        self.sv[c]=v; self.sg[c]=g; return v

def run_portfolio(policy_term, sum_assured, age_at_entry, disc_rate_ann, mort_table):
    rt=FastRecursiveBasicTerm(disc_rate_ann,mort_table)
    out=[]
    for pt,sa,aa in zip(policy_term,sum_assured,age_at_entry):
        rt.bind(pt,sa,aa)
        out.append(rt.pv_net_cf())
    return out
