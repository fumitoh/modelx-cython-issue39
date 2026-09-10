
from VA_US_S_mxg_e6aefd4967_nomx_cy cimport _mx_sys


cdef class _c_Data(_mx_sys.BaseSpace):

    cdef object _v_input_dir
    cdef bint _has_input_dir
    cdef object _v_model_point_table
    cdef bint _has_model_point_table
    cdef object _v_mort_table
    cdef bint _has_mort_table
    cdef object _v_fund_table
    cdef bint _has_fund_table
    cdef object _v_return_scenario
    cdef bint _has_return_scenario
    cdef object _v_rate_scenario
    cdef bint _has_rate_scenario
    cdef object _v_gawa_pct_table
    cdef bint _has_gawa_pct_table
    cdef object _v_cdsc_table
    cdef bint _has_cdsc_table
    cdef object _v_transaction_table
    cdef bint _has_transaction_table

    cdef public str model_point_file
    cdef public str mort_table_file
    cdef public str fund_file
    cdef public str return_scenario_file
    cdef public str rate_scenario_file
    cdef public str gawa_pct_file
    cdef public str cdsc_file
    cdef public str transaction_file
    cdef public object pd


    cpdef _mx_copy_refs(_c_Data self, object base, object base_root)

    cdef object _f_input_dir(_c_Data self)
    cdef object _f_model_point_table(_c_Data self)
    cdef object _f_mort_table(_c_Data self)
    cdef object _f_fund_table(_c_Data self)
    cdef object _f_return_scenario(_c_Data self)
    cdef object _f_rate_scenario(_c_Data self)
    cdef object _f_gawa_pct_table(_c_Data self)
    cdef object _f_cdsc_table(_c_Data self)
    cdef object _f_transaction_table(_c_Data self)

    cpdef object input_dir(_c_Data self)
    cpdef object model_point_table(_c_Data self)
    cpdef object mort_table(_c_Data self)
    cpdef object fund_table(_c_Data self)
    cpdef object return_scenario(_c_Data self)
    cpdef object rate_scenario(_c_Data self)
    cpdef object gawa_pct_table(_c_Data self)
    cpdef object cdsc_table(_c_Data self)
    cpdef object transaction_table(_c_Data self)



cdef class _c_Projection(_mx_sys.BaseSpace):

    cdef object _v_model_point
    cdef bint _has_model_point
    cdef object _v_policy_id
    cdef bint _has_policy_id
    cdef long long _v_age_at_entry
    cdef bint _has_age_at_entry
    cdef str _v_sex
    cdef bint _has_sex
    cdef object _v_designated_lives
    cdef bint _has_designated_lives
    cdef object _v_tax_status
    cdef bint _has_tax_status
    cdef double _v_pols_if_init
    cdef bint _has_pols_if_init
    cdef double _v_premium_tax_rate
    cdef bint _has_premium_tax_rate
    cdef double _v_premium_single
    cdef bint _has_premium_single
    cdef str _v_fund_set
    cdef bint _has_fund_set
    cdef object _v_sub_ids
    cdef bint _has_sub_ids
    cdef double[3] _v_alloc
    cdef bint[3] _has_alloc
    cdef double[3] _v_fund_expense_rate
    cdef bint[3] _has_fund_expense_rate
    cdef str _v_glwb_option
    cdef bint _has_glwb_option
    cdef str _v_stepup_basis
    cdef bint _has_stepup_basis
    cdef str _v_gmdb_option
    cdef bint _has_gmdb_option
    cdef str _v_cdsc_schedule
    cdef bint _has_cdsc_schedule
    cdef str _v_fee_reset_rule
    cdef bint _has_fee_reset_rule
    cdef str _v_rollup_rule
    cdef bint _has_rollup_rule
    cdef long long _v_wd_start_age
    cdef bint _has_wd_start_age
    cdef double _v_wd_intensity
    cdef bint _has_wd_intensity
    cdef str _v_scenario_id
    cdef bint _has_scenario_id
    cdef str _v_txn_id
    cdef bint _has_txn_id
    cdef long long _v_duration_mth_init
    cdef bint _has_duration_mth_init
    cdef bint _v_is_inforce
    cdef bint _has_is_inforce
    cdef double _v_av_pp_init
    cdef bint _has_av_pp_init
    cdef double _v_gwb_pp_init
    cdef bint _has_gwb_pp_init
    cdef double _v_gawa_pp_init
    cdef bint _has_gawa_pp_init
    cdef double _v_gawa_pct_init
    cdef bint _has_gawa_pct_init
    cdef bint _v_has_wd_init
    cdef bint _has_has_wd_init
    cdef double _v_bb_pp_init
    cdef bint _has_bb_pp_init
    cdef double _v_rb_pp_init
    cdef bint _has_rb_pp_init
    cdef double _v_np_pp_init
    cdef bint _has_np_pp_init
    cdef double _v_rp_pp_init
    cdef bint _has_rp_pp_init
    cdef double _v_adj_pp_init
    cdef bint _has_adj_pp_init
    cdef long long _v_bonus_end_init
    cdef bint _has_bonus_end_init
    cdef long long _v_policy_term
    cdef bint _has_policy_term
    cdef long long _v_proj_len
    cdef bint _has_proj_len
    cdef long long[721] _v_duration_mth
    cdef bint[721] _has_duration_mth
    cdef long long[721] _v_policy_year
    cdef bint[721] _has_policy_year
    cdef long long[721] _v_duration
    cdef bint[721] _has_duration
    cdef long long[721] _v_age
    cdef bint[721] _has_age
    cdef long long[721] _v_age_at_anniv
    cdef bint[721] _has_age_at_anniv
    cdef long long[721] _v_contract_quarter
    cdef bint[721] _has_contract_quarter
    cdef bint[721] _v_is_anniv
    cdef bint[721] _has_is_anniv
    cdef bint[721] _v_is_quarterly_anniv
    cdef bint[721] _has_is_quarterly_anniv
    cdef bint[721] _v_is_year_start
    cdef bint[721] _has_is_year_start
    cdef long long[710] _v_t_of_month
    cdef bint[710] _has_t_of_month
    cdef dict _v_phase
    cdef double[721][3] _v_inv_return_mth
    cdef bint[721][3] _has_inv_return_mth
    cdef dict _v_scenario_rate
    cdef double[69] _v_vix_sq
    cdef bint[69] _has_vix_sq
    cdef double[721] _v_cmt10
    cdef bint[721] _has_cmt10
    cdef double[721][3] _v_unit_growth
    cdef bint[721][3] _has_unit_growth
    cdef dict _v_sa_pp_at
    cdef double[721][3] _v_sa_pp
    cdef bint[721][3] _has_sa_pp
    cdef dict _v_av_pp_at
    cdef double[721] _v_av_pp
    cdef bint[721] _has_av_pp
    cdef dict _v_sa_weight
    cdef dict _v_gross_inv_income_pp
    cdef dict _v_fund_expense_pp
    cdef double[721] _v_asset_charge_pp
    cdef bint[721] _has_asset_charge_pp
    cdef dict _v_inv_income_pp
    cdef double[721] _v_prem_scheduled_pp
    cdef bint[721] _has_prem_scheduled_pp
    cdef double[721] _v_premium_pp
    cdef bint[721] _has_premium_pp
    cdef double[721] _v_prem_to_av_pp
    cdef bint[721] _has_prem_to_av_pp
    cdef double[721] _v_wd_scheduled_pp
    cdef bint[721] _has_wd_scheduled_pp
    cdef bint[721] _v_is_wd_month
    cdef bint[721] _has_is_wd_month
    cdef bint[721] _v_is_wd_taken
    cdef bint[721] _has_is_wd_taken
    cdef bint[721] _v_has_wd_by
    cdef bint[721] _has_has_wd_by
    cdef bint[721] _v_is_first_wd
    cdef bint[721] _has_is_first_wd
    cdef bint[721] _v_is_wd_year
    cdef bint[721] _has_is_wd_year
    cdef double[107] _v_gawa_pct_at_age
    cdef bint[107] _has_gawa_pct_at_age
    cdef double[721] _v_wd_limit_pp
    cdef bint[721] _has_wd_limit_pp
    cdef double[721] _v_wd_glwb_pp
    cdef bint[721] _has_wd_glwb_pp
    cdef double[721] _v_wd_pp_due
    cdef bint[721] _has_wd_pp_due
    cdef double[721] _v_wd_pp
    cdef bint[721] _has_wd_pp
    cdef double[721] _v_sum_wd_pp
    cdef bint[721] _has_sum_wd_pp
    cdef double[721] _v_wd_excess_pp
    cdef bint[721] _has_wd_excess_pp
    cdef double[721] _v_wd_nonexcess_pp
    cdef bint[721] _has_wd_nonexcess_pp
    cdef double[721] _v_cv_pre_excess_pp
    cdef bint[721] _has_cv_pre_excess_pp
    cdef double[721] _v_excess_factor
    cdef bint[721] _has_excess_factor
    cdef double[721] _v_free_wd_allow
    cdef bint[721] _has_free_wd_allow
    cdef double[721] _v_free_wd_avail
    cdef bint[721] _has_free_wd_avail
    cdef double[721] _v_wd_free_pp
    cdef bint[721] _has_wd_free_pp
    cdef double[721] _v_free_wd_used_cum_pp
    cdef bint[721] _has_free_wd_used_cum_pp
    cdef double[721] _v_wd_exempt_pp
    cdef bint[721] _has_wd_exempt_pp
    cdef double[721] _v_wd_chargeable_pp
    cdef bint[721] _has_wd_chargeable_pp
    cdef double[721] _v_surr_charge_rate
    cdef bint[721] _has_surr_charge_rate
    cdef double[721] _v_wd_charge_pp
    cdef bint[721] _has_wd_charge_pp
    cdef double[721] _v_wd_payment_pp
    cdef bint[721] _has_wd_payment_pp
    cdef double[721] _v_surr_free_pp
    cdef bint[721] _has_surr_free_pp
    cdef double[721] _v_surr_chargeable_pp
    cdef bint[721] _has_surr_chargeable_pp
    cdef double[721] _v_surr_charge_pp
    cdef bint[721] _has_surr_charge_pp
    cdef double[721] _v_surr_benefit_pp
    cdef bint[721] _has_surr_benefit_pp
    cdef double[721] _v_phi_glwb
    cdef bint[721] _has_phi_glwb
    cdef dict _v_fee_rate_vix_raw
    cdef dict _v_fee_rate_vix_clip
    cdef double[69] _v_phi_glwb_vix
    cdef bint[69] _has_phi_glwb_vix
    cdef double[721] _v_phi_gmdb
    cdef bint[721] _has_phi_gmdb
    cdef double _v_rollup_pct
    cdef bint _has_rollup_pct
    cdef double[721] _v_rollup_rate
    cdef bint[721] _has_rollup_rate
    cdef double[721] _v_fee_glwb_pp_due
    cdef bint[721] _has_fee_glwb_pp_due
    cdef double[721] _v_fee_gmdb_pp_due
    cdef bint[721] _has_fee_gmdb_pp_due
    cdef double[721] _v_maint_fee_pp_due
    cdef bint[721] _has_maint_fee_pp_due
    cdef double[721] _v_charge_pp_due
    cdef bint[721] _has_charge_pp_due
    cdef double[721] _v_charge_scale
    cdef bint[721] _has_charge_scale
    cdef double[721] _v_fee_glwb_pp
    cdef bint[721] _has_fee_glwb_pp
    cdef double[721] _v_fee_gmdb_pp
    cdef bint[721] _has_fee_gmdb_pp
    cdef double[721] _v_maint_fee_pp
    cdef bint[721] _has_maint_fee_pp
    cdef double[721] _v_charge_pp
    cdef bint[721] _has_charge_pp
    cdef dict _v_charge_income_pp
    cdef dict _v_gwb_pp_at
    cdef double[721] _v_bb_pp_bef_anniv
    cdef bint[721] _has_bb_pp_bef_anniv
    cdef double[721] _v_bonus_pp
    cdef bint[721] _has_bonus_pp
    cdef double[721] _v_gwb_pp_aft_bonus
    cdef bint[721] _has_gwb_pp_aft_bonus
    cdef double[721] _v_stepup_base_pp
    cdef bint[721] _has_stepup_base_pp
    cdef bint[721] _v_is_stepup
    cdef bint[721] _has_is_stepup
    cdef double[721] _v_gwb_pp_aft_stepup
    cdef bint[721] _has_gwb_pp_aft_stepup
    cdef long long _v_gwb_adj_year
    cdef bint _has_gwb_adj_year
    cdef bint[721] _v_is_gwb_adj_date
    cdef bint[721] _has_is_gwb_adj_date
    cdef double[721] _v_adj_pp_bef_anniv
    cdef bint[721] _has_adj_pp_bef_anniv
    cdef double[721] _v_adj_pp
    cdef bint[721] _has_adj_pp
    cdef double[721] _v_gwb_pp
    cdef bint[721] _has_gwb_pp
    cdef double[721] _v_bb_pp
    cdef bint[721] _has_bb_pp
    cdef long long[721] _v_bonus_end
    cdef bint[721] _has_bonus_end
    cdef double[721] _v_gawa_pct_fixed
    cdef bint[721] _has_gawa_pct_fixed
    cdef dict _v_gawa_pp_at
    cdef double[721] _v_gawa_pp
    cdef bint[721] _has_gawa_pp
    cdef double[721] _v_np_pp
    cdef bint[721] _has_np_pp
    cdef double[721] _v_rp_reduction_pp
    cdef bint[721] _has_rp_reduction_pp
    cdef double[721] _v_rp_pp
    cdef bint[721] _has_rp_pp
    cdef double[721] _v_rb_prior_anniv_pp
    cdef bint[721] _has_rb_prior_anniv_pp
    cdef double[721] _v_gmdb_allow_pp
    cdef bint[721] _has_gmdb_allow_pp
    cdef double[721] _v_gmdb_wd_dfd_pp
    cdef bint[721] _has_gmdb_wd_dfd_pp
    cdef double[721] _v_gmdb_wd_excess_pp
    cdef bint[721] _has_gmdb_wd_excess_pp
    cdef double[721] _v_gmdb_wd_factor
    cdef bint[721] _has_gmdb_wd_factor
    cdef double[721] _v_gmdb_dfd_acc_pp
    cdef bint[721] _has_gmdb_dfd_acc_pp
    cdef double[721] _v_gmdb_factor_acc
    cdef bint[721] _has_gmdb_factor_acc
    cdef dict _v_rb_pp_at
    cdef double[721] _v_rb_pp
    cdef bint[721] _has_rb_pp
    cdef double[721] _v_gmdb_guarantee_pp
    cdef bint[721] _has_gmdb_guarantee_pp
    cdef double[721] _v_db_pp
    cdef bint[721] _has_db_pp
    cdef dict _v_gmdb_claim_pp
    cdef bint _v_forlife_flag
    cdef bint _has_forlife_flag
    cdef bint[721] _v_depleted_flag
    cdef bint[721] _has_depleted_flag
    cdef double[721] _v_glwb_payment_pp
    cdef bint[721] _has_glwb_payment_pp
    cdef double[721] _v_mort_rate
    cdef bint[721] _has_mort_rate
    cdef double[721] _v_mort_rate_mth
    cdef bint[721] _has_mort_rate_mth
    cdef double[721] _v_lapse_rate_base
    cdef bint[721] _has_lapse_rate_base
    cdef double[721] _v_moneyness_glwb
    cdef bint[721] _has_moneyness_glwb
    cdef double[721] _v_moneyness_gmdb
    cdef bint[721] _has_moneyness_gmdb
    cdef dict _v_lapse_itm_mult
    cdef double[721] _v_lapse_dyn_mult
    cdef bint[721] _has_lapse_dyn_mult
    cdef double[721] _v_lapse_wd_factor
    cdef bint[721] _has_lapse_wd_factor
    cdef double[721] _v_lapse_rate
    cdef bint[721] _has_lapse_rate
    cdef double[721] _v_lapse_rate_mth
    cdef bint[721] _has_lapse_rate_mth
    cdef double[721] _v_pols_if
    cdef bint[721] _has_pols_if
    cdef dict _v_pols_if_at
    cdef double[721] _v_pols_death
    cdef bint[721] _has_pols_death
    cdef double[721] _v_pols_lapse
    cdef bint[721] _has_pols_lapse
    cdef double[721] _v_pols_maturity
    cdef bint[721] _has_pols_maturity
    cdef dict _v_pols_decr
    cdef dict _v_claim_pp
    cdef dict _v_claim_from_av_pp
    cdef double[721] _v_premiums
    cdef bint[721] _has_premiums
    cdef dict _v_prem_to_av
    cdef double[721] _v_asset_charges
    cdef bint[721] _has_asset_charges
    cdef double[721] _v_fees_glwb
    cdef bint[721] _has_fees_glwb
    cdef double[721] _v_fees_gmdb
    cdef bint[721] _has_fees_gmdb
    cdef double[721] _v_maint_fees
    cdef bint[721] _has_maint_fees
    cdef dict _v_wd_charges
    cdef double[721] _v_charge_income
    cdef bint[721] _has_charge_income
    cdef double[721] _v_withdrawals
    cdef bint[721] _has_withdrawals
    cdef double[721] _v_glwb_payments
    cdef bint[721] _has_glwb_payments
    cdef dict _v_claims
    cdef dict _v_claims_from_av
    cdef dict _v_claims_over_av
    cdef dict _v_gmdb_claims
    cdef double[721] _v_commissions
    cdef bint[721] _has_commissions
    cdef double[721] _v_premium_taxes
    cdef bint[721] _has_premium_taxes
    cdef double[721] _v_inflation_factor
    cdef bint[721] _has_inflation_factor
    cdef double[721] _v_expenses
    cdef bint[721] _has_expenses
    cdef double[721] _v_net_cf
    cdef bint[721] _has_net_cf
    cdef dict _v_net_cf_ga
    cdef dict _v_av_at
    cdef dict _v_inv_income
    cdef dict _v_wd_from_av
    cdef dict _v_charges_from_av
    cdef dict _v_av_change
    cdef dict _v_check_av_roll_fwd_resid
    cdef object _v_check_av_roll_fwd
    cdef bint _has_check_av_roll_fwd
    cdef dict _v_check_pols_roll_fwd_resid
    cdef object _v_check_pols_roll_fwd
    cdef bint _has_check_pols_roll_fwd
    cdef dict _v_check_charge_split_resid
    cdef object _v_check_charge_split
    cdef bint _has_check_charge_split
    cdef object _v_result_cf
    cdef bint _has_result_cf
    cdef object _v_result_pols
    cdef bint _has_result_pols
    cdef object _v_result_av
    cdef bint _has_result_av
    cdef object _v_result_bases
    cdef bint _has_result_bases
    cdef double _v_bench_net_cf
    cdef bint _has_bench_net_cf

    cdef public _c_Data data
    cdef public long long point_id
    cdef public long long omega_age
    cdef public str rate_sheet_date
    cdef public double asset_charge_me
    cdef public double asset_charge_admin
    cdef public double phi_glwb_curr
    cdef public double phi_glwb_max
    cdef public double phi_gmdb_curr
    cdef public double phi_gmdb_max
    cdef public double fee_increase_max
    cdef public long long fee_reset_years
    cdef public double maint_fee
    cdef public double maint_fee_waiver_av
    cdef public double free_wd_rate
    cdef public long long surr_charge_years
    cdef public double bonus_pct
    cdef public long long bonus_period_years
    cdef public long long bonus_restart_age
    cdef public double gwb_cap
    cdef public double gwb_adj_pct
    cdef public long long gwb_adj_age
    cdef public long long gwb_adj_min_year
    cdef public double rollup_pct_young
    cdef public double rollup_pct_old
    cdef public long long rollup_age_split
    cdef public long long gmdb_growth_cutoff_age
    cdef public long long forlife_age
    cdef public double av_depletion_threshold
    cdef public double lapse_rate_sc
    cdef public double lapse_rate_shock
    cdef public double lapse_rate_ult
    cdef public double lapse_itm_upper
    cdef public double lapse_itm_lower
    cdef public double lapse_itm_mult_coef
    cdef public double lapse_itm_threshold
    cdef public double lapse_wd_year_factor
    cdef public double vix_fee_coef
    cdef public double vix_divisor
    cdef public double vix_offset
    cdef public double vix_band
    cdef public double vix_corridor_lo
    cdef public double vix_corridor_hi
    cdef public double cmt_spread
    cdef public double cmt_spread_predraw
    cdef public double cmt_round_step
    cdef public double cmt_floor
    cdef public double cmt_cap
    cdef public double expense_maint
    cdef public long long expense_base_year
    cdef public long long valuation_year
    cdef public double expense_av_rate
    cdef public double inflation_rate
    cdef public double expense_acq
    cdef public double comm_rate_acq
    cdef public object math
    cdef public object pd


    cpdef _mx_copy_refs(_c_Projection self, object base, object base_root)

    cdef object _f_model_point(_c_Projection self)
    cdef object _f_policy_id(_c_Projection self)
    cdef long long _f_age_at_entry(_c_Projection self)
    cdef str _f_sex(_c_Projection self)
    cdef object _f_designated_lives(_c_Projection self)
    cdef object _f_tax_status(_c_Projection self)
    cdef double _f_pols_if_init(_c_Projection self)
    cdef double _f_premium_tax_rate(_c_Projection self)
    cdef double _f_premium_single(_c_Projection self)
    cdef str _f_fund_set(_c_Projection self)
    cdef object _f_sub_ids(_c_Projection self)
    cdef double _f_alloc(_c_Projection self, long long i)
    cdef double _f_fund_expense_rate(_c_Projection self, long long i)
    cdef str _f_glwb_option(_c_Projection self)
    cdef str _f_stepup_basis(_c_Projection self)
    cdef str _f_gmdb_option(_c_Projection self)
    cdef str _f_cdsc_schedule(_c_Projection self)
    cdef str _f_fee_reset_rule(_c_Projection self)
    cdef str _f_rollup_rule(_c_Projection self)
    cdef long long _f_wd_start_age(_c_Projection self)
    cdef double _f_wd_intensity(_c_Projection self)
    cdef str _f_scenario_id(_c_Projection self)
    cdef str _f_txn_id(_c_Projection self)
    cdef long long _f_duration_mth_init(_c_Projection self)
    cdef bint _f_is_inforce(_c_Projection self)
    cdef double _f_av_pp_init(_c_Projection self)
    cdef double _f_gwb_pp_init(_c_Projection self)
    cdef double _f_gawa_pp_init(_c_Projection self)
    cdef double _f_gawa_pct_init(_c_Projection self)
    cdef bint _f_has_wd_init(_c_Projection self)
    cdef double _f_bb_pp_init(_c_Projection self)
    cdef double _f_rb_pp_init(_c_Projection self)
    cdef double _f_np_pp_init(_c_Projection self)
    cdef double _f_rp_pp_init(_c_Projection self)
    cdef double _f_adj_pp_init(_c_Projection self)
    cdef long long _f_bonus_end_init(_c_Projection self)
    cdef long long _f_policy_term(_c_Projection self)
    cdef long long _f_proj_len(_c_Projection self)
    cdef long long _f_duration_mth(_c_Projection self, long long t)
    cdef long long _f_policy_year(_c_Projection self, long long t)
    cdef long long _f_duration(_c_Projection self, long long t)
    cdef long long _f_age(_c_Projection self, long long t)
    cdef long long _f_age_at_anniv(_c_Projection self, long long t)
    cdef long long _f_contract_quarter(_c_Projection self, long long t)
    cdef bint _f_is_anniv(_c_Projection self, long long t)
    cdef bint _f_is_quarterly_anniv(_c_Projection self, long long t)
    cdef bint _f_is_year_start(_c_Projection self, long long t)
    cdef long long _f_t_of_month(_c_Projection self, long long m)
    cdef object _f_phase(_c_Projection self, object t)
    cdef double _f_inv_return_mth(_c_Projection self, long long t, long long i)
    cdef double _f_scenario_rate(_c_Projection self, long long t, str name)
    cdef double _f_vix_sq(_c_Projection self, long long k)
    cdef double _f_cmt10(_c_Projection self, long long t)
    cdef double _f_unit_growth(_c_Projection self, long long t, long long i)
    cdef double _f_sa_pp_at(_c_Projection self, long long t, long long i, str timing)
    cdef double _f_sa_pp(_c_Projection self, long long t, long long i)
    cdef double _f_av_pp_at(_c_Projection self, long long t, str timing)
    cdef double _f_av_pp(_c_Projection self, long long t)
    cdef object _f_sa_weight(_c_Projection self, object t, object i)
    cdef object _f_gross_inv_income_pp(_c_Projection self, object t)
    cdef object _f_fund_expense_pp(_c_Projection self, object t)
    cdef double _f_asset_charge_pp(_c_Projection self, long long t)
    cdef object _f_inv_income_pp(_c_Projection self, object t)
    cdef double _f_prem_scheduled_pp(_c_Projection self, long long t)
    cdef double _f_premium_pp(_c_Projection self, long long t)
    cdef double _f_prem_to_av_pp(_c_Projection self, long long t)
    cdef double _f_wd_scheduled_pp(_c_Projection self, long long t)
    cdef bint _f_is_wd_month(_c_Projection self, long long t)
    cdef bint _f_is_wd_taken(_c_Projection self, long long t)
    cdef bint _f_has_wd_by(_c_Projection self, long long t)
    cdef bint _f_is_first_wd(_c_Projection self, long long t)
    cdef bint _f_is_wd_year(_c_Projection self, long long t)
    cdef double _f_gawa_pct_at_age(_c_Projection self, long long a)
    cdef double _f_wd_limit_pp(_c_Projection self, long long t)
    cdef double _f_wd_glwb_pp(_c_Projection self, long long t)
    cdef double _f_wd_pp_due(_c_Projection self, long long t)
    cdef double _f_wd_pp(_c_Projection self, long long t)
    cdef double _f_sum_wd_pp(_c_Projection self, long long t)
    cdef double _f_wd_excess_pp(_c_Projection self, long long t)
    cdef double _f_wd_nonexcess_pp(_c_Projection self, long long t)
    cdef double _f_cv_pre_excess_pp(_c_Projection self, long long t)
    cdef double _f_excess_factor(_c_Projection self, long long t)
    cdef double _f_free_wd_allow(_c_Projection self, long long t)
    cdef double _f_free_wd_avail(_c_Projection self, long long t)
    cdef double _f_wd_free_pp(_c_Projection self, long long t)
    cdef double _f_free_wd_used_cum_pp(_c_Projection self, long long t)
    cdef double _f_wd_exempt_pp(_c_Projection self, long long t)
    cdef double _f_wd_chargeable_pp(_c_Projection self, long long t)
    cdef double _f_surr_charge_rate(_c_Projection self, long long t)
    cdef double _f_wd_charge_pp(_c_Projection self, long long t)
    cdef double _f_wd_payment_pp(_c_Projection self, long long t)
    cdef double _f_surr_free_pp(_c_Projection self, long long t)
    cdef double _f_surr_chargeable_pp(_c_Projection self, long long t)
    cdef double _f_surr_charge_pp(_c_Projection self, long long t)
    cdef double _f_surr_benefit_pp(_c_Projection self, long long t)
    cdef double _f_phi_glwb(_c_Projection self, long long t)
    cdef double _f_fee_rate_vix_raw(_c_Projection self, double phi_0, double vix_sq_avg)
    cdef double _f_fee_rate_vix_clip(_c_Projection self, double prior, double raw)
    cdef double _f_phi_glwb_vix(_c_Projection self, long long k)
    cdef double _f_phi_gmdb(_c_Projection self, long long t)
    cdef double _f_rollup_pct(_c_Projection self)
    cdef double _f_rollup_rate(_c_Projection self, long long t)
    cdef double _f_fee_glwb_pp_due(_c_Projection self, long long t)
    cdef double _f_fee_gmdb_pp_due(_c_Projection self, long long t)
    cdef double _f_maint_fee_pp_due(_c_Projection self, long long t)
    cdef double _f_charge_pp_due(_c_Projection self, long long t)
    cdef double _f_charge_scale(_c_Projection self, long long t)
    cdef double _f_fee_glwb_pp(_c_Projection self, long long t)
    cdef double _f_fee_gmdb_pp(_c_Projection self, long long t)
    cdef double _f_maint_fee_pp(_c_Projection self, long long t)
    cdef double _f_charge_pp(_c_Projection self, long long t)
    cdef object _f_charge_income_pp(_c_Projection self, object t)
    cdef double _f_gwb_pp_at(_c_Projection self, long long t, str timing)
    cdef double _f_bb_pp_bef_anniv(_c_Projection self, long long t)
    cdef double _f_bonus_pp(_c_Projection self, long long t)
    cdef double _f_gwb_pp_aft_bonus(_c_Projection self, long long t)
    cdef double _f_stepup_base_pp(_c_Projection self, long long t)
    cdef bint _f_is_stepup(_c_Projection self, long long t)
    cdef double _f_gwb_pp_aft_stepup(_c_Projection self, long long t)
    cdef long long _f_gwb_adj_year(_c_Projection self)
    cdef bint _f_is_gwb_adj_date(_c_Projection self, long long t)
    cdef double _f_adj_pp_bef_anniv(_c_Projection self, long long t)
    cdef double _f_adj_pp(_c_Projection self, long long t)
    cdef double _f_gwb_pp(_c_Projection self, long long t)
    cdef double _f_bb_pp(_c_Projection self, long long t)
    cdef long long _f_bonus_end(_c_Projection self, long long t)
    cdef double _f_gawa_pct_fixed(_c_Projection self, long long t)
    cdef double _f_gawa_pp_at(_c_Projection self, long long t, str timing)
    cdef double _f_gawa_pp(_c_Projection self, long long t)
    cdef double _f_np_pp(_c_Projection self, long long t)
    cdef double _f_rp_reduction_pp(_c_Projection self, long long t)
    cdef double _f_rp_pp(_c_Projection self, long long t)
    cdef double _f_rb_prior_anniv_pp(_c_Projection self, long long t)
    cdef double _f_gmdb_allow_pp(_c_Projection self, long long t)
    cdef double _f_gmdb_wd_dfd_pp(_c_Projection self, long long t)
    cdef double _f_gmdb_wd_excess_pp(_c_Projection self, long long t)
    cdef double _f_gmdb_wd_factor(_c_Projection self, long long t)
    cdef double _f_gmdb_dfd_acc_pp(_c_Projection self, long long t)
    cdef double _f_gmdb_factor_acc(_c_Projection self, long long t)
    cdef double _f_rb_pp_at(_c_Projection self, long long t, str timing)
    cdef double _f_rb_pp(_c_Projection self, long long t)
    cdef double _f_gmdb_guarantee_pp(_c_Projection self, long long t)
    cdef double _f_db_pp(_c_Projection self, long long t)
    cdef object _f_gmdb_claim_pp(_c_Projection self, object t)
    cdef bint _f_forlife_flag(_c_Projection self)
    cdef bint _f_depleted_flag(_c_Projection self, long long t)
    cdef double _f_glwb_payment_pp(_c_Projection self, long long t)
    cdef double _f_mort_rate(_c_Projection self, long long t)
    cdef double _f_mort_rate_mth(_c_Projection self, long long t)
    cdef double _f_lapse_rate_base(_c_Projection self, long long t)
    cdef double _f_moneyness_glwb(_c_Projection self, long long t)
    cdef double _f_moneyness_gmdb(_c_Projection self, long long t)
    cdef double _f_lapse_itm_mult(_c_Projection self, double m)
    cdef double _f_lapse_dyn_mult(_c_Projection self, long long t)
    cdef double _f_lapse_wd_factor(_c_Projection self, long long t)
    cdef double _f_lapse_rate(_c_Projection self, long long t)
    cdef double _f_lapse_rate_mth(_c_Projection self, long long t)
    cdef double _f_pols_if(_c_Projection self, long long t)
    cdef double _f_pols_if_at(_c_Projection self, long long t, str timing)
    cdef double _f_pols_death(_c_Projection self, long long t)
    cdef double _f_pols_lapse(_c_Projection self, long long t)
    cdef double _f_pols_maturity(_c_Projection self, long long t)
    cdef double _f_pols_decr(_c_Projection self, long long t, str kind)
    cdef double _f_claim_pp(_c_Projection self, long long t, str kind)
    cdef object _f_claim_from_av_pp(_c_Projection self, object t, object kind)
    cdef double _f_premiums(_c_Projection self, long long t)
    cdef object _f_prem_to_av(_c_Projection self, object t)
    cdef double _f_asset_charges(_c_Projection self, long long t)
    cdef double _f_fees_glwb(_c_Projection self, long long t)
    cdef double _f_fees_gmdb(_c_Projection self, long long t)
    cdef double _f_maint_fees(_c_Projection self, long long t)
    cdef object _f_wd_charges(_c_Projection self, object t)
    cdef double _f_charge_income(_c_Projection self, long long t)
    cdef double _f_withdrawals(_c_Projection self, long long t)
    cdef double _f_glwb_payments(_c_Projection self, long long t)
    cdef double _f_claims(_c_Projection self, long long t, object kind=*)
    cdef object _f_claims_from_av(_c_Projection self, object t, object kind)
    cdef object _f_claims_over_av(_c_Projection self, object t, object kind=*)
    cdef object _f_gmdb_claims(_c_Projection self, object t)
    cdef double _f_commissions(_c_Projection self, long long t)
    cdef double _f_premium_taxes(_c_Projection self, long long t)
    cdef double _f_inflation_factor(_c_Projection self, long long t)
    cdef double _f_expenses(_c_Projection self, long long t)
    cdef double _f_net_cf(_c_Projection self, long long t)
    cdef object _f_net_cf_ga(_c_Projection self, object t)
    cdef object _f_av_at(_c_Projection self, object t, object timing)
    cdef object _f_inv_income(_c_Projection self, object t)
    cdef object _f_wd_from_av(_c_Projection self, object t)
    cdef object _f_charges_from_av(_c_Projection self, object t)
    cdef object _f_av_change(_c_Projection self, object t)
    cdef object _f_check_av_roll_fwd_resid(_c_Projection self, object t)
    cdef object _f_check_av_roll_fwd(_c_Projection self)
    cdef object _f_check_pols_roll_fwd_resid(_c_Projection self, object t)
    cdef object _f_check_pols_roll_fwd(_c_Projection self)
    cdef object _f_check_charge_split_resid(_c_Projection self, object t)
    cdef object _f_check_charge_split(_c_Projection self)
    cdef object _f_result_cf(_c_Projection self)
    cdef object _f_result_pols(_c_Projection self)
    cdef object _f_result_av(_c_Projection self)
    cdef object _f_result_bases(_c_Projection self)
    cdef double _f_bench_net_cf(_c_Projection self)

    cpdef object model_point(_c_Projection self)
    cpdef object policy_id(_c_Projection self)
    cpdef long long age_at_entry(_c_Projection self)
    cpdef str sex(_c_Projection self)
    cpdef object designated_lives(_c_Projection self)
    cpdef object tax_status(_c_Projection self)
    cpdef double pols_if_init(_c_Projection self)
    cpdef double premium_tax_rate(_c_Projection self)
    cpdef double premium_single(_c_Projection self)
    cpdef str fund_set(_c_Projection self)
    cpdef object sub_ids(_c_Projection self)
    cpdef double alloc(_c_Projection self, long long i)
    cpdef double fund_expense_rate(_c_Projection self, long long i)
    cpdef str glwb_option(_c_Projection self)
    cpdef str stepup_basis(_c_Projection self)
    cpdef str gmdb_option(_c_Projection self)
    cpdef str cdsc_schedule(_c_Projection self)
    cpdef str fee_reset_rule(_c_Projection self)
    cpdef str rollup_rule(_c_Projection self)
    cpdef long long wd_start_age(_c_Projection self)
    cpdef double wd_intensity(_c_Projection self)
    cpdef str scenario_id(_c_Projection self)
    cpdef str txn_id(_c_Projection self)
    cpdef long long duration_mth_init(_c_Projection self)
    cpdef bint is_inforce(_c_Projection self)
    cpdef double av_pp_init(_c_Projection self)
    cpdef double gwb_pp_init(_c_Projection self)
    cpdef double gawa_pp_init(_c_Projection self)
    cpdef double gawa_pct_init(_c_Projection self)
    cpdef bint has_wd_init(_c_Projection self)
    cpdef double bb_pp_init(_c_Projection self)
    cpdef double rb_pp_init(_c_Projection self)
    cpdef double np_pp_init(_c_Projection self)
    cpdef double rp_pp_init(_c_Projection self)
    cpdef double adj_pp_init(_c_Projection self)
    cpdef long long bonus_end_init(_c_Projection self)
    cpdef long long policy_term(_c_Projection self)
    cpdef long long proj_len(_c_Projection self)
    cpdef long long duration_mth(_c_Projection self, long long t)
    cpdef long long policy_year(_c_Projection self, long long t)
    cpdef long long duration(_c_Projection self, long long t)
    cpdef long long age(_c_Projection self, long long t)
    cpdef long long age_at_anniv(_c_Projection self, long long t)
    cpdef long long contract_quarter(_c_Projection self, long long t)
    cpdef bint is_anniv(_c_Projection self, long long t)
    cpdef bint is_quarterly_anniv(_c_Projection self, long long t)
    cpdef bint is_year_start(_c_Projection self, long long t)
    cpdef long long t_of_month(_c_Projection self, long long m)
    cpdef object phase(_c_Projection self, object t)
    cpdef double inv_return_mth(_c_Projection self, long long t, long long i)
    cpdef double scenario_rate(_c_Projection self, long long t, str name)
    cpdef double vix_sq(_c_Projection self, long long k)
    cpdef double cmt10(_c_Projection self, long long t)
    cpdef double unit_growth(_c_Projection self, long long t, long long i)
    cpdef double sa_pp_at(_c_Projection self, long long t, long long i, str timing)
    cpdef double sa_pp(_c_Projection self, long long t, long long i)
    cpdef double av_pp_at(_c_Projection self, long long t, str timing)
    cpdef double av_pp(_c_Projection self, long long t)
    cpdef object sa_weight(_c_Projection self, object t, object i)
    cpdef object gross_inv_income_pp(_c_Projection self, object t)
    cpdef object fund_expense_pp(_c_Projection self, object t)
    cpdef double asset_charge_pp(_c_Projection self, long long t)
    cpdef object inv_income_pp(_c_Projection self, object t)
    cpdef double prem_scheduled_pp(_c_Projection self, long long t)
    cpdef double premium_pp(_c_Projection self, long long t)
    cpdef double prem_to_av_pp(_c_Projection self, long long t)
    cpdef double wd_scheduled_pp(_c_Projection self, long long t)
    cpdef bint is_wd_month(_c_Projection self, long long t)
    cpdef bint is_wd_taken(_c_Projection self, long long t)
    cpdef bint has_wd_by(_c_Projection self, long long t)
    cpdef bint is_first_wd(_c_Projection self, long long t)
    cpdef bint is_wd_year(_c_Projection self, long long t)
    cpdef double gawa_pct_at_age(_c_Projection self, long long a)
    cpdef double wd_limit_pp(_c_Projection self, long long t)
    cpdef double wd_glwb_pp(_c_Projection self, long long t)
    cpdef double wd_pp_due(_c_Projection self, long long t)
    cpdef double wd_pp(_c_Projection self, long long t)
    cpdef double sum_wd_pp(_c_Projection self, long long t)
    cpdef double wd_excess_pp(_c_Projection self, long long t)
    cpdef double wd_nonexcess_pp(_c_Projection self, long long t)
    cpdef double cv_pre_excess_pp(_c_Projection self, long long t)
    cpdef double excess_factor(_c_Projection self, long long t)
    cpdef double free_wd_allow(_c_Projection self, long long t)
    cpdef double free_wd_avail(_c_Projection self, long long t)
    cpdef double wd_free_pp(_c_Projection self, long long t)
    cpdef double free_wd_used_cum_pp(_c_Projection self, long long t)
    cpdef double wd_exempt_pp(_c_Projection self, long long t)
    cpdef double wd_chargeable_pp(_c_Projection self, long long t)
    cpdef double surr_charge_rate(_c_Projection self, long long t)
    cpdef double wd_charge_pp(_c_Projection self, long long t)
    cpdef double wd_payment_pp(_c_Projection self, long long t)
    cpdef double surr_free_pp(_c_Projection self, long long t)
    cpdef double surr_chargeable_pp(_c_Projection self, long long t)
    cpdef double surr_charge_pp(_c_Projection self, long long t)
    cpdef double surr_benefit_pp(_c_Projection self, long long t)
    cpdef double phi_glwb(_c_Projection self, long long t)
    cpdef double fee_rate_vix_raw(_c_Projection self, double phi_0, double vix_sq_avg)
    cpdef double fee_rate_vix_clip(_c_Projection self, double prior, double raw)
    cpdef double phi_glwb_vix(_c_Projection self, long long k)
    cpdef double phi_gmdb(_c_Projection self, long long t)
    cpdef double rollup_pct(_c_Projection self)
    cpdef double rollup_rate(_c_Projection self, long long t)
    cpdef double fee_glwb_pp_due(_c_Projection self, long long t)
    cpdef double fee_gmdb_pp_due(_c_Projection self, long long t)
    cpdef double maint_fee_pp_due(_c_Projection self, long long t)
    cpdef double charge_pp_due(_c_Projection self, long long t)
    cpdef double charge_scale(_c_Projection self, long long t)
    cpdef double fee_glwb_pp(_c_Projection self, long long t)
    cpdef double fee_gmdb_pp(_c_Projection self, long long t)
    cpdef double maint_fee_pp(_c_Projection self, long long t)
    cpdef double charge_pp(_c_Projection self, long long t)
    cpdef object charge_income_pp(_c_Projection self, object t)
    cpdef double gwb_pp_at(_c_Projection self, long long t, str timing)
    cpdef double bb_pp_bef_anniv(_c_Projection self, long long t)
    cpdef double bonus_pp(_c_Projection self, long long t)
    cpdef double gwb_pp_aft_bonus(_c_Projection self, long long t)
    cpdef double stepup_base_pp(_c_Projection self, long long t)
    cpdef bint is_stepup(_c_Projection self, long long t)
    cpdef double gwb_pp_aft_stepup(_c_Projection self, long long t)
    cpdef long long gwb_adj_year(_c_Projection self)
    cpdef bint is_gwb_adj_date(_c_Projection self, long long t)
    cpdef double adj_pp_bef_anniv(_c_Projection self, long long t)
    cpdef double adj_pp(_c_Projection self, long long t)
    cpdef double gwb_pp(_c_Projection self, long long t)
    cpdef double bb_pp(_c_Projection self, long long t)
    cpdef long long bonus_end(_c_Projection self, long long t)
    cpdef double gawa_pct_fixed(_c_Projection self, long long t)
    cpdef double gawa_pp_at(_c_Projection self, long long t, str timing)
    cpdef double gawa_pp(_c_Projection self, long long t)
    cpdef double np_pp(_c_Projection self, long long t)
    cpdef double rp_reduction_pp(_c_Projection self, long long t)
    cpdef double rp_pp(_c_Projection self, long long t)
    cpdef double rb_prior_anniv_pp(_c_Projection self, long long t)
    cpdef double gmdb_allow_pp(_c_Projection self, long long t)
    cpdef double gmdb_wd_dfd_pp(_c_Projection self, long long t)
    cpdef double gmdb_wd_excess_pp(_c_Projection self, long long t)
    cpdef double gmdb_wd_factor(_c_Projection self, long long t)
    cpdef double gmdb_dfd_acc_pp(_c_Projection self, long long t)
    cpdef double gmdb_factor_acc(_c_Projection self, long long t)
    cpdef double rb_pp_at(_c_Projection self, long long t, str timing)
    cpdef double rb_pp(_c_Projection self, long long t)
    cpdef double gmdb_guarantee_pp(_c_Projection self, long long t)
    cpdef double db_pp(_c_Projection self, long long t)
    cpdef object gmdb_claim_pp(_c_Projection self, object t)
    cpdef bint forlife_flag(_c_Projection self)
    cpdef bint depleted_flag(_c_Projection self, long long t)
    cpdef double glwb_payment_pp(_c_Projection self, long long t)
    cpdef double mort_rate(_c_Projection self, long long t)
    cpdef double mort_rate_mth(_c_Projection self, long long t)
    cpdef double lapse_rate_base(_c_Projection self, long long t)
    cpdef double moneyness_glwb(_c_Projection self, long long t)
    cpdef double moneyness_gmdb(_c_Projection self, long long t)
    cpdef double lapse_itm_mult(_c_Projection self, double m)
    cpdef double lapse_dyn_mult(_c_Projection self, long long t)
    cpdef double lapse_wd_factor(_c_Projection self, long long t)
    cpdef double lapse_rate(_c_Projection self, long long t)
    cpdef double lapse_rate_mth(_c_Projection self, long long t)
    cpdef double pols_if(_c_Projection self, long long t)
    cpdef double pols_if_at(_c_Projection self, long long t, str timing)
    cpdef double pols_death(_c_Projection self, long long t)
    cpdef double pols_lapse(_c_Projection self, long long t)
    cpdef double pols_maturity(_c_Projection self, long long t)
    cpdef double pols_decr(_c_Projection self, long long t, str kind)
    cpdef double claim_pp(_c_Projection self, long long t, str kind)
    cpdef object claim_from_av_pp(_c_Projection self, object t, object kind)
    cpdef double premiums(_c_Projection self, long long t)
    cpdef object prem_to_av(_c_Projection self, object t)
    cpdef double asset_charges(_c_Projection self, long long t)
    cpdef double fees_glwb(_c_Projection self, long long t)
    cpdef double fees_gmdb(_c_Projection self, long long t)
    cpdef double maint_fees(_c_Projection self, long long t)
    cpdef object wd_charges(_c_Projection self, object t)
    cpdef double charge_income(_c_Projection self, long long t)
    cpdef double withdrawals(_c_Projection self, long long t)
    cpdef double glwb_payments(_c_Projection self, long long t)
    cpdef double claims(_c_Projection self, long long t, object kind=*)
    cpdef object claims_from_av(_c_Projection self, object t, object kind)
    cpdef object claims_over_av(_c_Projection self, object t, object kind=*)
    cpdef object gmdb_claims(_c_Projection self, object t)
    cpdef double commissions(_c_Projection self, long long t)
    cpdef double premium_taxes(_c_Projection self, long long t)
    cpdef double inflation_factor(_c_Projection self, long long t)
    cpdef double expenses(_c_Projection self, long long t)
    cpdef double net_cf(_c_Projection self, long long t)
    cpdef object net_cf_ga(_c_Projection self, object t)
    cpdef object av_at(_c_Projection self, object t, object timing)
    cpdef object inv_income(_c_Projection self, object t)
    cpdef object wd_from_av(_c_Projection self, object t)
    cpdef object charges_from_av(_c_Projection self, object t)
    cpdef object av_change(_c_Projection self, object t)
    cpdef object check_av_roll_fwd_resid(_c_Projection self, object t)
    cpdef object check_av_roll_fwd(_c_Projection self)
    cpdef object check_pols_roll_fwd_resid(_c_Projection self, object t)
    cpdef object check_pols_roll_fwd(_c_Projection self)
    cpdef object check_charge_split_resid(_c_Projection self, object t)
    cpdef object check_charge_split(_c_Projection self)
    cpdef object result_cf(_c_Projection self)
    cpdef object result_pols(_c_Projection self)
    cpdef object result_av(_c_Projection self)
    cpdef object result_bases(_c_Projection self)
    cpdef double bench_net_cf(_c_Projection self)


