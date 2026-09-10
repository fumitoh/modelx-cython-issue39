
from Term_UK_A_mxg_778c82b8ac_nomx_cy cimport _mx_sys


cdef class _c_Data(_mx_sys.BaseSpace):

    cdef object _v_input_dir
    cdef bint _has_input_dir
    cdef object _v_model_point_table
    cdef bint _has_model_point_table
    cdef object _v_mort_table
    cdef bint _has_mort_table
    cdef object _v_select_factor_table
    cdef bint _has_select_factor_table
    cdef object _v_lapse_table
    cdef bint _has_lapse_table

    cdef public str model_point_file
    cdef public str mort_table_file
    cdef public str select_factor_file
    cdef public str lapse_table_file
    cdef public object pd


    cpdef _mx_copy_refs(_c_Data self, object base, object base_root)

    cdef object _f_input_dir(_c_Data self)
    cdef object _f_model_point_table(_c_Data self)
    cdef object _f_mort_table(_c_Data self)
    cdef object _f_select_factor_table(_c_Data self)
    cdef object _f_lapse_table(_c_Data self)

    cpdef object input_dir(_c_Data self)
    cpdef object model_point_table(_c_Data self)
    cpdef object mort_table(_c_Data self)
    cpdef object select_factor_table(_c_Data self)
    cpdef object lapse_table(_c_Data self)



cdef class _c_Projection(_mx_sys.BaseSpace):

    cdef object _v_model_point
    cdef bint _has_model_point
    cdef str _v_shape
    cdef bint _has_shape
    cdef bint _v_is_joint
    cdef bint _has_is_joint
    cdef long long[3] _v_age_at_entry
    cdef bint[3] _has_age_at_entry
    cdef dict _v_sex
    cdef dict _v_smoker
    cdef long long _v_policy_term
    cdef bint _has_policy_term
    cdef double _v_sum_assured
    cdef bint _has_sum_assured
    cdef double _v_fib_income
    cdef bint _has_fib_income
    cdef double _v_sched_rate
    cdef bint _has_sched_rate
    cdef bint _v_indexation
    cdef bint _has_indexation
    cdef bint _v_wop
    cdef bint _has_wop
    cdef double _v_premium_mth_pp
    cdef bint _has_premium_mth_pp
    cdef object _v_premium_mode
    cdef bint _has_premium_mode
    cdef str _v_mort_basis
    cdef bint _has_mort_basis
    cdef double _v_pols_if_init
    cdef bint _has_pols_if_init
    cdef long long _v_duration_inforce
    cdef bint _has_duration_inforce
    cdef double _v_fib_commute_rate
    cdef bint _has_fib_commute_rate
    cdef long long _v_proj_start
    cdef bint _has_proj_start
    cdef long long _v_proj_len
    cdef bint _has_proj_len
    cdef long long _v_term_mths
    cdef bint _has_term_mths
    cdef long long[26] _v_duration
    cdef bint[26] _has_duration
    cdef long long[26][3] _v_age
    cdef bint[26][3] _has_age
    cdef double[26] _v_select_factor
    cdef bint[26] _has_select_factor
    cdef double[26][3] _v_mort_rate_base
    cdef bint[26][3] _has_mort_rate_base
    cdef double[26][3] _v_mort_rate_life
    cdef bint[26][3] _has_mort_rate_life
    cdef double[26] _v_mort_rate
    cdef bint[26] _has_mort_rate
    cdef double[26] _v_lapse_cum
    cdef bint[26] _has_lapse_cum
    cdef double[26] _v_sel_lapse_factor
    cdef bint[26] _has_sel_lapse_factor
    cdef double[26] _v_lapse_rate_base
    cdef bint[26] _has_lapse_rate_base
    cdef double[26] _v_rebroke_factor
    cdef bint[26] _has_rebroke_factor
    cdef double[26] _v_lapse_rate
    cdef bint[26] _has_lapse_rate
    cdef double[26] _v_pols_if
    cdef bint[26] _has_pols_if
    cdef dict _v_pols_if_at
    cdef double[26] _v_pols_death
    cdef bint[26] _has_pols_death
    cdef double[26] _v_pols_lapse
    cdef bint[26] _has_pols_lapse
    cdef dict _v_pols_maturity
    cdef double[26] _v_wop_waived_frac
    cdef bint[26] _has_wop_waived_frac
    cdef double[26] _v_pols_payer
    cdef bint[26] _has_pols_payer
    cdef double _v_idx_increase
    cdef bint _has_idx_increase
    cdef double[26] _v_idx_factor
    cdef bint[26] _has_idx_factor
    cdef double[26] _v_idx_prem_factor
    cdef bint[26] _has_idx_prem_factor
    cdef double[26] _v_premium_pp
    cdef bint[26] _has_premium_pp
    cdef double[26] _v_premiums
    cdef bint[26] _has_premiums
    cdef double _v_sched_rate_mth
    cdef bint _has_sched_rate_mth
    cdef double[295] _v_benefit_sched
    cdef bint[295] _has_benefit_sched
    cdef double[295] _v_annuity_certain_factor
    cdef bint[295] _has_annuity_certain_factor
    cdef double[26] _v_fib_commute_pp
    cdef bint[26] _has_fib_commute_pp
    cdef double[26] _v_benefit_pp
    cdef bint[26] _has_benefit_pp
    cdef double[26] _v_fib_cum
    cdef bint[26] _has_fib_cum
    cdef dict _v_claims
    cdef double[26] _v_claim_expenses
    cdef bint[26] _has_claim_expenses
    cdef double[26] _v_inflation_factor
    cdef bint[26] _has_inflation_factor
    cdef double[26] _v_expenses
    cdef bint[26] _has_expenses
    cdef double _v_comm_init_pp
    cdef bint _has_comm_init_pp
    cdef double[26] _v_comm_clawback
    cdef bint[26] _has_comm_clawback
    cdef double[26] _v_commissions
    cdef bint[26] _has_commissions
    cdef double[26] _v_net_cf
    cdef bint[26] _has_net_cf
    cdef dict _v_check_pols_roll_fwd_resid
    cdef object _v_check_pols_roll_fwd
    cdef bint _has_check_pols_roll_fwd
    cdef dict _v_check_fib_ledger_resid
    cdef object _v_check_fib_ledger
    cdef bint _has_check_fib_ledger
    cdef object _v_result_cf
    cdef bint _has_result_cf
    cdef object _v_result_pols
    cdef bint _has_result_pols
    cdef double _v_bench_net_cf
    cdef bint _has_bench_net_cf

    cdef public _c_Data data
    cdef public long long point_id
    cdef public long long select_period
    cdef public double mort_scale
    cdef public double sel_lapse_lambda
    cdef public double sel_lapse_ref
    cdef public double premium_market_ratio
    cdef public double rebroke_cap
    cdef public double rpi_rate
    cdef public double idx_cover_cap
    cdef public double idx_prem_mult
    cdef public double idx_prem_cap
    cdef public double idx_accept_rate
    cdef public double expense_acq
    cdef public double expense_maint
    cdef public double expense_claim
    cdef public double inflation_rate
    cdef public double comm_init_rate
    cdef public double comm_renewal_rate
    cdef public long long clawback_mths
    cdef public double fib_commute_disc_rate
    cdef public double wop_inc_rate
    cdef public double wop_rec_rate
    cdef public double wop_prem_loading
    cdef public object pd


    cpdef _mx_copy_refs(_c_Projection self, object base, object base_root)

    cdef object _f_model_point(_c_Projection self)
    cdef str _f_shape(_c_Projection self)
    cdef bint _f_is_joint(_c_Projection self)
    cdef long long _f_age_at_entry(_c_Projection self, long long life=*)
    cdef str _f_sex(_c_Projection self, long long life=*)
    cdef str _f_smoker(_c_Projection self, long long life=*)
    cdef long long _f_policy_term(_c_Projection self)
    cdef double _f_sum_assured(_c_Projection self)
    cdef double _f_fib_income(_c_Projection self)
    cdef double _f_sched_rate(_c_Projection self)
    cdef bint _f_indexation(_c_Projection self)
    cdef bint _f_wop(_c_Projection self)
    cdef double _f_premium_mth_pp(_c_Projection self)
    cdef object _f_premium_mode(_c_Projection self)
    cdef str _f_mort_basis(_c_Projection self)
    cdef double _f_pols_if_init(_c_Projection self)
    cdef long long _f_duration_inforce(_c_Projection self)
    cdef double _f_fib_commute_rate(_c_Projection self)
    cdef long long _f_proj_start(_c_Projection self)
    cdef long long _f_proj_len(_c_Projection self)
    cdef long long _f_term_mths(_c_Projection self)
    cdef long long _f_duration(_c_Projection self, long long t)
    cdef long long _f_age(_c_Projection self, long long t, long long life=*)
    cdef double _f_select_factor(_c_Projection self, long long t)
    cdef double _f_mort_rate_base(_c_Projection self, long long t, long long life=*)
    cdef double _f_mort_rate_life(_c_Projection self, long long t, long long life=*)
    cdef double _f_mort_rate(_c_Projection self, long long t)
    cdef double _f_lapse_cum(_c_Projection self, long long t)
    cdef double _f_sel_lapse_factor(_c_Projection self, long long t)
    cdef double _f_lapse_rate_base(_c_Projection self, long long t)
    cdef double _f_rebroke_factor(_c_Projection self, long long t)
    cdef double _f_lapse_rate(_c_Projection self, long long t)
    cdef double _f_pols_if(_c_Projection self, long long t)
    cdef double _f_pols_if_at(_c_Projection self, long long t, str timing)
    cdef double _f_pols_death(_c_Projection self, long long t)
    cdef double _f_pols_lapse(_c_Projection self, long long t)
    cdef object _f_pols_maturity(_c_Projection self, object t)
    cdef double _f_wop_waived_frac(_c_Projection self, long long t)
    cdef double _f_pols_payer(_c_Projection self, long long t)
    cdef double _f_idx_increase(_c_Projection self)
    cdef double _f_idx_factor(_c_Projection self, long long t)
    cdef double _f_idx_prem_factor(_c_Projection self, long long t)
    cdef double _f_premium_pp(_c_Projection self, long long t)
    cdef double _f_premiums(_c_Projection self, long long t)
    cdef double _f_sched_rate_mth(_c_Projection self)
    cdef double _f_benefit_sched(_c_Projection self, long long k)
    cdef double _f_annuity_certain_factor(_c_Projection self, long long m)
    cdef double _f_fib_commute_pp(_c_Projection self, long long t)
    cdef double _f_benefit_pp(_c_Projection self, long long t)
    cdef double _f_fib_cum(_c_Projection self, long long t)
    cdef double _f_claims(_c_Projection self, long long t, object kind=*)
    cdef double _f_claim_expenses(_c_Projection self, long long t)
    cdef double _f_inflation_factor(_c_Projection self, long long t)
    cdef double _f_expenses(_c_Projection self, long long t)
    cdef double _f_comm_init_pp(_c_Projection self)
    cdef double _f_comm_clawback(_c_Projection self, long long t)
    cdef double _f_commissions(_c_Projection self, long long t)
    cdef double _f_net_cf(_c_Projection self, long long t)
    cdef object _f_check_pols_roll_fwd_resid(_c_Projection self, object t)
    cdef object _f_check_pols_roll_fwd(_c_Projection self)
    cdef object _f_check_fib_ledger_resid(_c_Projection self, object t)
    cdef object _f_check_fib_ledger(_c_Projection self)
    cdef object _f_result_cf(_c_Projection self)
    cdef object _f_result_pols(_c_Projection self)
    cdef double _f_bench_net_cf(_c_Projection self)

    cpdef object model_point(_c_Projection self)
    cpdef str shape(_c_Projection self)
    cpdef bint is_joint(_c_Projection self)
    cpdef long long age_at_entry(_c_Projection self, long long life=*)
    cpdef str sex(_c_Projection self, long long life=*)
    cpdef str smoker(_c_Projection self, long long life=*)
    cpdef long long policy_term(_c_Projection self)
    cpdef double sum_assured(_c_Projection self)
    cpdef double fib_income(_c_Projection self)
    cpdef double sched_rate(_c_Projection self)
    cpdef bint indexation(_c_Projection self)
    cpdef bint wop(_c_Projection self)
    cpdef double premium_mth_pp(_c_Projection self)
    cpdef object premium_mode(_c_Projection self)
    cpdef str mort_basis(_c_Projection self)
    cpdef double pols_if_init(_c_Projection self)
    cpdef long long duration_inforce(_c_Projection self)
    cpdef double fib_commute_rate(_c_Projection self)
    cpdef long long proj_start(_c_Projection self)
    cpdef long long proj_len(_c_Projection self)
    cpdef long long term_mths(_c_Projection self)
    cpdef long long duration(_c_Projection self, long long t)
    cpdef long long age(_c_Projection self, long long t, long long life=*)
    cpdef double select_factor(_c_Projection self, long long t)
    cpdef double mort_rate_base(_c_Projection self, long long t, long long life=*)
    cpdef double mort_rate_life(_c_Projection self, long long t, long long life=*)
    cpdef double mort_rate(_c_Projection self, long long t)
    cpdef double lapse_cum(_c_Projection self, long long t)
    cpdef double sel_lapse_factor(_c_Projection self, long long t)
    cpdef double lapse_rate_base(_c_Projection self, long long t)
    cpdef double rebroke_factor(_c_Projection self, long long t)
    cpdef double lapse_rate(_c_Projection self, long long t)
    cpdef double pols_if(_c_Projection self, long long t)
    cpdef double pols_if_at(_c_Projection self, long long t, str timing)
    cpdef double pols_death(_c_Projection self, long long t)
    cpdef double pols_lapse(_c_Projection self, long long t)
    cpdef object pols_maturity(_c_Projection self, object t)
    cpdef double wop_waived_frac(_c_Projection self, long long t)
    cpdef double pols_payer(_c_Projection self, long long t)
    cpdef double idx_increase(_c_Projection self)
    cpdef double idx_factor(_c_Projection self, long long t)
    cpdef double idx_prem_factor(_c_Projection self, long long t)
    cpdef double premium_pp(_c_Projection self, long long t)
    cpdef double premiums(_c_Projection self, long long t)
    cpdef double sched_rate_mth(_c_Projection self)
    cpdef double benefit_sched(_c_Projection self, long long k)
    cpdef double annuity_certain_factor(_c_Projection self, long long m)
    cpdef double fib_commute_pp(_c_Projection self, long long t)
    cpdef double benefit_pp(_c_Projection self, long long t)
    cpdef double fib_cum(_c_Projection self, long long t)
    cpdef double claims(_c_Projection self, long long t, object kind=*)
    cpdef double claim_expenses(_c_Projection self, long long t)
    cpdef double inflation_factor(_c_Projection self, long long t)
    cpdef double expenses(_c_Projection self, long long t)
    cpdef double comm_init_pp(_c_Projection self)
    cpdef double comm_clawback(_c_Projection self, long long t)
    cpdef double commissions(_c_Projection self, long long t)
    cpdef double net_cf(_c_Projection self, long long t)
    cpdef object check_pols_roll_fwd_resid(_c_Projection self, object t)
    cpdef object check_pols_roll_fwd(_c_Projection self)
    cpdef object check_fib_ledger_resid(_c_Projection self, object t)
    cpdef object check_fib_ledger(_c_Projection self)
    cpdef object result_cf(_c_Projection self)
    cpdef object result_pols(_c_Projection self)
    cpdef double bench_net_cf(_c_Projection self)


