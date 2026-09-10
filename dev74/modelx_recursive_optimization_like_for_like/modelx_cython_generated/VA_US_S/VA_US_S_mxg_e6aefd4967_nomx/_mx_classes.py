from . import _mx_sys



_v_cells_names_Data = [
    'input_dir',
    'model_point_table',
    'mort_table',
    'fund_table',
    'return_scenario',
    'rate_scenario',
    'gawa_pct_table',
    'cdsc_table',
    'transaction_table',
]
_v_space_params_Data = []


class _c_Data(_mx_sys.BaseSpace):

    def __init__(self, parent):

        # modelx variables
        self._space = self
        self._parent = parent
        self._model = parent._model
        self._name = "Data"


        self._mx_spaces = {

        }

        self._mx_cells = {}     # Populated on calling self._cells
        self._mx_is_cells_set = False

        self._mx_roots = []     # Dynamic Space only

        # Cache variables
        self._v_input_dir = None
        self._has_input_dir = False
        self._v_model_point_table = None
        self._has_model_point_table = False
        self._v_mort_table = None
        self._has_mort_table = False
        self._v_fund_table = None
        self._has_fund_table = False
        self._v_return_scenario = None
        self._has_return_scenario = False
        self._v_rate_scenario = None
        self._has_rate_scenario = False
        self._v_gawa_pct_table = None
        self._has_gawa_pct_table = False
        self._v_cdsc_table = None
        self._has_cdsc_table = False
        self._v_transaction_table = None
        self._has_transaction_table = False

    def _mx_assign_refs(self, io_data, pickle_data):

        # Reference assignment
        self.model_point_file = 'model_point_table.csv'
        self.mort_table_file = 'mort_table.csv'
        self.fund_file = 'fund_table.csv'
        self.return_scenario_file = 'return_scenario.csv'
        self.rate_scenario_file = 'rate_scenario.csv'
        self.gawa_pct_file = 'gawa_pct_table.csv'
        self.cdsc_file = 'cdsc_table.csv'
        self.transaction_file = 'transaction_table.csv'
        self.pd = _mx_sys.import_module('pandas')

    def _mx_copy_refs(self, base, base_root):

        # Reference assignment
        self.model_point_file = base.model_point_file
        self.mort_table_file = base.mort_table_file
        self.fund_file = base.fund_file
        self.return_scenario_file = base.return_scenario_file
        self.rate_scenario_file = base.rate_scenario_file
        self.gawa_pct_file = base.gawa_pct_file
        self.cdsc_file = base.cdsc_file
        self.transaction_file = base.transaction_file
        self.pd = base.pd

    def _f_input_dir(self):
        """The directory holding the input CSVs: the model folder's parent.

        Inputs are *external* files, not data stored inside the model, so the model folder
        is pure formulas.  The path is resolved at run time from where the model was read,
        following ``annuallife.TradLife_A``.
        """
        return self._model.path.parent                                        # noqa: F821

    def _f_model_point_table(self):
        """The model point table, read from *model_point_table.csv*."""
        return self.pd.read_csv(self.input_dir() / self.model_point_file, index_col="point_id")  # noqa: F821

    def _f_mort_table(self):
        """Annual mortality by attained age and sex, read from *mort_table.csv*."""
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.mort_table_file, index_col=["age", "sex"])     # noqa: F821

    def _f_fund_table(self):
        """Subaccount allocations and fund expense ratios, from *fund_table.csv*."""
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.fund_file, index_col=["fund_set", "sub_id"])   # noqa: F821

    def _f_return_scenario(self):
        """Gross subaccount returns, read from *return_scenario.csv*.

        Indexed by ``(scenario_id, sub_id, t)`` and read as a step function of ``t``: each
        row states the monthly gross fund return that holds from that month until the next
        row for the same scenario and subaccount.
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.return_scenario_file,                          # noqa: F821
            index_col=["scenario_id", "sub_id", "t"])

    def _f_rate_scenario(self):
        """The exogenous market rate series, read from *rate_scenario.csv*.

        Indexed by ``(scenario_id, t)`` and read as a step function of ``t``. It carries the
        quarterly average of daily VIX-squared driving the optional non-discretionary fee
        reset [S4][S6] and the 10-year Constant Maturity Treasury rate driving the optional
        formula-linked GMDB roll-up [S7]. Neither is used by the base run.
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.rate_scenario_file,                            # noqa: F821
            index_col=["scenario_id", "t"])

    def _f_gawa_pct_table(self):
        """The GAWA% grid by attained age band, read from *gawa_pct_table.csv*.

        Indexed by ``(gawa_grid, age_from)``; the applicable row is the highest ``age_from``
        at or below the attained age at the first withdrawal [S3].
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.gawa_pct_file, index_col=["gawa_grid", "age_from"])  # noqa: F821

    def _f_cdsc_table(self):
        """The withdrawal charge scale, read from *cdsc_table.csv*.

        Indexed by ``(cdsc_schedule, completed_years)``, where the key is completed years
        **since receipt of the premium being withdrawn**, not the contract year [S2].
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.cdsc_file,                                     # noqa: F821
            index_col=["cdsc_schedule", "completed_years"])

    def _f_transaction_table(self):
        """Scheduled policyholder transactions, read from *transaction_table.csv*.

        Indexed by ``(txn_id, t)`` with a gross premium and a gross withdrawal per month; a
        month with no row takes neither. Scheduled withdrawals are **added to** the
        utilization withdrawal the base run derives from the GLWB, which is how the excess
        algebra is exercised.
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.transaction_file, index_col=["txn_id", "t"])   # noqa: F821


    def input_dir(self):
        if self._has_input_dir:
            return self._v_input_dir
        else:
            val = self._v_input_dir = self._f_input_dir()
            self._has_input_dir = True
            return val

    def model_point_table(self):
        if self._has_model_point_table:
            return self._v_model_point_table
        else:
            val = self._v_model_point_table = self._f_model_point_table()
            self._has_model_point_table = True
            return val

    def mort_table(self):
        if self._has_mort_table:
            return self._v_mort_table
        else:
            val = self._v_mort_table = self._f_mort_table()
            self._has_mort_table = True
            return val

    def fund_table(self):
        if self._has_fund_table:
            return self._v_fund_table
        else:
            val = self._v_fund_table = self._f_fund_table()
            self._has_fund_table = True
            return val

    def return_scenario(self):
        if self._has_return_scenario:
            return self._v_return_scenario
        else:
            val = self._v_return_scenario = self._f_return_scenario()
            self._has_return_scenario = True
            return val

    def rate_scenario(self):
        if self._has_rate_scenario:
            return self._v_rate_scenario
        else:
            val = self._v_rate_scenario = self._f_rate_scenario()
            self._has_rate_scenario = True
            return val

    def gawa_pct_table(self):
        if self._has_gawa_pct_table:
            return self._v_gawa_pct_table
        else:
            val = self._v_gawa_pct_table = self._f_gawa_pct_table()
            self._has_gawa_pct_table = True
            return val

    def cdsc_table(self):
        if self._has_cdsc_table:
            return self._v_cdsc_table
        else:
            val = self._v_cdsc_table = self._f_cdsc_table()
            self._has_cdsc_table = True
            return val

    def transaction_table(self):
        if self._has_transaction_table:
            return self._v_transaction_table
        else:
            val = self._v_transaction_table = self._f_transaction_table()
            self._has_transaction_table = True
            return val










_v_cells_names_Projection = [
    'model_point',
    'policy_id',
    'age_at_entry',
    'sex',
    'designated_lives',
    'tax_status',
    'pols_if_init',
    'premium_tax_rate',
    'premium_single',
    'fund_set',
    'sub_ids',
    'alloc',
    'fund_expense_rate',
    'glwb_option',
    'stepup_basis',
    'gmdb_option',
    'cdsc_schedule',
    'fee_reset_rule',
    'rollup_rule',
    'wd_start_age',
    'wd_intensity',
    'scenario_id',
    'txn_id',
    'duration_mth_init',
    'is_inforce',
    'av_pp_init',
    'gwb_pp_init',
    'gawa_pp_init',
    'gawa_pct_init',
    'has_wd_init',
    'bb_pp_init',
    'rb_pp_init',
    'np_pp_init',
    'rp_pp_init',
    'adj_pp_init',
    'bonus_end_init',
    'policy_term',
    'proj_len',
    'duration_mth',
    'policy_year',
    'duration',
    'age',
    'age_at_anniv',
    'contract_quarter',
    'is_anniv',
    'is_quarterly_anniv',
    'is_year_start',
    't_of_month',
    'phase',
    'inv_return_mth',
    'scenario_rate',
    'vix_sq',
    'cmt10',
    'unit_growth',
    'sa_pp_at',
    'sa_pp',
    'av_pp_at',
    'av_pp',
    'sa_weight',
    'gross_inv_income_pp',
    'fund_expense_pp',
    'asset_charge_pp',
    'inv_income_pp',
    'prem_scheduled_pp',
    'premium_pp',
    'prem_to_av_pp',
    'wd_scheduled_pp',
    'is_wd_month',
    'is_wd_taken',
    'has_wd_by',
    'is_first_wd',
    'is_wd_year',
    'gawa_pct_at_age',
    'wd_limit_pp',
    'wd_glwb_pp',
    'wd_pp_due',
    'wd_pp',
    'sum_wd_pp',
    'wd_excess_pp',
    'wd_nonexcess_pp',
    'cv_pre_excess_pp',
    'excess_factor',
    'free_wd_allow',
    'free_wd_avail',
    'wd_free_pp',
    'free_wd_used_cum_pp',
    'wd_exempt_pp',
    'wd_chargeable_pp',
    'surr_charge_rate',
    'wd_charge_pp',
    'wd_payment_pp',
    'surr_free_pp',
    'surr_chargeable_pp',
    'surr_charge_pp',
    'surr_benefit_pp',
    'phi_glwb',
    'fee_rate_vix_raw',
    'fee_rate_vix_clip',
    'phi_glwb_vix',
    'phi_gmdb',
    'rollup_pct',
    'rollup_rate',
    'fee_glwb_pp_due',
    'fee_gmdb_pp_due',
    'maint_fee_pp_due',
    'charge_pp_due',
    'charge_scale',
    'fee_glwb_pp',
    'fee_gmdb_pp',
    'maint_fee_pp',
    'charge_pp',
    'charge_income_pp',
    'gwb_pp_at',
    'bb_pp_bef_anniv',
    'bonus_pp',
    'gwb_pp_aft_bonus',
    'stepup_base_pp',
    'is_stepup',
    'gwb_pp_aft_stepup',
    'gwb_adj_year',
    'is_gwb_adj_date',
    'adj_pp_bef_anniv',
    'adj_pp',
    'gwb_pp',
    'bb_pp',
    'bonus_end',
    'gawa_pct_fixed',
    'gawa_pp_at',
    'gawa_pp',
    'np_pp',
    'rp_reduction_pp',
    'rp_pp',
    'rb_prior_anniv_pp',
    'gmdb_allow_pp',
    'gmdb_wd_dfd_pp',
    'gmdb_wd_excess_pp',
    'gmdb_wd_factor',
    'gmdb_dfd_acc_pp',
    'gmdb_factor_acc',
    'rb_pp_at',
    'rb_pp',
    'gmdb_guarantee_pp',
    'db_pp',
    'gmdb_claim_pp',
    'forlife_flag',
    'depleted_flag',
    'glwb_payment_pp',
    'mort_rate',
    'mort_rate_mth',
    'lapse_rate_base',
    'moneyness_glwb',
    'moneyness_gmdb',
    'lapse_itm_mult',
    'lapse_dyn_mult',
    'lapse_wd_factor',
    'lapse_rate',
    'lapse_rate_mth',
    'pols_if',
    'pols_if_at',
    'pols_death',
    'pols_lapse',
    'pols_maturity',
    'pols_decr',
    'claim_pp',
    'claim_from_av_pp',
    'premiums',
    'prem_to_av',
    'asset_charges',
    'fees_glwb',
    'fees_gmdb',
    'maint_fees',
    'wd_charges',
    'charge_income',
    'withdrawals',
    'glwb_payments',
    'claims',
    'claims_from_av',
    'claims_over_av',
    'gmdb_claims',
    'commissions',
    'premium_taxes',
    'inflation_factor',
    'expenses',
    'net_cf',
    'net_cf_ga',
    'av_at',
    'inv_income',
    'wd_from_av',
    'charges_from_av',
    'av_change',
    'check_av_roll_fwd_resid',
    'check_av_roll_fwd',
    'check_pols_roll_fwd_resid',
    'check_pols_roll_fwd',
    'check_charge_split_resid',
    'check_charge_split',
    'result_cf',
    'result_pols',
    'result_av',
    'result_bases',
    'bench_net_cf',
]
_v_space_params_Projection = [
    'point_id',
]


class _c_Projection(_mx_sys.BaseSpace):

    def __init__(self, parent):

        # modelx variables
        self._space = self
        self._parent = parent
        self._model = parent._model
        self._name = "Projection"


        self._mx_spaces = {

        }

        self._mx_cells = {}     # Populated on calling self._cells
        self._mx_is_cells_set = False
        self._mx_itemspaces = {}
        self._mx_roots = []     # Dynamic Space only

        # Cache variables
        self._v_model_point = None
        self._has_model_point = False
        self._v_policy_id = None
        self._has_policy_id = False
        self._v_age_at_entry = None
        self._has_age_at_entry = False
        self._v_sex = None
        self._has_sex = False
        self._v_designated_lives = None
        self._has_designated_lives = False
        self._v_tax_status = None
        self._has_tax_status = False
        self._v_pols_if_init = None
        self._has_pols_if_init = False
        self._v_premium_tax_rate = None
        self._has_premium_tax_rate = False
        self._v_premium_single = None
        self._has_premium_single = False
        self._v_fund_set = None
        self._has_fund_set = False
        self._v_sub_ids = None
        self._has_sub_ids = False
        self._v_alloc = {}
        self._v_fund_expense_rate = {}
        self._v_glwb_option = None
        self._has_glwb_option = False
        self._v_stepup_basis = None
        self._has_stepup_basis = False
        self._v_gmdb_option = None
        self._has_gmdb_option = False
        self._v_cdsc_schedule = None
        self._has_cdsc_schedule = False
        self._v_fee_reset_rule = None
        self._has_fee_reset_rule = False
        self._v_rollup_rule = None
        self._has_rollup_rule = False
        self._v_wd_start_age = None
        self._has_wd_start_age = False
        self._v_wd_intensity = None
        self._has_wd_intensity = False
        self._v_scenario_id = None
        self._has_scenario_id = False
        self._v_txn_id = None
        self._has_txn_id = False
        self._v_duration_mth_init = None
        self._has_duration_mth_init = False
        self._v_is_inforce = None
        self._has_is_inforce = False
        self._v_av_pp_init = None
        self._has_av_pp_init = False
        self._v_gwb_pp_init = None
        self._has_gwb_pp_init = False
        self._v_gawa_pp_init = None
        self._has_gawa_pp_init = False
        self._v_gawa_pct_init = None
        self._has_gawa_pct_init = False
        self._v_has_wd_init = None
        self._has_has_wd_init = False
        self._v_bb_pp_init = None
        self._has_bb_pp_init = False
        self._v_rb_pp_init = None
        self._has_rb_pp_init = False
        self._v_np_pp_init = None
        self._has_np_pp_init = False
        self._v_rp_pp_init = None
        self._has_rp_pp_init = False
        self._v_adj_pp_init = None
        self._has_adj_pp_init = False
        self._v_bonus_end_init = None
        self._has_bonus_end_init = False
        self._v_policy_term = None
        self._has_policy_term = False
        self._v_proj_len = None
        self._has_proj_len = False
        self._v_duration_mth = {}
        self._v_policy_year = {}
        self._v_duration = {}
        self._v_age = {}
        self._v_age_at_anniv = {}
        self._v_contract_quarter = {}
        self._v_is_anniv = {}
        self._v_is_quarterly_anniv = {}
        self._v_is_year_start = {}
        self._v_t_of_month = {}
        self._v_phase = {}
        self._v_inv_return_mth = {}
        self._v_scenario_rate = {}
        self._v_vix_sq = {}
        self._v_cmt10 = {}
        self._v_unit_growth = {}
        self._v_sa_pp_at = {}
        self._v_sa_pp = {}
        self._v_av_pp_at = {}
        self._v_av_pp = {}
        self._v_sa_weight = {}
        self._v_gross_inv_income_pp = {}
        self._v_fund_expense_pp = {}
        self._v_asset_charge_pp = {}
        self._v_inv_income_pp = {}
        self._v_prem_scheduled_pp = {}
        self._v_premium_pp = {}
        self._v_prem_to_av_pp = {}
        self._v_wd_scheduled_pp = {}
        self._v_is_wd_month = {}
        self._v_is_wd_taken = {}
        self._v_has_wd_by = {}
        self._v_is_first_wd = {}
        self._v_is_wd_year = {}
        self._v_gawa_pct_at_age = {}
        self._v_wd_limit_pp = {}
        self._v_wd_glwb_pp = {}
        self._v_wd_pp_due = {}
        self._v_wd_pp = {}
        self._v_sum_wd_pp = {}
        self._v_wd_excess_pp = {}
        self._v_wd_nonexcess_pp = {}
        self._v_cv_pre_excess_pp = {}
        self._v_excess_factor = {}
        self._v_free_wd_allow = {}
        self._v_free_wd_avail = {}
        self._v_wd_free_pp = {}
        self._v_free_wd_used_cum_pp = {}
        self._v_wd_exempt_pp = {}
        self._v_wd_chargeable_pp = {}
        self._v_surr_charge_rate = {}
        self._v_wd_charge_pp = {}
        self._v_wd_payment_pp = {}
        self._v_surr_free_pp = {}
        self._v_surr_chargeable_pp = {}
        self._v_surr_charge_pp = {}
        self._v_surr_benefit_pp = {}
        self._v_phi_glwb = {}
        self._v_fee_rate_vix_raw = {}
        self._v_fee_rate_vix_clip = {}
        self._v_phi_glwb_vix = {}
        self._v_phi_gmdb = {}
        self._v_rollup_pct = None
        self._has_rollup_pct = False
        self._v_rollup_rate = {}
        self._v_fee_glwb_pp_due = {}
        self._v_fee_gmdb_pp_due = {}
        self._v_maint_fee_pp_due = {}
        self._v_charge_pp_due = {}
        self._v_charge_scale = {}
        self._v_fee_glwb_pp = {}
        self._v_fee_gmdb_pp = {}
        self._v_maint_fee_pp = {}
        self._v_charge_pp = {}
        self._v_charge_income_pp = {}
        self._v_gwb_pp_at = {}
        self._v_bb_pp_bef_anniv = {}
        self._v_bonus_pp = {}
        self._v_gwb_pp_aft_bonus = {}
        self._v_stepup_base_pp = {}
        self._v_is_stepup = {}
        self._v_gwb_pp_aft_stepup = {}
        self._v_gwb_adj_year = None
        self._has_gwb_adj_year = False
        self._v_is_gwb_adj_date = {}
        self._v_adj_pp_bef_anniv = {}
        self._v_adj_pp = {}
        self._v_gwb_pp = {}
        self._v_bb_pp = {}
        self._v_bonus_end = {}
        self._v_gawa_pct_fixed = {}
        self._v_gawa_pp_at = {}
        self._v_gawa_pp = {}
        self._v_np_pp = {}
        self._v_rp_reduction_pp = {}
        self._v_rp_pp = {}
        self._v_rb_prior_anniv_pp = {}
        self._v_gmdb_allow_pp = {}
        self._v_gmdb_wd_dfd_pp = {}
        self._v_gmdb_wd_excess_pp = {}
        self._v_gmdb_wd_factor = {}
        self._v_gmdb_dfd_acc_pp = {}
        self._v_gmdb_factor_acc = {}
        self._v_rb_pp_at = {}
        self._v_rb_pp = {}
        self._v_gmdb_guarantee_pp = {}
        self._v_db_pp = {}
        self._v_gmdb_claim_pp = {}
        self._v_forlife_flag = None
        self._has_forlife_flag = False
        self._v_depleted_flag = {}
        self._v_glwb_payment_pp = {}
        self._v_mort_rate = {}
        self._v_mort_rate_mth = {}
        self._v_lapse_rate_base = {}
        self._v_moneyness_glwb = {}
        self._v_moneyness_gmdb = {}
        self._v_lapse_itm_mult = {}
        self._v_lapse_dyn_mult = {}
        self._v_lapse_wd_factor = {}
        self._v_lapse_rate = {}
        self._v_lapse_rate_mth = {}
        self._v_pols_if = {}
        self._v_pols_if_at = {}
        self._v_pols_death = {}
        self._v_pols_lapse = {}
        self._v_pols_maturity = {}
        self._v_pols_decr = {}
        self._v_claim_pp = {}
        self._v_claim_from_av_pp = {}
        self._v_premiums = {}
        self._v_prem_to_av = {}
        self._v_asset_charges = {}
        self._v_fees_glwb = {}
        self._v_fees_gmdb = {}
        self._v_maint_fees = {}
        self._v_wd_charges = {}
        self._v_charge_income = {}
        self._v_withdrawals = {}
        self._v_glwb_payments = {}
        self._v_claims = {}
        self._v_claims_from_av = {}
        self._v_claims_over_av = {}
        self._v_gmdb_claims = {}
        self._v_commissions = {}
        self._v_premium_taxes = {}
        self._v_inflation_factor = {}
        self._v_expenses = {}
        self._v_net_cf = {}
        self._v_net_cf_ga = {}
        self._v_av_at = {}
        self._v_inv_income = {}
        self._v_wd_from_av = {}
        self._v_charges_from_av = {}
        self._v_av_change = {}
        self._v_check_av_roll_fwd_resid = {}
        self._v_check_av_roll_fwd = None
        self._has_check_av_roll_fwd = False
        self._v_check_pols_roll_fwd_resid = {}
        self._v_check_pols_roll_fwd = None
        self._has_check_pols_roll_fwd = False
        self._v_check_charge_split_resid = {}
        self._v_check_charge_split = None
        self._has_check_charge_split = False
        self._v_result_cf = None
        self._has_result_cf = False
        self._v_result_pols = None
        self._has_result_pols = False
        self._v_result_av = None
        self._has_result_av = False
        self._v_result_bases = None
        self._has_result_bases = False
        self._v_bench_net_cf = None
        self._has_bench_net_cf = False

    def _mx_assign_refs(self, io_data, pickle_data):

        # Reference assignment
        self.data = self._parent.Data
        self.point_id = 1
        self.omega_age = 120
        self.rate_sheet_date = '2026-04-27'
        self.asset_charge_me = 0.01
        self.asset_charge_admin = 0.003
        self.phi_glwb_curr = 0.0125
        self.phi_glwb_max = 0.03
        self.phi_gmdb_curr = 0.009
        self.phi_gmdb_max = 0.018
        self.fee_increase_max = 0.0025
        self.fee_reset_years = 5
        self.maint_fee = 35.0
        self.maint_fee_waiver_av = 50000.0
        self.free_wd_rate = 0.1
        self.surr_charge_years = 7
        self.bonus_pct = 0.06
        self.bonus_period_years = 10
        self.bonus_restart_age = 81
        self.gwb_cap = 10000000.0
        self.gwb_adj_pct = 1.05
        self.gwb_adj_age = 70
        self.gwb_adj_min_year = 12
        self.rollup_pct_young = 0.06
        self.rollup_pct_old = 0.05
        self.rollup_age_split = 70
        self.gmdb_growth_cutoff_age = 80
        self.forlife_age = 60
        self.av_depletion_threshold = 0.005
        self.lapse_rate_sc = 0.04
        self.lapse_rate_shock = 0.25
        self.lapse_rate_ult = 0.15
        self.lapse_itm_upper = 1.0
        self.lapse_itm_lower = 0.5
        self.lapse_itm_mult_coef = 1.25
        self.lapse_itm_threshold = 1.1
        self.lapse_wd_year_factor = 0.6
        self.vix_fee_coef = 0.0005
        self.vix_divisor = 33.0
        self.vix_offset = 10.0
        self.vix_band = 0.004
        self.vix_corridor_lo = 0.006
        self.vix_corridor_hi = 0.025
        self.cmt_spread = 0.01
        self.cmt_spread_predraw = 0.015
        self.cmt_round_step = 0.001
        self.cmt_floor = 0.04
        self.cmt_cap = 0.08
        self.expense_maint = 100.0
        self.expense_base_year = 2015
        self.valuation_year = 2026
        self.expense_av_rate = 0.0007
        self.inflation_rate = 0.025
        self.expense_acq = 0.0
        self.comm_rate_acq = 0.0
        self.math = _mx_sys.import_module('math')
        self.pd = _mx_sys.import_module('pandas')

    def _mx_copy_refs(self, base, base_root):

        # Reference assignment
        self.data = self._parent.Data if base.data._mx_is_in(base_root) else base.data
        self.point_id = base.point_id
        self.omega_age = base.omega_age
        self.rate_sheet_date = base.rate_sheet_date
        self.asset_charge_me = base.asset_charge_me
        self.asset_charge_admin = base.asset_charge_admin
        self.phi_glwb_curr = base.phi_glwb_curr
        self.phi_glwb_max = base.phi_glwb_max
        self.phi_gmdb_curr = base.phi_gmdb_curr
        self.phi_gmdb_max = base.phi_gmdb_max
        self.fee_increase_max = base.fee_increase_max
        self.fee_reset_years = base.fee_reset_years
        self.maint_fee = base.maint_fee
        self.maint_fee_waiver_av = base.maint_fee_waiver_av
        self.free_wd_rate = base.free_wd_rate
        self.surr_charge_years = base.surr_charge_years
        self.bonus_pct = base.bonus_pct
        self.bonus_period_years = base.bonus_period_years
        self.bonus_restart_age = base.bonus_restart_age
        self.gwb_cap = base.gwb_cap
        self.gwb_adj_pct = base.gwb_adj_pct
        self.gwb_adj_age = base.gwb_adj_age
        self.gwb_adj_min_year = base.gwb_adj_min_year
        self.rollup_pct_young = base.rollup_pct_young
        self.rollup_pct_old = base.rollup_pct_old
        self.rollup_age_split = base.rollup_age_split
        self.gmdb_growth_cutoff_age = base.gmdb_growth_cutoff_age
        self.forlife_age = base.forlife_age
        self.av_depletion_threshold = base.av_depletion_threshold
        self.lapse_rate_sc = base.lapse_rate_sc
        self.lapse_rate_shock = base.lapse_rate_shock
        self.lapse_rate_ult = base.lapse_rate_ult
        self.lapse_itm_upper = base.lapse_itm_upper
        self.lapse_itm_lower = base.lapse_itm_lower
        self.lapse_itm_mult_coef = base.lapse_itm_mult_coef
        self.lapse_itm_threshold = base.lapse_itm_threshold
        self.lapse_wd_year_factor = base.lapse_wd_year_factor
        self.vix_fee_coef = base.vix_fee_coef
        self.vix_divisor = base.vix_divisor
        self.vix_offset = base.vix_offset
        self.vix_band = base.vix_band
        self.vix_corridor_lo = base.vix_corridor_lo
        self.vix_corridor_hi = base.vix_corridor_hi
        self.cmt_spread = base.cmt_spread
        self.cmt_spread_predraw = base.cmt_spread_predraw
        self.cmt_round_step = base.cmt_round_step
        self.cmt_floor = base.cmt_floor
        self.cmt_cap = base.cmt_cap
        self.expense_maint = base.expense_maint
        self.expense_base_year = base.expense_base_year
        self.valuation_year = base.valuation_year
        self.expense_av_rate = base.expense_av_rate
        self.inflation_rate = base.inflation_rate
        self.expense_acq = base.expense_acq
        self.comm_rate_acq = base.comm_rate_acq
        self.math = base.math
        self.pd = base.pd

    def _f_model_point(self):
        """The selected model point as a Series."""
        return self.data.model_point_table().loc[self.point_id]                    # noqa: F821

    def _f_policy_id(self):
        """The contract identifier of the selected model point."""
        return self.model_point()["policy_id"]

    def _f_age_at_entry(self):
        """x: the issue age (ANB) of the selected model point."""
        return int(self.model_point()["age_at_entry"])

    def _f_sex(self):
        """The sex of the Designated Life, M or F."""
        return self.model_point()["sex"]

    def _f_designated_lives(self):
        """``single`` or ``joint``.

        Reported only: the joint-life election of the modeled GLWB is out of scope in the
        product spec, so the GAWA% grid and the For Life test are the single-life ones
        **[std]**.
        """
        return self.model_point()["designated_lives"]

    def _f_tax_status(self):
        """``NQ`` or ``Q``.

        Reported only. The base run is non-qualified **[std]**, which keeps the RMD term of
        ``L = max(GAWA, RMD)`` disclosed but inactive; no RMD module is implemented.
        """
        return self.model_point()["tax_status"]

    def _f_pols_if_init(self):
        """l(0): in-force probability at entry, 1 for a single-contract model point."""
        return float(self.model_point()["pols_if_init"])

    def _f_premium_tax_rate(self):
        """tau: premium tax deducted from the purchase payment, 0% **[std]**, 0-3.5% [S2].

        Set to zero so that GWB at issue equals gross premium and the worked example is
        checkable; premium tax is contractually deducted from the amounts that initialize the
        guarantee bases [S1].
        """
        return float(self.model_point()["premium_tax_rate"])

    def _f_premium_single(self):
        """The single purchase payment stated on the model point, paid at ``t = 0``."""
        return float(self.model_point()["premium"])

    def _f_fund_set(self):
        """The key into *fund_table.csv* naming this contract's subaccount allocation."""
        return self.model_point()["fund_set"]

    def _f_sub_ids(self):
        """The subaccount indices of the model point's allocation set, in file order.

        Two subaccounts **[std]** — the minimum that exercises pro-rata charge allocation and
        unit accounting. Real contracts offer far more; one carrier's build-your-own menu
        lists 76 options across 12 asset classes [S4].
        """
        return list(self.data.fund_table().loc[self.fund_set()].index)              # noqa: F821

    def _f_alloc(self, i):
        """alloc[i]: the share of net premium allocated to subaccount i, no rebalancing."""
        return float(self.data.fund_table().loc[(self.fund_set(), i), "alloc"])     # noqa: F821

    def _f_fund_expense_rate(self, i):
        """e_i: the annual fund expense ratio of subaccount i, paid to the fund [S2]."""
        return float(self.data.fund_table().loc[(self.fund_set(), i), "fund_expense"])  # noqa: F821

    def _f_glwb_option(self):
        """The GLWB election, and the key into the GAWA% grid; ``single_core`` [S3]."""
        return self.model_point()["glwb_option"]

    def _f_stepup_basis(self):
        """``annual_CV`` or ``highest_quarterly_CV`` [S1][S3].

        ``annual_CV`` is the representative election: the step-up test uses the Contract
        Value at the anniversary. ``highest_quarterly_CV`` uses the highest contract value
        over the four most recent Contract Quarterly Anniversaries; the source also adjusts
        each of those for subsequent premiums and withdrawals under the same
        dollar-for-dollar / proportional rule, which is **not implemented** — see the model
        docstring.
        """
        return self.model_point()["glwb_stepup_basis"]

    def _f_gmdb_option(self):
        """``rollup``, ``HQAV`` or ``basic``.

        ``rollup`` is the representative election: ``RB(t) = RB(t-1)(1 + rho)`` at each
        anniversary to the age cutoff, with a dollar-for-dollar withdrawal allowance applied
        at Contract Year end [S1][S3]. ``HQAV`` is the annual ratchet ``max(RB, AV)`` at each
        anniversary with proportional withdrawal treatment [S1][S4][S7]. ``basic`` is the
        included no-charge proportional return of premium [S1][S2]; on that election the base
        *is* the return of premium, so :func:`np_pp` is not floored under it as well — see
        :func:`gmdb_guarantee_pp`. The notes' fourth form, ``combination``, is **not
        implemented** — see the model docstring.
        """
        return self.model_point()["gmdb_option"]

    def _f_cdsc_schedule(self):
        """The key into *cdsc_table.csv* naming this contract's withdrawal charge scale."""
        return self.model_point()["cdsc_schedule"]

    def _f_fee_reset_rule(self):
        """``none``, ``quinquennial`` or ``vix``.

        ``none`` is the base run **[std]**: the insurer does not increase the rider charge
        and the owner does not opt out. ``quinquennial`` applies the maximum single increase
        of +0.25% at each fifth Contract Anniversary up to the guaranteed maximum [S1].
        ``vix`` applies a second carrier's non-discretionary VIX-squared formula [S4][S6].
        """
        return self.model_point()["fee_reset_rule"]

    def _f_rollup_rule(self):
        """``fixed`` or ``cmt_linked``.

        ``fixed`` is the base run **[std]**: 6.00% at election ages up to 69 and 5.00% from
        70 [S3]. ``cmt_linked`` is a third carrier's formula rate, a 20-day average 10-year
        CMT plus 1.00% (1.50% before the first withdrawal), rounded to 0.10%, floored at 4%
        and capped at 8% [S7].
        """
        return self.model_point()["rollup_rule"]

    def _f_wd_start_age(self):
        """The attained age at which GLWB withdrawals begin; 70 in the base run **[std]**.

        Zero means the contract never withdraws. The base-run value rests on the finding that
        activation clusters at the RMD age [REG-R64 **[unverified]**][REG-R57][REG-R58]. The
        prescribed alternative is VM-21's Withdrawal Delay Cohort Method, which is **not
        implemented**.
        """
        return int(self.model_point()["wd_start_age"])

    def _f_wd_intensity(self):
        """The fraction of the annual limit withdrawn once activated; 100% **[std]**.

        100% matches VM-21 §6.C.3's Guarantee Actuarial Present Value construction [R1]. The
        prescribed partial-withdrawal assumption is 90% for lifetime GMWBs and 70% for
        non-lifetime ones [R1].
        """
        return float(self.model_point()["wd_intensity"])

    def _f_scenario_id(self):
        """The scenario the model point runs on, a key into the two scenario tables."""
        return self.model_point()["scenario_id"]

    def _f_txn_id(self):
        """The scheduled transaction programme, a key into *transaction_table.csv*."""
        return self.model_point()["txn_id"]

    def _f_duration_mth_init(self):
        """Policy months already elapsed at ``t = 0``; 0 for an at-issue cell.

        An in-force cell enters mid-contract, so ``t = 1`` is policy month
        ``duration_mth_init() + 1``. The worked example's carried state is entered this way
        on model point 2.
        """
        return int(self.model_point()["duration_mth_init"])

    def _f_is_inforce(self):
        """True when the model point enters mid-contract rather than at issue."""
        return self.duration_mth_init() > 0

    def _f_av_pp_init(self):
        """AV carried into ``t = 0``; 0 at issue, the in-force cell's contract value else.

        An in-force contract value is split across subaccounts by ``alloc[i]`` **[std]**: the
        notes give an ``av_initial`` model point attribute but no subaccount split, and the
        worked example's carried state is exactly at its 60/40 target allocation.
        """
        return float(self.model_point()["av_init"])

    def _f_gwb_pp_init(self):
        """GWB carried into ``t = 0``; 0 at issue, where the premium creates it [S1]."""
        return float(self.model_point()["gwb_init"])

    def _f_gawa_pp_init(self):
        """GAWA carried into ``t = 0``; 0 until the first withdrawal fixes it [S1]."""
        return float(self.model_point()["gawa_init"])

    def _f_gawa_pct_init(self):
        """The GAWA% already locked at ``t = 0``; 0 when no withdrawal has been taken."""
        return float(self.model_point()["gawa_pct_init"])

    def _f_has_wd_init(self):
        """Whether a withdrawal had already been taken before ``t = 0``.

        Inferred from ``gawa_pct_init``, which is non-zero exactly when the GAWA% has been
        locked, so an in-force cell needs no separate flag column.
        """
        return self.gawa_pct_init() > 0.0

    def _f_bb_pp_init(self):
        """Bonus Base carried into ``t = 0``; it initializes at GWB [S1]."""
        return float(self.model_point()["bb_init"])

    def _f_rb_pp_init(self):
        """GMDB Benefit Base carried into ``t = 0``."""
        return float(self.model_point()["rb_init"])

    def _f_np_pp_init(self):
        """Cumulative Net Premiums carried into ``t = 0``."""
        return float(self.model_point()["np_init"])

    def _f_rp_pp_init(self):
        """Remaining Premium carried into ``t = 0``; the CDSC basis [S2]."""
        return float(self.model_point()["rp_init"])

    def _f_adj_pp_init(self):
        """GWB Adjustment carried into ``t = 0``; 105% of net premium at issue [S3]."""
        return float(self.model_point()["adj_init"])

    def _f_bonus_end_init(self):
        """The contract year the Bonus Period ends, carried into ``t = 0``.

        Zero on an at-issue cell, where it is set to ``bonus_period_years`` = 10 [S1].
        """
        return int(self.model_point()["bonus_end_init"])

    def _f_policy_term(self):
        """Contract term in years: entry age to ``omega_age`` **[std]**."""
        return self.omega_age - self.age_at_entry()                                 # noqa: F821

    def _f_proj_len(self):
        """Projection length in months from ``t = 0``, net of months already elapsed."""
        return 12 * self.policy_term() - self.duration_mth_init()

    def _f_duration_mth(self, t):
        """The policy month at projection month t: ``duration_mth_init() + t``."""
        return self.duration_mth_init() + t

    def _f_policy_year(self, t):
        """y(t) = ceil(policy month / 12): the contract year; 0 at issue."""
        return (self.duration_mth(t) + 11) // 12

    def _f_duration(self, t):
        """Completed contract years at month t, ``policy_year(t) - 1``, floored at 0."""
        return max(0, self.policy_year(t) - 1)

    def _f_age(self, t):
        """a(t) = x + y - 1: the attained age (ANB) during month t."""
        return self.age_at_entry() + self.duration(t)

    def _f_age_at_anniv(self, t):
        """The attained age just after the Contract Anniversary at the end of month t.

        ``x + y``, one more than :func:`age`, and the age the GMDB growth cutoff and the
        Bonus Period restart cutoff are stated against [S1].
        """
        return self.age_at_entry() + self.policy_year(t)

    def _f_contract_quarter(self, t):
        """k(t) = ceil(policy month / 3): the contract quarter containing month t."""
        return (self.duration_mth(t) + 2) // 3

    def _f_is_anniv(self, t):
        """True at the end of a Contract Anniversary month, ``policy month = 0 (mod 12)``."""
        return t >= 1 and t <= self.proj_len() and self.duration_mth(t) % 12 == 0

    def _f_is_quarterly_anniv(self, t):
        """True at a Contract Quarterly Anniversary, ``policy month = 0 (mod 3)`` **[std]**."""
        return t >= 1 and t <= self.proj_len() and self.duration_mth(t) % 3 == 0

    def _f_is_year_start(self, t):
        """True in the first month of a contract year, where SumW_y resets [S1]."""
        return t >= 1 and (self.duration_mth(t) - 1) % 12 == 0

    def _f_t_of_month(self, m):
        """The projection index t of policy month m; negative before the entry instant."""
        return m - self.duration_mth_init()

    def _f_phase(self, t):
        """ACCUM, DEPLETED or EXPIRED at month t."""
        if t > self.proj_len():
            return "EXPIRED"
        return "DEPLETED" if self.depleted_flag(t) else "ACCUM"

    def _f_inv_return_mth(self, t, i):
        """r_i(t): the gross monthly fund return of subaccount i, a scenario input.

        Read from *return_scenario.csv* as a step function of the **policy** month, so a flat
        path is one row per subaccount. VM-21 requires each variable subaccount to be mapped
        to a crafted proxy fund, normally a linear combination of recognized market indices
        [R1]; the model takes the return series as an input rather than hard-coding one.
        """
        sub = self.data.return_scenario().loc[(self.scenario_id(), i)]              # noqa: F821
        months = [m for m in sub.index if m <= max(self.duration_mth(t), 0)]
        return float(sub.loc[max(months), "gross_return"])

    def _f_scenario_rate(self, t, name):
        """Step-function lookup of column ``name`` in the model point's rate scenario.

        Each row of *rate_scenario.csv* states the level that holds from its own policy month
        until the next row of the same scenario, so a flat path is one row.
        """
        sub = self.data.rate_scenario().loc[self.scenario_id()]                     # noqa: F821
        months = [m for m in sub.index if m <= max(self.duration_mth(t), 0)]
        return float(sub.loc[max(months), name])

    def _f_vix_sq(self, k):
        """The quarterly average of daily VIX-squared for contract quarter k [S4][S6].

        Read at the last month of the quarter. Used only by the ``vix`` fee reset rule.
        """
        return self.scenario_rate(self.t_of_month(3 * k), "vix_sq")

    def _f_cmt10(self, t):
        """The 20-day average 10-year Constant Maturity Treasury rate at month t [S7].

        Used only by the ``cmt_linked`` roll-up rule.
        """
        return self.scenario_rate(t, "cmt10")

    def _f_unit_growth(self, t, i):
        """The monthly unit value factor of subaccount i.

        ``(1 + r_i(t)) x (1 - e_i/12) x (1 - (m + alpha)/12)`` — a monthly discretization of
        a daily accrual **[std]** [S2]. The fund's own expense and the base contract asset
        charge live **inside** the unit value; charges assessed per contract or on a benefit
        base do not, and are collected by cancelling units instead. Do not additionally
        compound daily: pick one discretization and document it, because reconciling to an
        admin system requires knowing which was used.
        """
        return ((1.0 + self.inv_return_mth(t, i))
                * (1.0 - self.fund_expense_rate(i) / 12.0)
                * (1.0 - (self.asset_charge_me + self.asset_charge_admin) / 12.0))  # noqa: F821

    def _f_sa_pp_at(self, t, i, timing):
        """SA_i at month t read at the point given by ``timing``; see the Space docstring.

        A withdrawal and a unit cancellation both scale the subaccount by
        ``(1 - amount / AV)`` — pro-rata deduction — so neither moves the value weights.
        """
        if t < 0:
            return 0.0
        if t == 0:
            return self.alloc(i) * (self.av_pp_init() + self.prem_to_av_pp(0))
        if self.depleted_flag(t - 1) or t > self.proj_len():
            return 0.0
        sa = self.sa_pp(t - 1, i)
        if timing == "BEF_PREM":
            return sa
        sa = sa + self.alloc(i) * self.prem_to_av_pp(t)
        if timing == "BEF_WD":
            return sa
        base = self.av_pp_at(t, "BEF_WD")
        sa = sa * (1.0 - self.wd_pp(t) / base) if base > 0.0 else 0.0
        if timing == "BEF_INV":
            return sa
        sa = sa * self.unit_growth(t, i)
        if timing == "BEF_FEE":
            return sa
        base = self.av_pp_at(t, "BEF_FEE")
        sa = sa * (1.0 - self.charge_pp(t) / base) if base > 0.0 else 0.0
        if timing == "EOM":
            return sa
        raise ValueError("invalid timing")

    def _f_sa_pp(self, t, i):
        """SA_i(t): the value of subaccount i per contract at the end of month t."""
        return self.sa_pp_at(t, i, "EOM")

    def _f_av_pp_at(self, t, timing):
        """AV at month t read at the point given by ``timing``: the sum over subaccounts."""
        return sum(self.sa_pp_at(t, i, timing) for i in self.sub_ids())

    def _f_av_pp(self, t):
        """AV(t): the contract value per contract at the end of month t."""
        return self.av_pp_at(t, "EOM")

    def _f_sa_weight(self, t, i):
        """w_i(t): the value weight of subaccount i, the pro-rata deduction key [S2].

        Read at ``BEF_FEE``, where the notes read it: after the month's growth and before the
        charges that cancel units.
        """
        base = self.av_pp_at(t, "BEF_FEE")
        return self.sa_pp_at(t, i, "BEF_FEE") / base if base > 0.0 else 0.0

    def _f_gross_inv_income_pp(self, t):
        """The gross fund return over month t, before any charge."""
        if t < 1 or self.depleted_flag(t - 1):
            return 0.0
        return sum(self.sa_pp_at(t, i, "BEF_INV") * self.inv_return_mth(t, i) for i in self.sub_ids())

    def _f_fund_expense_pp(self, t):
        """The funds' own expense collected inside the unit value.

        ``Σ_i SA_i(1 + r_i) e_i/12``. **Not insurer revenue** — it is paid to the underlying
        funds — so it never enters :func:`charge_income` or :func:`net_cf`.
        """
        if t < 1 or self.depleted_flag(t - 1):
            return 0.0
        return sum(self.sa_pp_at(t, i, "BEF_INV") * (1.0 + self.inv_return_mth(t, i))
                   * self.fund_expense_rate(i) / 12.0 for i in self.sub_ids())

    def _f_asset_charge_pp(self, t):
        """The M&E and administrative asset charge collected inside the unit value.

        ``Σ_i SA_i^{pre-charge}(t) (m + alpha)/12`` where the pre-charge value is net of the
        fund's own expense, which is deducted first inside :func:`unit_growth`. This is
        insurer charge income.
        """
        if t < 1 or self.depleted_flag(t - 1):
            return 0.0
        rate = (self.asset_charge_me + self.asset_charge_admin) / 12.0             # noqa: F821
        return sum(self.sa_pp_at(t, i, "BEF_INV") * (1.0 + self.inv_return_mth(t, i))
                   * (1.0 - self.fund_expense_rate(i) / 12.0) * rate for i in self.sub_ids())

    def _f_inv_income_pp(self, t):
        """The change in AV over month t from investment, net of both per-unit charges.

        ``AV(BEF_FEE) - AV(BEF_INV)``, and identically
        ``gross_inv_income_pp - fund_expense_pp - asset_charge_pp``.
        """
        if t < 1:
            return 0.0
        return self.av_pp_at(t, "BEF_FEE") - self.av_pp_at(t, "BEF_INV")

    def _f_prem_scheduled_pp(self, t):
        """The gross premium scheduled for month t in *transaction_table.csv*, else zero."""
        if t < 1:
            return 0.0
        table = self.data.transaction_table()                                 # noqa: F821
        key = (self.txn_id(), self.duration_mth(t))
        return float(table.loc[key, "prem_amount"]) if key in table.index else 0.0

    def _f_premium_pp(self, t):
        """P(t): the gross premium paid at BOM of month t.

        The model point's single purchase payment at ``t = 0``, plus anything scheduled in
        *transaction_table.csv*. The chassis is flexible-premium [S1][S2] and premium receipt
        is retained as an active term in every guarantee-base recursion, so a subsequent
        payment is a data change rather than a formula change.
        """
        if t == 0:
            return self.premium_single() + self.prem_scheduled_pp(t)
        if t < 0 or t > self.proj_len() or self.depleted_flag(t - 1):
            return 0.0
        return self.prem_scheduled_pp(t)

    def _f_prem_to_av_pp(self, t):
        """P(t)(1 - tau): the net premium that buys units and raises the guarantee bases.

        The per-contract counterpart of :func:`prem_to_av`, and the name every
        account-value model in this library uses for the premium credited to the account
        value. Not to be confused with ``WholeLife_US_A.premium_net_pp``, which is a *gross*
        premium net of the dividend offset — a different concept entirely.
        """
        return self.premium_pp(t) * (1.0 - self.premium_tax_rate())

    def _f_wd_scheduled_pp(self, t):
        """The gross withdrawal scheduled for month t in *transaction_table.csv*, else zero."""
        if t < 1:
            return 0.0
        table = self.data.transaction_table()                                 # noqa: F821
        key = (self.txn_id(), self.duration_mth(t))
        return float(table.loc[key, "wd_amount"]) if key in table.index else 0.0

    def _f_is_wd_month(self, t):
        """True when the GLWB utilization withdrawal falls in month t.

        Base run **[std]**: the contract activates in the first month of the contract year in
        which the attained age reaches :func:`wd_start_age`, and withdraws in the first month
        of every contract year thereafter. ``wd_start_age = 0`` never withdraws.
        """
        if t < 1 or t > self.proj_len() or self.wd_start_age() <= 0:
            return False
        if self.depleted_flag(t - 1) or not self.is_year_start(t):
            return False
        return self.age(t) >= self.wd_start_age()

    def _f_is_wd_taken(self, t):
        """True when any withdrawal is taken in month t, before its amount is known.

        Stated as a predicate rather than ``wd_pp(t) > 0`` so that the first-withdrawal test
        can run *before* the GAWA% is fixed, which is what the amount itself depends on.
        """
        if t < 1 or t > self.proj_len() or self.depleted_flag(t - 1):
            return False
        return self.wd_scheduled_pp(t) > 0.0 or self.is_wd_month(t)

    def _f_has_wd_by(self, t):
        """True when a withdrawal has been taken at or before month t."""
        if t < 1:
            return self.has_wd_init()
        return self.has_wd_by(t - 1) or self.is_wd_taken(t)

    def _f_is_first_wd(self, t):
        """True in the month of the contract's first withdrawal.

        The notes are explicit that this test must run **before** the annual limit ``L`` is
        formed: a first withdrawal tested against ``GAWA = 0`` would score entirely as excess
        and wreck both benefit bases [S1].
        """
        return self.is_wd_taken(t) and not self.has_wd_by(t - 1)

    def _f_is_wd_year(self, t):
        """True when any withdrawal falls in the contract year containing month t.

        Drives the VM-21 withdrawal-year surrender factor ``kappa`` [R1] and the rule that
        *any* withdrawal in a Contract Year kills that year's bonus [S1].
        """
        first = self.t_of_month(12 * (self.policy_year(t) - 1) + 1)
        return any(self.is_wd_taken(u) for u in range(max(1, first),
                                                 min(first + 12, self.proj_len() + 1)))

    def _f_gawa_pct_at_age(self, a):
        """g(a): the GAWA% for attained age a, from *gawa_pct_table.csv* [S3]."""
        grid = self.data.gawa_pct_table().loc[self.glwb_option()]                  # noqa: F821
        bands = [b for b in grid.index if b <= a]
        if not bands:
            return 0.0
        return float(grid.loc[max(bands), "gawa_pct"])

    def _f_wd_limit_pp(self, t):
        """L(t) = max(GAWA, RMD): the annual withdrawal limit governing month t [S1].

        At the first withdrawal the GAWA is fixed on the **pre-withdrawal** GWB, so the limit
        is formed from that. The RMD term is disclosed but inactive: the base run is
        non-qualified and no RMD module is implemented.
        """
        if self.is_first_wd(t):
            return self.gawa_pct_at_age(self.age(t)) * self.gwb_pp_at(t, "BEF_WD")
        return self.gawa_pp_at(t, "BEF_WD")

    def _f_wd_glwb_pp(self, t):
        """The GLWB utilization withdrawal: ``wd_intensity x L(t)`` once activated **[std]**."""
        return self.wd_intensity() * self.wd_limit_pp(t) if self.is_wd_month(t) else 0.0

    def _f_wd_pp_due(self, t):
        """The gross withdrawal requested at BOM of month t, before capping at AV.

        Scheduled withdrawals **add to** the utilization withdrawal, which is how a model
        point exercises the excess algebra without disturbing the base run.
        """
        if t < 1 or t > self.proj_len() or self.depleted_flag(t - 1):
            return 0.0
        return self.wd_scheduled_pp(t) + self.wd_glwb_pp(t)

    def _f_wd_pp(self, t):
        """W(t): the gross amount removed from the contract value at BOM of month t.

        Measured **inclusive of withdrawal charges, MVAs, advisory fees and every other
        charge** for all guarantee calculations [S1]; using net proceeds would understate the
        benefit-base reduction. Capped at the available contract value **[std]**.
        """
        return min(self.wd_pp_due(t), self.av_pp_at(t, "BEF_WD"))

    def _f_sum_wd_pp(self, t):
        """SumW_y: cumulative withdrawals in the current contract year, including W(t) [S1]."""
        if t < 1:
            return 0.0
        prev = 0.0 if self.is_year_start(t) else self.sum_wd_pp(t - 1)
        return prev + self.wd_pp(t)

    def _f_wd_excess_pp(self, t):
        """E(t) = min(W, SumW_y - L) if SumW_y > L else 0: the excess withdrawal [S1].

        This is the **guarantee** excess, not the charge base — see the Space docstring's
        note on the divergence from :mod:`.MYGA_US_S`.
        """
        if self.wd_pp(t) <= 0.0:
            return 0.0
        over = self.sum_wd_pp(t) - self.wd_limit_pp(t)
        return min(self.wd_pp(t), over) if over > 0.0 else 0.0

    def _f_wd_nonexcess_pp(self, t):
        """N(t) = W(t) - E(t): the guaranteed portion of the withdrawal [S1]."""
        return self.wd_pp(t) - self.wd_excess_pp(t)

    def _f_cv_pre_excess_pp(self, t):
        """CV_pre: the contract value after the non-excess portion has been deducted [S1].

        The order is decisive: the non-excess portion reduces the base dollar-for-dollar
        **first**, and the proportional factor for the excess is computed against the
        contract value *after* that reduction. Reversing it changes both GWB and GAWA.
        """
        return self.av_pp_at(t, "BEF_WD") - self.wd_nonexcess_pp(t)

    def _f_excess_factor(self, t):
        """``1 - E(t)/CV_pre``: the pro-rata factor applied to GWB, GAWA and BB [S1]."""
        base = self.cv_pre_excess_pp(t)
        if base <= 0.0:
            return 0.0
        return max(0.0, 1.0 - self.wd_excess_pp(t) / base)

    def _f_free_wd_allow(self, t):
        """The charge-free amount at month t: earnings first, then 10% of Remaining Premium.

        The notes state it as ``max(0, AV - RP)`` plus ``max(0, 0.10 RP - earnings)``, which
        is ``max(earnings, 0.10 x RP)`` [S1]. Aged-out premium is free too, which the CDSC
        scale delivers by reaching 0.0% at seven completed years [S2].
        """
        rp = self.rp_pp(t - 1) + self.premium_pp(t) if t >= 1 else self.rp_pp_init()
        earnings = max(0.0, self.av_pp_at(t, "BEF_WD") - rp)
        return max(earnings, self.free_wd_rate * rp)                          # noqa: F821

    def _f_free_wd_avail(self, t):
        """The free-withdrawal allowance still unused in the contract year at BOM of month t."""
        if t < 1:
            return 0.0
        used = 0.0 if self.is_year_start(t) else self.free_wd_used_cum_pp(t - 1)
        return max(0.0, self.free_wd_allow(t) - used)

    def _f_wd_free_pp(self, t):
        """The free-allowance portion of month t's withdrawal: ``min(FW, E(t))``.

        The chassis name for the same thing — :mod:`.MYGA_US_S` has
        ``min(W, FW)`` — differing only in that here the allowance is applied to the
        *guarantee excess* rather than to the whole withdrawal, because the non-excess
        portion is already exempt from the CDSC under the within-``L`` rule [S1]. The
        portion of ``W(t)`` bearing no charge *at all* is therefore the wider
        :func:`wd_exempt_pp`, not this cells.
        """
        return min(self.free_wd_avail(t), self.wd_excess_pp(t))

    def _f_free_wd_used_cum_pp(self, t):
        """The free allowance consumed so far in the contract year, including month t.

        The year-to-date cumulative of :func:`wd_free_pp`, reset at each contract year
        start; it is what :func:`free_wd_avail` and :func:`surr_free_pp` net off.
        """
        if t < 1:
            return 0.0
        prev = 0.0 if self.is_year_start(t) else self.free_wd_used_cum_pp(t - 1)
        return prev + self.wd_free_pp(t)

    def _f_wd_exempt_pp(self, t):
        """The portion of W(t) bearing no withdrawal charge at all.

        Two exemptions stack: **no CDSC applies to cumulative withdrawals within L** [S1],
        which covers the non-excess portion outright, and the free-withdrawal allowance
        covers part of what is left. So this is identically
        ``wd_nonexcess_pp(t) + wd_free_pp(t)``, and it — not :func:`wd_free_pp` — is what
        complements :func:`wd_chargeable_pp`.
        """
        return min(self.wd_pp(t), self.wd_nonexcess_pp(t) + self.free_wd_avail(t))

    def _f_wd_chargeable_pp(self, t):
        """The portion of W(t) exposed to the CDSC: ``max(0, E(t) - free allowance)``."""
        return self.wd_pp(t) - self.wd_exempt_pp(t)

    def _f_surr_charge_rate(self, t):
        """The CDSC rate at month t, read off the **contract duration** [S2].

        The scale runs 8.5% down to 0.0% at seven completed years and is read from
        *cdsc_table.csv*, keyed by :func:`duration`.

        The notes key it on *completed years since receipt of the premium being withdrawn*
        [S2], which coincides with the contract duration only while the contract is single
        premium. It is **not implemented** by premium tranche: :func:`rp_pp` carries Remaining
        Premium as one undifferentiated pool, so a subsequent premium does not restart its
        own charge clock — model point 4 pays a second premium at policy month 73 and is read
        at that contract's 6-completed-year band rather than at the new tranche's 8.5%. Named
        in the model docstring's and the README's *not implemented* lists and pinned by a
        test; splitting the pool needs a withdrawal-ordering rule across tranches that no
        retrieved source states.
        """
        grid = self.data.cdsc_table().loc[self.cdsc_schedule()]                    # noqa: F821
        years = min(self.duration(t), int(grid.index.max()))
        return float(grid.loc[years, "surr_charge_rate"])

    def _f_wd_charge_pp(self, t):
        """c(t): the withdrawal charge on month t's withdrawal [S2]."""
        return self.surr_charge_rate(t) * self.wd_chargeable_pp(t)

    def _f_wd_payment_pp(self, t):
        """The cash paid on month t's withdrawal, ``W(t) - c(t)``."""
        return self.wd_pp(t) - self.wd_charge_pp(t)

    def _f_surr_free_pp(self, t):
        """The charge-free amount left for a full surrender at the end of month t."""
        rp = self.rp_pp(t)
        earnings = max(0.0, self.av_pp(t) - rp)
        allow = max(earnings, self.free_wd_rate * rp)                         # noqa: F821
        return max(0.0, allow - self.free_wd_used_cum_pp(t))

    def _f_surr_chargeable_pp(self, t):
        """The Remaining Premium withdrawn on a full surrender, net of the free amount [S2]."""
        return min(self.rp_pp(t), max(0.0, self.av_pp(t) - self.surr_free_pp(t)))

    def _f_surr_charge_pp(self, t):
        """The CDSC on a full surrender at the end of month t."""
        return self.surr_charge_rate(t) * self.surr_chargeable_pp(t)

    def _f_surr_benefit_pp(self, t):
        """Surrender proceeds: ``AV(t)`` less the CDSC.

        There is **no nonforfeiture floor** under this value. NAIC Model #805 expressly
        excludes variable annuities and reaches a VA only through its fixed account under
        Model #250 §7.B [REG-R42][REG-R43], and electing the Roll-up GMDB removes the Fixed
        Account Options [S1]. Contrast :mod:`.MYGA_US_S`, where
        ``max(SV, MGSV)`` is the whole point.
        """
        return self.av_pp(t) - self.surr_charge_pp(t)

    def _f_phi_glwb(self, t):
        """phi_G: the annual GLWB rider charge rate in force in month t.

        1.25% of the GWB currently [S3], guaranteed maximum 3.00% **[std]** within an
        observed 1.20%-3.00% band by option and vintage [S1]. ``fee_reset_rule`` selects the
        reset mechanism; the base run does not increase the charge and the owner does not opt
        out **[std]**, because opting out forfeits bonus, step-up and GWB Adjustment and
        blocks future premium [S1], so a rational opt-out is a joint decision rather than an
        independent lapse-style rate.
        """
        rule = self.fee_reset_rule()
        if rule == "none":
            return self.phi_glwb_curr                                         # noqa: F821
        elif rule == "quinquennial":
            steps = self.duration(t) // self.fee_reset_years                       # noqa: F821
            return min(self.phi_glwb_max,                                     # noqa: F821
                       self.phi_glwb_curr + self.fee_increase_max * steps)         # noqa: F821
        elif rule == "vix":
            return self.phi_glwb_vix(self.contract_quarter(t))
        else:
            raise ValueError("invalid fee_reset_rule")

    def _f_fee_rate_vix_raw(self, phi_0, vix_sq_avg):
        """The unclipped VIX-squared fee formula [S4][S6].

        ``phi_0 + 0.05% x [ QuarterlyAverage(daily VIX^2) / 33 - 10 ]``. The disclosed
        examples are an initial 1.45% with a quarterly average of 204.42 giving 1.26%, and
        602.30 giving an unclipped 1.86%.
        """
        return phi_0 + self.vix_fee_coef * (vix_sq_avg / self.vix_divisor - self.vix_offset)  # noqa: F821

    def _f_fee_rate_vix_clip(self, prior, raw):
        """Clip a VIX-formula rate to the movement band and the absolute corridor [S4].

        The band is +/-0.40% annualized against the prior quarter's rate (advisory class) and
        the corridor is [0.60%, 2.50%]. The second disclosed example clips to 1.82% against a
        prior rate of 1.42%.
        """
        lo = max(self.vix_corridor_lo, prior - self.vix_band)                      # noqa: F821
        hi = min(self.vix_corridor_hi, prior + self.vix_band)                      # noqa: F821
        return min(hi, max(lo, raw))

    def _f_phi_glwb_vix(self, k):
        """The VIX-formula GLWB charge rate in contract quarter k [S4][S6]."""
        if k <= 1:
            return self.phi_glwb_curr                                         # noqa: F821
        prior = self.phi_glwb_vix(k - 1)
        return self.fee_rate_vix_clip(
            prior, self.fee_rate_vix_raw(self.phi_glwb_curr, self.vix_sq(k)))           # noqa: F821

    def _f_phi_gmdb(self, t):
        """phi_D: the annual GMDB rider charge rate in force in month t.

        0.90% of the GMDB Benefit Base currently, guaranteed maximum 1.80% [S2][S3]. The
        ``basic`` death benefit is included at no charge [S1][S2], so the rate is zero there.
        """
        return 0.0 if self.gmdb_option() == "basic" else self.phi_gmdb_curr        # noqa: F821

    def _f_rollup_pct(self):
        """rho at election: 6.00% at age 69 or younger, 5.00% from 70 [S3]."""
        if self.age_at_entry() >= self.rollup_age_split:                           # noqa: F821
            return self.rollup_pct_old                                        # noqa: F821
        return self.rollup_pct_young                                          # noqa: F821

    def _f_rollup_rate(self, t):
        """rho(t): the GMDB roll-up percentage credited at the anniversary ending month t.

        ``fixed`` is the base run [S3]. ``cmt_linked`` is a third carrier's formula rate:
        the 10-year CMT plus 1.00%, or 1.50% before the first withdrawal, rounded to 0.10%,
        floored at 4% and capped at 8% [S7].
        """
        if self.rollup_rule() == "fixed":
            return self.rollup_pct()
        elif self.rollup_rule() == "cmt_linked":
            spread = self.cmt_spread if self.has_wd_by(t) else self.cmt_spread_predraw  # noqa: F821
            raw = self.cmt10(t) + spread
            step = self.cmt_round_step                                        # noqa: F821
            rounded = self.math.floor(raw / step + 0.5) * step                # noqa: F821
            return max(self.cmt_floor, min(self.cmt_cap, rounded))                 # noqa: F821
        else:
            raise ValueError("invalid rollup_rule")

    def _f_fee_glwb_pp_due(self, t):
        """Fee_G = (phi_G/4) x GWB at a Contract Quarterly Anniversary [S1][S3].

        The base is the **benefit base, not the account value** — putting the rider fee on
        account value is the most common and most consequential error on this product. The
        fee therefore rises as markets fall, until the account reaches zero, at which point
        it stops [S4].
        """
        if t < 1 or self.depleted_flag(t - 1) or not self.is_quarterly_anniv(t):
            return 0.0
        return (self.phi_glwb(t) / 4.0) * self.gwb_pp_at(t, "BEF_ANNIV")

    def _f_fee_gmdb_pp_due(self, t):
        """Fee_D = (phi_D/4) x RB at a Contract Quarterly Anniversary [S2][S3].

        The charge base is the GMDB Benefit Base; the quarterly frequency aligns it with the
        GLWB fee **[std]**, the research file recording quarterly for the GMWB family only.
        """
        if t < 1 or self.depleted_flag(t - 1) or not self.is_quarterly_anniv(t):
            return 0.0
        return (self.phi_gmdb(t) / 4.0) * self.rb_pp_at(t, "BEF_ANNIV")

    def _f_maint_fee_pp_due(self, t):
        """f_c: the $35 annual contract fee, waived at a contract value of $50,000 or more.

        Assessed at the Contract Anniversary and deducted proportionally across investment
        divisions [S2]. The waiver is tested on the contract value after the rider fees
        **[std]**, the notes placing the contract fee after them in the processing order.
        """
        if t < 1 or self.depleted_flag(t - 1) or not self.is_anniv(t):
            return 0.0
        after_riders = (self.av_pp_at(t, "BEF_FEE")
                        - self.fee_glwb_pp_due(t) - self.fee_gmdb_pp_due(t))
        return 0.0 if after_riders >= self.maint_fee_waiver_av else self.maint_fee  # noqa: F821

    def _f_charge_pp_due(self, t):
        """The total unit cancellation due at EOM before capping at the contract value."""
        return self.fee_glwb_pp_due(t) + self.fee_gmdb_pp_due(t) + self.maint_fee_pp_due(t)

    def _f_charge_scale(self, t):
        """The fraction of the charges due that the contract value can actually pay **[std]**.

        Charges are collected only up to the available contract value; the shortfall is not
        carried forward. This binds in at most one month per contract, the one in which the
        account is exhausted, and it is what makes :func:`check_av_roll_fwd` close there.
        """
        due = self.charge_pp_due(t)
        if due <= 0.0:
            return 0.0
        return min(1.0, self.av_pp_at(t, "BEF_FEE") / due)

    def _f_fee_glwb_pp(self, t):
        """The GLWB rider fee actually collected in month t."""
        return self.fee_glwb_pp_due(t) * self.charge_scale(t)

    def _f_fee_gmdb_pp(self, t):
        """The GMDB rider fee actually collected in month t."""
        return self.fee_gmdb_pp_due(t) * self.charge_scale(t)

    def _f_maint_fee_pp(self, t):
        """The annual contract fee actually collected in month t."""
        return self.maint_fee_pp_due(t) * self.charge_scale(t)

    def _f_charge_pp(self, t):
        """The total unit cancellation at EOM of month t: the two rider fees and f_c."""
        return self.charge_pp_due(t) * self.charge_scale(t)

    def _f_charge_income_pp(self, t):
        """Insurer charge income per contract in month t.

        The asset charge collected inside the unit value plus the charges collected by unit
        cancellation. The funds' own expense is **not** included — it is paid to the funds.
        """
        return self.asset_charge_pp(t) + self.charge_pp(t)

    def _f_gwb_pp_at(self, t, timing):
        """GWB at month t read at ``BEF_PREM``, ``BEF_WD`` or ``BEF_ANNIV`` [S1]."""
        if t < 1:
            return self.gwb_pp_init()
        if self.depleted_flag(t - 1):
            return self.gwb_pp(t - 1)
        g = self.gwb_pp(t - 1)
        if timing == "BEF_PREM":
            return g
        g = min(self.gwb_cap, g + self.prem_to_av_pp(t))                           # noqa: F821
        if timing == "BEF_WD":
            return g
        if self.wd_pp(t) > 0.0:
            if self.sum_wd_pp(t) <= self.wd_limit_pp(t):
                g = max(g - self.wd_pp(t), 0.0)
            else:
                g = max((g - self.wd_nonexcess_pp(t)) * self.excess_factor(t), 0.0)
        if timing == "BEF_ANNIV":
            return g
        raise ValueError("invalid timing")

    def _f_bb_pp_bef_anniv(self, t):
        """The Bonus Base carried into the anniversary events of month t [S1].

        Increased by net premium, set to ``min(GWB_after, BB_before)`` on an excess
        withdrawal, and otherwise unaffected by withdrawals. Applying the bonus does not
        change it.
        """
        if t < 1:
            return self.bb_pp_init()
        if self.depleted_flag(t - 1):
            return self.bb_pp(t - 1)
        b = min(self.gwb_cap, self.bb_pp(t - 1) + self.prem_to_av_pp(t))                # noqa: F821
        if self.wd_pp(t) > 0.0 and self.sum_wd_pp(t) > self.wd_limit_pp(t):
            b = min(self.gwb_pp_at(t, "BEF_ANNIV"), b)
        return b

    def _f_bonus_pp(self, t):
        """The GLWB bonus credited at the Contract Anniversary ending month t.

        ``b x BB`` if **no withdrawal was taken in the contract year** and the year is within
        the Bonus Period [S1]. *Any* withdrawal kills the whole year's bonus, including an
        automatic withdrawal or an RMD; pro-rating it for a partial year is wrong.
        """
        if not self.is_anniv(t) or self.depleted_flag(t - 1):
            return 0.0
        if self.policy_year(t) > self.bonus_end(t - 1) or self.is_wd_year(t):
            return 0.0
        return self.bonus_pct * self.bb_pp_bef_anniv(t)                            # noqa: F821

    def _f_gwb_pp_aft_bonus(self, t):
        """GWB after anniversary sub-step 3, the GLWB bonus."""
        return self.gwb_pp_at(t, "BEF_ANNIV") + self.bonus_pp(t)

    def _f_stepup_base_pp(self, t):
        """The contract value the step-up test is made against [S1][S3].

        ``annual_CV``: the Contract Value at the anniversary. ``highest_quarterly_CV``: the
        highest contract value over the four most recent Contract Quarterly Anniversaries.
        """
        basis = self.stepup_basis()
        if basis == "annual_CV":
            return self.av_pp(t)
        elif basis == "highest_quarterly_CV":
            return max(self.av_pp(t - 3 * j) for j in range(0, 4) if t - 3 * j >= 0)
        else:
            raise ValueError("invalid stepup_basis")

    def _f_is_stepup(self, t):
        """True when the anniversary step-up fires: the contract value exceeds the GWB [S1]."""
        return self.is_anniv(t) and self.stepup_base_pp(t) > self.gwb_pp_aft_bonus(t)

    def _f_gwb_pp_aft_stepup(self, t):
        """GWB after anniversary sub-step 4, the step-up.

        The **[std]** order — bonus first, then step-up — gives
        ``max(GWB_old + bonus, AV)``; the reverse gives ``max(GWB_old, AV) + bonus``, which
        is strictly more generous. The research file does not settle the interaction, and the
        choice made here follows the one design in the set that states it explicitly [S8].
        Treat the alternative as a first-order sensitivity, not a rounding issue.
        """
        return max(self.gwb_pp_aft_bonus(t), self.stepup_base_pp(t)) if self.is_anniv(t) else self.gwb_pp_aft_bonus(t)

    def _f_gwb_adj_year(self):
        """The contract year of the GWB Adjustment Date [S1].

        The later of the anniversary on or after the Designated Life's 70th birthday and the
        12th Contract Anniversary.
        """
        return max(self.gwb_adj_min_year, self.gwb_adj_age - self.age_at_entry())       # noqa: F821

    def _f_is_gwb_adj_date(self, t):
        """True at the Contract Anniversary that is the GWB Adjustment Date."""
        return self.is_anniv(t) and self.policy_year(t) == self.gwb_adj_year()

    def _f_adj_pp_bef_anniv(self, t):
        """ADJ carried into the anniversary events of month t [S1][S3].

        Initialized at 105% of net premium at endorsement, increased by ``s x P(1-tau)`` for
        premiums before the first anniversary after endorsement and by ``P(1-tau)`` for later
        ones, and **voided without value** by any earlier partial withdrawal.
        """
        if t < 1:
            return self.adj_pp_init()
        if self.has_wd_by(t):
            return 0.0
        rate = self.gwb_adj_pct if self.duration_mth(t) <= 12 else 1.0             # noqa: F821
        return self.adj_pp(t - 1) + rate * self.prem_to_av_pp(t)

    def _f_adj_pp(self, t):
        """ADJ(t): the GWB Adjustment amount at the end of month t; 0 once it terminates."""
        if t < 0:
            return 0.0
        if t == 0:
            return self.adj_pp_init() + self.gwb_adj_pct * self.prem_to_av_pp(0)        # noqa: F821
        if self.is_gwb_adj_date(t) or self.policy_year(t) > self.gwb_adj_year():
            return 0.0
        return self.adj_pp_bef_anniv(t)

    def _f_gwb_pp(self, t):
        """GWB(t): the Guaranteed Withdrawal Balance at the end of month t [S1].

        Anniversary sub-steps 5 to 7 finish here: the GWB Adjustment Date test, which raises
        the GWB to the Adjustment only if no withdrawal has ever been taken, and the
        $10,000,000 cap. In the depleted state the balance is run down by each payment when
        the For Life Guarantee is not in effect, and is left alone when it is.
        """
        if t < 0:
            return 0.0
        if t == 0:
            return min(self.gwb_cap, self.gwb_pp_init() + self.prem_to_av_pp(0))        # noqa: F821
        if self.depleted_flag(t - 1):
            g = self.gwb_pp(t - 1)
            return g if self.forlife_flag() else max(0.0, g - self.glwb_payment_pp(t))
        g = self.gwb_pp_aft_stepup(t)
        if self.is_gwb_adj_date(t) and not self.has_wd_by(t):
            g = max(g, self.adj_pp_bef_anniv(t))
        return min(self.gwb_cap, g)                                           # noqa: F821

    def _f_bb_pp(self, t):
        """BB(t): the Bonus Base at the end of month t [S1].

        A step-up sets it to ``max(GWB_after_step-up, BB_before)``; the bonus itself never
        changes it.
        """
        if t < 0:
            return 0.0
        if t == 0:
            return min(self.gwb_cap, self.bb_pp_init() + self.prem_to_av_pp(0))         # noqa: F821
        if self.depleted_flag(t - 1):
            return self.bb_pp(t - 1)
        b = self.bb_pp_bef_anniv(t)
        if self.is_stepup(t):
            b = max(self.gwb_pp_aft_stepup(t), b)
        return min(self.gwb_cap, b)                                           # noqa: F821

    def _f_bonus_end(self, t):
        """The contract year in which the Bonus Period ends [S1].

        Ten Contract Years from the endorsement effective date, **restarting** on each
        Bonus-Base-increasing step-up occurring on or before the anniversary following the
        Designated Life's 80th birthday. A hard-coded 10-year window from issue materially
        understates the guarantee in rising markets.
        """
        if t <= 0:
            return self.bonus_end_init() if self.is_inforce() else self.bonus_period_years  # noqa: F821
        prev = self.bonus_end(t - 1)
        if (self.is_stepup(t) and self.age_at_anniv(t) <= self.bonus_restart_age        # noqa: F821
                and self.gwb_pp_aft_stepup(t) > self.bb_pp_bef_anniv(t)):
            return self.policy_year(t) + self.bonus_period_years                   # noqa: F821
        return prev

    def _f_gawa_pct_fixed(self, t):
        """The GAWA% locked at the first withdrawal; 0 until then [S1].

        If the contract value reaches zero with the percentage not yet fixed, it is fixed at
        the percentage for the attained age at that moment [S1].
        """
        if t < 0:
            return 0.0
        if t == 0:
            return self.gawa_pct_init()
        prev = self.gawa_pct_fixed(t - 1)
        if prev > 0.0:
            return prev
        if self.is_first_wd(t) or self.depleted_flag(t):
            return self.gawa_pct_at_age(self.age(t))
        return 0.0

    def _f_gawa_pp_at(self, t, timing):
        """GAWA at month t read at ``BEF_PREM``, ``BEF_WD`` or ``BEF_ANNIV`` [S1]."""
        if t < 1:
            return self.gawa_pp_init()
        if self.depleted_flag(t - 1):
            return self.gawa_pp(t - 1)
        g = self.gawa_pp(t - 1)
        if timing == "BEF_PREM":
            return g
        if self.has_wd_by(t - 1) and self.prem_to_av_pp(t) > 0.0:
            g = g + self.gawa_pct_fixed(t - 1) * self.prem_to_av_pp(t)
        if timing == "BEF_WD":
            return g
        if self.is_first_wd(t):
            g = self.gawa_pct_at_age(self.age(t)) * self.gwb_pp_at(t, "BEF_WD")
        if self.wd_pp(t) > 0.0 and self.sum_wd_pp(t) > self.wd_limit_pp(t):
            g = min(g * self.excess_factor(t), self.gwb_pp_at(t, "BEF_ANNIV"))
        if timing == "BEF_ANNIV":
            return g
        raise ValueError("invalid timing")

    def _f_gawa_pp(self, t):
        """GAWA(t): the Guaranteed Annual Withdrawal Amount at the end of month t [S1].

        After the first withdrawal, both the bonus and the step-up raise it to
        ``max(g x GWB, GAWA)``. If the For Life Guarantee is not in effect and ``GWB < GAWA``
        at a Contract Year end, GAWA is set equal to GWB.
        """
        if t < 0:
            return 0.0
        if t == 0:
            return self.gawa_pp_init()
        if self.depleted_flag(t - 1):
            return self.gawa_pp(t - 1)
        g = self.gawa_pp_at(t, "BEF_ANNIV")
        if self.is_anniv(t):
            pct = self.gawa_pct_fixed(t)
            if self.has_wd_by(t) and pct > 0.0:
                if self.bonus_pp(t) > 0.0:
                    g = max(pct * self.gwb_pp_aft_bonus(t), g)
                if self.is_stepup(t):
                    g = max(pct * self.gwb_pp_aft_stepup(t), g)
            if not self.forlife_flag() and self.gwb_pp(t) < g:
                g = self.gwb_pp(t)
        if g <= 0.0 and self.depleted_flag(t) and self.gawa_pct_fixed(t) > 0.0:
            g = self.gawa_pct_fixed(t) * self.gwb_pp(t)
        return g

    def _f_np_pp(self, t):
        """NP(t): cumulative Net Premiums, a floor under the death benefit [S1].

        Updated by premium only, as the notes' state table has it: it is never reduced for a
        withdrawal. Under the ``rollup`` and ``HQAV`` elections it is therefore an unreduced
        floor beneath ``DB``. Under ``gmdb_option = "basic"`` the elected form is itself the
        proportional return of premium — carried on :func:`rb_pp`, which *does* fall with a
        withdrawal — and this cells is not layered over it, or the election would have no
        effect at all. See :func:`gmdb_guarantee_pp`.
        """
        if t < 0:
            return 0.0
        if t == 0:
            return self.np_pp_init() + self.prem_to_av_pp(0)
        if self.depleted_flag(t - 1):
            return self.np_pp(t - 1)
        return self.np_pp(t - 1) + self.prem_to_av_pp(t)

    def _f_rp_reduction_pp(self, t):
        """The premium portion of month t's withdrawal, earnings coming out first **[std]**.

        The sources state that Remaining Premium falls by "withdrawals of premium including
        withdrawal charges" [S2] and that earnings come out free first [S1], but give no
        algebra; this is the reading that makes the two consistent.
        """
        if t < 1 or self.wd_pp(t) <= 0.0:
            return 0.0
        rp = self.rp_pp(t - 1) + self.premium_pp(t)
        earnings = max(0.0, self.av_pp_at(t, "BEF_WD") - rp)
        return min(rp, max(0.0, self.wd_pp(t) - earnings))

    def _f_rp_pp(self, t):
        """RP(t): Remaining Premium, the basis the CDSC is charged on [S2]."""
        if t < 0:
            return 0.0
        if t == 0:
            return self.rp_pp_init() + self.premium_pp(0)
        if self.depleted_flag(t - 1):
            return self.rp_pp(t - 1)
        return max(0.0, self.rp_pp(t - 1) + self.premium_pp(t) - self.rp_reduction_pp(t))

    def _f_rb_prior_anniv_pp(self, t):
        """RB at the Contract Anniversary preceding month t, the d-f-d allowance base [S1]."""
        u = self.t_of_month(12 * (self.policy_year(t) - 1))
        return self.rb_pp(max(0, u))

    def _f_gmdb_allow_pp(self, t):
        """The contract year's dollar-for-dollar GMDB withdrawal allowance [S1].

        ``rho x RB`` at the previous anniversary. Withdrawals inside it reduce the Benefit
        Base dollar for dollar; anything above it reduces it proportionally.
        """
        return self.rollup_rate(t) * self.rb_prior_anniv_pp(t)

    def _f_gmdb_wd_dfd_pp(self, t):
        """The dollar-for-dollar portion of month t's withdrawal against the allowance [S1]."""
        if t < 1 or self.wd_pp(t) <= 0.0 or self.gmdb_option() != "rollup":
            return 0.0
        used = 0.0 if self.is_year_start(t) else self.gmdb_dfd_acc_pp(t - 1)
        return min(self.wd_pp(t), max(0.0, self.gmdb_allow_pp(t) - used))

    def _f_gmdb_wd_excess_pp(self, t):
        """The portion of month t's withdrawal above the GMDB d-f-d allowance [S1]."""
        if t < 1 or self.gmdb_option() != "rollup":
            return 0.0
        return self.wd_pp(t) - self.gmdb_wd_dfd_pp(t)

    def _f_gmdb_wd_factor(self, t):
        """The proportional factor month t's excess GMDB withdrawal accrues **[std]**.

        The notes say the adjustment above the allowance is "proportional to the contract
        value reduction from the excess" but leave the base unstated. The model measures it
        the same way the GLWB does: against the contract value after the dollar-for-dollar
        portion has been deducted.
        """
        if self.gmdb_wd_excess_pp(t) <= 0.0:
            return 1.0
        base = self.av_pp_at(t, "BEF_WD") - self.gmdb_wd_dfd_pp(t)
        if base <= 0.0:
            return 0.0
        return max(0.0, 1.0 - self.gmdb_wd_excess_pp(t) / base)

    def _f_gmdb_dfd_acc_pp(self, t):
        """The dollar-for-dollar reduction accrued so far in the contract year [S1].

        **GMDB withdrawal adjustments are applied at Contract Year end**, not at the
        withdrawal; applying them immediately changes the base the roll-up compounds on.
        """
        if t < 1:
            return 0.0
        prev = 0.0 if self.is_year_start(t) else self.gmdb_dfd_acc_pp(t - 1)
        return prev + self.gmdb_wd_dfd_pp(t)

    def _f_gmdb_factor_acc(self, t):
        """The proportional factor accrued so far in the contract year **[std]**."""
        if t < 1:
            return 1.0
        prev = 1.0 if self.is_year_start(t) else self.gmdb_factor_acc(t - 1)
        return prev * self.gmdb_wd_factor(t)

    def _f_rb_pp_at(self, t, timing):
        """RB at month t read at ``BEF_PREM``, ``BEF_WD`` or ``BEF_ANNIV``.

        The ``rollup`` form accrues its withdrawal adjustment and applies it at the Contract
        Year end; the ``HQAV`` and ``basic`` forms reduce the base proportionally at the
        withdrawal itself [S1].
        """
        if t < 1:
            return self.rb_pp_init()
        if self.depleted_flag(t - 1):
            return self.rb_pp(t - 1)
        r = self.rb_pp(t - 1)
        if timing == "BEF_PREM":
            return r
        r = r + self.prem_to_av_pp(t)
        if timing == "BEF_WD":
            return r
        if self.wd_pp(t) > 0.0 and self.gmdb_option() != "rollup":
            base = self.av_pp_at(t, "BEF_WD")
            r = r * max(0.0, 1.0 - self.wd_pp(t) / base) if base > 0.0 else 0.0
        if timing == "BEF_ANNIV":
            return r
        raise ValueError("invalid timing")

    def _f_rb_pp(self, t):
        """RB(t): the GMDB Benefit Base at the end of month t.

        Growth cutoffs are **age-based, not duration-based**: roll-up and ratchet growth stop
        at the Contract Anniversary preceding the oldest Covered Life's 81st birthday [S1],
        so an issue-age-60 cell gets 20 roll-up credits and an issue-age-75 cell gets 5.
        """
        if t < 0:
            return 0.0
        if t == 0:
            return self.rb_pp_init() + self.prem_to_av_pp(0)
        if self.depleted_flag(t - 1):
            return self.rb_pp(t - 1)
        r = self.rb_pp_at(t, "BEF_ANNIV")
        if not self.is_anniv(t):
            return r
        option = self.gmdb_option()
        if option == "rollup":
            r = max(0.0, (r - self.gmdb_dfd_acc_pp(t)) * self.gmdb_factor_acc(t))
            if self.age_at_anniv(t) <= self.gmdb_growth_cutoff_age:                # noqa: F821
                r = r * (1.0 + self.rollup_rate(t))
        elif option == "HQAV":
            if self.age_at_anniv(t) <= self.gmdb_growth_cutoff_age:                # noqa: F821
                r = max(r, self.av_pp(t))
        elif option == "basic":
            pass
        else:
            raise ValueError("invalid gmdb_option")
        return r

    def _f_gmdb_guarantee_pp(self, t):
        """The guarantee actually floored under the death benefit [S1].

        ``max(NP(t), RB(t))`` under the ``rollup`` and ``HQAV`` elections, exactly as the
        notes' ``DB = max(AV, NP, RB)`` reads: there ``NP`` is the *included* return of
        premium and ``RB`` the separately elected base, and the two are different guarantees.

        Under ``basic`` they are the **same** guarantee — the elected form *is* the return of
        premium — and the notes' two tables then contradict each other. The GMDB form table
        reduces it ``G <- G x (1 - W/AV_pre)``, "proportional, **not** dollar-for-dollar",
        while the state table updates ``NP`` by premium alone. Layering the unreduced ``NP``
        over the reduced base would make the emphasized rule unreachable and the election a
        dead switch, so on that election the elected form governs alone **[std]**. The
        README section *The basic GMDB election and the unreduced NP floor* sets out the
        conflict and the choice; :func:`np_pp` still carries cumulative net premiums, and a
        test pins the difference on model point 9.
        """
        if self.gmdb_option() == "basic":
            return self.rb_pp(t)
        return max(self.np_pp(t), self.rb_pp(t))

    def _f_db_pp(self, t):
        """DB(t) = max(AV(t), NP(t), RB(t)): the **gross** death benefit outflow [S1].

        Zero once the contract value has reached zero with the GLWB in force: all other
        endorsements terminate without value and **no death benefit is payable on subsequent
        death** [S1].
        """
        if self.depleted_flag(t):
            return 0.0
        return max(self.av_pp(t), self.gmdb_guarantee_pp(t))

    def _f_gmdb_claim_pp(self, t):
        """``max(0, max(NP, RB) - AV)``: the **net general-account strain** on death [S1].

        Project ``DB(t)`` as the outflow and derive this as the strain — never the reverse,
        never both. Projecting only the guarantee excess understates gross benefit outgo and
        breaks reconciliation with statutory exhibits; projecting both double counts.
        """
        if self.depleted_flag(t):
            return 0.0
        return max(0.0, self.gmdb_guarantee_pp(t) - self.av_pp(t))

    def _f_forlife_flag(self):
        """Whether the For Life Guarantee is in effect from issue [S1].

        True when the Designated Life is 59 1/2 or older. On an age-nearest-birthday basis an
        ANB of 60 is exactly an actual age of 59 1/2 or more, so the test is
        ``age_at_entry() >= 60`` with no approximation **[std]**.
        """
        return self.age_at_entry() >= self.forlife_age                             # noqa: F821

    def _f_depleted_flag(self, t):
        """True once the contract value has reached zero with the GLWB in force [S1].

        Absorbing: once set it never clears. The threshold is half a cent **[std]** — the
        charge cap in :func:`charge_scale` and the withdrawal cap in :func:`wd_pp` both drive
        the account to exactly zero, so the threshold only guards floating point.
        """
        if t < 0:
            return False
        if t > 0 and self.depleted_flag(t - 1):
            return True
        return self.av_pp(t) <= self.av_depletion_threshold                        # noqa: F821

    def _f_glwb_payment_pp(self, t):
        """The insurer-funded GLWB payment in month t once the contract is depleted [S1].

        With the For Life Guarantee in effect, GAWA is paid for the life of the Designated
        Life. Without it, payments continue until the earlier of death and GWB depletion, the
        final one truncated to the remaining GWB. The notes place the routine at BOM and the
        payment "at each Contract Anniversary"; the model pays it at the BOM of the first
        month of each contract year **[std]**, the instant just after the anniversary, which
        keeps it on the same clock as the pre-depletion withdrawals.
        """
        if t < 1 or t > self.proj_len() or not self.depleted_flag(t - 1):
            return 0.0
        if not self.is_year_start(t):
            return 0.0
        amount = self.gawa_pp(t - 1)
        return amount if self.forlife_flag() else min(amount, self.gwb_pp(t - 1))

    def _f_mort_rate(self, t):
        """The annual mortality rate at the attained age and sex, from *mort_table.csv*.

        The shipped table is an illustrative annuitant curve **[std]**, *not* a published
        basis. The prescribed basis is the 2012 IAM **Basic** Table improved to December 31,
        2017 on Projection Scale G2, generational, with no further improvement in the
        projection [R1][REG-R59]; it may not be redistributed here, so swap it in by
        repointing ``Data.mort_table_file``. **Do not use CSO or VBT life tables** —
        annuitant mortality is a different and generally lighter basis [REG-R59].
        """
        table = self.data.mort_table()                                        # noqa: F821
        top = max(a for a, s in table.index)
        return float(table.loc[(min(self.age(t), top), self.sex()), "mort_rate"])

    def _f_mort_rate_mth(self, t):
        """q^d(t): the monthly mortality rate, ``1 - (1 - q_x)^(1/12)`` **[std]**."""
        return 1.0 - (1.0 - self.mort_rate(t)) ** (1.0 / 12.0)

    def _f_lapse_rate_base(self, t):
        """q^w_base(y): VM-21 Table 6.3's "under 50% ITM" column **[std]** [R1].

        4.0% p.a. during the surrender-charge period (contract years 1 to 7 here [S2]),
        25.0% in the first year after it, 15.0% thereafter.
        """
        year = self.policy_year(t)
        if year <= self.surr_charge_years:                                    # noqa: F821
            return self.lapse_rate_sc                                         # noqa: F821
        elif year == self.surr_charge_years + 1:                              # noqa: F821
            return self.lapse_rate_shock                                      # noqa: F821
        return self.lapse_rate_ult                                            # noqa: F821

    def _f_moneyness_glwb(self, t):
        """M_G(t) = GWB(t) / AV(t): the living-benefit in-the-moneyness ratio [R1]."""
        return self.gwb_pp(t) / self.av_pp(t) if self.av_pp(t) > 0.0 else 0.0

    def _f_moneyness_gmdb(self, t):
        """M_D(t) = max(NP(t), RB(t)) / AV(t): the death-benefit moneyness ratio [R1].

        Measured on the guarantee actually floored under ``DB``, not on ``RB`` alone.
        """
        return self.gmdb_guarantee_pp(t) / self.av_pp(t) if self.av_pp(t) > 0.0 else 0.0

    def _f_lapse_itm_mult(self, m):
        """lambda(M): the VM-21 §7.B.1 Alternative Methodology multiplier [R1].

        ``min[U, max(L, 1 - Mult (M - D))]`` with U = 1.00, L = 0.50, Mult = 1.25, D = 1.10 —
        the only closed-form dynamic lapse formula the Valuation Manual publishes for VAs.
        Note that it floors suppression at 50% while Table 6.3's own ITM grading implies an
        84% suppression; compose one or the other, never both.
        """
        raw = 1.0 - self.lapse_itm_mult_coef * (m - self.lapse_itm_threshold)      # noqa: F821
        return min(self.lapse_itm_upper, max(self.lapse_itm_lower, raw))           # noqa: F821

    def _f_lapse_dyn_mult(self, t):
        """lambda*(t) = min(lambda(M_G), lambda(M_D)) [R1].

        The contract carries both a VAGLB and a GMDB, and VM-21 §6.C.6 directs that such
        contracts use the **lower** of the two ITM-based rates.
        """
        return min(self.lapse_itm_mult(self.moneyness_glwb(t)),
                   self.lapse_itm_mult(self.moneyness_gmdb(t)))

    def _f_lapse_wd_factor(self, t):
        """kappa(t): 0.60 in any contract year with a projected withdrawal, else 1.00 [R1]."""
        return self.lapse_wd_year_factor if self.is_wd_year(t) else 1.0            # noqa: F821

    def _f_lapse_rate(self, t):
        """q^w_annual(t) = min[1, base x lambda* x kappa] **[std] composition** [R1].

        The **annual** total surrender rate; :func:`lapse_rate_mth` is the monthly one, the
        pair matching :func:`mort_rate` / :func:`mort_rate_mth`. Zero whenever the contract
        value is zero: the prescribed surrender assumption for a GMWB contract at ``AV = 0``
        is 0% [R1]. This is the single most important behavioural assumption on the product,
        because it determines how many deeply in-the-money contracts persist to become
        claims.
        """
        if self.av_pp(t) <= 0.0:
            return 0.0
        return min(1.0, self.lapse_rate_base(t) * self.lapse_dyn_mult(t) * self.lapse_wd_factor(t))

    def _f_lapse_rate_mth(self, t):
        """q^w(t): the monthly surrender rate, ``1 - (1 - q^w_annual)^(1/12)`` **[std]**."""
        return 1.0 - (1.0 - self.lapse_rate(t)) ** (1.0 / 12.0)

    def _f_pols_if(self, t):
        """The in-force probability at the **start** of projection month t.

        The notes' ``l(t-1)``, and the weight applied to month ``t``'s cash flows, so that
        the ``pols_if`` column of :func:`result_cf` reconciles with the row it sits on:
        ``premiums(t) / premium_pp(t)`` is exactly ``pols_if(t)``. This is the library-wide
        convention, set by :mod:`.Term_US_A` and by ``savings.CashValue_SE``.

        The notes' own end-of-month ``l(t)`` is :func:`pols_if_at` ``(t, "AFT_DECR")``. The
        two coincide — ``pols_if(t + 1) == pols_if_at(t, "AFT_DECR")`` — everywhere but the
        horizon month, where the survivors leave as :func:`pols_maturity` and nothing is in
        force at the start of the month after it.
        """
        if t <= 0:
            return self.pols_if_init()
        if t > self.proj_len():
            return 0.0
        return self.pols_if_at(t - 1, "AFT_DECR")

    def _f_pols_if_at(self, t, timing):
        """In-force at month t read at ``BEF_DECR``, ``BEF_LAPSE`` or ``AFT_DECR``.

        The order is the notes' ``l(t) = l(t-1)(1 - q^d(t))(1 - q^w(t))`` — **death first,
        then surrender** **[std]**. ``"BEF_DECR"`` is :func:`pols_if` ``(t)`` and
        ``"AFT_DECR"`` is the notes' ``l(t)``, the end-of-month count.
        """
        if t < 1:
            return self.pols_if_init()
        pols = self.pols_if(t)
        if timing == "BEF_DECR":
            return pols
        pols = pols * (1.0 - self.mort_rate_mth(t))
        if timing == "BEF_LAPSE":
            return pols
        pols = pols * (1.0 - self.lapse_rate_mth(t))
        if timing == "AFT_DECR":
            return pols
        raise ValueError("invalid timing")

    def _f_pols_death(self, t):
        """Deaths in month t, on the contracts in force at the start of it."""
        return 0.0 if t < 1 else self.pols_if(t) * self.mort_rate_mth(t)

    def _f_pols_lapse(self, t):
        """Full surrenders in month t, on the survivors of mortality."""
        return 0.0 if t < 1 else self.pols_if_at(t, "BEF_LAPSE") * self.lapse_rate_mth(t)

    def _f_pols_maturity(self, t):
        """Survivors carried out at the projection horizon; zero in every other month.

        Not a decrement — the projection runs out — but needed for the in-force roll-forward
        to close; see the Space docstring.
        """
        return self.pols_if_at(t, "AFT_DECR") if t == self.proj_len() else 0.0

    def _f_pols_decr(self, t, kind):
        """The number of contracts leaving in month t by benefit ``kind``."""
        if kind == "DEATH":
            return self.pols_death(t)
        elif kind == "LAPSE":
            return self.pols_lapse(t)
        elif kind == "MATURITY":
            return self.pols_maturity(t)
        else:
            raise ValueError("invalid kind")

    def _f_claim_pp(self, t, kind):
        """The benefit paid per contract in month t by ``kind``.

        ``"DEATH"`` is the gross death benefit :func:`db_pp`. ``"LAPSE"`` is the surrender
        proceeds :func:`surr_benefit_pp`. ``"MATURITY"`` is the surrender value of the
        survivors at the projection horizon.
        """
        if kind == "DEATH":
            return self.db_pp(t)
        elif kind == "LAPSE":
            return self.surr_benefit_pp(t)
        elif kind == "MATURITY":
            return self.surr_benefit_pp(t)
        else:
            raise ValueError("invalid kind")

    def _f_claim_from_av_pp(self, t, kind):
        """The contract value released per contract by a claim of ``kind``.

        Always ``AV(t)``: the separate account gives up the account value, and whatever the
        guarantee adds on top is general-account money, reported as :func:`claims_over_av`.
        """
        if kind in ("DEATH", "LAPSE", "MATURITY"):
            return self.av_pp(t)
        raise ValueError("invalid kind")

    def _f_premiums(self, t):
        """Premium income in month t, weighted by the contracts in force at the start of it.

        ``pols_if(0)`` is ``pols_if_init()``, so the entry instant needs no special case.
        """
        return 0.0 if t < 0 else self.premium_pp(t) * self.pols_if(t)

    def _f_prem_to_av(self, t):
        """Net premium credited to the block's contract value in month t."""
        return 0.0 if t < 0 else self.prem_to_av_pp(t) * self.pols_if(t)

    def _f_asset_charges(self, t):
        """Charge income from the M&E and administrative asset charge, in-force weighted."""
        return 0.0 if t < 1 else self.asset_charge_pp(t) * self.pols_if(t)

    def _f_fees_glwb(self, t):
        """Charge income from the GLWB rider fee, in-force weighted."""
        return 0.0 if t < 1 else self.fee_glwb_pp(t) * self.pols_if(t)

    def _f_fees_gmdb(self, t):
        """Charge income from the GMDB rider fee, in-force weighted."""
        return 0.0 if t < 1 else self.fee_gmdb_pp(t) * self.pols_if(t)

    def _f_maint_fees(self, t):
        """Charge income from the annual contract fee, in-force weighted."""
        return 0.0 if t < 1 else self.maint_fee_pp(t) * self.pols_if(t)

    def _f_wd_charges(self, t):
        """The CDSC collected on withdrawals, in-force weighted — a **memo line**.

        The notes' ledger lists the withdrawal charge twice: once as charge income ``c(t)``
        and once as a deduction inside withdrawal proceeds ``W(t) - c(t)``. Counting both
        double-counts it. :func:`withdrawals` carries the net proceeds into :func:`net_cf`
        and this line reports the charge separately.
        """
        return 0.0 if t < 1 else self.wd_charge_pp(t) * self.pols_if(t)

    def _f_charge_income(self, t):
        """Total insurer charge income in month t, excluding the double-counted CDSC."""
        return self.asset_charges(t) + self.fees_glwb(t) + self.fees_gmdb(t) + self.maint_fees(t)

    def _f_withdrawals(self, t):
        """Withdrawal proceeds ``W(t) - c(t)``, weighted by :func:`pols_if` ``(t)``."""
        return 0.0 if t < 1 else self.wd_payment_pp(t) * self.pols_if(t)

    def _f_glwb_payments(self, t):
        """Insurer-funded post-depletion GLWB payments, weighted by ``pols_if(t)``."""
        return 0.0 if t < 1 else self.glwb_payment_pp(t) * self.pols_if(t)

    def _f_claims(self, t, kind=None):
        """Benefit outgo in month t, for one ``kind`` or, with ``kind=None``, all three."""
        if kind is None:
            return (self.claims(t, "DEATH") + self.claims(t, "LAPSE")
                    + self.claims(t, "MATURITY"))
        return self.claim_pp(t, kind) * self.pols_decr(t, kind)

    def _f_claims_from_av(self, t, kind):
        """The contract value released by a claim of ``kind``, in-force weighted."""
        return self.claim_from_av_pp(t, kind) * self.pols_decr(t, kind)

    def _f_claims_over_av(self, t, kind=None):
        """Benefit paid less the contract value released, ``claims - claims_from_av``.

        On death this is exactly the GMDB guarantee claim — the general-account strain. On a
        surrender it is negative by the withdrawal charge, which the separate account keeps.
        A reconciliation quantity, never a ledger line of its own.
        """
        if kind is None:
            return (self.claims_over_av(t, "DEATH") + self.claims_over_av(t, "LAPSE")
                    + self.claims_over_av(t, "MATURITY"))
        return self.claims(t, kind) - self.claims_from_av(t, kind)

    def _f_gmdb_claims(self, t):
        """The net general-account strain on death, ``GuaranteeClaim x deaths`` — a memo."""
        return 0.0 if t < 1 else self.gmdb_claim_pp(t) * self.pols_death(t)

    def _f_commissions(self, t):
        """Acquisition commission; **0 in the base run [std]**, the notes not modelling it."""
        return self.comm_rate_acq * self.premiums(t)                               # noqa: F821

    def _f_premium_taxes(self, t):
        """Premium tax deducted from the purchase payment, 0% **[std]** [S2]."""
        return self.premium_tax_rate() * self.premiums(t)

    def _f_inflation_factor(self, t):
        """The VM-21 §6.C.2 expense inflation factor for the contract year containing t.

        ``1.025^(valuation year - 2015 + completed contract years)`` [R1].
        """
        return (1.0 + self.inflation_rate) ** (                               # noqa: F821
            self.valuation_year - self.expense_base_year + self.duration(t))            # noqa: F821

    def _f_expenses(self, t):
        """VM-21 §6.C.2 prescribed maintenance expense [R1].

        ``[100 x 1.025^(valuation year - 2015)]/12`` per contract per month, inflating 2.5%
        a year, **plus 7 basis points of projected account value** for a company-administered
        block. Acquisition expense is not modelled in the base run **[std]**.
        """
        if t == 0:
            return self.expense_acq * self.pols_if(0)                              # noqa: F821
        if t < 0 or t > self.proj_len():
            return 0.0
        per_contract = (self.expense_maint / 12.0) * self.inflation_factor(t)      # noqa: F821
        per_av = (self.expense_av_rate / 12.0) * self.av_pp(t)                     # noqa: F821
        return (per_contract + per_av) * self.pols_if(t)

    def _f_net_cf(self, t):
        """The technical notes' cash flow ledger, summed with the notes' own signs.

        Premium income and every charge income line are positive; the gross death benefit,
        surrender and horizon proceeds, withdrawal proceeds, post-depletion GLWB payments and
        maintenance expense are negative. Note what this **is not**: because a VA's separate
        account is legally segregated, this line mixes separate-account movements (premium
        in, benefits out) with transfers into the general account (the charges), and it omits
        investment return entirely, so it does not reconcile to the account value.
        :func:`net_cf_ga` is the insurer's own view; :func:`check_av_roll_fwd` is the
        account-value identity.
        """
        return (self.premiums(t) + self.charge_income(t)
                - self.withdrawals(t) - self.glwb_payments(t) - self.claims(t)
                - self.expenses(t) - self.commissions(t) - self.premium_taxes(t))

    def _f_net_cf_ga(self, t):
        """The general-account view: charge income less guarantee strain and expenses.

        The notes require both the gross death benefit and the net general-account strain and
        say they are not interchangeable. This line assembles the net one: charge income,
        less the GMDB guarantee claim, less insurer-funded post-depletion GLWB payments, less
        expenses, commissions and premium tax. It is the memo, not the ledger.
        """
        return (self.charge_income(t) - self.gmdb_claims(t) - self.glwb_payments(t)
                - self.expenses(t) - self.commissions(t) - self.premium_taxes(t))

    def _f_av_at(self, t, timing):
        """The in-force weighted contract value at month t; see :func:`av_pp_at`.

        Every timing inside the month is weighted by the contracts in force at the start of
        it, :func:`pols_if` ``(t)``. ``"EOM"`` is weighted by ``pols_if(t + 1)`` — the count
        still in force once the month's decrements have gone — which is zero in the horizon
        month, where the survivors leave as :func:`pols_maturity` and their contract value
        is released through :func:`claims_from_av`.
        """
        if t < 0:
            return 0.0
        if timing == "EOM":
            return self.av_pp(t) * self.pols_if(t + 1)
        return self.av_pp_at(t, timing) * self.pols_if(t)

    def _f_inv_income(self, t):
        """Investment income credited to the block's contract value in month t."""
        return 0.0 if t < 1 else self.inv_income_pp(t) * self.pols_if(t)

    def _f_wd_from_av(self, t):
        """The contract value released by month t's withdrawals, gross of the charge."""
        return 0.0 if t < 1 else self.wd_pp(t) * self.pols_if(t)

    def _f_charges_from_av(self, t):
        """The contract value cancelled by month t's per-contract and benefit-base charges."""
        return 0.0 if t < 1 else self.charge_pp(t) * self.pols_if(t)

    def _f_av_change(self, t):
        """The change in the block's contract value over month t."""
        return self.av_at(t, "EOM") - self.av_at(t - 1, "EOM")

    def _f_check_av_roll_fwd_resid(self, t):
        """Contract value roll-forward residual; zero to floating point for every t >= 1.

        ``AV(t) - AV(t-1) = net premium in - withdrawals out + investment income net of the
        per-unit charges - the charges collected by unit cancellation - the contract value
        released by each claim kind``. The cash *paid* on a death may exceed the contract
        value released; that excess is :func:`claims_over_av` and is not part of this
        identity. ``t = 0`` is the entry instant and is excluded.

        The signed residual, for a debugging session that wants to know *where* the identity
        fails; :func:`check_av_roll_fwd` is the library-wide boolean over all ``t``.
        """
        if t < 1:
            return 0.0
        expected = (self.prem_to_av(t) - self.wd_from_av(t) + self.inv_income(t)
                    - self.charges_from_av(t)
                    - self.claims_from_av(t, "DEATH") - self.claims_from_av(t, "LAPSE")
                    - self.claims_from_av(t, "MATURITY"))
        return self.av_change(t) - expected

    def _f_check_av_roll_fwd(self):
        """True when the contract value roll-forward closes at **every** projected month.

        No argument and a ``bool`` return, following ``savings.CashValue_SE`` and the
        library-wide convention, so one test can call the same check across every model.
        The per-month signed residual is :func:`check_av_roll_fwd_resid`; the tolerance is
        1e-6 of a currency unit on a contract value of order 1e5.
        """
        return all(abs(self.check_av_roll_fwd_resid(t)) < 1e-6
                   for t in range(1, self.proj_len() + 1))

    def _f_check_pols_roll_fwd_resid(self, t):
        """In-force roll-forward residual; zero to floating point for every t >= 1.

        ``pols_if(t) - pols_if(t+1) = deaths + surrenders + horizon survivors``, written on
        the start-of-month counts :func:`pols_if` carries. In the horizon month
        ``pols_if(t+1)`` is zero and :func:`pols_maturity` absorbs the survivors.
        """
        if t < 1:
            return 0.0
        return (self.pols_if(t) - self.pols_if(t + 1) - self.pols_death(t)
                - self.pols_lapse(t) - self.pols_maturity(t))

    def _f_check_pols_roll_fwd(self):
        """True when the in-force roll-forward closes at **every** projected month.

        No argument and a ``bool`` return; :func:`check_pols_roll_fwd_resid` is the signed
        per-month residual. In-force is a probability of order 1, so the tolerance is 1e-12.
        """
        return all(abs(self.check_pols_roll_fwd_resid(t)) < 1e-12
                   for t in range(1, self.proj_len() + 1))

    def _f_check_charge_split_resid(self, t):
        """Residual of the investment identity; zero to floating point for every t >= 1.

        ``gross fund return = fund expense + asset charge + the change in AV from
        investment``. It is the guard against the charge-base confusion the notes call the
        most consequential error on this product: M&E and admin are on **account value**, the
        rider fees on **benefit bases**, the contract fee **per contract** and the CDSC on
        **Remaining Premium** — four bases in one stack.
        """
        if t < 1:
            return 0.0
        return (self.gross_inv_income_pp(t) - self.fund_expense_pp(t)
                - self.asset_charge_pp(t) - self.inv_income_pp(t))

    def _f_check_charge_split(self):
        """True when the investment identity closes at **every** projected month.

        No argument and a ``bool`` return; :func:`check_charge_split_resid` is the signed
        per-month residual, measured per contract, so the tolerance is 1e-8.
        """
        return all(abs(self.check_charge_split_resid(t)) < 1e-8
                   for t in range(1, self.proj_len() + 1))

    def _f_result_cf(self):
        """Result table of cashflows, indexed by projection month t from 0 to ``proj_len()``.

        ``t = 0`` carries the purchase payment, as the notes' ledger indexes it. The
        ``pols_if`` column is the count in force at the **start** of each month and is the
        weight carried by every cash flow on that row, so the two reconcile.
        """
        ts = list(range(0, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "pols_if": [self.pols_if(t) for t in ts],
                "premiums": [self.premiums(t) for t in ts],
                "asset_charges": [self.asset_charges(t) for t in ts],
                "fees_glwb": [self.fees_glwb(t) for t in ts],
                "fees_gmdb": [self.fees_gmdb(t) for t in ts],
                "maint_fees": [self.maint_fees(t) for t in ts],
                "withdrawals": [self.withdrawals(t) for t in ts],
                "glwb_payments": [self.glwb_payments(t) for t in ts],
                "claims_death": [self.claims(t, "DEATH") for t in ts],
                "claims_lapse": [self.claims(t, "LAPSE") for t in ts],
                "claims_maturity": [self.claims(t, "MATURITY") for t in ts],
                "expenses": [self.expenses(t) for t in ts],
                "commissions": [self.commissions(t) for t in ts],
                "premium_taxes": [self.premium_taxes(t) for t in ts],
                "net_cf": [self.net_cf(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    def _f_result_pols(self):
        """Result table of in-force movements, indexed by projection month t.

        ``pols_if`` opens the month, the three decrement columns take contracts out of it,
        and ``pols_if_aft_decr`` — the notes' ``l(t)`` — closes it. Rows therefore read
        across: ``pols_if - pols_death - pols_lapse - pols_maturity`` is the next row's
        ``pols_if``.
        """
        ts = list(range(0, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "pols_if": [self.pols_if(t) for t in ts],
                "pols_death": [self.pols_death(t) for t in ts],
                "pols_lapse": [self.pols_lapse(t) for t in ts],
                "pols_maturity": [self.pols_maturity(t) for t in ts],
                "pols_if_aft_decr": [self.pols_if_at(t, "AFT_DECR") for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    def _f_result_av(self):
        """Result table of per-contract subaccount and contract values, indexed by t.

        One ``sa_pp_<i>`` column per subaccount, then the worked example's own columns: the
        contract value before the charges, the three charges, and the end-of-month value.
        """
        ts = list(range(0, self.proj_len() + 1))
        cols = {}
        for i in self.sub_ids():
            cols["sa_pp_%s" % i] = [self.sa_pp(t, i) for t in ts]
        cols["av_pp_bef_fee"] = [self.av_pp_at(t, "BEF_FEE") for t in ts]
        cols["fee_glwb_pp"] = [self.fee_glwb_pp(t) for t in ts]
        cols["fee_gmdb_pp"] = [self.fee_gmdb_pp(t) for t in ts]
        cols["maint_fee_pp"] = [self.maint_fee_pp(t) for t in ts]
        cols["asset_charge_pp"] = [self.asset_charge_pp(t) for t in ts]
        cols["fund_expense_pp"] = [self.fund_expense_pp(t) for t in ts]
        cols["av_pp"] = [self.av_pp(t) for t in ts]
        cols["surr_benefit_pp"] = [self.surr_benefit_pp(t) for t in ts]
        return self.pd.DataFrame(cols, index=self.pd.Index(ts, name="t"))          # noqa: F821

    def _f_result_bases(self):
        """Result table of the guarantee bases and moneyness ratios, indexed by t."""
        ts = list(range(0, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "gwb_pp": [self.gwb_pp(t) for t in ts],
                "gawa_pp": [self.gawa_pp(t) for t in ts],
                "bb_pp": [self.bb_pp(t) for t in ts],
                "rb_pp": [self.rb_pp(t) for t in ts],
                "np_pp": [self.np_pp(t) for t in ts],
                "rp_pp": [self.rp_pp(t) for t in ts],
                "adj_pp": [self.adj_pp(t) for t in ts],
                "wd_pp": [self.wd_pp(t) for t in ts],
                "db_pp": [self.db_pp(t) for t in ts],
                "gmdb_claim_pp": [self.gmdb_claim_pp(t) for t in ts],
                "moneyness_glwb": [self.moneyness_glwb(t) for t in ts],
                "moneyness_gmdb": [self.moneyness_gmdb(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    def _f_bench_net_cf(self):
        return sum(self.net_cf(t) for t in range(0, self.proj_len() + 1))


    def model_point(self):
        if self._has_model_point:
            return self._v_model_point
        else:
            val = self._v_model_point = self._f_model_point()
            self._has_model_point = True
            return val

    def policy_id(self):
        if self._has_policy_id:
            return self._v_policy_id
        else:
            val = self._v_policy_id = self._f_policy_id()
            self._has_policy_id = True
            return val

    def age_at_entry(self):
        if self._has_age_at_entry:
            return self._v_age_at_entry
        else:
            val = self._v_age_at_entry = self._f_age_at_entry()
            self._has_age_at_entry = True
            return val

    def sex(self):
        if self._has_sex:
            return self._v_sex
        else:
            val = self._v_sex = self._f_sex()
            self._has_sex = True
            return val

    def designated_lives(self):
        if self._has_designated_lives:
            return self._v_designated_lives
        else:
            val = self._v_designated_lives = self._f_designated_lives()
            self._has_designated_lives = True
            return val

    def tax_status(self):
        if self._has_tax_status:
            return self._v_tax_status
        else:
            val = self._v_tax_status = self._f_tax_status()
            self._has_tax_status = True
            return val

    def pols_if_init(self):
        if self._has_pols_if_init:
            return self._v_pols_if_init
        else:
            val = self._v_pols_if_init = self._f_pols_if_init()
            self._has_pols_if_init = True
            return val

    def premium_tax_rate(self):
        if self._has_premium_tax_rate:
            return self._v_premium_tax_rate
        else:
            val = self._v_premium_tax_rate = self._f_premium_tax_rate()
            self._has_premium_tax_rate = True
            return val

    def premium_single(self):
        if self._has_premium_single:
            return self._v_premium_single
        else:
            val = self._v_premium_single = self._f_premium_single()
            self._has_premium_single = True
            return val

    def fund_set(self):
        if self._has_fund_set:
            return self._v_fund_set
        else:
            val = self._v_fund_set = self._f_fund_set()
            self._has_fund_set = True
            return val

    def sub_ids(self):
        if self._has_sub_ids:
            return self._v_sub_ids
        else:
            val = self._v_sub_ids = self._f_sub_ids()
            self._has_sub_ids = True
            return val

    def alloc(self, i):
        if i in self._v_alloc:
            return self._v_alloc[i]
        else:
            val = self._f_alloc(i)
            self._v_alloc[i] = val
            return val

    def fund_expense_rate(self, i):
        if i in self._v_fund_expense_rate:
            return self._v_fund_expense_rate[i]
        else:
            val = self._f_fund_expense_rate(i)
            self._v_fund_expense_rate[i] = val
            return val

    def glwb_option(self):
        if self._has_glwb_option:
            return self._v_glwb_option
        else:
            val = self._v_glwb_option = self._f_glwb_option()
            self._has_glwb_option = True
            return val

    def stepup_basis(self):
        if self._has_stepup_basis:
            return self._v_stepup_basis
        else:
            val = self._v_stepup_basis = self._f_stepup_basis()
            self._has_stepup_basis = True
            return val

    def gmdb_option(self):
        if self._has_gmdb_option:
            return self._v_gmdb_option
        else:
            val = self._v_gmdb_option = self._f_gmdb_option()
            self._has_gmdb_option = True
            return val

    def cdsc_schedule(self):
        if self._has_cdsc_schedule:
            return self._v_cdsc_schedule
        else:
            val = self._v_cdsc_schedule = self._f_cdsc_schedule()
            self._has_cdsc_schedule = True
            return val

    def fee_reset_rule(self):
        if self._has_fee_reset_rule:
            return self._v_fee_reset_rule
        else:
            val = self._v_fee_reset_rule = self._f_fee_reset_rule()
            self._has_fee_reset_rule = True
            return val

    def rollup_rule(self):
        if self._has_rollup_rule:
            return self._v_rollup_rule
        else:
            val = self._v_rollup_rule = self._f_rollup_rule()
            self._has_rollup_rule = True
            return val

    def wd_start_age(self):
        if self._has_wd_start_age:
            return self._v_wd_start_age
        else:
            val = self._v_wd_start_age = self._f_wd_start_age()
            self._has_wd_start_age = True
            return val

    def wd_intensity(self):
        if self._has_wd_intensity:
            return self._v_wd_intensity
        else:
            val = self._v_wd_intensity = self._f_wd_intensity()
            self._has_wd_intensity = True
            return val

    def scenario_id(self):
        if self._has_scenario_id:
            return self._v_scenario_id
        else:
            val = self._v_scenario_id = self._f_scenario_id()
            self._has_scenario_id = True
            return val

    def txn_id(self):
        if self._has_txn_id:
            return self._v_txn_id
        else:
            val = self._v_txn_id = self._f_txn_id()
            self._has_txn_id = True
            return val

    def duration_mth_init(self):
        if self._has_duration_mth_init:
            return self._v_duration_mth_init
        else:
            val = self._v_duration_mth_init = self._f_duration_mth_init()
            self._has_duration_mth_init = True
            return val

    def is_inforce(self):
        if self._has_is_inforce:
            return self._v_is_inforce
        else:
            val = self._v_is_inforce = self._f_is_inforce()
            self._has_is_inforce = True
            return val

    def av_pp_init(self):
        if self._has_av_pp_init:
            return self._v_av_pp_init
        else:
            val = self._v_av_pp_init = self._f_av_pp_init()
            self._has_av_pp_init = True
            return val

    def gwb_pp_init(self):
        if self._has_gwb_pp_init:
            return self._v_gwb_pp_init
        else:
            val = self._v_gwb_pp_init = self._f_gwb_pp_init()
            self._has_gwb_pp_init = True
            return val

    def gawa_pp_init(self):
        if self._has_gawa_pp_init:
            return self._v_gawa_pp_init
        else:
            val = self._v_gawa_pp_init = self._f_gawa_pp_init()
            self._has_gawa_pp_init = True
            return val

    def gawa_pct_init(self):
        if self._has_gawa_pct_init:
            return self._v_gawa_pct_init
        else:
            val = self._v_gawa_pct_init = self._f_gawa_pct_init()
            self._has_gawa_pct_init = True
            return val

    def has_wd_init(self):
        if self._has_has_wd_init:
            return self._v_has_wd_init
        else:
            val = self._v_has_wd_init = self._f_has_wd_init()
            self._has_has_wd_init = True
            return val

    def bb_pp_init(self):
        if self._has_bb_pp_init:
            return self._v_bb_pp_init
        else:
            val = self._v_bb_pp_init = self._f_bb_pp_init()
            self._has_bb_pp_init = True
            return val

    def rb_pp_init(self):
        if self._has_rb_pp_init:
            return self._v_rb_pp_init
        else:
            val = self._v_rb_pp_init = self._f_rb_pp_init()
            self._has_rb_pp_init = True
            return val

    def np_pp_init(self):
        if self._has_np_pp_init:
            return self._v_np_pp_init
        else:
            val = self._v_np_pp_init = self._f_np_pp_init()
            self._has_np_pp_init = True
            return val

    def rp_pp_init(self):
        if self._has_rp_pp_init:
            return self._v_rp_pp_init
        else:
            val = self._v_rp_pp_init = self._f_rp_pp_init()
            self._has_rp_pp_init = True
            return val

    def adj_pp_init(self):
        if self._has_adj_pp_init:
            return self._v_adj_pp_init
        else:
            val = self._v_adj_pp_init = self._f_adj_pp_init()
            self._has_adj_pp_init = True
            return val

    def bonus_end_init(self):
        if self._has_bonus_end_init:
            return self._v_bonus_end_init
        else:
            val = self._v_bonus_end_init = self._f_bonus_end_init()
            self._has_bonus_end_init = True
            return val

    def policy_term(self):
        if self._has_policy_term:
            return self._v_policy_term
        else:
            val = self._v_policy_term = self._f_policy_term()
            self._has_policy_term = True
            return val

    def proj_len(self):
        if self._has_proj_len:
            return self._v_proj_len
        else:
            val = self._v_proj_len = self._f_proj_len()
            self._has_proj_len = True
            return val

    def duration_mth(self, t):
        if t in self._v_duration_mth:
            return self._v_duration_mth[t]
        else:
            val = self._f_duration_mth(t)
            self._v_duration_mth[t] = val
            return val

    def policy_year(self, t):
        if t in self._v_policy_year:
            return self._v_policy_year[t]
        else:
            val = self._f_policy_year(t)
            self._v_policy_year[t] = val
            return val

    def duration(self, t):
        if t in self._v_duration:
            return self._v_duration[t]
        else:
            val = self._f_duration(t)
            self._v_duration[t] = val
            return val

    def age(self, t):
        if t in self._v_age:
            return self._v_age[t]
        else:
            val = self._f_age(t)
            self._v_age[t] = val
            return val

    def age_at_anniv(self, t):
        if t in self._v_age_at_anniv:
            return self._v_age_at_anniv[t]
        else:
            val = self._f_age_at_anniv(t)
            self._v_age_at_anniv[t] = val
            return val

    def contract_quarter(self, t):
        if t in self._v_contract_quarter:
            return self._v_contract_quarter[t]
        else:
            val = self._f_contract_quarter(t)
            self._v_contract_quarter[t] = val
            return val

    def is_anniv(self, t):
        if t in self._v_is_anniv:
            return self._v_is_anniv[t]
        else:
            val = self._f_is_anniv(t)
            self._v_is_anniv[t] = val
            return val

    def is_quarterly_anniv(self, t):
        if t in self._v_is_quarterly_anniv:
            return self._v_is_quarterly_anniv[t]
        else:
            val = self._f_is_quarterly_anniv(t)
            self._v_is_quarterly_anniv[t] = val
            return val

    def is_year_start(self, t):
        if t in self._v_is_year_start:
            return self._v_is_year_start[t]
        else:
            val = self._f_is_year_start(t)
            self._v_is_year_start[t] = val
            return val

    def t_of_month(self, m):
        if m in self._v_t_of_month:
            return self._v_t_of_month[m]
        else:
            val = self._f_t_of_month(m)
            self._v_t_of_month[m] = val
            return val

    def phase(self, t):
        if t in self._v_phase:
            return self._v_phase[t]
        else:
            val = self._f_phase(t)
            self._v_phase[t] = val
            return val

    def inv_return_mth(self, t, i):
        if (t, i) in self._v_inv_return_mth:
            return self._v_inv_return_mth[(t, i)]
        else:
            val = self._f_inv_return_mth(t, i)
            self._v_inv_return_mth[(t, i)] = val
            return val

    def scenario_rate(self, t, name):
        if (t, name) in self._v_scenario_rate:
            return self._v_scenario_rate[(t, name)]
        else:
            val = self._f_scenario_rate(t, name)
            self._v_scenario_rate[(t, name)] = val
            return val

    def vix_sq(self, k):
        if k in self._v_vix_sq:
            return self._v_vix_sq[k]
        else:
            val = self._f_vix_sq(k)
            self._v_vix_sq[k] = val
            return val

    def cmt10(self, t):
        if t in self._v_cmt10:
            return self._v_cmt10[t]
        else:
            val = self._f_cmt10(t)
            self._v_cmt10[t] = val
            return val

    def unit_growth(self, t, i):
        if (t, i) in self._v_unit_growth:
            return self._v_unit_growth[(t, i)]
        else:
            val = self._f_unit_growth(t, i)
            self._v_unit_growth[(t, i)] = val
            return val

    def sa_pp_at(self, t, i, timing):
        if (t, i, timing) in self._v_sa_pp_at:
            return self._v_sa_pp_at[(t, i, timing)]
        else:
            val = self._f_sa_pp_at(t, i, timing)
            self._v_sa_pp_at[(t, i, timing)] = val
            return val

    def sa_pp(self, t, i):
        if (t, i) in self._v_sa_pp:
            return self._v_sa_pp[(t, i)]
        else:
            val = self._f_sa_pp(t, i)
            self._v_sa_pp[(t, i)] = val
            return val

    def av_pp_at(self, t, timing):
        if (t, timing) in self._v_av_pp_at:
            return self._v_av_pp_at[(t, timing)]
        else:
            val = self._f_av_pp_at(t, timing)
            self._v_av_pp_at[(t, timing)] = val
            return val

    def av_pp(self, t):
        if t in self._v_av_pp:
            return self._v_av_pp[t]
        else:
            val = self._f_av_pp(t)
            self._v_av_pp[t] = val
            return val

    def sa_weight(self, t, i):
        if (t, i) in self._v_sa_weight:
            return self._v_sa_weight[(t, i)]
        else:
            val = self._f_sa_weight(t, i)
            self._v_sa_weight[(t, i)] = val
            return val

    def gross_inv_income_pp(self, t):
        if t in self._v_gross_inv_income_pp:
            return self._v_gross_inv_income_pp[t]
        else:
            val = self._f_gross_inv_income_pp(t)
            self._v_gross_inv_income_pp[t] = val
            return val

    def fund_expense_pp(self, t):
        if t in self._v_fund_expense_pp:
            return self._v_fund_expense_pp[t]
        else:
            val = self._f_fund_expense_pp(t)
            self._v_fund_expense_pp[t] = val
            return val

    def asset_charge_pp(self, t):
        if t in self._v_asset_charge_pp:
            return self._v_asset_charge_pp[t]
        else:
            val = self._f_asset_charge_pp(t)
            self._v_asset_charge_pp[t] = val
            return val

    def inv_income_pp(self, t):
        if t in self._v_inv_income_pp:
            return self._v_inv_income_pp[t]
        else:
            val = self._f_inv_income_pp(t)
            self._v_inv_income_pp[t] = val
            return val

    def prem_scheduled_pp(self, t):
        if t in self._v_prem_scheduled_pp:
            return self._v_prem_scheduled_pp[t]
        else:
            val = self._f_prem_scheduled_pp(t)
            self._v_prem_scheduled_pp[t] = val
            return val

    def premium_pp(self, t):
        if t in self._v_premium_pp:
            return self._v_premium_pp[t]
        else:
            val = self._f_premium_pp(t)
            self._v_premium_pp[t] = val
            return val

    def prem_to_av_pp(self, t):
        if t in self._v_prem_to_av_pp:
            return self._v_prem_to_av_pp[t]
        else:
            val = self._f_prem_to_av_pp(t)
            self._v_prem_to_av_pp[t] = val
            return val

    def wd_scheduled_pp(self, t):
        if t in self._v_wd_scheduled_pp:
            return self._v_wd_scheduled_pp[t]
        else:
            val = self._f_wd_scheduled_pp(t)
            self._v_wd_scheduled_pp[t] = val
            return val

    def is_wd_month(self, t):
        if t in self._v_is_wd_month:
            return self._v_is_wd_month[t]
        else:
            val = self._f_is_wd_month(t)
            self._v_is_wd_month[t] = val
            return val

    def is_wd_taken(self, t):
        if t in self._v_is_wd_taken:
            return self._v_is_wd_taken[t]
        else:
            val = self._f_is_wd_taken(t)
            self._v_is_wd_taken[t] = val
            return val

    def has_wd_by(self, t):
        if t in self._v_has_wd_by:
            return self._v_has_wd_by[t]
        else:
            val = self._f_has_wd_by(t)
            self._v_has_wd_by[t] = val
            return val

    def is_first_wd(self, t):
        if t in self._v_is_first_wd:
            return self._v_is_first_wd[t]
        else:
            val = self._f_is_first_wd(t)
            self._v_is_first_wd[t] = val
            return val

    def is_wd_year(self, t):
        if t in self._v_is_wd_year:
            return self._v_is_wd_year[t]
        else:
            val = self._f_is_wd_year(t)
            self._v_is_wd_year[t] = val
            return val

    def gawa_pct_at_age(self, a):
        if a in self._v_gawa_pct_at_age:
            return self._v_gawa_pct_at_age[a]
        else:
            val = self._f_gawa_pct_at_age(a)
            self._v_gawa_pct_at_age[a] = val
            return val

    def wd_limit_pp(self, t):
        if t in self._v_wd_limit_pp:
            return self._v_wd_limit_pp[t]
        else:
            val = self._f_wd_limit_pp(t)
            self._v_wd_limit_pp[t] = val
            return val

    def wd_glwb_pp(self, t):
        if t in self._v_wd_glwb_pp:
            return self._v_wd_glwb_pp[t]
        else:
            val = self._f_wd_glwb_pp(t)
            self._v_wd_glwb_pp[t] = val
            return val

    def wd_pp_due(self, t):
        if t in self._v_wd_pp_due:
            return self._v_wd_pp_due[t]
        else:
            val = self._f_wd_pp_due(t)
            self._v_wd_pp_due[t] = val
            return val

    def wd_pp(self, t):
        if t in self._v_wd_pp:
            return self._v_wd_pp[t]
        else:
            val = self._f_wd_pp(t)
            self._v_wd_pp[t] = val
            return val

    def sum_wd_pp(self, t):
        if t in self._v_sum_wd_pp:
            return self._v_sum_wd_pp[t]
        else:
            val = self._f_sum_wd_pp(t)
            self._v_sum_wd_pp[t] = val
            return val

    def wd_excess_pp(self, t):
        if t in self._v_wd_excess_pp:
            return self._v_wd_excess_pp[t]
        else:
            val = self._f_wd_excess_pp(t)
            self._v_wd_excess_pp[t] = val
            return val

    def wd_nonexcess_pp(self, t):
        if t in self._v_wd_nonexcess_pp:
            return self._v_wd_nonexcess_pp[t]
        else:
            val = self._f_wd_nonexcess_pp(t)
            self._v_wd_nonexcess_pp[t] = val
            return val

    def cv_pre_excess_pp(self, t):
        if t in self._v_cv_pre_excess_pp:
            return self._v_cv_pre_excess_pp[t]
        else:
            val = self._f_cv_pre_excess_pp(t)
            self._v_cv_pre_excess_pp[t] = val
            return val

    def excess_factor(self, t):
        if t in self._v_excess_factor:
            return self._v_excess_factor[t]
        else:
            val = self._f_excess_factor(t)
            self._v_excess_factor[t] = val
            return val

    def free_wd_allow(self, t):
        if t in self._v_free_wd_allow:
            return self._v_free_wd_allow[t]
        else:
            val = self._f_free_wd_allow(t)
            self._v_free_wd_allow[t] = val
            return val

    def free_wd_avail(self, t):
        if t in self._v_free_wd_avail:
            return self._v_free_wd_avail[t]
        else:
            val = self._f_free_wd_avail(t)
            self._v_free_wd_avail[t] = val
            return val

    def wd_free_pp(self, t):
        if t in self._v_wd_free_pp:
            return self._v_wd_free_pp[t]
        else:
            val = self._f_wd_free_pp(t)
            self._v_wd_free_pp[t] = val
            return val

    def free_wd_used_cum_pp(self, t):
        if t in self._v_free_wd_used_cum_pp:
            return self._v_free_wd_used_cum_pp[t]
        else:
            val = self._f_free_wd_used_cum_pp(t)
            self._v_free_wd_used_cum_pp[t] = val
            return val

    def wd_exempt_pp(self, t):
        if t in self._v_wd_exempt_pp:
            return self._v_wd_exempt_pp[t]
        else:
            val = self._f_wd_exempt_pp(t)
            self._v_wd_exempt_pp[t] = val
            return val

    def wd_chargeable_pp(self, t):
        if t in self._v_wd_chargeable_pp:
            return self._v_wd_chargeable_pp[t]
        else:
            val = self._f_wd_chargeable_pp(t)
            self._v_wd_chargeable_pp[t] = val
            return val

    def surr_charge_rate(self, t):
        if t in self._v_surr_charge_rate:
            return self._v_surr_charge_rate[t]
        else:
            val = self._f_surr_charge_rate(t)
            self._v_surr_charge_rate[t] = val
            return val

    def wd_charge_pp(self, t):
        if t in self._v_wd_charge_pp:
            return self._v_wd_charge_pp[t]
        else:
            val = self._f_wd_charge_pp(t)
            self._v_wd_charge_pp[t] = val
            return val

    def wd_payment_pp(self, t):
        if t in self._v_wd_payment_pp:
            return self._v_wd_payment_pp[t]
        else:
            val = self._f_wd_payment_pp(t)
            self._v_wd_payment_pp[t] = val
            return val

    def surr_free_pp(self, t):
        if t in self._v_surr_free_pp:
            return self._v_surr_free_pp[t]
        else:
            val = self._f_surr_free_pp(t)
            self._v_surr_free_pp[t] = val
            return val

    def surr_chargeable_pp(self, t):
        if t in self._v_surr_chargeable_pp:
            return self._v_surr_chargeable_pp[t]
        else:
            val = self._f_surr_chargeable_pp(t)
            self._v_surr_chargeable_pp[t] = val
            return val

    def surr_charge_pp(self, t):
        if t in self._v_surr_charge_pp:
            return self._v_surr_charge_pp[t]
        else:
            val = self._f_surr_charge_pp(t)
            self._v_surr_charge_pp[t] = val
            return val

    def surr_benefit_pp(self, t):
        if t in self._v_surr_benefit_pp:
            return self._v_surr_benefit_pp[t]
        else:
            val = self._f_surr_benefit_pp(t)
            self._v_surr_benefit_pp[t] = val
            return val

    def phi_glwb(self, t):
        if t in self._v_phi_glwb:
            return self._v_phi_glwb[t]
        else:
            val = self._f_phi_glwb(t)
            self._v_phi_glwb[t] = val
            return val

    def fee_rate_vix_raw(self, phi_0, vix_sq_avg):
        if (phi_0, vix_sq_avg) in self._v_fee_rate_vix_raw:
            return self._v_fee_rate_vix_raw[(phi_0, vix_sq_avg)]
        else:
            val = self._f_fee_rate_vix_raw(phi_0, vix_sq_avg)
            self._v_fee_rate_vix_raw[(phi_0, vix_sq_avg)] = val
            return val

    def fee_rate_vix_clip(self, prior, raw):
        if (prior, raw) in self._v_fee_rate_vix_clip:
            return self._v_fee_rate_vix_clip[(prior, raw)]
        else:
            val = self._f_fee_rate_vix_clip(prior, raw)
            self._v_fee_rate_vix_clip[(prior, raw)] = val
            return val

    def phi_glwb_vix(self, k):
        if k in self._v_phi_glwb_vix:
            return self._v_phi_glwb_vix[k]
        else:
            val = self._f_phi_glwb_vix(k)
            self._v_phi_glwb_vix[k] = val
            return val

    def phi_gmdb(self, t):
        if t in self._v_phi_gmdb:
            return self._v_phi_gmdb[t]
        else:
            val = self._f_phi_gmdb(t)
            self._v_phi_gmdb[t] = val
            return val

    def rollup_pct(self):
        if self._has_rollup_pct:
            return self._v_rollup_pct
        else:
            val = self._v_rollup_pct = self._f_rollup_pct()
            self._has_rollup_pct = True
            return val

    def rollup_rate(self, t):
        if t in self._v_rollup_rate:
            return self._v_rollup_rate[t]
        else:
            val = self._f_rollup_rate(t)
            self._v_rollup_rate[t] = val
            return val

    def fee_glwb_pp_due(self, t):
        if t in self._v_fee_glwb_pp_due:
            return self._v_fee_glwb_pp_due[t]
        else:
            val = self._f_fee_glwb_pp_due(t)
            self._v_fee_glwb_pp_due[t] = val
            return val

    def fee_gmdb_pp_due(self, t):
        if t in self._v_fee_gmdb_pp_due:
            return self._v_fee_gmdb_pp_due[t]
        else:
            val = self._f_fee_gmdb_pp_due(t)
            self._v_fee_gmdb_pp_due[t] = val
            return val

    def maint_fee_pp_due(self, t):
        if t in self._v_maint_fee_pp_due:
            return self._v_maint_fee_pp_due[t]
        else:
            val = self._f_maint_fee_pp_due(t)
            self._v_maint_fee_pp_due[t] = val
            return val

    def charge_pp_due(self, t):
        if t in self._v_charge_pp_due:
            return self._v_charge_pp_due[t]
        else:
            val = self._f_charge_pp_due(t)
            self._v_charge_pp_due[t] = val
            return val

    def charge_scale(self, t):
        if t in self._v_charge_scale:
            return self._v_charge_scale[t]
        else:
            val = self._f_charge_scale(t)
            self._v_charge_scale[t] = val
            return val

    def fee_glwb_pp(self, t):
        if t in self._v_fee_glwb_pp:
            return self._v_fee_glwb_pp[t]
        else:
            val = self._f_fee_glwb_pp(t)
            self._v_fee_glwb_pp[t] = val
            return val

    def fee_gmdb_pp(self, t):
        if t in self._v_fee_gmdb_pp:
            return self._v_fee_gmdb_pp[t]
        else:
            val = self._f_fee_gmdb_pp(t)
            self._v_fee_gmdb_pp[t] = val
            return val

    def maint_fee_pp(self, t):
        if t in self._v_maint_fee_pp:
            return self._v_maint_fee_pp[t]
        else:
            val = self._f_maint_fee_pp(t)
            self._v_maint_fee_pp[t] = val
            return val

    def charge_pp(self, t):
        if t in self._v_charge_pp:
            return self._v_charge_pp[t]
        else:
            val = self._f_charge_pp(t)
            self._v_charge_pp[t] = val
            return val

    def charge_income_pp(self, t):
        if t in self._v_charge_income_pp:
            return self._v_charge_income_pp[t]
        else:
            val = self._f_charge_income_pp(t)
            self._v_charge_income_pp[t] = val
            return val

    def gwb_pp_at(self, t, timing):
        if (t, timing) in self._v_gwb_pp_at:
            return self._v_gwb_pp_at[(t, timing)]
        else:
            val = self._f_gwb_pp_at(t, timing)
            self._v_gwb_pp_at[(t, timing)] = val
            return val

    def bb_pp_bef_anniv(self, t):
        if t in self._v_bb_pp_bef_anniv:
            return self._v_bb_pp_bef_anniv[t]
        else:
            val = self._f_bb_pp_bef_anniv(t)
            self._v_bb_pp_bef_anniv[t] = val
            return val

    def bonus_pp(self, t):
        if t in self._v_bonus_pp:
            return self._v_bonus_pp[t]
        else:
            val = self._f_bonus_pp(t)
            self._v_bonus_pp[t] = val
            return val

    def gwb_pp_aft_bonus(self, t):
        if t in self._v_gwb_pp_aft_bonus:
            return self._v_gwb_pp_aft_bonus[t]
        else:
            val = self._f_gwb_pp_aft_bonus(t)
            self._v_gwb_pp_aft_bonus[t] = val
            return val

    def stepup_base_pp(self, t):
        if t in self._v_stepup_base_pp:
            return self._v_stepup_base_pp[t]
        else:
            val = self._f_stepup_base_pp(t)
            self._v_stepup_base_pp[t] = val
            return val

    def is_stepup(self, t):
        if t in self._v_is_stepup:
            return self._v_is_stepup[t]
        else:
            val = self._f_is_stepup(t)
            self._v_is_stepup[t] = val
            return val

    def gwb_pp_aft_stepup(self, t):
        if t in self._v_gwb_pp_aft_stepup:
            return self._v_gwb_pp_aft_stepup[t]
        else:
            val = self._f_gwb_pp_aft_stepup(t)
            self._v_gwb_pp_aft_stepup[t] = val
            return val

    def gwb_adj_year(self):
        if self._has_gwb_adj_year:
            return self._v_gwb_adj_year
        else:
            val = self._v_gwb_adj_year = self._f_gwb_adj_year()
            self._has_gwb_adj_year = True
            return val

    def is_gwb_adj_date(self, t):
        if t in self._v_is_gwb_adj_date:
            return self._v_is_gwb_adj_date[t]
        else:
            val = self._f_is_gwb_adj_date(t)
            self._v_is_gwb_adj_date[t] = val
            return val

    def adj_pp_bef_anniv(self, t):
        if t in self._v_adj_pp_bef_anniv:
            return self._v_adj_pp_bef_anniv[t]
        else:
            val = self._f_adj_pp_bef_anniv(t)
            self._v_adj_pp_bef_anniv[t] = val
            return val

    def adj_pp(self, t):
        if t in self._v_adj_pp:
            return self._v_adj_pp[t]
        else:
            val = self._f_adj_pp(t)
            self._v_adj_pp[t] = val
            return val

    def gwb_pp(self, t):
        if t in self._v_gwb_pp:
            return self._v_gwb_pp[t]
        else:
            val = self._f_gwb_pp(t)
            self._v_gwb_pp[t] = val
            return val

    def bb_pp(self, t):
        if t in self._v_bb_pp:
            return self._v_bb_pp[t]
        else:
            val = self._f_bb_pp(t)
            self._v_bb_pp[t] = val
            return val

    def bonus_end(self, t):
        if t in self._v_bonus_end:
            return self._v_bonus_end[t]
        else:
            val = self._f_bonus_end(t)
            self._v_bonus_end[t] = val
            return val

    def gawa_pct_fixed(self, t):
        if t in self._v_gawa_pct_fixed:
            return self._v_gawa_pct_fixed[t]
        else:
            val = self._f_gawa_pct_fixed(t)
            self._v_gawa_pct_fixed[t] = val
            return val

    def gawa_pp_at(self, t, timing):
        if (t, timing) in self._v_gawa_pp_at:
            return self._v_gawa_pp_at[(t, timing)]
        else:
            val = self._f_gawa_pp_at(t, timing)
            self._v_gawa_pp_at[(t, timing)] = val
            return val

    def gawa_pp(self, t):
        if t in self._v_gawa_pp:
            return self._v_gawa_pp[t]
        else:
            val = self._f_gawa_pp(t)
            self._v_gawa_pp[t] = val
            return val

    def np_pp(self, t):
        if t in self._v_np_pp:
            return self._v_np_pp[t]
        else:
            val = self._f_np_pp(t)
            self._v_np_pp[t] = val
            return val

    def rp_reduction_pp(self, t):
        if t in self._v_rp_reduction_pp:
            return self._v_rp_reduction_pp[t]
        else:
            val = self._f_rp_reduction_pp(t)
            self._v_rp_reduction_pp[t] = val
            return val

    def rp_pp(self, t):
        if t in self._v_rp_pp:
            return self._v_rp_pp[t]
        else:
            val = self._f_rp_pp(t)
            self._v_rp_pp[t] = val
            return val

    def rb_prior_anniv_pp(self, t):
        if t in self._v_rb_prior_anniv_pp:
            return self._v_rb_prior_anniv_pp[t]
        else:
            val = self._f_rb_prior_anniv_pp(t)
            self._v_rb_prior_anniv_pp[t] = val
            return val

    def gmdb_allow_pp(self, t):
        if t in self._v_gmdb_allow_pp:
            return self._v_gmdb_allow_pp[t]
        else:
            val = self._f_gmdb_allow_pp(t)
            self._v_gmdb_allow_pp[t] = val
            return val

    def gmdb_wd_dfd_pp(self, t):
        if t in self._v_gmdb_wd_dfd_pp:
            return self._v_gmdb_wd_dfd_pp[t]
        else:
            val = self._f_gmdb_wd_dfd_pp(t)
            self._v_gmdb_wd_dfd_pp[t] = val
            return val

    def gmdb_wd_excess_pp(self, t):
        if t in self._v_gmdb_wd_excess_pp:
            return self._v_gmdb_wd_excess_pp[t]
        else:
            val = self._f_gmdb_wd_excess_pp(t)
            self._v_gmdb_wd_excess_pp[t] = val
            return val

    def gmdb_wd_factor(self, t):
        if t in self._v_gmdb_wd_factor:
            return self._v_gmdb_wd_factor[t]
        else:
            val = self._f_gmdb_wd_factor(t)
            self._v_gmdb_wd_factor[t] = val
            return val

    def gmdb_dfd_acc_pp(self, t):
        if t in self._v_gmdb_dfd_acc_pp:
            return self._v_gmdb_dfd_acc_pp[t]
        else:
            val = self._f_gmdb_dfd_acc_pp(t)
            self._v_gmdb_dfd_acc_pp[t] = val
            return val

    def gmdb_factor_acc(self, t):
        if t in self._v_gmdb_factor_acc:
            return self._v_gmdb_factor_acc[t]
        else:
            val = self._f_gmdb_factor_acc(t)
            self._v_gmdb_factor_acc[t] = val
            return val

    def rb_pp_at(self, t, timing):
        if (t, timing) in self._v_rb_pp_at:
            return self._v_rb_pp_at[(t, timing)]
        else:
            val = self._f_rb_pp_at(t, timing)
            self._v_rb_pp_at[(t, timing)] = val
            return val

    def rb_pp(self, t):
        if t in self._v_rb_pp:
            return self._v_rb_pp[t]
        else:
            val = self._f_rb_pp(t)
            self._v_rb_pp[t] = val
            return val

    def gmdb_guarantee_pp(self, t):
        if t in self._v_gmdb_guarantee_pp:
            return self._v_gmdb_guarantee_pp[t]
        else:
            val = self._f_gmdb_guarantee_pp(t)
            self._v_gmdb_guarantee_pp[t] = val
            return val

    def db_pp(self, t):
        if t in self._v_db_pp:
            return self._v_db_pp[t]
        else:
            val = self._f_db_pp(t)
            self._v_db_pp[t] = val
            return val

    def gmdb_claim_pp(self, t):
        if t in self._v_gmdb_claim_pp:
            return self._v_gmdb_claim_pp[t]
        else:
            val = self._f_gmdb_claim_pp(t)
            self._v_gmdb_claim_pp[t] = val
            return val

    def forlife_flag(self):
        if self._has_forlife_flag:
            return self._v_forlife_flag
        else:
            val = self._v_forlife_flag = self._f_forlife_flag()
            self._has_forlife_flag = True
            return val

    def depleted_flag(self, t):
        if t in self._v_depleted_flag:
            return self._v_depleted_flag[t]
        else:
            val = self._f_depleted_flag(t)
            self._v_depleted_flag[t] = val
            return val

    def glwb_payment_pp(self, t):
        if t in self._v_glwb_payment_pp:
            return self._v_glwb_payment_pp[t]
        else:
            val = self._f_glwb_payment_pp(t)
            self._v_glwb_payment_pp[t] = val
            return val

    def mort_rate(self, t):
        if t in self._v_mort_rate:
            return self._v_mort_rate[t]
        else:
            val = self._f_mort_rate(t)
            self._v_mort_rate[t] = val
            return val

    def mort_rate_mth(self, t):
        if t in self._v_mort_rate_mth:
            return self._v_mort_rate_mth[t]
        else:
            val = self._f_mort_rate_mth(t)
            self._v_mort_rate_mth[t] = val
            return val

    def lapse_rate_base(self, t):
        if t in self._v_lapse_rate_base:
            return self._v_lapse_rate_base[t]
        else:
            val = self._f_lapse_rate_base(t)
            self._v_lapse_rate_base[t] = val
            return val

    def moneyness_glwb(self, t):
        if t in self._v_moneyness_glwb:
            return self._v_moneyness_glwb[t]
        else:
            val = self._f_moneyness_glwb(t)
            self._v_moneyness_glwb[t] = val
            return val

    def moneyness_gmdb(self, t):
        if t in self._v_moneyness_gmdb:
            return self._v_moneyness_gmdb[t]
        else:
            val = self._f_moneyness_gmdb(t)
            self._v_moneyness_gmdb[t] = val
            return val

    def lapse_itm_mult(self, m):
        if m in self._v_lapse_itm_mult:
            return self._v_lapse_itm_mult[m]
        else:
            val = self._f_lapse_itm_mult(m)
            self._v_lapse_itm_mult[m] = val
            return val

    def lapse_dyn_mult(self, t):
        if t in self._v_lapse_dyn_mult:
            return self._v_lapse_dyn_mult[t]
        else:
            val = self._f_lapse_dyn_mult(t)
            self._v_lapse_dyn_mult[t] = val
            return val

    def lapse_wd_factor(self, t):
        if t in self._v_lapse_wd_factor:
            return self._v_lapse_wd_factor[t]
        else:
            val = self._f_lapse_wd_factor(t)
            self._v_lapse_wd_factor[t] = val
            return val

    def lapse_rate(self, t):
        if t in self._v_lapse_rate:
            return self._v_lapse_rate[t]
        else:
            val = self._f_lapse_rate(t)
            self._v_lapse_rate[t] = val
            return val

    def lapse_rate_mth(self, t):
        if t in self._v_lapse_rate_mth:
            return self._v_lapse_rate_mth[t]
        else:
            val = self._f_lapse_rate_mth(t)
            self._v_lapse_rate_mth[t] = val
            return val

    def pols_if(self, t):
        if t in self._v_pols_if:
            return self._v_pols_if[t]
        else:
            val = self._f_pols_if(t)
            self._v_pols_if[t] = val
            return val

    def pols_if_at(self, t, timing):
        if (t, timing) in self._v_pols_if_at:
            return self._v_pols_if_at[(t, timing)]
        else:
            val = self._f_pols_if_at(t, timing)
            self._v_pols_if_at[(t, timing)] = val
            return val

    def pols_death(self, t):
        if t in self._v_pols_death:
            return self._v_pols_death[t]
        else:
            val = self._f_pols_death(t)
            self._v_pols_death[t] = val
            return val

    def pols_lapse(self, t):
        if t in self._v_pols_lapse:
            return self._v_pols_lapse[t]
        else:
            val = self._f_pols_lapse(t)
            self._v_pols_lapse[t] = val
            return val

    def pols_maturity(self, t):
        if t in self._v_pols_maturity:
            return self._v_pols_maturity[t]
        else:
            val = self._f_pols_maturity(t)
            self._v_pols_maturity[t] = val
            return val

    def pols_decr(self, t, kind):
        if (t, kind) in self._v_pols_decr:
            return self._v_pols_decr[(t, kind)]
        else:
            val = self._f_pols_decr(t, kind)
            self._v_pols_decr[(t, kind)] = val
            return val

    def claim_pp(self, t, kind):
        if (t, kind) in self._v_claim_pp:
            return self._v_claim_pp[(t, kind)]
        else:
            val = self._f_claim_pp(t, kind)
            self._v_claim_pp[(t, kind)] = val
            return val

    def claim_from_av_pp(self, t, kind):
        if (t, kind) in self._v_claim_from_av_pp:
            return self._v_claim_from_av_pp[(t, kind)]
        else:
            val = self._f_claim_from_av_pp(t, kind)
            self._v_claim_from_av_pp[(t, kind)] = val
            return val

    def premiums(self, t):
        if t in self._v_premiums:
            return self._v_premiums[t]
        else:
            val = self._f_premiums(t)
            self._v_premiums[t] = val
            return val

    def prem_to_av(self, t):
        if t in self._v_prem_to_av:
            return self._v_prem_to_av[t]
        else:
            val = self._f_prem_to_av(t)
            self._v_prem_to_av[t] = val
            return val

    def asset_charges(self, t):
        if t in self._v_asset_charges:
            return self._v_asset_charges[t]
        else:
            val = self._f_asset_charges(t)
            self._v_asset_charges[t] = val
            return val

    def fees_glwb(self, t):
        if t in self._v_fees_glwb:
            return self._v_fees_glwb[t]
        else:
            val = self._f_fees_glwb(t)
            self._v_fees_glwb[t] = val
            return val

    def fees_gmdb(self, t):
        if t in self._v_fees_gmdb:
            return self._v_fees_gmdb[t]
        else:
            val = self._f_fees_gmdb(t)
            self._v_fees_gmdb[t] = val
            return val

    def maint_fees(self, t):
        if t in self._v_maint_fees:
            return self._v_maint_fees[t]
        else:
            val = self._f_maint_fees(t)
            self._v_maint_fees[t] = val
            return val

    def wd_charges(self, t):
        if t in self._v_wd_charges:
            return self._v_wd_charges[t]
        else:
            val = self._f_wd_charges(t)
            self._v_wd_charges[t] = val
            return val

    def charge_income(self, t):
        if t in self._v_charge_income:
            return self._v_charge_income[t]
        else:
            val = self._f_charge_income(t)
            self._v_charge_income[t] = val
            return val

    def withdrawals(self, t):
        if t in self._v_withdrawals:
            return self._v_withdrawals[t]
        else:
            val = self._f_withdrawals(t)
            self._v_withdrawals[t] = val
            return val

    def glwb_payments(self, t):
        if t in self._v_glwb_payments:
            return self._v_glwb_payments[t]
        else:
            val = self._f_glwb_payments(t)
            self._v_glwb_payments[t] = val
            return val

    def claims(self, t, kind=None):
        if (t, kind) in self._v_claims:
            return self._v_claims[(t, kind)]
        else:
            val = self._f_claims(t, kind)
            self._v_claims[(t, kind)] = val
            return val

    def claims_from_av(self, t, kind):
        if (t, kind) in self._v_claims_from_av:
            return self._v_claims_from_av[(t, kind)]
        else:
            val = self._f_claims_from_av(t, kind)
            self._v_claims_from_av[(t, kind)] = val
            return val

    def claims_over_av(self, t, kind=None):
        if (t, kind) in self._v_claims_over_av:
            return self._v_claims_over_av[(t, kind)]
        else:
            val = self._f_claims_over_av(t, kind)
            self._v_claims_over_av[(t, kind)] = val
            return val

    def gmdb_claims(self, t):
        if t in self._v_gmdb_claims:
            return self._v_gmdb_claims[t]
        else:
            val = self._f_gmdb_claims(t)
            self._v_gmdb_claims[t] = val
            return val

    def commissions(self, t):
        if t in self._v_commissions:
            return self._v_commissions[t]
        else:
            val = self._f_commissions(t)
            self._v_commissions[t] = val
            return val

    def premium_taxes(self, t):
        if t in self._v_premium_taxes:
            return self._v_premium_taxes[t]
        else:
            val = self._f_premium_taxes(t)
            self._v_premium_taxes[t] = val
            return val

    def inflation_factor(self, t):
        if t in self._v_inflation_factor:
            return self._v_inflation_factor[t]
        else:
            val = self._f_inflation_factor(t)
            self._v_inflation_factor[t] = val
            return val

    def expenses(self, t):
        if t in self._v_expenses:
            return self._v_expenses[t]
        else:
            val = self._f_expenses(t)
            self._v_expenses[t] = val
            return val

    def net_cf(self, t):
        if t in self._v_net_cf:
            return self._v_net_cf[t]
        else:
            val = self._f_net_cf(t)
            self._v_net_cf[t] = val
            return val

    def net_cf_ga(self, t):
        if t in self._v_net_cf_ga:
            return self._v_net_cf_ga[t]
        else:
            val = self._f_net_cf_ga(t)
            self._v_net_cf_ga[t] = val
            return val

    def av_at(self, t, timing):
        if (t, timing) in self._v_av_at:
            return self._v_av_at[(t, timing)]
        else:
            val = self._f_av_at(t, timing)
            self._v_av_at[(t, timing)] = val
            return val

    def inv_income(self, t):
        if t in self._v_inv_income:
            return self._v_inv_income[t]
        else:
            val = self._f_inv_income(t)
            self._v_inv_income[t] = val
            return val

    def wd_from_av(self, t):
        if t in self._v_wd_from_av:
            return self._v_wd_from_av[t]
        else:
            val = self._f_wd_from_av(t)
            self._v_wd_from_av[t] = val
            return val

    def charges_from_av(self, t):
        if t in self._v_charges_from_av:
            return self._v_charges_from_av[t]
        else:
            val = self._f_charges_from_av(t)
            self._v_charges_from_av[t] = val
            return val

    def av_change(self, t):
        if t in self._v_av_change:
            return self._v_av_change[t]
        else:
            val = self._f_av_change(t)
            self._v_av_change[t] = val
            return val

    def check_av_roll_fwd_resid(self, t):
        if t in self._v_check_av_roll_fwd_resid:
            return self._v_check_av_roll_fwd_resid[t]
        else:
            val = self._f_check_av_roll_fwd_resid(t)
            self._v_check_av_roll_fwd_resid[t] = val
            return val

    def check_av_roll_fwd(self):
        if self._has_check_av_roll_fwd:
            return self._v_check_av_roll_fwd
        else:
            val = self._v_check_av_roll_fwd = self._f_check_av_roll_fwd()
            self._has_check_av_roll_fwd = True
            return val

    def check_pols_roll_fwd_resid(self, t):
        if t in self._v_check_pols_roll_fwd_resid:
            return self._v_check_pols_roll_fwd_resid[t]
        else:
            val = self._f_check_pols_roll_fwd_resid(t)
            self._v_check_pols_roll_fwd_resid[t] = val
            return val

    def check_pols_roll_fwd(self):
        if self._has_check_pols_roll_fwd:
            return self._v_check_pols_roll_fwd
        else:
            val = self._v_check_pols_roll_fwd = self._f_check_pols_roll_fwd()
            self._has_check_pols_roll_fwd = True
            return val

    def check_charge_split_resid(self, t):
        if t in self._v_check_charge_split_resid:
            return self._v_check_charge_split_resid[t]
        else:
            val = self._f_check_charge_split_resid(t)
            self._v_check_charge_split_resid[t] = val
            return val

    def check_charge_split(self):
        if self._has_check_charge_split:
            return self._v_check_charge_split
        else:
            val = self._v_check_charge_split = self._f_check_charge_split()
            self._has_check_charge_split = True
            return val

    def result_cf(self):
        if self._has_result_cf:
            return self._v_result_cf
        else:
            val = self._v_result_cf = self._f_result_cf()
            self._has_result_cf = True
            return val

    def result_pols(self):
        if self._has_result_pols:
            return self._v_result_pols
        else:
            val = self._v_result_pols = self._f_result_pols()
            self._has_result_pols = True
            return val

    def result_av(self):
        if self._has_result_av:
            return self._v_result_av
        else:
            val = self._v_result_av = self._f_result_av()
            self._has_result_av = True
            return val

    def result_bases(self):
        if self._has_result_bases:
            return self._v_result_bases
        else:
            val = self._v_result_bases = self._f_result_bases()
            self._has_result_bases = True
            return val

    def bench_net_cf(self):
        if self._has_bench_net_cf:
            return self._v_bench_net_cf
        else:
            val = self._v_bench_net_cf = self._f_bench_net_cf()
            self._has_bench_net_cf = True
            return val



    def _mx_copy_params(self, other):
        # Parameter assignment
        other.point_id = self.point_id

    @staticmethod
    def _mx_assign_params(_mx_space, point_id):
        # Parameter assignment
        _mx_space.point_id = point_id

    def __call__(self, point_id):
        _mx_key = point_id
        if _mx_key in self._mx_itemspaces:
            return self._mx_itemspaces[_mx_key]
        else:
            _mx_base = self
            _mx_root = _mx_base.__class__(self)
            for _mx_s, _mx_b in zip(_mx_root._mx_walk(), _mx_base._mx_walk()):
                _mx_s._mx_copy_refs(_mx_b, _mx_base)
                for _mx_r in self._mx_roots:
                    _mx_r._mx_copy_params(_mx_s)

                self._mx_assign_params(_mx_s, point_id)
                _mx_s._mx_roots.extend(self._mx_roots)
                _mx_s._mx_roots.append(_mx_root)

            self._mx_itemspaces[_mx_key] = _mx_root
            return _mx_root



    def __getitem__(self, item):
        return self.__call__(item)


    def __delitem__(self, item):
        del self._mx_itemspaces[item]


