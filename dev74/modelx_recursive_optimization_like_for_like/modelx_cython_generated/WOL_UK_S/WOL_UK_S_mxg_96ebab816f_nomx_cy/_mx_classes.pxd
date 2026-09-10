
from WOL_UK_S_mxg_96ebab816f_nomx_cy cimport _mx_sys


cdef class _c_Data(_mx_sys.BaseSpace):

    cdef object _v_input_dir
    cdef bint _has_input_dir
    cdef object _v_model_point_table
    cdef bint _has_model_point_table
    cdef object _v_mort_table
    cdef bint _has_mort_table
    cdef object _v_lapse_table
    cdef bint _has_lapse_table

    cdef public str model_point_file
    cdef public str mort_table_file
    cdef public str lapse_table_file
    cdef public object pd


    cpdef _mx_copy_refs(_c_Data self, object base, object base_root)

    cdef object _f_input_dir(_c_Data self)
    cdef object _f_model_point_table(_c_Data self)
    cdef object _f_mort_table(_c_Data self)
    cdef object _f_lapse_table(_c_Data self)

    cpdef object input_dir(_c_Data self)
    cpdef object model_point_table(_c_Data self)
    cpdef object mort_table(_c_Data self)
    cpdef object lapse_table(_c_Data self)



cdef class _c_Projection(_mx_sys.BaseSpace):

    cdef object _v_model_point
    cdef bint _has_model_point
    cdef str _v_cell
    cdef bint _has_cell
    cdef long long _v_age_at_entry
    cdef bint _has_age_at_entry
    cdef str _v_sex
    cdef bint _has_sex
    cdef str _v_smoker
    cdef bint _has_smoker
    cdef double _v_sum_assured
    cdef bint _has_sum_assured
    cdef double _v_premium_mth
    cdef bint _has_premium_mth
    cdef str _v_escalation
    cdef bint _has_escalation
    cdef long long _v_cessation_mths
    cdef bint _has_cessation_mths
    cdef long long _v_moratorium_mths
    cdef bint _has_moratorium_mths
    cdef double _v_adb_multiplier
    cdef bint _has_adb_multiplier
    cdef bint _v_pu_variant
    cdef bint _has_pu_variant
    cdef double _v_pols_if_init
    cdef bint _has_pols_if_init
    cdef long long _v_proj_len
    cdef bint _has_proj_len
    cdef long long[961] _v_duration
    cdef bint[961] _has_duration
    cdef dict _v_duration_mth
    cdef long long[961] _v_policy_year
    cdef bint[961] _has_policy_year
    cdef long long[961] _v_age
    cdef bint[961] _has_age
    cdef str _v_mort_basis
    cdef bint _has_mort_basis
    cdef double _v_mort_loading
    cdef bint _has_mort_loading
    cdef double[961] _v_mort_improve_factor
    cdef bint[961] _has_mort_improve_factor
    cdef double[961] _v_mort_rate
    cdef bint[961] _has_mort_rate
    cdef double[961] _v_mort_rate_mth
    cdef bint[961] _has_mort_rate_mth
    cdef double _v_esc_cover_step
    cdef bint _has_esc_cover_step
    cdef double _v_esc_prem_step
    cdef bint _has_esc_prem_step
    cdef double[961] _v_cover_pp
    cdef bint[961] _has_cover_pp
    cdef double[961] _v_premium_pp
    cdef bint[961] _has_premium_pp
    cdef double[961] _v_prem_cum_pp
    cdef bint[961] _has_prem_cum_pp
    cdef bint[961] _v_in_moratorium
    cdef bint[961] _has_in_moratorium
    cdef long long[961] _v_payments_made
    cdef bint[961] _has_payments_made
    cdef long long _v_payments_expected
    cdef bint _has_payments_expected
    cdef bint[961] _v_pu_eligible
    cdef bint[961] _has_pu_eligible
    cdef object _v_crossover_mth
    cdef bint _has_crossover_mth
    cdef double[961] _v_lapse_rate_base
    cdef bint[961] _has_lapse_rate_base
    cdef double[961] _v_lapse_rate
    cdef bint[961] _has_lapse_rate
    cdef double[961] _v_lapse_rate_mth
    cdef bint[961] _has_lapse_rate_mth
    cdef double[961] _v_pols_if
    cdef bint[961] _has_pols_if
    cdef double[961] _v_pols_pu
    cdef bint[961] _has_pols_pu
    cdef double[961] _v_pu_benefit
    cdef bint[961] _has_pu_benefit
    cdef double[961] _v_pols_all
    cdef bint[961] _has_pols_all
    cdef dict _v_pols_if_at
    cdef double[961] _v_pols_death
    cdef bint[961] _has_pols_death
    cdef dict _v_pols_death_pu
    cdef double[961] _v_pols_exit
    cdef bint[961] _has_pols_exit
    cdef double[961] _v_pols_convert
    cdef bint[961] _has_pols_convert
    cdef dict _v_pols_lapse
    cdef dict _v_pols_maturity
    cdef dict _v_benefit_pp
    cdef double[961] _v_premiums
    cdef bint[961] _has_premiums
    cdef dict _v_claims
    cdef double _v_expense_acq_pp
    cdef bint _has_expense_acq_pp
    cdef double _v_expense_maint_pp
    cdef bint _has_expense_maint_pp
    cdef double[961] _v_inflation_factor
    cdef bint[961] _has_inflation_factor
    cdef double[961] _v_expenses
    cdef bint[961] _has_expenses
    cdef double[961] _v_commissions
    cdef bint[961] _has_commissions
    cdef double[961] _v_net_cf
    cdef bint[961] _has_net_cf
    cdef dict _v_check_pols_roll_fwd_resid
    cdef object _v_check_pols_roll_fwd
    cdef bint _has_check_pols_roll_fwd
    cdef object _v_check_truncation
    cdef bint _has_check_truncation
    cdef object _v_result_cf
    cdef bint _has_result_cf
    cdef object _v_result_pols
    cdef bint _has_result_pols
    cdef double _v_bench_net_cf
    cdef bint _has_bench_net_cf

    cdef public _c_Data data
    cdef public long long point_id
    cdef public long long omega_age
    cdef public double mort_loading_o50
    cdef public double mort_loading_uw
    cdef public double mort_improvement
    cdef public double acc_share
    cdef public double suicide_share
    cdef public long long suicide_mths
    cdef public double rpi_rate
    cdef public double esc_fixed_cover
    cdef public double esc_fixed_prem
    cdef public double esc_rpi_cover_cap
    cdef public double esc_rpi_prem_mult
    cdef public double esc_rpi_prem_cap
    cdef public double esc_take_up
    cdef public double lapse_crossover_beta
    cdef public double expense_acq_o50
    cdef public double expense_acq_uw
    cdef public double expense_maint_o50
    cdef public double expense_maint_uw
    cdef public double inflation_rate
    cdef public double comm_init_rate
    cdef public object pd


    cpdef _mx_copy_refs(_c_Projection self, object base, object base_root)

    cdef object _f_model_point(_c_Projection self)
    cdef str _f_cell(_c_Projection self)
    cdef long long _f_age_at_entry(_c_Projection self)
    cdef str _f_sex(_c_Projection self)
    cdef str _f_smoker(_c_Projection self)
    cdef double _f_sum_assured(_c_Projection self)
    cdef double _f_premium_mth(_c_Projection self)
    cdef str _f_escalation(_c_Projection self)
    cdef long long _f_cessation_mths(_c_Projection self)
    cdef long long _f_moratorium_mths(_c_Projection self)
    cdef double _f_adb_multiplier(_c_Projection self)
    cdef bint _f_pu_variant(_c_Projection self)
    cdef double _f_pols_if_init(_c_Projection self)
    cdef long long _f_proj_len(_c_Projection self)
    cdef long long _f_duration(_c_Projection self, long long t)
    cdef object _f_duration_mth(_c_Projection self, object t)
    cdef long long _f_policy_year(_c_Projection self, long long t)
    cdef long long _f_age(_c_Projection self, long long t)
    cdef str _f_mort_basis(_c_Projection self)
    cdef double _f_mort_loading(_c_Projection self)
    cdef double _f_mort_improve_factor(_c_Projection self, long long t)
    cdef double _f_mort_rate(_c_Projection self, long long t)
    cdef double _f_mort_rate_mth(_c_Projection self, long long t)
    cdef double _f_esc_cover_step(_c_Projection self)
    cdef double _f_esc_prem_step(_c_Projection self)
    cdef double _f_cover_pp(_c_Projection self, long long t)
    cdef double _f_premium_pp(_c_Projection self, long long t)
    cdef double _f_prem_cum_pp(_c_Projection self, long long t)
    cdef bint _f_in_moratorium(_c_Projection self, long long t)
    cdef long long _f_payments_made(_c_Projection self, long long t)
    cdef long long _f_payments_expected(_c_Projection self)
    cdef bint _f_pu_eligible(_c_Projection self, long long t)
    cdef object _f_crossover_mth(_c_Projection self)
    cdef double _f_lapse_rate_base(_c_Projection self, long long t)
    cdef double _f_lapse_rate(_c_Projection self, long long t)
    cdef double _f_lapse_rate_mth(_c_Projection self, long long t)
    cdef double _f_pols_if(_c_Projection self, long long t)
    cdef double _f_pols_pu(_c_Projection self, long long t)
    cdef double _f_pu_benefit(_c_Projection self, long long t)
    cdef double _f_pols_all(_c_Projection self, long long t)
    cdef double _f_pols_if_at(_c_Projection self, long long t, str timing)
    cdef double _f_pols_death(_c_Projection self, long long t)
    cdef object _f_pols_death_pu(_c_Projection self, object t)
    cdef double _f_pols_exit(_c_Projection self, long long t)
    cdef double _f_pols_convert(_c_Projection self, long long t)
    cdef object _f_pols_lapse(_c_Projection self, object t)
    cdef object _f_pols_maturity(_c_Projection self, object t)
    cdef double _f_benefit_pp(_c_Projection self, long long t, str kind)
    cdef double _f_premiums(_c_Projection self, long long t)
    cdef double _f_claims(_c_Projection self, long long t, object kind=*)
    cdef double _f_expense_acq_pp(_c_Projection self)
    cdef double _f_expense_maint_pp(_c_Projection self)
    cdef double _f_inflation_factor(_c_Projection self, long long t)
    cdef double _f_expenses(_c_Projection self, long long t)
    cdef double _f_commissions(_c_Projection self, long long t)
    cdef double _f_net_cf(_c_Projection self, long long t)
    cdef object _f_check_pols_roll_fwd_resid(_c_Projection self, object t)
    cdef object _f_check_pols_roll_fwd(_c_Projection self)
    cdef object _f_check_truncation(_c_Projection self)
    cdef object _f_result_cf(_c_Projection self)
    cdef object _f_result_pols(_c_Projection self)
    cdef double _f_bench_net_cf(_c_Projection self)

    cpdef object model_point(_c_Projection self)
    cpdef str cell(_c_Projection self)
    cpdef long long age_at_entry(_c_Projection self)
    cpdef str sex(_c_Projection self)
    cpdef str smoker(_c_Projection self)
    cpdef double sum_assured(_c_Projection self)
    cpdef double premium_mth(_c_Projection self)
    cpdef str escalation(_c_Projection self)
    cpdef long long cessation_mths(_c_Projection self)
    cpdef long long moratorium_mths(_c_Projection self)
    cpdef double adb_multiplier(_c_Projection self)
    cpdef bint pu_variant(_c_Projection self)
    cpdef double pols_if_init(_c_Projection self)
    cpdef long long proj_len(_c_Projection self)
    cpdef long long duration(_c_Projection self, long long t)
    cpdef object duration_mth(_c_Projection self, object t)
    cpdef long long policy_year(_c_Projection self, long long t)
    cpdef long long age(_c_Projection self, long long t)
    cpdef str mort_basis(_c_Projection self)
    cpdef double mort_loading(_c_Projection self)
    cpdef double mort_improve_factor(_c_Projection self, long long t)
    cpdef double mort_rate(_c_Projection self, long long t)
    cpdef double mort_rate_mth(_c_Projection self, long long t)
    cpdef double esc_cover_step(_c_Projection self)
    cpdef double esc_prem_step(_c_Projection self)
    cpdef double cover_pp(_c_Projection self, long long t)
    cpdef double premium_pp(_c_Projection self, long long t)
    cpdef double prem_cum_pp(_c_Projection self, long long t)
    cpdef bint in_moratorium(_c_Projection self, long long t)
    cpdef long long payments_made(_c_Projection self, long long t)
    cpdef long long payments_expected(_c_Projection self)
    cpdef bint pu_eligible(_c_Projection self, long long t)
    cpdef object crossover_mth(_c_Projection self)
    cpdef double lapse_rate_base(_c_Projection self, long long t)
    cpdef double lapse_rate(_c_Projection self, long long t)
    cpdef double lapse_rate_mth(_c_Projection self, long long t)
    cpdef double pols_if(_c_Projection self, long long t)
    cpdef double pols_pu(_c_Projection self, long long t)
    cpdef double pu_benefit(_c_Projection self, long long t)
    cpdef double pols_all(_c_Projection self, long long t)
    cpdef double pols_if_at(_c_Projection self, long long t, str timing)
    cpdef double pols_death(_c_Projection self, long long t)
    cpdef object pols_death_pu(_c_Projection self, object t)
    cpdef double pols_exit(_c_Projection self, long long t)
    cpdef double pols_convert(_c_Projection self, long long t)
    cpdef object pols_lapse(_c_Projection self, object t)
    cpdef object pols_maturity(_c_Projection self, object t)
    cpdef double benefit_pp(_c_Projection self, long long t, str kind)
    cpdef double premiums(_c_Projection self, long long t)
    cpdef double claims(_c_Projection self, long long t, object kind=*)
    cpdef double expense_acq_pp(_c_Projection self)
    cpdef double expense_maint_pp(_c_Projection self)
    cpdef double inflation_factor(_c_Projection self, long long t)
    cpdef double expenses(_c_Projection self, long long t)
    cpdef double commissions(_c_Projection self, long long t)
    cpdef double net_cf(_c_Projection self, long long t)
    cpdef object check_pols_roll_fwd_resid(_c_Projection self, object t)
    cpdef object check_pols_roll_fwd(_c_Projection self)
    cpdef object check_truncation(_c_Projection self)
    cpdef object result_cf(_c_Projection self)
    cpdef object result_pols(_c_Projection self)
    cpdef double bench_net_cf(_c_Projection self)


