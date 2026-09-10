
from ULSG_US_S_mxg_82773408d0_nomx_cy cimport _mx_sys


cdef class _c_Data(_mx_sys.BaseSpace):

    cdef object _v_input_dir
    cdef bint _has_input_dir
    cdef object _v_model_point_table
    cdef bint _has_model_point_table
    cdef object _v_coi_rates
    cdef bint _has_coi_rates
    cdef object _v_corridor_factors
    cdef bint _has_corridor_factors
    cdef object _v_mort_table
    cdef bint _has_mort_table
    cdef object _v_class_factor_table
    cdef bint _has_class_factor_table
    cdef object _v_lapse_table
    cdef bint _has_lapse_table
    cdef object _v_surr_charge_table
    cdef bint _has_surr_charge_table
    cdef object _v_rop_table
    cdef bint _has_rop_table

    cdef public str model_point_file
    cdef public str coi_rates_file
    cdef public str corridor_file
    cdef public str mort_table_file
    cdef public str class_factor_file
    cdef public str lapse_table_file
    cdef public str surr_charge_file
    cdef public str rop_file
    cdef public object pd


    cpdef _mx_copy_refs(_c_Data self, object base, object base_root)

    cdef object _f_input_dir(_c_Data self)
    cdef object _f_model_point_table(_c_Data self)
    cdef object _f_coi_rates(_c_Data self)
    cdef object _f_corridor_factors(_c_Data self)
    cdef object _f_mort_table(_c_Data self)
    cdef object _f_class_factor_table(_c_Data self)
    cdef object _f_lapse_table(_c_Data self)
    cdef object _f_surr_charge_table(_c_Data self)
    cdef object _f_rop_table(_c_Data self)

    cpdef object input_dir(_c_Data self)
    cpdef object model_point_table(_c_Data self)
    cpdef object coi_rates(_c_Data self)
    cpdef object corridor_factors(_c_Data self)
    cpdef object mort_table(_c_Data self)
    cpdef object class_factor_table(_c_Data self)
    cpdef object lapse_table(_c_Data self)
    cpdef object surr_charge_table(_c_Data self)
    cpdef object rop_table(_c_Data self)



cdef class _c_Projection(_mx_sys.BaseSpace):

    cdef object _v_model_point
    cdef bint _has_model_point
    cdef long long _v_age_at_entry
    cdef bint _has_age_at_entry
    cdef str _v_sex
    cdef bint _has_sex
    cdef str _v_rate_class
    cdef bint _has_rate_class
    cdef double _v_sum_assured
    cdef bint _has_sum_assured
    cdef long long _v_guarantee_age
    cdef bint _has_guarantee_age
    cdef str _v_premium_type
    cdef bint _has_premium_type
    cdef str _v_premium_mode
    cdef bint _has_premium_mode
    cdef double _v_premium_pp_ann
    cdef bint _has_premium_pp_ann
    cdef double _v_load_prem_rate
    cdef bint _has_load_prem_rate
    cdef double _v_av_pp_init
    cdef bint _has_av_pp_init
    cdef double _v_sg_pp_init
    cdef bint _has_sg_pp_init
    cdef double _v_loan_bal_init
    cdef bint _has_loan_bal_init
    cdef double _v_cum_prem_init
    cdef bint _has_cum_prem_init
    cdef double _v_pols_if_init
    cdef bint _has_pols_if_init
    cdef long long _v_duration_mth_init
    cdef bint _has_duration_mth_init
    cdef bint _v_has_surr_charge
    cdef bint _has_has_surr_charge
    cdef str _v_surr_charge_id
    cdef bint _has_surr_charge_id
    cdef bint _v_rop_elected
    cdef bint _has_rop_elected
    cdef long long _v_coi_rate_dp
    cdef bint _has_coi_rate_dp
    cdef long long[733] _v_duration_mth
    cdef bint[733] _has_duration_mth
    cdef long long[733] _v_duration
    cdef bint[733] _has_duration
    cdef long long[733] _v_policy_year
    cdef bint[733] _has_policy_year
    cdef long long[733] _v_age
    cdef bint[733] _has_age
    cdef long long _v_proj_len
    cdef bint _has_proj_len
    cdef double[733] _v_sum_assured_at
    cdef bint[733] _has_sum_assured_at
    cdef double[733] _v_units
    cdef bint[733] _has_units
    cdef double[733] _v_crediting_rate_ann
    cdef bint[733] _has_crediting_rate_ann
    cdef double[733] _v_inv_return_mth
    cdef bint[733] _has_inv_return_mth
    cdef double _v_guar_rate_mth
    cdef bint _has_guar_rate_mth
    cdef double _v_sg_rate_mth
    cdef bint _has_sg_rate_mth
    cdef double _v_naar_factor
    cdef bint _has_naar_factor
    cdef double _v_sg_naar_factor
    cdef bint _has_sg_naar_factor
    cdef double _v_loan_rate_mth
    cdef bint _has_loan_rate_mth
    cdef double _v_loan_cr_rate_mth
    cdef bint _has_loan_cr_rate_mth
    cdef long long _v_premium_freq
    cdef bint _has_premium_freq
    cdef bint[733] _v_is_premium_mth
    cdef bint[733] _has_is_premium_mth
    cdef double[733] _v_prem_persistency
    cdef bint[733] _has_prem_persistency
    cdef double[733] _v_premium_pp
    cdef bint[733] _has_premium_pp
    cdef double[733] _v_prem_to_av_pp
    cdef bint[733] _has_prem_to_av_pp
    cdef double[733] _v_prem_to_sg_pp
    cdef bint[733] _has_prem_to_sg_pp
    cdef dict _v_prem_to_av
    cdef double[733] _v_premiums
    cdef bint[733] _has_premiums
    cdef double[733] _v_cum_prem_pp
    cdef bint[733] _has_cum_prem_pp
    cdef double[733] _v_wd_pp
    cdef bint[733] _has_wd_pp
    cdef double[733] _v_wd_fee_pp
    cdef bint[733] _has_wd_fee_pp
    cdef dict _v_wd_fees
    cdef double[733] _v_corridor_factor
    cdef bint[733] _has_corridor_factor
    cdef double[733] _v_db_pp
    cdef bint[733] _has_db_pp
    cdef double[733] _v_net_amt_at_risk
    cdef bint[733] _has_net_amt_at_risk
    cdef double[733] _v_sg_net_amt_at_risk
    cdef bint[733] _has_sg_net_amt_at_risk
    cdef object _v_coi_rate_scale
    cdef bint _has_coi_rate_scale
    cdef double[733] _v_coi_rate_guar
    cdef bint[733] _has_coi_rate_guar
    cdef double[733] _v_coi_rate
    cdef bint[733] _has_coi_rate
    cdef double[733] _v_sg_coi_rate
    cdef bint[733] _has_sg_coi_rate
    cdef double[733] _v_coi_pp
    cdef bint[733] _has_coi_pp
    cdef double[733] _v_sg_coi_pp
    cdef bint[733] _has_sg_coi_pp
    cdef double[733] _v_rider_charge_pp
    cdef bint[733] _has_rider_charge_pp
    cdef double[733] _v_maint_fee_pp
    cdef bint[733] _has_maint_fee_pp
    cdef double[733] _v_sg_maint_fee_pp
    cdef bint[733] _has_sg_maint_fee_pp
    cdef dict _v_mth_deduction_pp
    cdef dict _v_sg_deduction_pp
    cdef dict _v_maint_fee_taken_pp
    cdef dict _v_coi_taken_pp
    cdef dict _v_mth_deduction_taken_pp
    cdef dict _v_mth_deduction_forgone_pp
    cdef dict _v_maint_fee
    cdef dict _v_coi
    cdef dict _v_mth_deduction
    cdef dict _v_mth_deduction_forgone
    cdef dict _v_av_pp_at
    cdef double[733] _v_inv_income_pp
    cdef bint[733] _has_inv_income_pp
    cdef double[733] _v_av_pp
    cdef bint[733] _has_av_pp
    cdef dict _v_av_at
    cdef dict _v_inv_income
    cdef dict _v_av_change
    cdef double[733] _v_loan_bal_pp
    cdef bint[733] _has_loan_bal_pp
    cdef dict _v_sg_pp_at
    cdef double[733] _v_sg_inv_income_pp
    cdef bint[733] _has_sg_inv_income_pp
    cdef double[733] _v_sg_pp
    cdef bint[733] _has_sg_pp
    cdef double[733] _v_sg_net_pp
    cdef bint[733] _has_sg_net_pp
    cdef bint[733] _v_is_guar_active
    cdef bint[733] _has_is_guar_active
    cdef bint[733] _v_is_guar_supported
    cdef bint[733] _has_is_guar_supported
    cdef dict _v_catch_up_prem_pp
    cdef double[733] _v_surr_charge_rate
    cdef bint[733] _has_surr_charge_rate
    cdef double[733] _v_surr_charge_pp
    cdef bint[733] _has_surr_charge_pp
    cdef double[733] _v_csv_pp
    cdef bint[733] _has_csv_pp
    cdef double[733] _v_ncsv_pp
    cdef bint[733] _has_ncsv_pp
    cdef dict _v_surr_charge
    cdef bint[733] _v_is_shortfall
    cdef bint[733] _has_is_shortfall
    cdef dict _v_cure_premium_pp
    cdef long long[733] _v_grace_mth
    cdef bint[733] _has_grace_mth
    cdef bint[733] _v_is_lapsed
    cdef bint[733] _has_is_lapsed
    cdef dict _v_status
    cdef long long[733] _v_rop_anniversary
    cdef bint[733] _has_rop_anniversary
    cdef double[733] _v_rop_ratio
    cdef bint[733] _has_rop_ratio
    cdef double[733] _v_rop_rate
    cdef bint[733] _has_rop_rate
    cdef double _v_class_factor
    cdef bint _has_class_factor
    cdef double[733] _v_mort_improve_rate
    cdef bint[733] _has_mort_improve_rate
    cdef double[733] _v_mort_improve_factor
    cdef bint[733] _has_mort_improve_factor
    cdef double[733] _v_mort_rate
    cdef bint[733] _has_mort_rate
    cdef double[733] _v_mort_rate_mth
    cdef bint[733] _has_mort_rate_mth
    cdef double[733] _v_lapse_rate_base
    cdef bint[733] _has_lapse_rate_base
    cdef double _v_lapse_rate_guar_mult
    cdef bint _has_lapse_rate_guar_mult
    cdef double _v_lapse_rate_pattern_mult
    cdef bint _has_lapse_rate_pattern_mult
    cdef double[733] _v_lapse_rate_dyn_mult
    cdef bint[733] _has_lapse_rate_dyn_mult
    cdef double[733] _v_lapse_rate
    cdef bint[733] _has_lapse_rate
    cdef double[733] _v_lapse_rate_mth
    cdef bint[733] _has_lapse_rate_mth
    cdef double[733] _v_pols_if
    cdef bint[733] _has_pols_if
    cdef dict _v_pols_if_at
    cdef double[733] _v_pols_death
    cdef bint[733] _has_pols_death
    cdef double[733] _v_pols_lapse
    cdef bint[733] _has_pols_lapse
    cdef double[733] _v_pols_rop
    cdef bint[733] _has_pols_rop
    cdef double[733] _v_pols_lapse_grace
    cdef bint[733] _has_pols_lapse_grace
    cdef dict _v_pols_maturity
    cdef dict _v_claim_pp
    cdef dict _v_claims_from_av
    cdef dict _v_claims_over_av
    cdef dict _v_claims
    cdef double[733] _v_withdrawals
    cdef bint[733] _has_withdrawals
    cdef double[733] _v_inflation_factor
    cdef bint[733] _has_inflation_factor
    cdef double[733] _v_expenses
    cdef bint[733] _has_expenses
    cdef double[733] _v_premium_taxes
    cdef bint[733] _has_premium_taxes
    cdef dict _v_margin_expense
    cdef dict _v_margin_mortality
    cdef dict _v_margin_rop
    cdef double[733] _v_net_cf
    cdef bint[733] _has_net_cf
    cdef object _v_solve_len
    cdef bint _has_solve_len
    cdef dict _v_sg_pp_solve
    cdef dict _v_guar_min_sg
    cdef object _v_no_lapse_premium
    cdef bint _has_no_lapse_premium
    cdef object _v_check_av_roll_fwd
    cdef bint _has_check_av_roll_fwd
    cdef object _v_check_sg_roll_fwd
    cdef bint _has_check_sg_roll_fwd
    cdef object _v_check_margin
    cdef bint _has_check_margin
    cdef object _v_result_cf
    cdef bint _has_result_cf
    cdef object _v_result_pols
    cdef bint _has_result_pols
    cdef object _v_result_av
    cdef bint _has_result_av
    cdef object _v_result_guar
    cdef bint _has_result_guar
    cdef double _v_bench_net_cf
    cdef bint _has_bench_net_cf

    cdef public _c_Data data
    cdef public long long point_id
    cdef public long long charges_cease_age
    cdef public long long lifetime_guarantee_age
    cdef public double guar_rate_ann
    cdef public double crediting_rate_curr
    cdef public double sg_rate_ann
    cdef public double coi_curr_factor
    cdef public double coi_sg_factor
    cdef public double load_prem_rate_sg
    cdef public double expense_pol_mth
    cdef public double expense_unit_mth
    cdef public double expense_unit_mth_sg
    cdef public double loan_rate_ann
    cdef public double loan_cr_rate_ann
    cdef public double wd_fee
    cdef public long long wd_first_year
    cdef public long long ten_pay_years
    cdef public double prem_persistency_ann
    cdef public long long grace_months
    cdef public double rop_cap_rate
    cdef public double mort_ae_factor
    cdef public double mort_improve_rate_init
    cdef public long long mort_improve_full_age
    cdef public long long mort_improve_end_age
    cdef public long long mort_improve_max_years
    cdef public double lapse_guar_mult
    cdef public double lapse_pattern_mult_single
    cdef public double lapse_pattern_mult_ten_pay
    cdef public double lapse_dyn_mult_guar_only
    cdef public double lapse_dyn_mult_guar_failed
    cdef public double lapse_rate_floor
    cdef public double lapse_rate_cap
    cdef public double expense_acq
    cdef public double expense_acq_prem_rate
    cdef public double expense_maint
    cdef public double expense_claim
    cdef public double inflation_rate
    cdef public double premium_tax_rate
    cdef public double solve_tol
    cdef public long long solve_max_doublings
    cdef public object pd
    cdef public object math


    cpdef _mx_copy_refs(_c_Projection self, object base, object base_root)

    cdef object _f_model_point(_c_Projection self)
    cdef long long _f_age_at_entry(_c_Projection self)
    cdef str _f_sex(_c_Projection self)
    cdef str _f_rate_class(_c_Projection self)
    cdef double _f_sum_assured(_c_Projection self)
    cdef long long _f_guarantee_age(_c_Projection self)
    cdef str _f_premium_type(_c_Projection self)
    cdef str _f_premium_mode(_c_Projection self)
    cdef double _f_premium_pp_ann(_c_Projection self)
    cdef double _f_load_prem_rate(_c_Projection self)
    cdef double _f_av_pp_init(_c_Projection self)
    cdef double _f_sg_pp_init(_c_Projection self)
    cdef double _f_loan_bal_init(_c_Projection self)
    cdef double _f_cum_prem_init(_c_Projection self)
    cdef double _f_pols_if_init(_c_Projection self)
    cdef long long _f_duration_mth_init(_c_Projection self)
    cdef bint _f_has_surr_charge(_c_Projection self)
    cdef str _f_surr_charge_id(_c_Projection self)
    cdef bint _f_rop_elected(_c_Projection self)
    cdef long long _f_coi_rate_dp(_c_Projection self)
    cdef long long _f_duration_mth(_c_Projection self, long long t)
    cdef long long _f_duration(_c_Projection self, long long t)
    cdef long long _f_policy_year(_c_Projection self, long long t)
    cdef long long _f_age(_c_Projection self, long long t)
    cdef long long _f_proj_len(_c_Projection self)
    cdef double _f_sum_assured_at(_c_Projection self, long long t)
    cdef double _f_units(_c_Projection self, long long t)
    cdef double _f_crediting_rate_ann(_c_Projection self, long long t)
    cdef double _f_inv_return_mth(_c_Projection self, long long t)
    cdef double _f_guar_rate_mth(_c_Projection self)
    cdef double _f_sg_rate_mth(_c_Projection self)
    cdef double _f_naar_factor(_c_Projection self)
    cdef double _f_sg_naar_factor(_c_Projection self)
    cdef double _f_loan_rate_mth(_c_Projection self)
    cdef double _f_loan_cr_rate_mth(_c_Projection self)
    cdef long long _f_premium_freq(_c_Projection self)
    cdef bint _f_is_premium_mth(_c_Projection self, long long t)
    cdef double _f_prem_persistency(_c_Projection self, long long t)
    cdef double _f_premium_pp(_c_Projection self, long long t)
    cdef double _f_prem_to_av_pp(_c_Projection self, long long t)
    cdef double _f_prem_to_sg_pp(_c_Projection self, long long t)
    cdef object _f_prem_to_av(_c_Projection self, object t)
    cdef double _f_premiums(_c_Projection self, long long t)
    cdef double _f_cum_prem_pp(_c_Projection self, long long t)
    cdef double _f_wd_pp(_c_Projection self, long long t)
    cdef double _f_wd_fee_pp(_c_Projection self, long long t)
    cdef object _f_wd_fees(_c_Projection self, object t)
    cdef double _f_corridor_factor(_c_Projection self, long long t)
    cdef double _f_db_pp(_c_Projection self, long long t)
    cdef double _f_net_amt_at_risk(_c_Projection self, long long t)
    cdef double _f_sg_net_amt_at_risk(_c_Projection self, long long t)
    cdef object _f_coi_rate_scale(_c_Projection self)
    cdef double _f_coi_rate_guar(_c_Projection self, long long t)
    cdef double _f_coi_rate(_c_Projection self, long long t)
    cdef double _f_sg_coi_rate(_c_Projection self, long long t)
    cdef double _f_coi_pp(_c_Projection self, long long t)
    cdef double _f_sg_coi_pp(_c_Projection self, long long t)
    cdef double _f_rider_charge_pp(_c_Projection self, long long t)
    cdef double _f_maint_fee_pp(_c_Projection self, long long t)
    cdef double _f_sg_maint_fee_pp(_c_Projection self, long long t)
    cdef object _f_mth_deduction_pp(_c_Projection self, object t)
    cdef object _f_sg_deduction_pp(_c_Projection self, object t)
    cdef object _f_maint_fee_taken_pp(_c_Projection self, object t)
    cdef object _f_coi_taken_pp(_c_Projection self, object t)
    cdef object _f_mth_deduction_taken_pp(_c_Projection self, object t)
    cdef object _f_mth_deduction_forgone_pp(_c_Projection self, object t)
    cdef object _f_maint_fee(_c_Projection self, object t)
    cdef object _f_coi(_c_Projection self, object t)
    cdef object _f_mth_deduction(_c_Projection self, object t)
    cdef object _f_mth_deduction_forgone(_c_Projection self, object t)
    cdef double _f_av_pp_at(_c_Projection self, long long t, str timing)
    cdef double _f_inv_income_pp(_c_Projection self, long long t)
    cdef double _f_av_pp(_c_Projection self, long long t)
    cdef object _f_av_at(_c_Projection self, object t, object timing)
    cdef object _f_inv_income(_c_Projection self, object t)
    cdef object _f_av_change(_c_Projection self, object t)
    cdef double _f_loan_bal_pp(_c_Projection self, long long t)
    cdef double _f_sg_pp_at(_c_Projection self, long long t, str timing)
    cdef double _f_sg_inv_income_pp(_c_Projection self, long long t)
    cdef double _f_sg_pp(_c_Projection self, long long t)
    cdef double _f_sg_net_pp(_c_Projection self, long long t)
    cdef bint _f_is_guar_active(_c_Projection self, long long t)
    cdef bint _f_is_guar_supported(_c_Projection self, long long t)
    cdef object _f_catch_up_prem_pp(_c_Projection self, object t)
    cdef double _f_surr_charge_rate(_c_Projection self, long long t)
    cdef double _f_surr_charge_pp(_c_Projection self, long long t)
    cdef double _f_csv_pp(_c_Projection self, long long t)
    cdef double _f_ncsv_pp(_c_Projection self, long long t)
    cdef object _f_surr_charge(_c_Projection self, object t)
    cdef bint _f_is_shortfall(_c_Projection self, long long t)
    cdef object _f_cure_premium_pp(_c_Projection self, object t)
    cdef long long _f_grace_mth(_c_Projection self, long long t)
    cdef bint _f_is_lapsed(_c_Projection self, long long t)
    cdef object _f_status(_c_Projection self, object t)
    cdef long long _f_rop_anniversary(_c_Projection self, long long t)
    cdef double _f_rop_ratio(_c_Projection self, long long t)
    cdef double _f_rop_rate(_c_Projection self, long long t)
    cdef double _f_class_factor(_c_Projection self)
    cdef double _f_mort_improve_rate(_c_Projection self, long long t)
    cdef double _f_mort_improve_factor(_c_Projection self, long long t)
    cdef double _f_mort_rate(_c_Projection self, long long t)
    cdef double _f_mort_rate_mth(_c_Projection self, long long t)
    cdef double _f_lapse_rate_base(_c_Projection self, long long t)
    cdef double _f_lapse_rate_guar_mult(_c_Projection self)
    cdef double _f_lapse_rate_pattern_mult(_c_Projection self)
    cdef double _f_lapse_rate_dyn_mult(_c_Projection self, long long t)
    cdef double _f_lapse_rate(_c_Projection self, long long t)
    cdef double _f_lapse_rate_mth(_c_Projection self, long long t)
    cdef double _f_pols_if(_c_Projection self, long long t)
    cdef object _f_pols_if_at(_c_Projection self, object t, object timing)
    cdef double _f_pols_death(_c_Projection self, long long t)
    cdef double _f_pols_lapse(_c_Projection self, long long t)
    cdef double _f_pols_rop(_c_Projection self, long long t)
    cdef double _f_pols_lapse_grace(_c_Projection self, long long t)
    cdef object _f_pols_maturity(_c_Projection self, object t)
    cdef double _f_claim_pp(_c_Projection self, long long t, str kind)
    cdef object _f_claims_from_av(_c_Projection self, object t, object kind)
    cdef object _f_claims_over_av(_c_Projection self, object t)
    cdef double _f_claims(_c_Projection self, long long t, object kind=*)
    cdef double _f_withdrawals(_c_Projection self, long long t)
    cdef double _f_inflation_factor(_c_Projection self, long long t)
    cdef double _f_expenses(_c_Projection self, long long t)
    cdef double _f_premium_taxes(_c_Projection self, long long t)
    cdef object _f_margin_expense(_c_Projection self, object t)
    cdef object _f_margin_mortality(_c_Projection self, object t)
    cdef object _f_margin_rop(_c_Projection self, object t)
    cdef double _f_net_cf(_c_Projection self, long long t)
    cdef object _f_solve_len(_c_Projection self)
    cdef object _f_sg_pp_solve(_c_Projection self, object t, object prem)
    cdef object _f_guar_min_sg(_c_Projection self, object prem)
    cdef object _f_no_lapse_premium(_c_Projection self)
    cdef object _f_check_av_roll_fwd(_c_Projection self)
    cdef object _f_check_sg_roll_fwd(_c_Projection self)
    cdef object _f_check_margin(_c_Projection self)
    cdef object _f_result_cf(_c_Projection self)
    cdef object _f_result_pols(_c_Projection self)
    cdef object _f_result_av(_c_Projection self)
    cdef object _f_result_guar(_c_Projection self)
    cdef double _f_bench_net_cf(_c_Projection self)

    cpdef object model_point(_c_Projection self)
    cpdef long long age_at_entry(_c_Projection self)
    cpdef str sex(_c_Projection self)
    cpdef str rate_class(_c_Projection self)
    cpdef double sum_assured(_c_Projection self)
    cpdef long long guarantee_age(_c_Projection self)
    cpdef str premium_type(_c_Projection self)
    cpdef str premium_mode(_c_Projection self)
    cpdef double premium_pp_ann(_c_Projection self)
    cpdef double load_prem_rate(_c_Projection self)
    cpdef double av_pp_init(_c_Projection self)
    cpdef double sg_pp_init(_c_Projection self)
    cpdef double loan_bal_init(_c_Projection self)
    cpdef double cum_prem_init(_c_Projection self)
    cpdef double pols_if_init(_c_Projection self)
    cpdef long long duration_mth_init(_c_Projection self)
    cpdef bint has_surr_charge(_c_Projection self)
    cpdef str surr_charge_id(_c_Projection self)
    cpdef bint rop_elected(_c_Projection self)
    cpdef long long coi_rate_dp(_c_Projection self)
    cpdef long long duration_mth(_c_Projection self, long long t)
    cpdef long long duration(_c_Projection self, long long t)
    cpdef long long policy_year(_c_Projection self, long long t)
    cpdef long long age(_c_Projection self, long long t)
    cpdef long long proj_len(_c_Projection self)
    cpdef double sum_assured_at(_c_Projection self, long long t)
    cpdef double units(_c_Projection self, long long t)
    cpdef double crediting_rate_ann(_c_Projection self, long long t)
    cpdef double inv_return_mth(_c_Projection self, long long t)
    cpdef double guar_rate_mth(_c_Projection self)
    cpdef double sg_rate_mth(_c_Projection self)
    cpdef double naar_factor(_c_Projection self)
    cpdef double sg_naar_factor(_c_Projection self)
    cpdef double loan_rate_mth(_c_Projection self)
    cpdef double loan_cr_rate_mth(_c_Projection self)
    cpdef long long premium_freq(_c_Projection self)
    cpdef bint is_premium_mth(_c_Projection self, long long t)
    cpdef double prem_persistency(_c_Projection self, long long t)
    cpdef double premium_pp(_c_Projection self, long long t)
    cpdef double prem_to_av_pp(_c_Projection self, long long t)
    cpdef double prem_to_sg_pp(_c_Projection self, long long t)
    cpdef object prem_to_av(_c_Projection self, object t)
    cpdef double premiums(_c_Projection self, long long t)
    cpdef double cum_prem_pp(_c_Projection self, long long t)
    cpdef double wd_pp(_c_Projection self, long long t)
    cpdef double wd_fee_pp(_c_Projection self, long long t)
    cpdef object wd_fees(_c_Projection self, object t)
    cpdef double corridor_factor(_c_Projection self, long long t)
    cpdef double db_pp(_c_Projection self, long long t)
    cpdef double net_amt_at_risk(_c_Projection self, long long t)
    cpdef double sg_net_amt_at_risk(_c_Projection self, long long t)
    cpdef object coi_rate_scale(_c_Projection self)
    cpdef double coi_rate_guar(_c_Projection self, long long t)
    cpdef double coi_rate(_c_Projection self, long long t)
    cpdef double sg_coi_rate(_c_Projection self, long long t)
    cpdef double coi_pp(_c_Projection self, long long t)
    cpdef double sg_coi_pp(_c_Projection self, long long t)
    cpdef double rider_charge_pp(_c_Projection self, long long t)
    cpdef double maint_fee_pp(_c_Projection self, long long t)
    cpdef double sg_maint_fee_pp(_c_Projection self, long long t)
    cpdef object mth_deduction_pp(_c_Projection self, object t)
    cpdef object sg_deduction_pp(_c_Projection self, object t)
    cpdef object maint_fee_taken_pp(_c_Projection self, object t)
    cpdef object coi_taken_pp(_c_Projection self, object t)
    cpdef object mth_deduction_taken_pp(_c_Projection self, object t)
    cpdef object mth_deduction_forgone_pp(_c_Projection self, object t)
    cpdef object maint_fee(_c_Projection self, object t)
    cpdef object coi(_c_Projection self, object t)
    cpdef object mth_deduction(_c_Projection self, object t)
    cpdef object mth_deduction_forgone(_c_Projection self, object t)
    cpdef double av_pp_at(_c_Projection self, long long t, str timing)
    cpdef double inv_income_pp(_c_Projection self, long long t)
    cpdef double av_pp(_c_Projection self, long long t)
    cpdef object av_at(_c_Projection self, object t, object timing)
    cpdef object inv_income(_c_Projection self, object t)
    cpdef object av_change(_c_Projection self, object t)
    cpdef double loan_bal_pp(_c_Projection self, long long t)
    cpdef double sg_pp_at(_c_Projection self, long long t, str timing)
    cpdef double sg_inv_income_pp(_c_Projection self, long long t)
    cpdef double sg_pp(_c_Projection self, long long t)
    cpdef double sg_net_pp(_c_Projection self, long long t)
    cpdef bint is_guar_active(_c_Projection self, long long t)
    cpdef bint is_guar_supported(_c_Projection self, long long t)
    cpdef object catch_up_prem_pp(_c_Projection self, object t)
    cpdef double surr_charge_rate(_c_Projection self, long long t)
    cpdef double surr_charge_pp(_c_Projection self, long long t)
    cpdef double csv_pp(_c_Projection self, long long t)
    cpdef double ncsv_pp(_c_Projection self, long long t)
    cpdef object surr_charge(_c_Projection self, object t)
    cpdef bint is_shortfall(_c_Projection self, long long t)
    cpdef object cure_premium_pp(_c_Projection self, object t)
    cpdef long long grace_mth(_c_Projection self, long long t)
    cpdef bint is_lapsed(_c_Projection self, long long t)
    cpdef object status(_c_Projection self, object t)
    cpdef long long rop_anniversary(_c_Projection self, long long t)
    cpdef double rop_ratio(_c_Projection self, long long t)
    cpdef double rop_rate(_c_Projection self, long long t)
    cpdef double class_factor(_c_Projection self)
    cpdef double mort_improve_rate(_c_Projection self, long long t)
    cpdef double mort_improve_factor(_c_Projection self, long long t)
    cpdef double mort_rate(_c_Projection self, long long t)
    cpdef double mort_rate_mth(_c_Projection self, long long t)
    cpdef double lapse_rate_base(_c_Projection self, long long t)
    cpdef double lapse_rate_guar_mult(_c_Projection self)
    cpdef double lapse_rate_pattern_mult(_c_Projection self)
    cpdef double lapse_rate_dyn_mult(_c_Projection self, long long t)
    cpdef double lapse_rate(_c_Projection self, long long t)
    cpdef double lapse_rate_mth(_c_Projection self, long long t)
    cpdef double pols_if(_c_Projection self, long long t)
    cpdef object pols_if_at(_c_Projection self, object t, object timing)
    cpdef double pols_death(_c_Projection self, long long t)
    cpdef double pols_lapse(_c_Projection self, long long t)
    cpdef double pols_rop(_c_Projection self, long long t)
    cpdef double pols_lapse_grace(_c_Projection self, long long t)
    cpdef object pols_maturity(_c_Projection self, object t)
    cpdef double claim_pp(_c_Projection self, long long t, str kind)
    cpdef object claims_from_av(_c_Projection self, object t, object kind)
    cpdef object claims_over_av(_c_Projection self, object t)
    cpdef double claims(_c_Projection self, long long t, object kind=*)
    cpdef double withdrawals(_c_Projection self, long long t)
    cpdef double inflation_factor(_c_Projection self, long long t)
    cpdef double expenses(_c_Projection self, long long t)
    cpdef double premium_taxes(_c_Projection self, long long t)
    cpdef object margin_expense(_c_Projection self, object t)
    cpdef object margin_mortality(_c_Projection self, object t)
    cpdef object margin_rop(_c_Projection self, object t)
    cpdef double net_cf(_c_Projection self, long long t)
    cpdef object solve_len(_c_Projection self)
    cpdef object sg_pp_solve(_c_Projection self, object t, object prem)
    cpdef object guar_min_sg(_c_Projection self, object prem)
    cpdef object no_lapse_premium(_c_Projection self)
    cpdef object check_av_roll_fwd(_c_Projection self)
    cpdef object check_sg_roll_fwd(_c_Projection self)
    cpdef object check_margin(_c_Projection self)
    cpdef object result_cf(_c_Projection self)
    cpdef object result_pols(_c_Projection self)
    cpdef object result_av(_c_Projection self)
    cpdef object result_guar(_c_Projection self)
    cpdef double bench_net_cf(_c_Projection self)


