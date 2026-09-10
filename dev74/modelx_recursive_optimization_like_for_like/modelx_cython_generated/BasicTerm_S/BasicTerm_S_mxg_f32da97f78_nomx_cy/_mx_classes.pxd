
from BasicTerm_S_mxg_f32da97f78_nomx_cy cimport _mx_sys


cdef class _c_Projection(_mx_sys.BaseSpace):

    cdef long long[241] _v_age
    cdef bint[241] _has_age
    cdef long long _v_age_at_entry
    cdef bint _has_age_at_entry
    cdef object _v_check_pv_net_cf
    cdef bint _has_check_pv_net_cf
    cdef long long[241] _v_claim_pp
    cdef bint[241] _has_claim_pp
    cdef double[241] _v_claims
    cdef bint[241] _has_claims
    cdef double[241] _v_commissions
    cdef bint[241] _has_commissions
    cdef object _v_disc_factors
    cdef bint _has_disc_factors
    cdef const double[:] _v_disc_rate_mth
    cdef bint _has_disc_rate_mth
    cdef long long[241] _v_duration
    cdef bint[241] _has_duration
    cdef long long _v_expense_acq
    cdef bint _has_expense_acq
    cdef long long _v_expense_maint
    cdef bint _has_expense_maint
    cdef double[241] _v_expenses
    cdef bint[241] _has_expenses
    cdef double[241] _v_inflation_factor
    cdef bint[241] _has_inflation_factor
    cdef double _v_inflation_rate
    cdef bint _has_inflation_rate
    cdef double[241] _v_lapse_rate
    cdef bint[241] _has_lapse_rate
    cdef double _v_loading_prem
    cdef bint _has_loading_prem
    cdef object _v_model_point
    cdef bint _has_model_point
    cdef double[241] _v_mort_rate
    cdef bint[241] _has_mort_rate
    cdef double[241] _v_mort_rate_mth
    cdef bint[241] _has_mort_rate_mth
    cdef dict _v_net_cf
    cdef double _v_net_premium_pp
    cdef bint _has_net_premium_pp
    cdef long long _v_policy_term
    cdef bint _has_policy_term
    cdef double[241] _v_pols_death
    cdef bint[241] _has_pols_death
    cdef double[241] _v_pols_if
    cdef bint[241] _has_pols_if
    cdef long long _v_pols_if_init
    cdef bint _has_pols_if_init
    cdef double[241] _v_pols_lapse
    cdef bint[241] _has_pols_lapse
    cdef double[241] _v_pols_maturity
    cdef bint[241] _has_pols_maturity
    cdef double _v_premium_pp
    cdef bint _has_premium_pp
    cdef double[241] _v_premiums
    cdef bint[241] _has_premiums
    cdef long long _v_proj_len
    cdef bint _has_proj_len
    cdef double _v_pv_claims
    cdef bint _has_pv_claims
    cdef double _v_pv_commissions
    cdef bint _has_pv_commissions
    cdef double _v_pv_expenses
    cdef bint _has_pv_expenses
    cdef double _v_pv_net_cf
    cdef bint _has_pv_net_cf
    cdef double _v_pv_pols_if
    cdef bint _has_pv_pols_if
    cdef double _v_pv_premiums
    cdef bint _has_pv_premiums
    cdef object _v_result_cf
    cdef bint _has_result_cf
    cdef object _v_result_pv
    cdef bint _has_result_pv
    cdef object _v_sex
    cdef bint _has_sex
    cdef long long _v_sum_assured
    cdef bint _has_sum_assured

    cdef public object disc_rate_ann
    cdef public object model_point_table
    cdef public object mort_table
    cdef public object pd
    cdef public long long point_id
    cdef public object np


    cpdef _mx_copy_refs(_c_Projection self, object base, object base_root)

    cdef long long _f_age(_c_Projection self, long long t)
    cdef long long _f_age_at_entry(_c_Projection self)
    cdef object _f_check_pv_net_cf(_c_Projection self)
    cdef long long _f_claim_pp(_c_Projection self, long long t)
    cdef double _f_claims(_c_Projection self, long long t)
    cdef double _f_commissions(_c_Projection self, long long t)
    cdef object _f_disc_factors(_c_Projection self)
    cdef const double[:] _f_disc_rate_mth(_c_Projection self)
    cdef long long _f_duration(_c_Projection self, long long t)
    cdef long long _f_expense_acq(_c_Projection self)
    cdef long long _f_expense_maint(_c_Projection self)
    cdef double _f_expenses(_c_Projection self, long long t)
    cdef double _f_inflation_factor(_c_Projection self, long long t)
    cdef double _f_inflation_rate(_c_Projection self)
    cdef double _f_lapse_rate(_c_Projection self, long long t)
    cdef double _f_loading_prem(_c_Projection self)
    cdef object _f_model_point(_c_Projection self)
    cdef double _f_mort_rate(_c_Projection self, long long t)
    cdef double _f_mort_rate_mth(_c_Projection self, long long t)
    cdef object _f_net_cf(_c_Projection self, object t)
    cdef double _f_net_premium_pp(_c_Projection self)
    cdef long long _f_policy_term(_c_Projection self)
    cdef double _f_pols_death(_c_Projection self, long long t)
    cdef double _f_pols_if(_c_Projection self, long long t)
    cdef long long _f_pols_if_init(_c_Projection self)
    cdef double _f_pols_lapse(_c_Projection self, long long t)
    cdef double _f_pols_maturity(_c_Projection self, long long t)
    cdef double _f_premium_pp(_c_Projection self)
    cdef double _f_premiums(_c_Projection self, long long t)
    cdef long long _f_proj_len(_c_Projection self)
    cdef double _f_pv_claims(_c_Projection self)
    cdef double _f_pv_commissions(_c_Projection self)
    cdef double _f_pv_expenses(_c_Projection self)
    cdef double _f_pv_net_cf(_c_Projection self)
    cdef double _f_pv_pols_if(_c_Projection self)
    cdef double _f_pv_premiums(_c_Projection self)
    cdef object _f_result_cf(_c_Projection self)
    cdef object _f_result_pv(_c_Projection self)
    cdef object _f_sex(_c_Projection self)
    cdef long long _f_sum_assured(_c_Projection self)

    cpdef long long age(_c_Projection self, long long t)
    cpdef long long age_at_entry(_c_Projection self)
    cpdef object check_pv_net_cf(_c_Projection self)
    cpdef long long claim_pp(_c_Projection self, long long t)
    cpdef double claims(_c_Projection self, long long t)
    cpdef double commissions(_c_Projection self, long long t)
    cpdef object disc_factors(_c_Projection self)
    cpdef const double[:] disc_rate_mth(_c_Projection self)
    cpdef long long duration(_c_Projection self, long long t)
    cpdef long long expense_acq(_c_Projection self)
    cpdef long long expense_maint(_c_Projection self)
    cpdef double expenses(_c_Projection self, long long t)
    cpdef double inflation_factor(_c_Projection self, long long t)
    cpdef double inflation_rate(_c_Projection self)
    cpdef double lapse_rate(_c_Projection self, long long t)
    cpdef double loading_prem(_c_Projection self)
    cpdef object model_point(_c_Projection self)
    cpdef double mort_rate(_c_Projection self, long long t)
    cpdef double mort_rate_mth(_c_Projection self, long long t)
    cpdef object net_cf(_c_Projection self, object t)
    cpdef double net_premium_pp(_c_Projection self)
    cpdef long long policy_term(_c_Projection self)
    cpdef double pols_death(_c_Projection self, long long t)
    cpdef double pols_if(_c_Projection self, long long t)
    cpdef long long pols_if_init(_c_Projection self)
    cpdef double pols_lapse(_c_Projection self, long long t)
    cpdef double pols_maturity(_c_Projection self, long long t)
    cpdef double premium_pp(_c_Projection self)
    cpdef double premiums(_c_Projection self, long long t)
    cpdef long long proj_len(_c_Projection self)
    cpdef double pv_claims(_c_Projection self)
    cpdef double pv_commissions(_c_Projection self)
    cpdef double pv_expenses(_c_Projection self)
    cpdef double pv_net_cf(_c_Projection self)
    cpdef double pv_pols_if(_c_Projection self)
    cpdef double pv_premiums(_c_Projection self)
    cpdef object result_cf(_c_Projection self)
    cpdef object result_pv(_c_Projection self)
    cpdef object sex(_c_Projection self)
    cpdef long long sum_assured(_c_Projection self)


