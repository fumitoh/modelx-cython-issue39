from cython.cimports.ULSG_US_S_mxg_82773408d0_nomx_cy import _mx_sys
import cython as _mx_cy
from . import _mx_sys



_v_cells_names_Data = [
    'input_dir',
    'model_point_table',
    'coi_rates',
    'corridor_factors',
    'mort_table',
    'class_factor_table',
    'lapse_table',
    'surr_charge_table',
    'rop_table',
]
_v_space_params_Data = []


@_mx_cy.cclass
class _c_Data(_mx_sys.BaseSpace):
    
    _v_input_dir: object
    _has_input_dir: _mx_cy.bint
    _v_model_point_table: object
    _has_model_point_table: _mx_cy.bint
    _v_coi_rates: object
    _has_coi_rates: _mx_cy.bint
    _v_corridor_factors: object
    _has_corridor_factors: _mx_cy.bint
    _v_mort_table: object
    _has_mort_table: _mx_cy.bint
    _v_class_factor_table: object
    _has_class_factor_table: _mx_cy.bint
    _v_lapse_table: object
    _has_lapse_table: _mx_cy.bint
    _v_surr_charge_table: object
    _has_surr_charge_table: _mx_cy.bint
    _v_rop_table: object
    _has_rop_table: _mx_cy.bint
    
    model_point_file: str
    coi_rates_file: str
    corridor_file: str
    mort_table_file: str
    class_factor_file: str
    lapse_table_file: str
    surr_charge_file: str
    rop_file: str
    pd: object

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

    def _mx_assign_refs(self, io_data, pickle_data):

        # Reference assignment
        self.model_point_file = 'model_point_table.csv'
        self.coi_rates_file = 'coi_rates.csv'
        self.corridor_file = 'corridor_factors.csv'
        self.mort_table_file = 'mort_table.csv'
        self.class_factor_file = 'class_factor_table.csv'
        self.lapse_table_file = 'lapse_table.csv'
        self.surr_charge_file = 'surr_charge_table.csv'
        self.rop_file = 'rop_table.csv'
        self.pd = _mx_sys.import_module('pandas')

    @_mx_cy.ccall
    def _mx_copy_refs(self, base, base_root):
        
        base_: _c_Data = _mx_cy.cast(_c_Data, base)

        # Reference assignment
        self.model_point_file = base_.model_point_file
        self.coi_rates_file = base_.coi_rates_file
        self.corridor_file = base_.corridor_file
        self.mort_table_file = base_.mort_table_file
        self.class_factor_file = base_.class_factor_file
        self.lapse_table_file = base_.lapse_table_file
        self.surr_charge_file = base_.surr_charge_file
        self.rop_file = base_.rop_file
        self.pd = base_.pd

    @_mx_cy.cfunc
    def _f_input_dir(self) -> object:
        """The directory holding the input CSVs: the model folder's parent.

        Inputs are *external* files, not data stored inside the model, so the model
        folder is pure formulas.  The path is resolved at run time from where the model
        was read, following ``annuallife.TradLife_A``.
        """
        return self._model.path.parent                                        # noqa: F821

    @_mx_cy.cfunc
    def _f_model_point_table(self) -> object:
        """The model point table, read from *model_point_table.csv*."""
        return self.pd.read_csv(self.input_dir() / self.model_point_file, index_col="point_id")  # noqa: F821

    @_mx_cy.cfunc
    def _f_coi_rates(self) -> object:
        """Guaranteed maximum **annual** COI rates, read from *coi_rates.csv*.

        Per $1,000 of net amount at risk, keyed by sex, rate class and **attained** age.
        The monthly rate is the annual rate divided by twelve **[std]** structure; [R3]
        requires the guaranteed maxima to be stated in the policy, and [REG-R17] names the
        2017 CSO family the notes point at.
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.coi_rates_file,                                # noqa: F821
            index_col=["sex", "rate_class", "age"])

    @_mx_cy.cfunc
    def _f_corridor_factors(self) -> object:
        """The GPT corridor factor table by attained age, read from *corridor_factors.csv*."""
        return self.pd.read_csv(self.input_dir() / self.corridor_file, index_col="age")  # noqa: F821

    @_mx_cy.cfunc
    def _f_mort_table(self) -> object:
        """The best-estimate annual mortality table by attained age, read from *mort_table.csv*."""
        return self.pd.read_csv(self.input_dir() / self.mort_table_file, index_col="age")  # noqa: F821

    @_mx_cy.cfunc
    def _f_class_factor_table(self) -> object:
        """The underwriting-class factors, read from *class_factor_table.csv*."""
        return self.pd.read_csv(self.input_dir() / self.class_factor_file, index_col="rate_class")  # noqa: F821

    @_mx_cy.cfunc
    def _f_lapse_table(self) -> object:
        """The base annual lapse rates by policy year, read from *lapse_table.csv*."""
        return self.pd.read_csv(self.input_dir() / self.lapse_table_file, index_col="policy_year")  # noqa: F821

    @_mx_cy.cfunc
    def _f_surr_charge_table(self) -> object:
        """The surrender charge schedules, read from *surr_charge_table.csv*.

        One row per ``surr_charge_id``, giving the initial charge per $1,000 of initial
        face and the number of years over which it runs off linearly.
        """
        return self.pd.read_csv(self.input_dir() / self.surr_charge_file, index_col="surr_charge_id")  # noqa: F821

    @_mx_cy.cfunc
    def _f_rop_table(self) -> object:
        """The return-of-premium exercise windows, read from *rop_table.csv*.

        One row per policy anniversary carrying a window: the refund ratio applied to
        cumulative premiums [S1] and the **[std]** exercise rate.
        """
        return self.pd.read_csv(self.input_dir() / self.rop_file, index_col="anniversary")  # noqa: F821


    @_mx_cy.ccall
    def input_dir(self) -> object:
        if self._has_input_dir:
            return self._v_input_dir
        else:
            val = self._v_input_dir = self._f_input_dir()
            self._has_input_dir = True
            return val

    @_mx_cy.ccall
    def model_point_table(self) -> object:
        if self._has_model_point_table:
            return self._v_model_point_table
        else:
            val = self._v_model_point_table = self._f_model_point_table()
            self._has_model_point_table = True
            return val

    @_mx_cy.ccall
    def coi_rates(self) -> object:
        if self._has_coi_rates:
            return self._v_coi_rates
        else:
            val = self._v_coi_rates = self._f_coi_rates()
            self._has_coi_rates = True
            return val

    @_mx_cy.ccall
    def corridor_factors(self) -> object:
        if self._has_corridor_factors:
            return self._v_corridor_factors
        else:
            val = self._v_corridor_factors = self._f_corridor_factors()
            self._has_corridor_factors = True
            return val

    @_mx_cy.ccall
    def mort_table(self) -> object:
        if self._has_mort_table:
            return self._v_mort_table
        else:
            val = self._v_mort_table = self._f_mort_table()
            self._has_mort_table = True
            return val

    @_mx_cy.ccall
    def class_factor_table(self) -> object:
        if self._has_class_factor_table:
            return self._v_class_factor_table
        else:
            val = self._v_class_factor_table = self._f_class_factor_table()
            self._has_class_factor_table = True
            return val

    @_mx_cy.ccall
    def lapse_table(self) -> object:
        if self._has_lapse_table:
            return self._v_lapse_table
        else:
            val = self._v_lapse_table = self._f_lapse_table()
            self._has_lapse_table = True
            return val

    @_mx_cy.ccall
    def surr_charge_table(self) -> object:
        if self._has_surr_charge_table:
            return self._v_surr_charge_table
        else:
            val = self._v_surr_charge_table = self._f_surr_charge_table()
            self._has_surr_charge_table = True
            return val

    @_mx_cy.ccall
    def rop_table(self) -> object:
        if self._has_rop_table:
            return self._v_rop_table
        else:
            val = self._v_rop_table = self._f_rop_table()
            self._has_rop_table = True
            return val










_v_cells_names_Projection = [
    'model_point',
    'age_at_entry',
    'sex',
    'rate_class',
    'sum_assured',
    'guarantee_age',
    'premium_type',
    'premium_mode',
    'premium_pp_ann',
    'load_prem_rate',
    'av_pp_init',
    'sg_pp_init',
    'loan_bal_init',
    'cum_prem_init',
    'pols_if_init',
    'duration_mth_init',
    'has_surr_charge',
    'surr_charge_id',
    'rop_elected',
    'coi_rate_dp',
    'duration_mth',
    'duration',
    'policy_year',
    'age',
    'proj_len',
    'sum_assured_at',
    'units',
    'crediting_rate_ann',
    'inv_return_mth',
    'guar_rate_mth',
    'sg_rate_mth',
    'naar_factor',
    'sg_naar_factor',
    'loan_rate_mth',
    'loan_cr_rate_mth',
    'premium_freq',
    'is_premium_mth',
    'prem_persistency',
    'premium_pp',
    'prem_to_av_pp',
    'prem_to_sg_pp',
    'prem_to_av',
    'premiums',
    'cum_prem_pp',
    'wd_pp',
    'wd_fee_pp',
    'wd_fees',
    'corridor_factor',
    'db_pp',
    'net_amt_at_risk',
    'sg_net_amt_at_risk',
    'coi_rate_scale',
    'coi_rate_guar',
    'coi_rate',
    'sg_coi_rate',
    'coi_pp',
    'sg_coi_pp',
    'rider_charge_pp',
    'maint_fee_pp',
    'sg_maint_fee_pp',
    'mth_deduction_pp',
    'sg_deduction_pp',
    'maint_fee_taken_pp',
    'coi_taken_pp',
    'mth_deduction_taken_pp',
    'mth_deduction_forgone_pp',
    'maint_fee',
    'coi',
    'mth_deduction',
    'mth_deduction_forgone',
    'av_pp_at',
    'inv_income_pp',
    'av_pp',
    'av_at',
    'inv_income',
    'av_change',
    'loan_bal_pp',
    'sg_pp_at',
    'sg_inv_income_pp',
    'sg_pp',
    'sg_net_pp',
    'is_guar_active',
    'is_guar_supported',
    'catch_up_prem_pp',
    'surr_charge_rate',
    'surr_charge_pp',
    'csv_pp',
    'ncsv_pp',
    'surr_charge',
    'is_shortfall',
    'cure_premium_pp',
    'grace_mth',
    'is_lapsed',
    'status',
    'rop_anniversary',
    'rop_ratio',
    'rop_rate',
    'class_factor',
    'mort_improve_rate',
    'mort_improve_factor',
    'mort_rate',
    'mort_rate_mth',
    'lapse_rate_base',
    'lapse_rate_guar_mult',
    'lapse_rate_pattern_mult',
    'lapse_rate_dyn_mult',
    'lapse_rate',
    'lapse_rate_mth',
    'pols_if',
    'pols_if_at',
    'pols_death',
    'pols_lapse',
    'pols_rop',
    'pols_lapse_grace',
    'pols_maturity',
    'claim_pp',
    'claims_from_av',
    'claims_over_av',
    'claims',
    'withdrawals',
    'inflation_factor',
    'expenses',
    'premium_taxes',
    'margin_expense',
    'margin_mortality',
    'margin_rop',
    'net_cf',
    'solve_len',
    'sg_pp_solve',
    'guar_min_sg',
    'no_lapse_premium',
    'check_av_roll_fwd',
    'check_sg_roll_fwd',
    'check_margin',
    'result_cf',
    'result_pols',
    'result_av',
    'result_guar',
    'bench_net_cf',
]
_v_space_params_Projection = [
    'point_id',
]


@_mx_cy.cclass
class _c_Projection(_mx_sys.BaseSpace):
    
    _v_model_point: object
    _has_model_point: _mx_cy.bint
    _v_age_at_entry: _mx_cy.longlong
    _has_age_at_entry: _mx_cy.bint
    _v_sex: str
    _has_sex: _mx_cy.bint
    _v_rate_class: str
    _has_rate_class: _mx_cy.bint
    _v_sum_assured: _mx_cy.double
    _has_sum_assured: _mx_cy.bint
    _v_guarantee_age: _mx_cy.longlong
    _has_guarantee_age: _mx_cy.bint
    _v_premium_type: str
    _has_premium_type: _mx_cy.bint
    _v_premium_mode: str
    _has_premium_mode: _mx_cy.bint
    _v_premium_pp_ann: _mx_cy.double
    _has_premium_pp_ann: _mx_cy.bint
    _v_load_prem_rate: _mx_cy.double
    _has_load_prem_rate: _mx_cy.bint
    _v_av_pp_init: _mx_cy.double
    _has_av_pp_init: _mx_cy.bint
    _v_sg_pp_init: _mx_cy.double
    _has_sg_pp_init: _mx_cy.bint
    _v_loan_bal_init: _mx_cy.double
    _has_loan_bal_init: _mx_cy.bint
    _v_cum_prem_init: _mx_cy.double
    _has_cum_prem_init: _mx_cy.bint
    _v_pols_if_init: _mx_cy.double
    _has_pols_if_init: _mx_cy.bint
    _v_duration_mth_init: _mx_cy.longlong
    _has_duration_mth_init: _mx_cy.bint
    _v_has_surr_charge: _mx_cy.bint
    _has_has_surr_charge: _mx_cy.bint
    _v_surr_charge_id: str
    _has_surr_charge_id: _mx_cy.bint
    _v_rop_elected: _mx_cy.bint
    _has_rop_elected: _mx_cy.bint
    _v_coi_rate_dp: _mx_cy.longlong
    _has_coi_rate_dp: _mx_cy.bint
    _v_duration_mth: _mx_cy.longlong[733]
    _has_duration_mth: _mx_cy.bint[733]
    _v_duration: _mx_cy.longlong[733]
    _has_duration: _mx_cy.bint[733]
    _v_policy_year: _mx_cy.longlong[733]
    _has_policy_year: _mx_cy.bint[733]
    _v_age: _mx_cy.longlong[733]
    _has_age: _mx_cy.bint[733]
    _v_proj_len: _mx_cy.longlong
    _has_proj_len: _mx_cy.bint
    _v_sum_assured_at: _mx_cy.double[733]
    _has_sum_assured_at: _mx_cy.bint[733]
    _v_units: _mx_cy.double[733]
    _has_units: _mx_cy.bint[733]
    _v_crediting_rate_ann: _mx_cy.double[733]
    _has_crediting_rate_ann: _mx_cy.bint[733]
    _v_inv_return_mth: _mx_cy.double[733]
    _has_inv_return_mth: _mx_cy.bint[733]
    _v_guar_rate_mth: _mx_cy.double
    _has_guar_rate_mth: _mx_cy.bint
    _v_sg_rate_mth: _mx_cy.double
    _has_sg_rate_mth: _mx_cy.bint
    _v_naar_factor: _mx_cy.double
    _has_naar_factor: _mx_cy.bint
    _v_sg_naar_factor: _mx_cy.double
    _has_sg_naar_factor: _mx_cy.bint
    _v_loan_rate_mth: _mx_cy.double
    _has_loan_rate_mth: _mx_cy.bint
    _v_loan_cr_rate_mth: _mx_cy.double
    _has_loan_cr_rate_mth: _mx_cy.bint
    _v_premium_freq: _mx_cy.longlong
    _has_premium_freq: _mx_cy.bint
    _v_is_premium_mth: _mx_cy.bint[733]
    _has_is_premium_mth: _mx_cy.bint[733]
    _v_prem_persistency: _mx_cy.double[733]
    _has_prem_persistency: _mx_cy.bint[733]
    _v_premium_pp: _mx_cy.double[733]
    _has_premium_pp: _mx_cy.bint[733]
    _v_prem_to_av_pp: _mx_cy.double[733]
    _has_prem_to_av_pp: _mx_cy.bint[733]
    _v_prem_to_sg_pp: _mx_cy.double[733]
    _has_prem_to_sg_pp: _mx_cy.bint[733]
    _v_prem_to_av: dict
    _v_premiums: _mx_cy.double[733]
    _has_premiums: _mx_cy.bint[733]
    _v_cum_prem_pp: _mx_cy.double[733]
    _has_cum_prem_pp: _mx_cy.bint[733]
    _v_wd_pp: _mx_cy.double[733]
    _has_wd_pp: _mx_cy.bint[733]
    _v_wd_fee_pp: _mx_cy.double[733]
    _has_wd_fee_pp: _mx_cy.bint[733]
    _v_wd_fees: dict
    _v_corridor_factor: _mx_cy.double[733]
    _has_corridor_factor: _mx_cy.bint[733]
    _v_db_pp: _mx_cy.double[733]
    _has_db_pp: _mx_cy.bint[733]
    _v_net_amt_at_risk: _mx_cy.double[733]
    _has_net_amt_at_risk: _mx_cy.bint[733]
    _v_sg_net_amt_at_risk: _mx_cy.double[733]
    _has_sg_net_amt_at_risk: _mx_cy.bint[733]
    _v_coi_rate_scale: object
    _has_coi_rate_scale: _mx_cy.bint
    _v_coi_rate_guar: _mx_cy.double[733]
    _has_coi_rate_guar: _mx_cy.bint[733]
    _v_coi_rate: _mx_cy.double[733]
    _has_coi_rate: _mx_cy.bint[733]
    _v_sg_coi_rate: _mx_cy.double[733]
    _has_sg_coi_rate: _mx_cy.bint[733]
    _v_coi_pp: _mx_cy.double[733]
    _has_coi_pp: _mx_cy.bint[733]
    _v_sg_coi_pp: _mx_cy.double[733]
    _has_sg_coi_pp: _mx_cy.bint[733]
    _v_rider_charge_pp: _mx_cy.double[733]
    _has_rider_charge_pp: _mx_cy.bint[733]
    _v_maint_fee_pp: _mx_cy.double[733]
    _has_maint_fee_pp: _mx_cy.bint[733]
    _v_sg_maint_fee_pp: _mx_cy.double[733]
    _has_sg_maint_fee_pp: _mx_cy.bint[733]
    _v_mth_deduction_pp: dict
    _v_sg_deduction_pp: dict
    _v_maint_fee_taken_pp: dict
    _v_coi_taken_pp: dict
    _v_mth_deduction_taken_pp: dict
    _v_mth_deduction_forgone_pp: dict
    _v_maint_fee: dict
    _v_coi: dict
    _v_mth_deduction: dict
    _v_mth_deduction_forgone: dict
    _v_av_pp_at: dict
    _v_inv_income_pp: _mx_cy.double[733]
    _has_inv_income_pp: _mx_cy.bint[733]
    _v_av_pp: _mx_cy.double[733]
    _has_av_pp: _mx_cy.bint[733]
    _v_av_at: dict
    _v_inv_income: dict
    _v_av_change: dict
    _v_loan_bal_pp: _mx_cy.double[733]
    _has_loan_bal_pp: _mx_cy.bint[733]
    _v_sg_pp_at: dict
    _v_sg_inv_income_pp: _mx_cy.double[733]
    _has_sg_inv_income_pp: _mx_cy.bint[733]
    _v_sg_pp: _mx_cy.double[733]
    _has_sg_pp: _mx_cy.bint[733]
    _v_sg_net_pp: _mx_cy.double[733]
    _has_sg_net_pp: _mx_cy.bint[733]
    _v_is_guar_active: _mx_cy.bint[733]
    _has_is_guar_active: _mx_cy.bint[733]
    _v_is_guar_supported: _mx_cy.bint[733]
    _has_is_guar_supported: _mx_cy.bint[733]
    _v_catch_up_prem_pp: dict
    _v_surr_charge_rate: _mx_cy.double[733]
    _has_surr_charge_rate: _mx_cy.bint[733]
    _v_surr_charge_pp: _mx_cy.double[733]
    _has_surr_charge_pp: _mx_cy.bint[733]
    _v_csv_pp: _mx_cy.double[733]
    _has_csv_pp: _mx_cy.bint[733]
    _v_ncsv_pp: _mx_cy.double[733]
    _has_ncsv_pp: _mx_cy.bint[733]
    _v_surr_charge: dict
    _v_is_shortfall: _mx_cy.bint[733]
    _has_is_shortfall: _mx_cy.bint[733]
    _v_cure_premium_pp: dict
    _v_grace_mth: _mx_cy.longlong[733]
    _has_grace_mth: _mx_cy.bint[733]
    _v_is_lapsed: _mx_cy.bint[733]
    _has_is_lapsed: _mx_cy.bint[733]
    _v_status: dict
    _v_rop_anniversary: _mx_cy.longlong[733]
    _has_rop_anniversary: _mx_cy.bint[733]
    _v_rop_ratio: _mx_cy.double[733]
    _has_rop_ratio: _mx_cy.bint[733]
    _v_rop_rate: _mx_cy.double[733]
    _has_rop_rate: _mx_cy.bint[733]
    _v_class_factor: _mx_cy.double
    _has_class_factor: _mx_cy.bint
    _v_mort_improve_rate: _mx_cy.double[733]
    _has_mort_improve_rate: _mx_cy.bint[733]
    _v_mort_improve_factor: _mx_cy.double[733]
    _has_mort_improve_factor: _mx_cy.bint[733]
    _v_mort_rate: _mx_cy.double[733]
    _has_mort_rate: _mx_cy.bint[733]
    _v_mort_rate_mth: _mx_cy.double[733]
    _has_mort_rate_mth: _mx_cy.bint[733]
    _v_lapse_rate_base: _mx_cy.double[733]
    _has_lapse_rate_base: _mx_cy.bint[733]
    _v_lapse_rate_guar_mult: _mx_cy.double
    _has_lapse_rate_guar_mult: _mx_cy.bint
    _v_lapse_rate_pattern_mult: _mx_cy.double
    _has_lapse_rate_pattern_mult: _mx_cy.bint
    _v_lapse_rate_dyn_mult: _mx_cy.double[733]
    _has_lapse_rate_dyn_mult: _mx_cy.bint[733]
    _v_lapse_rate: _mx_cy.double[733]
    _has_lapse_rate: _mx_cy.bint[733]
    _v_lapse_rate_mth: _mx_cy.double[733]
    _has_lapse_rate_mth: _mx_cy.bint[733]
    _v_pols_if: _mx_cy.double[733]
    _has_pols_if: _mx_cy.bint[733]
    _v_pols_if_at: dict
    _v_pols_death: _mx_cy.double[733]
    _has_pols_death: _mx_cy.bint[733]
    _v_pols_lapse: _mx_cy.double[733]
    _has_pols_lapse: _mx_cy.bint[733]
    _v_pols_rop: _mx_cy.double[733]
    _has_pols_rop: _mx_cy.bint[733]
    _v_pols_lapse_grace: _mx_cy.double[733]
    _has_pols_lapse_grace: _mx_cy.bint[733]
    _v_pols_maturity: dict
    _v_claim_pp: dict
    _v_claims_from_av: dict
    _v_claims_over_av: dict
    _v_claims: dict
    _v_withdrawals: _mx_cy.double[733]
    _has_withdrawals: _mx_cy.bint[733]
    _v_inflation_factor: _mx_cy.double[733]
    _has_inflation_factor: _mx_cy.bint[733]
    _v_expenses: _mx_cy.double[733]
    _has_expenses: _mx_cy.bint[733]
    _v_premium_taxes: _mx_cy.double[733]
    _has_premium_taxes: _mx_cy.bint[733]
    _v_margin_expense: dict
    _v_margin_mortality: dict
    _v_margin_rop: dict
    _v_net_cf: _mx_cy.double[733]
    _has_net_cf: _mx_cy.bint[733]
    _v_solve_len: object
    _has_solve_len: _mx_cy.bint
    _v_sg_pp_solve: dict
    _v_guar_min_sg: dict
    _v_no_lapse_premium: object
    _has_no_lapse_premium: _mx_cy.bint
    _v_check_av_roll_fwd: object
    _has_check_av_roll_fwd: _mx_cy.bint
    _v_check_sg_roll_fwd: object
    _has_check_sg_roll_fwd: _mx_cy.bint
    _v_check_margin: object
    _has_check_margin: _mx_cy.bint
    _v_result_cf: object
    _has_result_cf: _mx_cy.bint
    _v_result_pols: object
    _has_result_pols: _mx_cy.bint
    _v_result_av: object
    _has_result_av: _mx_cy.bint
    _v_result_guar: object
    _has_result_guar: _mx_cy.bint
    _v_bench_net_cf: _mx_cy.double
    _has_bench_net_cf: _mx_cy.bint
    
    data: _c_Data
    point_id: _mx_cy.longlong
    charges_cease_age: _mx_cy.longlong
    lifetime_guarantee_age: _mx_cy.longlong
    guar_rate_ann: _mx_cy.double
    crediting_rate_curr: _mx_cy.double
    sg_rate_ann: _mx_cy.double
    coi_curr_factor: _mx_cy.double
    coi_sg_factor: _mx_cy.double
    load_prem_rate_sg: _mx_cy.double
    expense_pol_mth: _mx_cy.double
    expense_unit_mth: _mx_cy.double
    expense_unit_mth_sg: _mx_cy.double
    loan_rate_ann: _mx_cy.double
    loan_cr_rate_ann: _mx_cy.double
    wd_fee: _mx_cy.double
    wd_first_year: _mx_cy.longlong
    ten_pay_years: _mx_cy.longlong
    prem_persistency_ann: _mx_cy.double
    grace_months: _mx_cy.longlong
    rop_cap_rate: _mx_cy.double
    mort_ae_factor: _mx_cy.double
    mort_improve_rate_init: _mx_cy.double
    mort_improve_full_age: _mx_cy.longlong
    mort_improve_end_age: _mx_cy.longlong
    mort_improve_max_years: _mx_cy.longlong
    lapse_guar_mult: _mx_cy.double
    lapse_pattern_mult_single: _mx_cy.double
    lapse_pattern_mult_ten_pay: _mx_cy.double
    lapse_dyn_mult_guar_only: _mx_cy.double
    lapse_dyn_mult_guar_failed: _mx_cy.double
    lapse_rate_floor: _mx_cy.double
    lapse_rate_cap: _mx_cy.double
    expense_acq: _mx_cy.double
    expense_acq_prem_rate: _mx_cy.double
    expense_maint: _mx_cy.double
    expense_claim: _mx_cy.double
    inflation_rate: _mx_cy.double
    premium_tax_rate: _mx_cy.double
    solve_tol: _mx_cy.double
    solve_max_doublings: _mx_cy.longlong
    pd: object
    math: object

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

    def _mx_assign_refs(self, io_data, pickle_data):

        # Reference assignment
        self.data = self._parent.Data
        self.point_id = 1
        self.charges_cease_age = 121
        self.lifetime_guarantee_age = 121
        self.guar_rate_ann = 0.02
        self.crediting_rate_curr = 0.035
        self.sg_rate_ann = 0.055
        self.coi_curr_factor = 0.65
        self.coi_sg_factor = 0.55
        self.load_prem_rate_sg = 0.08
        self.expense_pol_mth = 5.5
        self.expense_unit_mth = 0.2
        self.expense_unit_mth_sg = 0.05
        self.loan_rate_ann = 0.05
        self.loan_cr_rate_ann = 0.03
        self.wd_fee = 25.0
        self.wd_first_year = 1
        self.ten_pay_years = 10
        self.prem_persistency_ann = 0.98
        self.grace_months = 2
        self.rop_cap_rate = 0.4
        self.mort_ae_factor = 1.0
        self.mort_improve_rate_init = 0.01
        self.mort_improve_full_age = 85
        self.mort_improve_end_age = 95
        self.mort_improve_max_years = 20
        self.lapse_guar_mult = 0.55
        self.lapse_pattern_mult_single = 0.6
        self.lapse_pattern_mult_ten_pay = 0.8
        self.lapse_dyn_mult_guar_only = 0.6
        self.lapse_dyn_mult_guar_failed = 2.0
        self.lapse_rate_floor = 0.003
        self.lapse_rate_cap = 0.5
        self.expense_acq = 300.0
        self.expense_acq_prem_rate = 0.9
        self.expense_maint = 75.0
        self.expense_claim = 300.0
        self.inflation_rate = 0.025
        self.premium_tax_rate = 0.0
        self.solve_tol = 0.01
        self.solve_max_doublings = 40
        self.pd = _mx_sys.import_module('pandas')
        self.math = _mx_sys.import_module('math')

    @_mx_cy.ccall
    def _mx_copy_refs(self, base, base_root):
        
        base_: _c_Projection = _mx_cy.cast(_c_Projection, base)

        # Reference assignment
        self.data = self._parent.Data if base_.data._mx_is_in(base_root) else base_.data
        self.point_id = base_.point_id
        self.charges_cease_age = base_.charges_cease_age
        self.lifetime_guarantee_age = base_.lifetime_guarantee_age
        self.guar_rate_ann = base_.guar_rate_ann
        self.crediting_rate_curr = base_.crediting_rate_curr
        self.sg_rate_ann = base_.sg_rate_ann
        self.coi_curr_factor = base_.coi_curr_factor
        self.coi_sg_factor = base_.coi_sg_factor
        self.load_prem_rate_sg = base_.load_prem_rate_sg
        self.expense_pol_mth = base_.expense_pol_mth
        self.expense_unit_mth = base_.expense_unit_mth
        self.expense_unit_mth_sg = base_.expense_unit_mth_sg
        self.loan_rate_ann = base_.loan_rate_ann
        self.loan_cr_rate_ann = base_.loan_cr_rate_ann
        self.wd_fee = base_.wd_fee
        self.wd_first_year = base_.wd_first_year
        self.ten_pay_years = base_.ten_pay_years
        self.prem_persistency_ann = base_.prem_persistency_ann
        self.grace_months = base_.grace_months
        self.rop_cap_rate = base_.rop_cap_rate
        self.mort_ae_factor = base_.mort_ae_factor
        self.mort_improve_rate_init = base_.mort_improve_rate_init
        self.mort_improve_full_age = base_.mort_improve_full_age
        self.mort_improve_end_age = base_.mort_improve_end_age
        self.mort_improve_max_years = base_.mort_improve_max_years
        self.lapse_guar_mult = base_.lapse_guar_mult
        self.lapse_pattern_mult_single = base_.lapse_pattern_mult_single
        self.lapse_pattern_mult_ten_pay = base_.lapse_pattern_mult_ten_pay
        self.lapse_dyn_mult_guar_only = base_.lapse_dyn_mult_guar_only
        self.lapse_dyn_mult_guar_failed = base_.lapse_dyn_mult_guar_failed
        self.lapse_rate_floor = base_.lapse_rate_floor
        self.lapse_rate_cap = base_.lapse_rate_cap
        self.expense_acq = base_.expense_acq
        self.expense_acq_prem_rate = base_.expense_acq_prem_rate
        self.expense_maint = base_.expense_maint
        self.expense_claim = base_.expense_claim
        self.inflation_rate = base_.inflation_rate
        self.premium_tax_rate = base_.premium_tax_rate
        self.solve_tol = base_.solve_tol
        self.solve_max_doublings = base_.solve_max_doublings
        self.pd = base_.pd
        self.math = base_.math

    @_mx_cy.cfunc
    def _f_model_point(self) -> object:
        """The selected model point as a Series."""
        return self.data.model_point_table().loc[self.point_id]                    # noqa: F821

    @_mx_cy.cfunc
    def _f_age_at_entry(self) -> _mx_cy.longlong:
        """The issue age (ANB) of the selected model point."""
        return int(self.model_point()["age_at_entry"])

    @_mx_cy.cfunc
    def _f_sex(self) -> str:
        """The sex of the selected model point."""
        return self.model_point()["sex"]

    @_mx_cy.cfunc
    def _f_rate_class(self) -> str:
        """The underwriting class of the selected model point (four NT, two tobacco) [S4]."""
        return self.model_point()["rate_class"]

    @_mx_cy.cfunc
    def _f_sum_assured(self) -> _mx_cy.double:
        """F: the initial face amount of the selected model point [S4][S6]."""
        return float(self.model_point()["sum_assured"])

    @_mx_cy.cfunc
    def _f_guarantee_age(self) -> _mx_cy.longlong:
        """The elected secondary-guarantee age, any attained age from 90 to 121 [S1][S2][S9].

        121 is the lifetime election, which is what the anchor cell carries and what
        switches :func:`lapse_rate_guar_mult` to the 0.55 multiplier [R7].
        """
        return int(self.model_point()["guarantee_age"])

    @_mx_cy.cfunc
    def _f_premium_type(self) -> str:
        """The premium pattern: ``"LEVEL"``, ``"SINGLE"`` or ``"TEN_PAY"`` **[std]**.

        A first-class model point attribute because funding pattern drives both the
        guarantee trajectory and observed lapse behaviour [R8].
        """
        return self.model_point()["premium_type"]

    @_mx_cy.cfunc
    def _f_premium_mode(self) -> str:
        """The premium mode: ``"A"``, ``"S"``, ``"Q"`` or ``"M"`` (EFT only) [S2]."""
        return self.model_point()["premium_mode"]

    @_mx_cy.cfunc
    def _f_premium_pp_ann(self) -> _mx_cy.double:
        """The scheduled annual premium per policy, or the single premium for ``"SINGLE"``.

        For the anchor cell this is the notes' solved level no-lapse premium
        ``P* = 10,800`` **[std]**; :func:`no_lapse_premium` re-derives it from the shadow
        recursion rather than reading it from here.
        """
        return float(self.model_point()["premium_pp_ann"])

    @_mx_cy.cfunc
    def _f_load_prem_rate(self) -> _mx_cy.double:
        """pi: the base premium expense charge, 25% of every premium, all years [S3][S7].

        Contractual here, unlike the universal life chassis where the load is a
        non-guaranteed element; it sits in the model point table for the same reason it
        does there, so that the table alone describes the policy.
        """
        return float(self.model_point()["load_prem_rate"])

    @_mx_cy.cfunc
    def _f_av_pp_init(self) -> _mx_cy.double:
        """AV_0: the base account value per policy at the outset, 0 at issue."""
        return float(self.model_point()["av_pp_init"])

    @_mx_cy.cfunc
    def _f_sg_pp_init(self) -> _mx_cy.double:
        """SG_0: the shadow account value per policy at the outset, 0 at issue.

        Not floored anywhere in the projection: a negative shadow balance measures the
        catch-up shortfall, and flooring it destroys :func:`catch_up_prem_pp`.
        """
        return float(self.model_point()["sg_pp_init"])

    @_mx_cy.cfunc
    def _f_loan_bal_init(self) -> _mx_cy.double:
        """L_0: the policy loan balance per policy at the outset, 0 in every shipped point."""
        return float(self.model_point()["loan_bal_init"])

    @_mx_cy.cfunc
    def _f_cum_prem_init(self) -> _mx_cy.double:
        """CumPrem_0: cumulative premiums already paid at the outset.

        The notes make this a model point attribute because it drives the return-of-premium
        refund [S1] and the 7-pay test [R5].  For the anchor cell it is the 25 annual
        premiums of $10,800 implied by the in-force snapshot **[std]**.
        """
        return float(self.model_point()["cum_prem_init"])

    @_mx_cy.cfunc
    def _f_pols_if_init(self) -> _mx_cy.double:
        """l_0: the in-force probability at the outset, 1 for a single-policy point."""
        return float(self.model_point()["pols_if_init"])

    @_mx_cy.cfunc
    def _f_duration_mth_init(self) -> _mx_cy.longlong:
        """Completed policy months already elapsed when the projection starts.

        0 for a new-business model point, so that ``t = 1`` is the issue month; 300 for
        the notes' worked-example cell, whose months 301-305 are ``t = 1`` to ``t = 5``.
        This is the notes' ``duration_months``.
        """
        return int(self.model_point()["duration_mth"])

    @_mx_cy.cfunc
    def _f_has_surr_charge(self) -> _mx_cy.bint:
        """Whether a surrender charge schedule applies to this model point."""
        return bool(self.model_point()["has_surr_charge"])

    @_mx_cy.cfunc
    def _f_surr_charge_id(self) -> str:
        """The surrender charge schedule ID, a row label of *surr_charge_table.csv*."""
        return self.model_point()["surr_charge_id"]

    @_mx_cy.cfunc
    def _f_rop_elected(self) -> _mx_cy.bint:
        """Whether the return-of-premium endorsement applies [S1].

        Built into the representative contract, so it is on for every point but the one
        that switches it off to isolate the guarantee mechanics.
        """
        return bool(self.model_point()["rop_elected"])

    @_mx_cy.cfunc
    def _f_coi_rate_dp(self) -> _mx_cy.longlong:
        """Decimal places the declared COI scales are quoted to per $1,000; -1 = exact.

        **The one place where the notes' rule and the notes' worked example disagree by
        more than rounding.**  The rule is that the current scale is 65% and the shadow
        scale 55% of the guaranteed maximum, which at the worked example's
        ``m^max = 8.615`` gives 5.59975 and 4.73825.  The worked example is computed with
        5.60 and 4.74 -- the same figures rounded to the cent per $1,000, which is how the
        notes quote them -- and the difference is about $0.12 a month of base deduction and
        $0.65 of shadow deduction, an order of magnitude more than the cent-level rounding
        that explains the rest of that table.

        Rather than pick one, the model ships both.  A model point that leaves this column
        blank takes the rule at full precision; the worked-example anchor sets it to 2 and
        holds both declared scales to the cent per $1,000, which is a perfectly ordinary
        way for an admin system to carry a rate table and reproduces the notes' table.
        """
        o = self.model_point()["coi_rate_dp"]
        return -1 if self.pd.isna(o) else int(o)                              # noqa: F821

    @_mx_cy.cfunc
    def _f_duration_mth(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """Completed policy months at the beginning of policy month t.

        ``duration_mth_init() + t - 1``, so it is 0 in the issue month of a new-business
        model point and 300 in the first month of the notes' worked example.  Note the
        contrast with the notes' own month index, which counts the current month as well;
        see :func:`surr_charge_rate`.
        """
        return self.duration_mth_init() + t - 1

    @_mx_cy.cfunc
    def _f_duration(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """Completed policy years at the beginning of policy month t."""
        return self.duration_mth(t) // 12

    @_mx_cy.cfunc
    def _f_policy_year(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """y: the policy year containing policy month t, 1-based."""
        return self.duration(t) + 1

    @_mx_cy.cfunc
    def _f_age(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """The attained age (ANB) in policy month t: ``age_at_entry() + duration(t)``.

        Age advances on the policy anniversary, not on the birthday, which is the ANB
        convention the whole model is built on **[std]**.  Mixing an ALB basis into the
        COI or mortality lookups shifts both by up to half a year of mortality, which the
        notes list among the pitfalls.
        """
        return self.age_at_entry() + self.duration(t)

    @_mx_cy.cfunc
    def _f_proj_len(self) -> _mx_cy.longlong:
        """Projection length in policy months.

        ``12 * (charges_cease_age - age_at_entry()) - duration_mth_init()``, the notes'
        maximum projection length: the projection runs to attained age 121, where premiums
        and all charges cease.  Coverage continues past that point under the contract
        [S7], but the illustrative mortality table reaches 1.0 at attained age 120, so
        nothing survives the horizon.
        """
        return 12 * (self.charges_cease_age - self.age_at_entry()) - self.duration_mth_init()  # noqa: F821

    @_mx_cy.cfunc
    def _f_sum_assured_at(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """F(t): the face amount in policy month t.

        Level: face increases are not permitted [S2] and elective decreases, option
        changes and the face reduction some designs attach to a withdrawal are not
        modelled -- the notes' withdrawal reduces the account and shadow balances only.
        The cells is kept so the chassis' shape is unchanged and a design with face
        movement can specialise it.
        """
        return self.sum_assured()

    @_mx_cy.cfunc
    def _f_units(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """U: the face amount in $1,000 units, ``sum_assured_at(t) / 1000``.

        Both per-unit charges are quoted per $1,000 of **initial** face per month, and the
        surrender charge per $1,000 of initial face; with a level face they coincide.
        """
        return self.sum_assured_at(t) / 1000

    @_mx_cy.cfunc
    def _f_crediting_rate_ann(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """i^c: the current declared annual effective credited rate, 3.50% **[std]**.

        A non-guaranteed element declared at insurer discretion within the guaranteed
        bounds and governed by ASOP 2 [REG-R26].  The base run holds the snapshot scale
        level, as the notes prescribe; re-rating is out of scope.
        """
        return self.crediting_rate_curr                                       # noqa: F821

    @_mx_cy.cfunc
    def _f_inv_return_mth(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """j_c: the monthly credited rate, ``(1 + i^c)^(1/12) - 1``, floored at j_g.

        0.0028709 at the **[std]** 3.50% current rate, matching the notes.  The floor is
        the contractual 2.0% guaranteed minimum [S3][S5][S7]; it does not bind at the
        snapshot scale.
        """
        return max((1 + self.crediting_rate_ann(t)) ** (1 / 12) - 1, self.guar_rate_mth())

    @_mx_cy.cfunc
    def _f_guar_rate_mth(self) -> _mx_cy.double:
        """j_g: the monthly guaranteed rate, ``(1 + i_guar)^(1/12) - 1`` = 0.0016516."""
        return (1 + self.guar_rate_ann) ** (1 / 12) - 1                       # noqa: F821

    @_mx_cy.cfunc
    def _f_sg_rate_mth(self) -> _mx_cy.double:
        """j^g: the monthly shadow credited rate, ``(1 + i^g)^(1/12) - 1`` = 0.0044717.

        5.5% annual effective **[std]**, comfortably below the AG 38 8E cap of a
        Moody's-composite-yield index plus 3% that classifies a Design #1 shadow account
        [R1], and well above the 2.0% base guarantee -- which is what makes the guarantee
        outlive the cash value.
        """
        return (1 + self.sg_rate_ann) ** (1 / 12) - 1                         # noqa: F821

    @_mx_cy.cfunc
    def _f_naar_factor(self) -> _mx_cy.double:
        """The base NAAR factor, ``1 + j_g`` = 1.0016516.

        The death benefit is discounted one month at the **guaranteed** rate, never the
        credited rate.  Using the undiscounted death benefit instead changes the cost of
        insurance by about 0.17% a month at the 2% guarantee, which the notes list first
        among the pitfalls; the same convention must hold on both accounts.
        """
        return 1 + self.guar_rate_mth()

    @_mx_cy.cfunc
    def _f_sg_naar_factor(self) -> _mx_cy.double:
        """The shadow NAAR factor, ``1 + j^g`` = 1.0044717 **[std]**.

        The shadow account discounts the death benefit at *its own* credited rate, which
        is what the notes' step 4 writes, so the two accounts see different net amounts at
        risk even before their balances diverge.
        """
        return 1 + self.sg_rate_mth()

    @_mx_cy.cfunc
    def _f_loan_rate_mth(self) -> _mx_cy.double:
        """The monthly charged loan rate, ``(1 + r_L)^(1/12) - 1`` at r_L = 5.0% [S4].

        Charged in arrears and guaranteed; monthly accrual is the model's discretization
        **[std]**.
        """
        return (1 + self.loan_rate_ann) ** (1 / 12) - 1                       # noqa: F821

    @_mx_cy.cfunc
    def _f_loan_cr_rate_mth(self) -> _mx_cy.double:
        """The monthly rate credited on the loaned account value, 3.0% annual [S4].

        Guaranteed, and 200 basis points below the charged rate -- the contractual loan
        spread.
        """
        return (1 + self.loan_cr_rate_ann) ** (1 / 12) - 1                    # noqa: F821

    @_mx_cy.cfunc
    def _f_premium_freq(self) -> _mx_cy.longlong:
        """Scheduled premium payments per policy year, from :func:`premium_mode` [S2].

        Annual 1, semi-annual 2, quarterly 4, monthly (EFT only) 12.  Non-annual modes
        carry modal factors in the source design; no carrier publishes them, so the
        scheduled annual premium is divided evenly **[std]** and every shipped model point
        is annual.
        """
        m = self.premium_mode()
        if m == "A":
            return 1
        elif m == "S":
            return 2
        elif m == "Q":
            return 4
        elif m == "M":
            return 12
        else:
            raise ValueError("invalid premium mode")

    @_mx_cy.cfunc
    def _f_is_premium_mth(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        """Whether a scheduled premium falls due at BOM of policy month t.

        ``LEVEL``    every ``12 / premium_freq()`` months from issue.
        ``SINGLE``   the issue month only.
        ``TEN_PAY``  as ``LEVEL``, for the first ``ten_pay_years`` policy years **[std]**.
        """
        pt = self.premium_type()
        if pt == "SINGLE":
            return self.duration_mth(t) == 0
        elif pt == "TEN_PAY":
            if self.duration(t) >= self.ten_pay_years:                             # noqa: F821
                return False
        elif pt != "LEVEL":
            raise ValueError("invalid premium type")
        return self.duration_mth(t) % (12 // self.premium_freq()) == 0

    @_mx_cy.cfunc
    def _f_prem_persistency(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """phi_t: the probability the scheduled premium is actually paid **[std]**.

        98% a year for a level payer, 100% for single-pay and ten-pay, which is what the
        notes prescribe; a missed premium is never made up, so it permanently lowers the
        shadow trajectory, and catch-up behaviour is not modelled in the base run.

        The model point may override it, and the worked-example anchor overrides it to
        1.00.  That is not a tuning: the notes' worked example is a contract-mechanics
        view with the behavioural assumptions suppressed, and premium persistency is a
        class (c) behavioural assumption.  The notes are also not self-consistent about
        where phi belongs -- their cash flow list writes premium income as
        ``l_t phi_t P_t`` while their step 2 credits ``(1 - pi) P_t`` to the account, which
        would hand the account value more than the insurer received.  This model applies
        phi once, to the premium actually received, so the account value, the shadow
        account, the cumulative premium and the premium income all move together.
        """
        o = self.model_point()["prem_persistency_override"]
        if not self.pd.isna(o):                                               # noqa: F821
            return float(o)
        return self.prem_persistency_ann if self.premium_type() == "LEVEL" else 1.0  # noqa: F821

    @_mx_cy.cfunc
    def _f_premium_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """P_t: the premium received per policy at BOM of policy month t.

        The scheduled premium in a premium month times :func:`prem_persistency`, zero
        otherwise, and zero from attained age 121 when premiums are no longer accepted
        [S7].  Premiums are flexible in amount and timing after the first [S2][S4]; the
        model projects the scheduled pattern, which is what the guarantee was solved on.
        """
        if self.age(t) >= self.charges_cease_age:                                  # noqa: F821
            return 0.0
        if not self.is_premium_mth(t):
            return 0.0
        if self.premium_type() == "SINGLE":
            return self.premium_pp_ann() * self.prem_persistency(t)
        return self.premium_pp_ann() / self.premium_freq() * self.prem_persistency(t)

    @_mx_cy.cfunc
    def _f_prem_to_av_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The net premium credited to the base account value, ``(1 - pi) P_t`` [S3][S7]."""
        return self.premium_pp(t) * (1 - self.load_prem_rate())

    @_mx_cy.cfunc
    def _f_prem_to_sg_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The net premium credited to the shadow account, ``(1 - pi^g) P_t`` **[std]**.

        The shadow load of 8% sits near the 7% market-wide load allowance AG 38 8B uses
        [R1] and far below the 25% base load, which is the whole point: the shadow account
        must credit premiums more generously than the real one for the guarantee to
        outlast the cash value.
        """
        return self.premium_pp(t) * (1 - self.load_prem_rate_sg)                   # noqa: F821

    @_mx_cy.cfunc
    def _f_prem_to_av(self, t: object) -> object:
        """Net premium credited to base account values, for the policies in force."""
        return self.prem_to_av_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_premiums(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Premium income at BOM of policy month t, weighted by the in force at BOM."""
        return self.premium_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_cum_prem_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """CumPrem_t: cumulative premiums paid per policy.

        ``CumPrem_0 = cum_prem_init()``; thereafter ``CumPrem_{t-1} + P_t``, exactly as the
        notes write it.  Withdrawals do **not** reduce it here -- that is the
        cumulative-premium-test variation's ``CumPrem^net``, not this one -- and it drives
        the return-of-premium refund [S1].
        """
        if t == 0:
            return self.cum_prem_init()
        return self.cum_prem_pp(t - 1) + self.premium_pp(t)

    @_mx_cy.cfunc
    def _f_wd_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """W_t: the partial withdrawal per policy at BOM of policy month t.

        Available after policy year 1 and not after attained age 121 [S2][S3][S4][S7].  The
        amount is the constant monthly figure in the model point's ``wd_pp`` column,
        **0 in every shipped model point**: the notes set utilisation to zero in the base
        model and give no pattern, so the mechanics are implemented and the behaviour is
        left to the data **[std]**.  A withdrawal reduces the account value by the amount
        plus the fee and the shadow account dollar-for-dollar, with no fee [S4].
        """
        if self.duration_mth(t) < 12 * self.wd_first_year:                         # noqa: F821
            return 0.0
        if self.age(t) >= self.charges_cease_age:                                  # noqa: F821
            return 0.0
        return float(self.model_point()["wd_pp"])

    @_mx_cy.cfunc
    def _f_wd_fee_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The $25 withdrawal fee, charged only in a month with a withdrawal [S2][S3][S4][S7].

        Retained by the insurer, so it is account-value outgo but not a liability cash
        flow; it appears in :func:`margin_expense`, not in :func:`claims`.  It is charged
        against the base account only, never the shadow account.
        """
        return self.wd_fee if self.wd_pp(t) > 0 else 0.0                           # noqa: F821

    @_mx_cy.cfunc
    def _f_wd_fees(self, t: object) -> object:
        """Withdrawal fees retained by the insurer, for the policies in force."""
        return self.wd_fee_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_corridor_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """kappa(x_t): the GPT corridor factor at the attained age [R4][REG-R13].

        The IRC 7702(d)(2) applicable percentages, every row of them: 250% to attained age
        40, then decreasing by a ratable portion for each full year through the statute's
        breakpoints -- 215% at 45, 185% at 50, 150% at 55, 130% at 60, 120% at 65, 115% at
        70, 105% from 75 to 90 -- and 100% from attained age 95 on, which is the statute's
        last row.  Ages beyond the table take its last row.  Because guaranteed UL account
        values are deliberately thin the corridor never binds in any shipped model point --
        but it is the reason the death benefit is a ``max`` rather than the face amount.
        """
        tbl = self.data.corridor_factors()                                    # noqa: F821
        a = min(max(self.age(t), int(tbl.index.min())), int(tbl.index.max()))
        return float(tbl.loc[a, "corridor_factor"])

    @_mx_cy.cfunc
    def _f_db_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """DB_t: the death benefit per policy, ``max(F, kappa(x_t) max(AV'_t, 0))`` [S2][S4].

        Level death benefit option only, the guarantee-focused segment's design [S2][S4].
        ``AV'_t`` is the account value after the premium, the withdrawal and the expense
        charges and **before** the cost of insurance, and it is floored at zero so an
        exhausted account cannot pull the death benefit below the face amount.
        """
        return max(self.sum_assured_at(t),
                   self.corridor_factor(t) * max(self.av_pp_at(t, "BEF_COI"), 0.0))

    @_mx_cy.cfunc
    def _f_net_amt_at_risk(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """NAAR_t: ``max(DB_t / (1 + j_g) - max(AV'_t, 0), 0)`` [S3].

        Two conventions here are the product's, not conveniences: the death benefit is
        discounted one month at the **guaranteed** rate (:func:`naar_factor`), and the
        account value is measured after the expense charges and before the cost of
        insurance.  The account input is floored at zero so that a deficit -- the
        guarantee-support regime, where the account is exhausted and the insurer is
        funding the deduction -- never inflates the net amount at risk above the
        discounted death benefit.  In that regime the cost of insurance is charged on
        essentially the whole face amount, which is what dominates late-duration
        guaranteed UL cash flows.
        """
        return max(0.0, self.db_pp(t) / self.naar_factor() - max(self.av_pp_at(t, "BEF_COI"), 0.0))

    @_mx_cy.cfunc
    def _f_sg_net_amt_at_risk(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """NAAR_t^g: the shadow net amount at risk, ``max(DB_t / (1 + j^g) - max(SG'_t, 0), 0)``.

        The same construction as :func:`net_amt_at_risk` on the shadow parameter set
        **[std]**, discounting at the shadow credited rate and flooring the shadow balance
        at zero so that catch-up territory -- a negative shadow account -- does not inflate
        the shadow cost of insurance.
        """
        return max(0.0, self.db_pp(t) / self.sg_naar_factor()
                   - max(self.sg_pp_at(t, "BEF_COI"), 0.0))

    @_mx_cy.cfunc
    def _f_coi_rate_scale(self) -> object:
        """The guaranteed maximum annual COI scale for this model point's cell.

        A Series indexed by **attained** age, per $1,000 of net amount at risk, sliced
        once from *coi_rates.csv* for this ``sex`` and ``rate_class``.  The shipped table
        covers the anchor cell M / StdNT over attained ages 45-121 only; a model point on
        any other cell, or a younger attained age, needs the table extended first.
        """
        return self.data.coi_rates().loc[(self.sex(), self.rate_class())]["coi_rate_guar_ann"]  # noqa: F821

    @_mx_cy.cfunc
    def _f_coi_rate_guar(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """m_t^max: the guaranteed maximum **monthly** COI rate per $1,000 of NAAR.

        The annual rate from *coi_rates.csv* divided by twelve -- the notes' simple-twelfth
        conversion, fixed **[std]**.  It differs materially from
        ``1 - (1 - q)^(1/12)`` at ages 85 and over, where q exceeds 0.10, and the notes are
        explicit that the two must not be mixed.  Model 585 requires the guaranteed maxima
        to be stated in the policy [R3]; carriers do not publish them, so the shipped
        scale is illustrative **[std]**, not the 2017 CSO table [REG-R17].
        """
        scale = self.coi_rate_scale()
        a = min(self.age(t), int(scale.index.max()))
        return float(scale[a]) / 12

    @_mx_cy.cfunc
    def _f_coi_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """m_t: the current monthly COI rate, 65% of the guaranteed maximum **[std]**.

        Current COI scales are not published by any carrier, so the factor is a pure
        modelling assumption and one of the first things to sensitivity-test.  The scale
        is held to :func:`coi_rate_dp` decimals per $1,000, which reconciles the notes'
        worked example with the notes' own factor rule -- see :func:`coi_rate_dp`.
        """
        r = self.coi_curr_factor * self.coi_rate_guar(t)                           # noqa: F821
        dp = self.coi_rate_dp()
        return r if dp < 0 else round(r, dp)

    @_mx_cy.cfunc
    def _f_sg_coi_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """m_t^g: the shadow monthly COI rate, 55% of the guaranteed maximum **[std]**.

        Kept below the current base rate of 65% so the shadow account depletes more slowly
        than the real one, which is the defining behaviour of the product [S2][S7].
        Rounded like :func:`coi_rate`.
        """
        r = self.coi_sg_factor * self.coi_rate_guar(t)                             # noqa: F821
        dp = self.coi_rate_dp()
        return r if dp < 0 else round(r, dp)

    @_mx_cy.cfunc
    def _f_coi_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """COI_t: the base cost of insurance charge, ``m_t NAAR_t / 1000``.

        Zero from attained age 121, when all charges cease [S3][S7].
        """
        if self.age(t) >= self.charges_cease_age:                                  # noqa: F821
            return 0.0
        return self.coi_rate(t) / 1000 * self.net_amt_at_risk(t)

    @_mx_cy.cfunc
    def _f_sg_coi_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """COI_t^g: the shadow cost of insurance charge, ``m_t^g NAAR_t^g / 1000`` **[std]**.

        Notional: it never leaves the insurer and is not a cash flow.  Zero from attained
        age 121, when the shadow charges cease with the base ones **[std]**.
        """
        if self.age(t) >= self.charges_cease_age:                                  # noqa: F821
            return 0.0
        return self.sg_coi_rate(t) / 1000 * self.sg_net_amt_at_risk(t)

    @_mx_cy.cfunc
    def _f_rider_charge_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Rider charges deducted monthly, 0 in the base model **[std]**.

        Rider charges are one of the sourced monthly charge categories [S2][S3][S4][S7][S9],
        but neither rider in scope carries one: the terminal illness accelerated benefit
        takes no premium [S2][S9], and the return-of-premium endorsement is built into the
        representative contract rather than charged for [S1].  The term is carried, as it is
        on the universal life chassis, so that a rider module can be added without changing
        the recursion.
        """
        return 0.0

    @_mx_cy.cfunc
    def _f_maint_fee_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The non-COI part of the base monthly deduction, ``e_pol + e_u U + rc`` [S3][S7].

        The $5.50 per-policy administrative charge [S3][S7], the $0.20 per $1,000 of initial
        face per month coverage charge **[std]** and rider charges.  Zero from attained age
        121, when charges cease [S3][S7].

        The name follows ``CashValue_SE.maint_fee``: this is a *charge* against the account
        value and therefore insurer income.  It is not :func:`expenses`, which is the
        insurer's own outgo.
        """
        if self.age(t) >= self.charges_cease_age:                                  # noqa: F821
            return 0.0
        return (self.expense_pol_mth + self.expense_unit_mth * self.units(t)            # noqa: F821
                + self.rider_charge_pp(t))

    @_mx_cy.cfunc
    def _f_sg_maint_fee_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The non-COI part of the shadow monthly deduction, ``e_u^g U`` **[std]**.

        $0.05 per $1,000 of initial face per month and **no per-policy charge** -- the
        simplest representative choice, since no carrier publishes shadow parameters and
        AG 38 8E only describes shadow accounts as carrying expense charges [R1].
        """
        if self.age(t) >= self.charges_cease_age:                                  # noqa: F821
            return 0.0
        return self.expense_unit_mth_sg * self.units(t)                            # noqa: F821

    @_mx_cy.cfunc
    def _f_mth_deduction_pp(self, t: object) -> object:
        """MD_t: the full base monthly deduction scheduled at BOM, ``maint_fee + COI``.

        This is what the worked example's "Base deductions" column shows.  What actually
        leaves the account is :func:`mth_deduction_taken_pp`; the remainder is
        :func:`mth_deduction_forgone_pp`.
        """
        return self.maint_fee_pp(t) + self.coi_pp(t)

    @_mx_cy.cfunc
    def _f_sg_deduction_pp(self, t: object) -> object:
        """The full shadow monthly deduction, ``sg_maint_fee_pp + sg_coi_pp`` **[std]**.

        The worked example's "Shdw deductions" column.  The shadow account is never
        floored, so it is always taken in full -- there is no shadow analogue of the
        forgone deduction.
        """
        return self.sg_maint_fee_pp(t) + self.sg_coi_pp(t)

    @_mx_cy.cfunc
    def _f_maint_fee_taken_pp(self, t: object) -> object:
        """The part of :func:`maint_fee_pp` the account value could actually carry.

        The expense charges are deducted before the cost of insurance, so they are met
        first out of the balance standing after the premium and the withdrawal.
        """
        return min(self.maint_fee_pp(t), max(self.av_pp_at(t, "BEF_FEE"), 0.0))

    @_mx_cy.cfunc
    def _f_coi_taken_pp(self, t: object) -> object:
        """The part of :func:`coi_pp` the account value could actually carry.

        The cost of insurance is deducted last, so it absorbs the shortfall first: this is
        the term that goes unpaid in the guarantee-support regime.
        """
        return min(self.coi_pp(t), max(self.av_pp_at(t, "BEF_COI"), 0.0))

    @_mx_cy.cfunc
    def _f_mth_deduction_taken_pp(self, t: object) -> object:
        """The monthly deduction actually taken from the account value in month t."""
        return self.maint_fee_taken_pp(t) + self.coi_taken_pp(t)

    @_mx_cy.cfunc
    def _f_mth_deduction_forgone_pp(self, t: object) -> object:
        """D_t: the monthly deduction forgone because the account value is exhausted.

        ``MD_t - (what the account could carry)``, which equals the notes' ``-AV''_t``
        whenever the balance before the charges is non-negative.  While the guarantee
        stands (:func:`is_guar_supported`) the insurer simply funds it and coverage
        continues with the account value at zero; when the guarantee has failed the same
        shortfall opens the grace period instead.

        **It is not a receivable.**  It must never accrue against future premiums or
        account value recoveries -- the notes list that among the pitfalls, because
        treating it as one understates the guarantee cost.  Nothing in the projection
        reads this cells except the diagnostics and :func:`cure_premium_pp`.

        It reports the shortfall whenever there is one, which includes the grace months and
        the months after a lapse -- where the notes' ``D_t`` is not defined at all, the
        shortfall being their *required grace payment* instead, and where the zero floor
        above it is this model's own **[std]** extension (:func:`av_pp_at`).  Read it beside
        :func:`is_guar_supported`, not on its own.
        """
        return self.mth_deduction_pp(t) - self.mth_deduction_taken_pp(t)

    @_mx_cy.cfunc
    def _f_maint_fee(self, t: object) -> object:
        """Non-COI monthly charges actually deducted from account values, in force."""
        return self.maint_fee_taken_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_coi(self, t: object) -> object:
        """Cost of insurance charges actually deducted from account values, in force."""
        return self.coi_taken_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_mth_deduction(self, t: object) -> object:
        """Monthly deductions actually taken from account values, in force."""
        return self.mth_deduction_taken_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_mth_deduction_forgone(self, t: object) -> object:
        """Monthly deductions forgone because the account value is exhausted, in force.

        While :func:`is_guar_supported` holds this is the running cost of the "negative
        account economics" regime the notes describe: the insurer is paying for coverage on
        a policy whose account value is zero.  In the grace months it is not -- there the
        shortfall is the notes' *required grace payment* on a policy about to terminate --
        so :func:`result_guar` prints it beside ``is_guar_active``.  After the lapse
        ``pols_if(t)`` is zero and so is this, whatever the per-policy cells say.
        """
        return self.mth_deduction_forgone_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_av_pp_at(self, t: _mx_cy.longlong, timing: str) -> _mx_cy.double:
        """Base account value per policy at an intra-month point of policy month t.

        The BOM events change the balance in this order, and ``timing`` names the point
        just before each of them:

        ``"BEF_PREM"``
            Before the premium: the closing balance of the previous month, ``AV_{t-1}``.

        ``"BEF_WD"``
            After the net premium, before the withdrawal.

        ``"BEF_FEE"``
            After the withdrawal and its fee, before the expense charges.

        ``"BEF_COI"``
            After the expense charges, before the cost of insurance.  **This is the notes'
            ``AV'(t)``**, and the balance the death benefit, the corridor test and the net
            amount at risk are all measured against.  The universal life chassis measures
            them one step earlier, at ``"BEF_FEE"``; the guaranteed-UL notes flag the
            difference as a deliberate deviation.

        ``"BEF_INV"``
            After the cost of insurance and **after the zero floor**, before interest.
            Interest is credited on this post-deduction balance; reversing the two
            overstates the account value by about one month's interest on the deduction
            every month.  The floor is what the guarantee buys: the account value stops at
            zero and the shortfall becomes :func:`mth_deduction_forgone_pp` rather than a
            negative balance.

            **Documented deviation [std].**  The notes floor the account value at zero
            *only while the guarantee is active* -- their step 6 sets ``AV''_t = 0`` in the
            guarantee branch and gives the grace branch no account-value recursion at all.
            This model applies the floor unconditionally, in the grace months and after a
            lapse as well.  A negative balance would break the account-value roll-forward,
            which closes on the deduction actually *taken*, and nothing is taken from an
            exhausted account.  No cash flow moves either way -- a policy in grace
            surrenders for nothing by construction and ``pols_if(t)`` is zero once it has
            lapsed -- but the per-policy account-value cells do keep running after the
            lapse, where they describe no policy.  See :func:`mth_deduction_forgone` and
            the README section "The forgone deduction is the product".

        The end-of-month balance ``AV_t`` is :func:`av_pp`.
        """
        if timing == "BEF_PREM":
            return self.av_pp(t - 1)
        elif timing == "BEF_WD":
            return self.av_pp_at(t, "BEF_PREM") + self.prem_to_av_pp(t)
        elif timing == "BEF_FEE":
            return self.av_pp_at(t, "BEF_WD") - self.wd_pp(t) - self.wd_fee_pp(t)
        elif timing == "BEF_COI":
            return self.av_pp_at(t, "BEF_FEE") - self.maint_fee_pp(t)
        elif timing == "BEF_INV":
            return max(0.0, self.av_pp_at(t, "BEF_COI") - self.coi_pp(t))
        else:
            raise ValueError("invalid timing")

    @_mx_cy.cfunc
    def _f_inv_income_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Interest credited to the base account value at EOM of policy month t.

        The unloaned part of the post-deduction balance earns the current monthly rate and
        the loaned part the guaranteed loaned rate of 3.0% [S4]::

            (AV''_t - L_{t-1}) x j_c + L_{t-1} x loan_cr_rate_mth()

        With the account value exhausted the credit is zero, which is why the worked
        example shows no interest from month 304.
        """
        loaned = self.loan_bal_pp(t - 1)
        unloaned = self.av_pp_at(t, "BEF_INV") - loaned
        return unloaned * self.inv_return_mth(t) + loaned * self.loan_cr_rate_mth()

    @_mx_cy.cfunc
    def _f_av_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """AV_t: the base account value per policy at the end of policy month t.

        ``AV_0 = av_pp_init()``; thereafter the floored post-deduction balance plus one
        month's interest.  An exhausted account never goes negative and the shortfall is
        recorded as :func:`mth_deduction_forgone_pp` instead.

        Floored at zero *throughout* -- in grace and after a lapse as well as under a live
        guarantee.  The notes floor it "only while the guarantee is active"; applying the
        floor unconditionally is a **[std]** deviation that moves no cash flow but does
        leave this cells running after the policy has gone.  :func:`av_pp_at` sets out why.
        """
        if t == 0:
            return self.av_pp_init()
        return self.av_pp_at(t, "BEF_INV") + self.inv_income_pp(t)

    @_mx_cy.cfunc
    def _f_av_at(self, t: object, timing: object) -> object:
        """Base account value in force at an intra-month point of policy month t.

        :func:`av_pp_at` times the number of policies in force, which is constant through
        the month because decrements are end-of-month events.  ``timing`` takes the same
        values as :func:`av_pp_at`, plus ``"EOM"`` for the closing balance before
        decrements.
        """
        if timing == "EOM":
            return self.av_pp(t) * self.pols_if(t)
        return self.av_pp_at(t, timing) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_inv_income(self, t: object) -> object:
        """Interest credited to base account values, for the policies in force.

        Decrements fall after the credit, so every policy in force at BOM earns a full
        month's interest.
        """
        return self.inv_income_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_av_change(self, t: object) -> object:
        """Change in the base account value in force over policy month t.

        ``av_at(t + 1, "BEF_PREM") - av_at(t, "BEF_PREM")``, following ``CashValue_SE``.
        """
        return self.av_at(t + 1, "BEF_PREM") - self.av_at(t, "BEF_PREM")

    @_mx_cy.cfunc
    def _f_loan_bal_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """L_t: the policy loan balance per policy at the end of policy month t.

        ``L_0 = loan_bal_init()``; thereafter ``L_{t-1} x (1 + r_L)^(1/12)`` at the
        guaranteed 5.0% charged in arrears [S4], accrued monthly **[std]**.  New loans and
        repayments are not modelled -- the notes give no utilisation pattern -- so this
        only rolls the model point's opening balance forward.  Indebtedness is deducted
        from the guarantee in-force test (:func:`sg_net_pp`), from death proceeds and from
        the surrender value; the shadow account itself is not reduced by it [S4][S2].
        """
        if t == 0:
            return self.loan_bal_init()
        return self.loan_bal_pp(t - 1) * (1 + self.loan_rate_mth())

    @_mx_cy.cfunc
    def _f_sg_pp_at(self, t: _mx_cy.longlong, timing: str) -> _mx_cy.double:
        """Shadow account value per policy at an intra-month point of policy month t.

        The same timings as :func:`av_pp_at`, on the shadow parameter set:

        ``"BEF_PREM"``
            The closing shadow balance of the previous month, ``SG_{t-1}``.

        ``"BEF_WD"``
            After the shadow net premium ``(1 - pi^g) P_t``, before the withdrawal.

        ``"BEF_FEE"``
            After the withdrawal, which reduces the shadow account dollar-for-dollar and
            carries **no fee** [S4] **[std]**, before the per-unit charge.

        ``"BEF_COI"``
            After the shadow per-unit charge, before the shadow cost of insurance.  **This
            is the notes' ``SG'(t)``.**

        ``"BEF_INV"``
            After the shadow cost of insurance, before interest.  This is the notes'
            ``SG''(t)`` and it is **not floored**: a negative shadow balance is the
            catch-up shortfall, and flooring it destroys :func:`catch_up_prem_pp` and
            misprices restoration.
        """
        if timing == "BEF_PREM":
            return self.sg_pp(t - 1)
        elif timing == "BEF_WD":
            return self.sg_pp_at(t, "BEF_PREM") + self.prem_to_sg_pp(t)
        elif timing == "BEF_FEE":
            return self.sg_pp_at(t, "BEF_WD") - self.wd_pp(t)
        elif timing == "BEF_COI":
            return self.sg_pp_at(t, "BEF_FEE") - self.sg_maint_fee_pp(t)
        elif timing == "BEF_INV":
            return self.sg_pp_at(t, "BEF_COI") - self.sg_coi_pp(t)
        else:
            raise ValueError("invalid timing")

    @_mx_cy.cfunc
    def _f_sg_inv_income_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Interest credited to the shadow account at EOM, ``SG''_t x j^g`` **[std]**.

        Credited on the post-deduction shadow balance with no floor and no loaned/unloaned
        split: the shadow account is notional and carries no loan of its own.
        """
        return self.sg_pp_at(t, "BEF_INV") * self.sg_rate_mth()

    @_mx_cy.cfunc
    def _f_sg_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """SG_t: the shadow account value per policy at the end of policy month t.

        ``SG_0 = sg_pp_init()``; thereafter ``SG''_t x (1 + j^g)``.  Notional throughout:
        it exists only to run the in-force test and is never payable [S2][S3].
        """
        if t == 0:
            return self.sg_pp_init()
        return self.sg_pp_at(t, "BEF_INV") + self.sg_inv_income_pp(t)

    @_mx_cy.cfunc
    def _f_sg_net_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """SG_t - L_t: the shadow account net of indebtedness, the in-force test quantity.

        Indebtedness is deducted from the guarantee measure rather than from the shadow
        account itself [S4][S2].  The mainstream design; the harshest observed alternative
        voids the guarantee outright on any loan [S5].
        """
        return self.sg_pp(t) - self.loan_bal_pp(t)

    @_mx_cy.cfunc
    def _f_is_guar_active(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        """The step-9 in-force test: ``SG_t - L_t > 0`` [S4][S2][S9].

        Measured at EOM, after the shadow interest credit and the loan accrual.  While it
        holds the policy cannot lapse however exhausted the real account value is; when it
        fails, an exhausted account opens the grace period.  Strictly greater than zero, as
        the notes require: a ``>= 0`` target on a monthly grid can leave the guarantee
        failing on the final monthiversary.
        """
        return self.sg_net_pp(t) > 0

    @_mx_cy.cfunc
    def _f_is_guar_supported(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        """The step-6 test: ``SG''_t - L_{t-1} > 0``, measured before the interest credits.

        This is the one that decides what happens to a failed deduction -- forgone by the
        insurer, or grace.  It is deliberately a different measurement point from
        :func:`is_guar_active`, and it is evaluated **after** the full monthly deduction
        attempt: testing before the deduction lets a policy lapse a month early or late and
        shifts claim timing at exactly the durations where the net amount at risk is the
        whole death benefit.
        """
        return self.sg_pp_at(t, "BEF_INV") - self.loan_bal_pp(t - 1) > 0

    @_mx_cy.cfunc
    def _f_catch_up_prem_pp(self, t: object) -> object:
        """C_t: the premium that would restore the guarantee, ``max(0, -(SG_t - L_t)) / (1 - pi^g)``.

        The negative net shadow balance grossed up for the shadow premium load **[std]**;
        paying it brings ``SG - L`` back to zero and the guarantee with it [S7][R1 ex. 7].
        A diagnostic only: the notes state expressly that catch-up behaviour is not
        modelled in the base run, so no policy ever pays it.  This is why the shadow
        account must never be floored at zero.
        """
        return max(0.0, -self.sg_net_pp(t)) / (1 - self.load_prem_rate_sg)         # noqa: F821

    @_mx_cy.cfunc
    def _f_surr_charge_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """SC per $1,000 of initial face in policy month t **[std]**.

        ``max(0, sc_init - (sc_init / runoff_years) x m / 12)`` where ``m`` is the notes'
        own month index ``duration_mth(t) + 1`` -- the current month counts.  With the
        shipped 15-year schedule at $18 per $1,000 this is the spec's
        ``18 x max(0, (180 - m) / 180)``: $17.90 in the issue month, zero from the last
        month of policy year 15.  Reading the notes' month index as ``duration_mth(t)``
        would shift the entire run-off by a month.
        """
        if not self.has_surr_charge():
            return 0.0
        row = self.data.surr_charge_table().loc[self.surr_charge_id()]              # noqa: F821
        init = float(row["sc_per_1000_init"])
        yrs = float(row["runoff_years"])
        m = self.duration_mth(t) + 1
        return max(0.0, init - (init / yrs) * (m / 12))

    @_mx_cy.cfunc
    def _f_surr_charge_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """SC_t: the surrender charge scheduled per policy in policy month t.

        Quoted on the **initial** face amount.  This is the schedule, not the amount
        collected: see :func:`surr_charge`.
        """
        return self.surr_charge_rate(t) * self.sum_assured() / 1000

    @_mx_cy.cfunc
    def _f_csv_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The cash surrender value per policy, ``AV_t - SC_t``, floored at zero.

        The floor is **[std]**: a negative cash surrender value would be a payment *from*
        the policyholder.  On this product it binds for years -- guaranteed UL account
        values are deliberately thin and the 15-year surrender charge starts at $9,000 on
        a $500,000 face.
        """
        return max(0.0, self.av_pp(t) - self.surr_charge_pp(t))

    @_mx_cy.cfunc
    def _f_ncsv_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """CSV_t in the notes: the net cash surrender value, ``max(AV_t - SC_t - L_t, 0)``.

        What a surrendering policyholder is paid, and the notes' surrender outgo.  The
        notes' symbol ``CSV_t`` already nets indebtedness, so it is this cells and not
        :func:`csv_pp`; the chassis keeps the two apart so the surrender-charge and the
        debt offsets can be read separately.
        """
        return max(0.0, self.csv_pp(t) - self.loan_bal_pp(t))

    @_mx_cy.cfunc
    def _f_surr_charge(self, t: object) -> object:
        """Surrender charge actually collected from the policies surrendering in month t.

        ``(AV_t - CSV_t) x pols_lapse(t)``, so it is capped by the account value where the
        :func:`csv_pp` floor binds -- which on this product is most of the first fifteen
        years.  Insurer income, and part of :func:`margin_expense`.
        """
        return (self.av_pp(t) - self.csv_pp(t)) * self.pols_lapse(t)

    @_mx_cy.cfunc
    def _f_is_shortfall(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        """Whether the monthly deduction attempt failed: ``AV'_t - COI_t < 0``.

        The notes' step 6 condition, evaluated **after** the full deduction attempt.  On
        its own it says nothing about lapse: while :func:`is_guar_supported` holds the
        shortfall is forgone by the insurer and coverage continues; only when the guarantee
        has failed as well does it open the grace period.
        """
        return self.av_pp_at(t, "BEF_COI") - self.coi_pp(t) < 0

    @_mx_cy.cfunc
    def _f_cure_premium_pp(self, t: object) -> object:
        """The payment that would cure a grace: the deduction shortfall, grossed up.

        ``D_t / (1 - pi)`` **[std]** -- the notes define the required grace payment as the
        amount curing the deduction shortfall, and a premium reaches the account value net
        of the load.  A diagnostic: the notes give no cure probability, so a policy that
        enters grace always lapses when the 61 days expire.
        """
        return self.mth_deduction_forgone_pp(t) / (1 - self.load_prem_rate())

    @_mx_cy.cfunc
    def _f_grace_mth(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """g_t: months elapsed in the grace period, 0 when not in grace [S7].

        The counter advances only when the deduction attempt failed **and** the guarantee
        is not supporting the policy; a failed deduction under an active guarantee is
        forgone and never opens a grace.  ``g_0 = 0``.
        """
        if t < 1:
            return 0
        if self.is_lapsed(t):
            return 0
        if not self.is_shortfall(t) or self.is_guar_supported(t):
            return 0
        return self.grace_mth(t - 1) + 1

    @_mx_cy.cfunc
    def _f_is_lapsed(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        """Whether the policy has terminated for insufficiency at or before BOM of month t.

        The 61-day grace period [S7] is taken as ``grace_months`` = 2 policy months
        **[std]**; when it expires without the required payment the policy lapses at BOM
        with no value -- the cash surrender value is zero in grace by construction.  Lapse
        for insufficiency requires all three of the notes' conditions: the deduction
        attempt failed, ``SG - L <= 0``, and the grace expired uncured.
        """
        if t <= 1:
            return False
        return self.is_lapsed(t - 1) or self.grace_mth(t - 1) >= self.grace_months      # noqa: F821

    @_mx_cy.cfunc
    def _f_status(self, t: object) -> object:
        """The worked example's Status column, in ASCII.

        ``"IN FORCE"``
            the account value is carrying the policy;
        ``"IN FORCE - GUARANTEE"``
            the account value is exhausted and the guarantee is
            carrying it -- the notes' "in force - guarantee";
        ``"GRACE"``
            the deduction failed with no guarantee behind it;
        ``"LAPSED"``
            the grace expired uncured.
        """
        if self.is_lapsed(t):
            return "LAPSED"
        if self.grace_mth(t) > 0:
            return "GRACE"
        if self.av_pp(t) <= 0:
            return "IN FORCE - GUARANTEE"
        return "IN FORCE"

    @_mx_cy.cfunc
    def _f_rop_anniversary(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """The return-of-premium anniversary whose window contains month t, or 0 [S1].

        The endorsement is exercisable during the 60 days following policy anniversaries
        20 and 25 [S1][S3][S4].  On a monthly grid the window is taken as the anniversary
        month itself **[std]**, so the exercise rate is applied once rather than spread
        over two monthiversaries.
        """
        if not self.rop_elected():
            return 0
        if self.duration_mth(t) % 12 != 0:
            return 0
        y = self.duration(t)
        return y if y in self.data.rop_table().index else 0                   # noqa: F821

    @_mx_cy.cfunc
    def _f_rop_ratio(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """rho: the fraction of cumulative premiums refunded in the window, 50% or 100% [S1]."""
        a = self.rop_anniversary(t)
        if a == 0:
            return 0.0
        return float(self.data.rop_table().loc[a, "refund_ratio"])             # noqa: F821

    @_mx_cy.cfunc
    def _f_rop_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """w^ROP: the fraction of eligible in-force exercising in the window **[std]**.

        5% at the year-20 window and 10% at the year-25 window.  No public exercise study
        exists; the rationale for keeping them modest is that the 100% refund dominates
        the cash surrender value on a thin-account product, but exercising forfeits a
        now-cheap guarantee.  Mis-setting them distorts years 20-26 of the cash flows.
        """
        a = self.rop_anniversary(t)
        if a == 0:
            return 0.0
        return float(self.data.rop_table().loc[a, "exercise_rate"])            # noqa: F821

    @_mx_cy.cfunc
    def _f_class_factor(self) -> _mx_cy.double:
        """The underwriting-class multiplier on the best-estimate mortality table **[std]**."""
        return float(self.data.class_factor_table().loc[self.rate_class(), "factor"])  # noqa: F821

    @_mx_cy.cfunc
    def _f_mort_improve_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The annual mortality improvement rate at the attained age in month t **[std]**.

        1.0% a year to attained age 85, grading linearly to 0% at attained age 95 and zero
        thereafter.  Improvement compounds, so at the late attained ages where the net
        amount at risk is the whole death benefit it is one of the two assumptions that
        move the claims most.
        """
        a = self.age(t)
        if a <= self.mort_improve_full_age:                                   # noqa: F821
            return self.mort_improve_rate_init                                # noqa: F821
        if a >= self.mort_improve_end_age:                                    # noqa: F821
            return 0.0
        return self.mort_improve_rate_init * (                                # noqa: F821
            (self.mort_improve_end_age - a)                                   # noqa: F821
            / (self.mort_improve_end_age - self.mort_improve_full_age))            # noqa: F821

    @_mx_cy.cfunc
    def _f_mort_improve_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The cumulative mortality improvement factor at policy month t **[std]**.

        1.0 in the first projected year, then one further year of improvement on each
        anniversary of the projection start, for at most ``mort_improve_max_years`` = 20
        years as the notes prescribe.  Improvement is applied on projection anniversaries
        **[std]**; for every shipped model point those coincide with policy
        anniversaries.
        """
        k = (t - 1) // 12
        if k <= 0:
            return 1.0
        if k > self.mort_improve_max_years:                                   # noqa: F821
            return self.mort_improve_factor(12 * self.mort_improve_max_years + 1)  # noqa: F821
        return self.mort_improve_factor(t - 12) * (1 - self.mort_improve_rate(t - 12))

    @_mx_cy.cfunc
    def _f_mort_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The annual best-estimate mortality rate in policy month t.

        Base table x :func:`class_factor` x the A/E factor, which is 100% in the base run
        **[std]**, x :func:`mort_improve_factor`, capped at 1.0.  The shipped table is a
        small illustrative one **[std]**, *not* the 2015 VBT the notes recommend -- that
        family is licensed and may not be reproduced here.  Ages beyond the table take its
        last row, where the rate is 1.0; the cap is what keeps a class factor above 1 from
        pushing the terminal rate past certainty.
        """
        tbl = self.data.mort_table()                                          # noqa: F821
        a = min(max(self.age(t), int(tbl.index.min())), int(tbl.index.max()))
        return min(1.0, float(tbl.loc[a, "mort_rate"]) * self.class_factor()
                   * self.mort_ae_factor * self.mort_improve_factor(t))            # noqa: F821

    @_mx_cy.cfunc
    def _f_mort_rate_mth(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """q_t^d: the monthly best-estimate mortality rate, ``1 - (1 - q)^(1/12)``.

        Note that the **experience** decrement uses the compound conversion while the
        contractual COI rate uses the simple twelfth (:func:`coi_rate_guar`).  The notes
        prescribe exactly that split; the two must not be interchanged.
        """
        return 1 - (1 - self.mort_rate(t)) ** (1 / 12)

    @_mx_cy.cfunc
    def _f_lapse_rate_base(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """b(d): the base annual lapse rate by policy year **[std]**.

        4.0%, 3.0%, 2.5%, then 2.0% in years 4-5, 1.5% in 6-10, 1.0% in 11-20 and 0.75%
        thereafter, read from *lapse_table.csv*; policy years beyond the table take its
        last row.  The shape is anchored to the public highlights of the SOA/LIMRA UL
        persistency and lapse studies [R7][REG-R20][REG-R21], whose detailed tables sit in
        a paid data package, so the levels are a standardization.
        """
        tbl = self.data.lapse_table()                                         # noqa: F821
        y = min(self.policy_year(t), int(tbl.index.max()))
        return float(tbl.loc[y, "lapse_rate_ann"])

    @_mx_cy.cfunc
    def _f_lapse_rate_guar_mult(self) -> _mx_cy.double:
        """G: the guarantee-duration lapse multiplier, 0.55 for a lifetime election.

        Lifetime secondary-guarantee lapse rates run 45% below non-lifetime rates on both
        count and amount bases in the 2015-2021 industry experience [R7]; the level is
        derived from that finding and the flat duration shape is **[std]**.  This is the
        first-order assumption for a lapse-supported product: every lapse of a funded
        guarantee releases the insurer from a deeply in-the-money claim.
        """
        if self.guarantee_age() >= self.lifetime_guarantee_age:                    # noqa: F821
            return self.lapse_guar_mult                                       # noqa: F821
        return 1.0

    @_mx_cy.cfunc
    def _f_lapse_rate_pattern_mult(self) -> _mx_cy.double:
        """Phi: the premium-pattern lapse multiplier **[std]**.

        Single-pay 0.6, ten-pay 0.8, level 1.0, in the direction [R8] reports -- higher
        lapses for level-pay, lower for single-pay.
        """
        pt = self.premium_type()
        if pt == "SINGLE":
            return self.lapse_pattern_mult_single                             # noqa: F821
        elif pt == "TEN_PAY":
            return self.lapse_pattern_mult_ten_pay                            # noqa: F821
        elif pt == "LEVEL":
            return 1.0
        else:
            raise ValueError("invalid premium type")

    @_mx_cy.cfunc
    def _f_lapse_rate_dyn_mult(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Psi_t: the funding-status dynamic lapse factor **[std]**.

        ``1.0``
            guarantee active and the account value still positive;
        ``0.6``
            guarantee active and the account value exhausted -- the policy is deep in
            the money to the policyholder, the regime [R8]'s tail scenarios keep 40%
            of policies in after 31 years;
        ``2.0``
            the guarantee has terminated and the policy is surviving on its account
            value alone -- a shock.  Where the account value has gone too the policy
            is already in grace and about to lapse, so the rate is academic there.

        Dynamic lapse is used by 63% of surveyed ULSG writers, and lapse and tail
        investment returns are rated the most critical ULSG assumptions [R8]; the formula
        itself is a standardization.
        """
        if not self.is_guar_active(t):
            return self.lapse_dyn_mult_guar_failed                            # noqa: F821
        if self.av_pp(t) > 0:
            return 1.0
        return self.lapse_dyn_mult_guar_only                                  # noqa: F821

    @_mx_cy.cfunc
    def _f_lapse_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The total annual lapse rate, ``min(0.5, max(0.003, b(d) G Phi Psi_t))`` **[std]**.

        The 0.3% annual floor is applied after the dynamic factor, as the notes write it,
        and the 50% cap wraps the result; the two cannot conflict.
        """
        rate = (self.lapse_rate_base(t) * self.lapse_rate_guar_mult()
                * self.lapse_rate_pattern_mult() * self.lapse_rate_dyn_mult(t))
        return min(self.lapse_rate_cap, max(self.lapse_rate_floor, rate))          # noqa: F821

    @_mx_cy.cfunc
    def _f_lapse_rate_mth(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """w_t: the monthly lapse rate, ``1 - (1 - w_annual)^(1/12)``."""
        return 1 - (1 - self.lapse_rate(t)) ** (1 / 12)

    @_mx_cy.cfunc
    def _f_pols_if(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """l_t: the number of policies in force at the beginning of policy month t.

        Decrements are end-of-month events, so the number in force is constant through the
        month and every BOM cash flow is weighted by it.  ``pols_if(1) = l_0 =
        pols_if_init()``.  A policy whose grace has expired is out at BOM with no value,
        which is why :func:`is_lapsed` is tested first.
        """
        if t == 1:
            return self.pols_if_init()
        if self.is_lapsed(t):
            return 0.0
        return (self.pols_if(t - 1) - self.pols_death(t - 1) - self.pols_lapse(t - 1)
                - self.pols_rop(t - 1) - self.pols_lapse_grace(t - 1))

    @_mx_cy.cfunc
    def _f_pols_if_at(self, t: object, timing: object) -> object:
        """Number of policies in force at time t, by ``timing``.

        All three ``CashValue_SE`` timings coincide for this product, and all equal
        :func:`pols_if`: there is no new business inside a projection and the contract has
        no maturity date, so nothing changes the policy count between BOM and the
        end-of-month decrements.
        """
        if timing in ("BEF_MAT", "BEF_NB", "BEF_DECR"):
            return self.pols_if(t)
        else:
            raise ValueError("invalid timing")

    @_mx_cy.cfunc
    def _f_pols_death(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Number of deaths at the end of policy month t, ``l_t x q_t^d``."""
        return self.pols_if(t) * self.mort_rate_mth(t)

    @_mx_cy.cfunc
    def _f_pols_lapse(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Number of surrenders at the end of policy month t.

        ``l_t (1 - q_t^d) w_t``: death is applied before lapse, which is the notes'
        ordering.
        """
        return self.pols_if(t) * (1 - self.mort_rate_mth(t)) * self.lapse_rate_mth(t)

    @_mx_cy.cfunc
    def _f_pols_rop(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Number of return-of-premium exercises at the end of policy month t.

        ``l_t (1 - q_t^d)(1 - w_t) w_t^ROP``, matching the notes'
        ``l_{t+1} = l_t (1 - q^d)(1 - w)(1 - w^ROP)``.  Exercise is a full surrender
        [S1][S3], so an exercising policy leaves with the refund and nothing else.
        """
        return (self.pols_if(t) * (1 - self.mort_rate_mth(t))
                * (1 - self.lapse_rate_mth(t)) * self.rop_rate(t))

    @_mx_cy.cfunc
    def _f_pols_lapse_grace(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Number of policies terminating for insufficiency at the end of policy month t.

        Non-zero only in the month before the grace period expires, when every remaining
        policy is out.  This is not a rate-based decrement: it is the contractual
        termination of a policy whose account value failed and whose guarantee had already
        gone, and it is needed for the in-force roll-forward to close.  The policies leave
        with no value, so it generates no claim -- the cash surrender value is zero in
        grace by construction.
        """
        if self.is_lapsed(t) or not self.is_lapsed(t + 1):
            return 0.0
        return self.pols_if(t) - self.pols_death(t) - self.pols_lapse(t) - self.pols_rop(t)

    @_mx_cy.cfunc
    def _f_pols_maturity(self, t: object) -> object:
        """Number of maturing policies: always zero.

        Guaranteed UL has no maturity date -- at attained age 121 premiums and charges
        cease and coverage continues [S7].  The cells is kept so the in-force roll-forward
        identity has the same shape as in the term and annuity models of this library,
        where it is not zero.
        """
        return 0.0

    @_mx_cy.cfunc
    def _f_claim_pp(self, t: _mx_cy.longlong, kind: str) -> _mx_cy.double:
        """The claim amount per policy by ``kind``.

        ``"DEATH"``
            ``DB_t - L_t``: the death benefit less outstanding indebtedness, standard UL
            treatment **[std]**.

        ``"LAPSE"``
            :func:`ncsv_pp`, the notes' ``CSV_t = max(AV_t - SC_t - L_t, 0)``.

        ``"REFUND"``
            ``min(rho CumPrem_t, 0.40 F) - L_t``, floored at zero [S1]: the
            return-of-premium refund, capped at 40% of the face amount and net of debt.
            On the anchor cell the cap binds -- 25 years of $10,800 premiums is $270,000
            against a $200,000 cap -- which is exactly why the cap exists.

        ``"WITHDRAWAL"``
            ``W_t``.  The $25 fee is retained by the insurer and is not part of the
            payment.  A withdrawal is not a claim -- the aggregate cash flow is
            :func:`withdrawals`, not ``claims(t, "WITHDRAWAL")``, which raises -- but the
            per-policy amount keeps its branch here because :func:`withdrawals` weights it.

        ``"GRACE"``
            Zero: a policy terminating in grace terminates without value [S7].
        """
        if kind == "DEATH":
            return self.db_pp(t) - self.loan_bal_pp(t)
        elif kind == "LAPSE":
            return self.ncsv_pp(t)
        elif kind == "REFUND":
            return max(0.0, min(self.rop_ratio(t) * self.cum_prem_pp(t),
                                self.rop_cap_rate * self.sum_assured_at(t))        # noqa: F821
                       - self.loan_bal_pp(t))
        elif kind == "WITHDRAWAL":
            return self.wd_pp(t)
        elif kind == "GRACE":
            return 0.0
        else:
            raise ValueError("invalid kind")

    @_mx_cy.cfunc
    def _f_claims_from_av(self, t: object, kind: object) -> object:
        """The part of a claim released from the account value, by ``kind``.

        Death, surrender and refund all release the end-of-month account value ``AV_t``,
        because decrements follow the interest credit; so does a policy terminating in
        grace, though its account value is zero by construction.  ``"MATURITY"`` is zero:
        the contract has no maturity date.

        ``"WITHDRAWAL"`` keeps its branch even though a withdrawal is not a claim: it is
        taken at BOM out of the account values of the policies still in force, and it is
        the same figure as :func:`withdrawals`.
        """
        if kind == "DEATH":
            return self.av_pp(t) * self.pols_death(t)
        elif kind == "LAPSE":
            return self.av_pp(t) * self.pols_lapse(t)
        elif kind == "REFUND":
            return self.av_pp(t) * self.pols_rop(t)
        elif kind == "GRACE":
            return self.av_pp(t) * self.pols_lapse_grace(t)
        elif kind == "WITHDRAWAL":
            return self.withdrawals(t)
        elif kind == "MATURITY":
            return 0.0
        else:
            raise ValueError("invalid kind")

    @_mx_cy.cfunc
    def _f_claims_over_av(self, t: object) -> object:
        """Death claims in excess of the account value released.

        ``(claim_pp(t, "DEATH") - AV_t) x pols_death(t)``.  The cost of insurance charge
        net of this is the mortality margin -- and in the guarantee-support regime, where
        the account value is zero and the charge is forgone, it is the whole face amount
        with no charge behind it.
        """
        return (self.claim_pp(t, "DEATH") - self.av_pp(t)) * self.pols_death(t)

    @_mx_cy.cfunc
    def _f_claims(self, t: _mx_cy.longlong, kind: object=None) -> _mx_cy.double:
        """Claim outgo in policy month t, optionally by ``kind``.

        ``kind`` is ``"DEATH"``, ``"LAPSE"``, ``"REFUND"``, ``"GRACE"``, or ``None`` for
        the total.  Death claims are weighted by :func:`pols_death`, surrenders by
        :func:`pols_lapse` and refunds by :func:`pols_rop`, all end-of-month events.

        ``"WITHDRAWAL"`` is deliberately **not** a claim kind and raises: a partial
        withdrawal is a payment on the owner's election out of a policy that stays in
        force, so it is :func:`withdrawals`.  Keeping it out of this cells is what keeps
        the ``kind is None`` total from double-counting it against the ``withdrawals``
        column of :func:`result_cf`.
        """
        if kind == "DEATH":
            return self.claim_pp(t, "DEATH") * self.pols_death(t)
        elif kind == "LAPSE":
            return self.claim_pp(t, "LAPSE") * self.pols_lapse(t)
        elif kind == "REFUND":
            return self.claim_pp(t, "REFUND") * self.pols_rop(t)
        elif kind == "GRACE":
            return 0.0
        elif kind is None:
            return sum(self.claims(t, k) for k in
                       ("DEATH", "LAPSE", "REFUND", "GRACE"))
        else:
            raise ValueError("invalid kind")

    @_mx_cy.cfunc
    def _f_withdrawals(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Partial withdrawal payments in policy month t, for the policies in force.

        ``W_t x l_t``.  Withdrawals are taken at BOM by policies still in force, so the
        weight is :func:`pols_if` and not a decrement.  A withdrawal is a payment on the
        owner's election, not a claim, which is why it is a cells and a ``result_cf()``
        column of its own rather than a ``kind`` of :func:`claims`.  The $25 fee is
        retained by the insurer and is :func:`wd_fees`, not part of this payment.

        Zero in every shipped model point: the notes set withdrawal utilisation to zero in
        the base model and give no pattern, so the mechanics are implemented and the
        behaviour is left to the data **[std]**.
        """
        return self.claim_pp(t, "WITHDRAWAL") * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_inflation_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The expense inflation factor, ``(1 + inflation_rate)^(y - 1)`` **[std]**.

        Expenses inflate by policy year, not by month, which is how the notes write the
        $75 per policy per year maintenance expense.
        """
        return (1 + self.inflation_rate) ** (self.policy_year(t) - 1)              # noqa: F821

    @_mx_cy.cfunc
    def _f_expenses(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The insurer's own expenses in policy month t **[std]**.

        Acquisition in policy year 1 -- $300 a policy in the issue month plus 90% of every
        first-year premium, which is the notes' combined commission and issue allowance --
        maintenance of $75 a policy a year inflating at 2.5%, spread evenly over the
        months, and $300 of claim expense per death.

        Not to be confused with :func:`maint_fee`, which is the *charge against the
        account value*.
        """
        acq = self.expense_acq if self.duration_mth(t) == 0 else 0.0               # noqa: F821
        if self.policy_year(t) == 1:
            acq = acq + self.expense_acq_prem_rate * self.premium_pp(t)            # noqa: F821
        return ((acq + self.expense_maint / 12 * self.inflation_factor(t)) * self.pols_if(t)  # noqa: F821
                + self.expense_claim * self.pols_death(t))                         # noqa: F821

    @_mx_cy.cfunc
    def _f_premium_taxes(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Percent-of-premium expense, **zero** on this product.

        The universal life chassis carries a 2.5% premium tax; the guaranteed-UL notes'
        expense list has no percent-of-premium item at all -- the commission sits inside
        the acquisition expense instead -- so the rate is zero and the cells is kept only
        so ``result_cf()`` has the chassis' shape.  Adding a tax here would be an
        unsourced assumption.
        """
        return self.premium_tax_rate * self.premiums(t)                            # noqa: F821

    @_mx_cy.cfunc
    def _f_margin_expense(self, t: object) -> object:
        """Expense margin: the charges the insurer keeps, net of its own outgo.

        ``pi x GP + withdrawal fees + the deduction's non-COI part actually taken
        + surrender charges collected + the account value left behind by a policy
        terminating in grace - expenses - premium taxes``.  The last of those is zero by
        construction, because the account value is exhausted before a grace can begin; it
        is carried so :func:`check_margin` closes without a special case.
        """
        return (self.load_prem_rate() * self.premiums(t)
                + self.wd_fees(t)
                + self.maint_fee(t)
                + self.surr_charge(t)
                + self.claims_from_av(t, "GRACE")
                - self.expenses(t)
                - self.premium_taxes(t))

    @_mx_cy.cfunc
    def _f_margin_mortality(self, t: object) -> object:
        """Mortality margin: :func:`coi` net of :func:`claims_over_av`.

        Deeply negative once the account value is exhausted: the cost of insurance is
        forgone while the death benefit is still the whole face amount.  That is the
        "negative account economics" regime the notes describe, and it is what dominates
        late-duration guaranteed UL liability cash flows.
        """
        return self.coi(t) - self.claims_over_av(t)

    @_mx_cy.cfunc
    def _f_margin_rop(self, t: object) -> object:
        """Return-of-premium margin: the account value released less the refund paid.

        ``(AV_t - claim_pp(t, "REFUND")) x pols_rop(t)``.  Large and negative on a
        thin-account product, which is the point of the endorsement: it is an option
        against the insurer whose cost depends on cumulative premiums against the reserve
        released.
        """
        return (self.av_pp(t) - self.claim_pp(t, "REFUND")) * self.pols_rop(t)

    @_mx_cy.cfunc
    def _f_net_cf(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Net liability cash flow in policy month t, **undiscounted**.

        ``premiums - death claims - surrender payments - refunds - withdrawal payments
        - expenses - premium taxes``.  Income-positive, as in every model of this library.
        Withdrawals are subtracted here as :func:`withdrawals` rather than through
        :func:`claims`, which no longer carries them.

        Like the rest of this library the model projects *gross liability cash flows*:
        there is no discounting and no change in account value in this figure, because
        reserves are a separate layer that consumes these flows.  Loads, charges, interest
        credits and every shadow-account entry are internal transfers and do not appear --
        see :func:`check_margin` for how they reconcile.
        """
        return (self.premiums(t) - self.claims(t) - self.withdrawals(t)
                - self.expenses(t) - self.premium_taxes(t))

    @_mx_cy.cfunc
    def _f_solve_len(self) -> object:
        """The number of months the funding-premium solve has to keep the guarantee alive.

        ``12 x (guarantee_age() - age_at_entry()) - duration_mth_init()``, the notes'
        stopping time.  A shorter guarantee age solves the same way with the earlier
        stopping time.
        """
        return 12 * (self.guarantee_age() - self.age_at_entry()) - self.duration_mth_init()

    @_mx_cy.cfunc
    def _f_sg_pp_solve(self, t: object, prem: object) -> object:
        """SG_t(P): the shadow account under a hypothetical premium scale ``prem``.

        ``prem`` is the annual premium for a level or ten-pay pattern and the single
        premium for a single-pay one; the payment months are the model point's own, so
        single-pay and n-pay premiums solve over their premium vectors exactly as the
        notes prescribe.

        A self-contained replay of the shadow recursion with **decrements off and premium
        persistency off** -- the solve is contractual, not behavioural, as the notes say --
        and with the death benefit held at the face amount.  The notes justify the latter
        by capping the search domain at the guideline premium limitation [R4], inside which
        the corridor does not bind for this thin-account design.

        It shares :func:`sg_coi_rate` and :func:`units` with the projection, so the COI
        lookups are cached across bisection iterates.
        """
        if t == 0:
            return self.sg_pp_init()
        p = prem / self.premium_freq() if self.is_premium_mth(t) else 0.0
        sgp = (self.sg_pp_solve(t - 1, prem) + (1 - self.load_prem_rate_sg) * p    # noqa: F821
               - self.sg_maint_fee_pp(t))
        naar = max(0.0, self.sum_assured_at(t) / self.sg_naar_factor() - max(sgp, 0.0))
        return (sgp - self.sg_coi_rate(t) / 1000 * naar) * (1 + self.sg_rate_mth())

    @_mx_cy.cfunc
    def _f_guar_min_sg(self, prem: object) -> object:
        """g(P): the smallest value of ``SG_t(P) - L_t`` over the guarantee period.

        Monotone non-decreasing in P on the notes' search domain, which is what makes
        bisection safe.  Evaluated in increasing ``t`` so the shadow recursion never
        recurses deeply.
        """
        return min(self.sg_pp_solve(t, prem) - self.loan_bal_pp(t)
                   for t in range(1, self.solve_len() + 1))

    @_mx_cy.cfunc
    def _f_no_lapse_premium(self) -> object:
        """P*: the smallest premium on this model point's pattern for which ``g(P) > 0``.

        The notes' funding-premium solve.  The bracket starts at zero and doubles the
        upper end until the guarantee is funded, then bisects to ``solve_tol`` = $0.01 of
        annual premium **[std]**.  The target is ``g(P) > 0`` strictly: a ``>= 0`` target
        on a monthly grid can leave the guarantee failing on the final monthiversary.

        A side calculation -- nothing in the projection depends on it.  For the
        new-business level-pay cell it returns about $10,800, which is the figure the notes
        calibrated the **[std]** shadow parametrization to produce; the illustrative COI
        curve shipped with the model is fitted so that it does.  On the in-force anchor it
        answers a different question -- the level premium needed **from the projection
        start**, given the opening shadow balance -- and returns far more, because the
        notes' opening shadow value is not the balance a fully funded policy would carry
        at duration 300.
        """
        lo = 0.0
        hi = max(self.premium_pp_ann(), 1.0)
        for _ in range(self.solve_max_doublings):                             # noqa: F821
            if self.guar_min_sg(hi) > 0:
                break
            hi = hi * 2
        else:
            raise ValueError("no_lapse_premium: no funding premium found")
        while hi - lo > self.solve_tol:                                       # noqa: F821
            mid = (lo + hi) / 2
            if self.guar_min_sg(mid) > 0:
                hi = mid
            else:
                lo = mid
        return hi

    @_mx_cy.cfunc
    def _f_check_av_roll_fwd(self) -> object:
        """Check the base account value roll-forward.

        Returns ``True`` when, for every projected month, the opening account value in
        force of month ``t + 1`` equals::

            av_at(t, "BEF_PREM")
                + prem_to_av(t)
                - withdrawals(t) - wd_fees(t)
                - mth_deduction(t)
                + inv_income(t)
                - claims_from_av(t, "DEATH") - claims_from_av(t, "LAPSE")
                - claims_from_av(t, "REFUND") - claims_from_av(t, "GRACE")

        This pins the notes' processing order: that interest is credited on the
        *post-deduction* balance, that decrements come after the credit, and that what
        leaves the account is the deduction actually taken and not the deduction
        scheduled.
        """
        res = []
        for t in range(1, self.proj_len() + 1):
            av = (self.av_at(t, "BEF_PREM")
                  + self.prem_to_av(t)
                  - self.withdrawals(t)
                  - self.wd_fees(t)
                  - self.mth_deduction(t)
                  + self.inv_income(t)
                  - self.claims_from_av(t, "DEATH")
                  - self.claims_from_av(t, "LAPSE")
                  - self.claims_from_av(t, "REFUND")
                  - self.claims_from_av(t, "GRACE"))
            res.append(self.math.isclose(self.av_at(t + 1, "BEF_PREM"), av,        # noqa: F821
                                    rel_tol=1e-9, abs_tol=1e-9))
        return all(res)

    @_mx_cy.cfunc
    def _f_check_sg_roll_fwd(self) -> object:
        """Check the shadow account roll-forward, per policy.

        Returns ``True`` when, for every projected month::

            sg_pp(t) == sg_pp(t - 1) + prem_to_sg_pp(t) - wd_pp(t)
                        - sg_deduction_pp(t) + sg_inv_income_pp(t)

        The shadow account is notional and carries no decrements, so this is a per-policy
        identity with no in-force weighting.  It is the check that the shadow account is
        never floored: if a zero floor crept in, this would fail the moment the balance
        went negative.
        """
        res = []
        for t in range(1, self.proj_len() + 1):
            sg = (self.sg_pp(t - 1) + self.prem_to_sg_pp(t) - self.wd_pp(t)
                  - self.sg_deduction_pp(t) + self.sg_inv_income_pp(t))
            res.append(self.math.isclose(self.sg_pp(t), sg, rel_tol=1e-9, abs_tol=1e-9))  # noqa: F821
        return all(res)

    @_mx_cy.cfunc
    def _f_check_margin(self) -> object:
        """Check the net cash flow against the expense, mortality and refund margins.

        Returns ``True`` when, for every projected month::

            net_cf(t) == margin_expense(t) + margin_mortality(t) + margin_rop(t)
                         + av_change(t) - inv_income(t)
                         + loan_bal_pp(t) * pols_lapse(t)

        The last three terms are what separates a *gross liability cash flow* model from
        ``CashValue_SE``, whose ``net_cf`` already nets the change in account value and the
        investment income; the loan term is the debt extinguished against the account value
        when a policy with a loan surrenders.  The identity holds while neither the
        :func:`csv_pp` nor the :func:`ncsv_pp` floor binds against a policy loan, which is
        the case for every shipped model point.
        """
        res = []
        for t in range(1, self.proj_len() + 1):
            rhs = (self.margin_expense(t) + self.margin_mortality(t) + self.margin_rop(t)
                   + self.av_change(t) - self.inv_income(t)
                   + self.loan_bal_pp(t) * self.pols_lapse(t))
            res.append(self.math.isclose(self.net_cf(t), rhs,                       # noqa: F821
                                    rel_tol=1e-9, abs_tol=1e-9))
        return all(res)

    @_mx_cy.cfunc
    def _f_result_cf(self) -> object:
        """Result table of cashflows, a DataFrame indexed by policy month ``t``.

        ``pols_if`` is the in-force weight applied to that same row's cash flows -- the
        number in force at the **start** of the month -- and the remaining columns are
        income-positive under ``net_cf``: ``premiums - claims_death - claims_lapse
        - claims_rop - withdrawals - expenses - premium_taxes``.  The surrender column is
        ``claims_lapse``, matching the ``"LAPSE"`` kind that produces it, and withdrawals
        are their own column rather than a claim.
        """
        ts = list(range(1, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "pols_if": [self.pols_if(t) for t in ts],
                "premiums": [self.premiums(t) for t in ts],
                "claims_death": [self.claims(t, "DEATH") for t in ts],
                "claims_lapse": [self.claims(t, "LAPSE") for t in ts],
                "claims_rop": [self.claims(t, "REFUND") for t in ts],
                "withdrawals": [self.withdrawals(t) for t in ts],
                "expenses": [self.expenses(t) for t in ts],
                "premium_taxes": [self.premium_taxes(t) for t in ts],
                "net_cf": [self.net_cf(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    @_mx_cy.cfunc
    def _f_result_pols(self) -> object:
        """Result table of policy decrements, a DataFrame indexed by policy month ``t``."""
        ts = list(range(1, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "pols_if": [self.pols_if(t) for t in ts],
                "pols_death": [self.pols_death(t) for t in ts],
                "pols_lapse": [self.pols_lapse(t) for t in ts],
                "pols_rop": [self.pols_rop(t) for t in ts],
                "pols_lapse_grace": [self.pols_lapse_grace(t) for t in ts],
                "pols_maturity": [self.pols_maturity(t) for t in ts],
                "mort_rate_mth": [self.mort_rate_mth(t) for t in ts],
                "lapse_rate_mth": [self.lapse_rate_mth(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    @_mx_cy.cfunc
    def _f_result_av(self) -> object:
        """Result table of the two account values, per policy.

        The columns are the columns of the worked example in the technical notes, in the
        notes' own order -- premium, net premium to each account, the deductions on each,
        the interest credited to each, the two closing balances -- followed by the forgone
        deduction, which the notes write inline in the deductions cell, and the status.
        """
        ts = list(range(1, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "premium_pp": [self.premium_pp(t) for t in ts],
                "prem_to_av_pp": [self.prem_to_av_pp(t) for t in ts],
                "mth_deduction_pp": [self.mth_deduction_pp(t) for t in ts],
                "inv_income_pp": [self.inv_income_pp(t) for t in ts],
                "av_pp": [self.av_pp(t) for t in ts],
                "prem_to_sg_pp": [self.prem_to_sg_pp(t) for t in ts],
                "sg_deduction_pp": [self.sg_deduction_pp(t) for t in ts],
                "sg_inv_income_pp": [self.sg_inv_income_pp(t) for t in ts],
                "sg_pp": [self.sg_pp(t) for t in ts],
                "forgone_pp": [self.mth_deduction_forgone_pp(t) for t in ts],
                "status": [self.status(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    @_mx_cy.cfunc
    def _f_result_guar(self) -> object:
        """Result table of the guarantee diagnostics, a DataFrame indexed by ``t``.

        The net amount at risk and cost of insurance on each account, the deduction the
        insurer forgoes across the policies in force -- the running cost of the guarantee --
        the shadow account net of debt, whether the guarantee is active, the catch-up
        premium that would restore it and the grace counter.
        """
        ts = list(range(1, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "net_amt_at_risk": [self.net_amt_at_risk(t) for t in ts],
                "coi_pp": [self.coi_pp(t) for t in ts],
                "mth_deduction_forgone": [self.mth_deduction_forgone(t) for t in ts],
                "sg_net_amt_at_risk": [self.sg_net_amt_at_risk(t) for t in ts],
                "sg_coi_pp": [self.sg_coi_pp(t) for t in ts],
                "sg_net_pp": [self.sg_net_pp(t) for t in ts],
                "is_guar_active": [self.is_guar_active(t) for t in ts],
                "catch_up_prem_pp": [self.catch_up_prem_pp(t) for t in ts],
                "grace_mth": [self.grace_mth(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    @_mx_cy.cfunc
    def _f_bench_net_cf(self) -> _mx_cy.double:
        return sum(self.net_cf(t) for t in range(1, self.proj_len() + 1))


    @_mx_cy.ccall
    def model_point(self) -> object:
        if self._has_model_point:
            return self._v_model_point
        else:
            val = self._v_model_point = self._f_model_point()
            self._has_model_point = True
            return val

    @_mx_cy.ccall
    def age_at_entry(self) -> _mx_cy.longlong:
        if self._has_age_at_entry:
            return self._v_age_at_entry
        else:
            val = self._v_age_at_entry = self._f_age_at_entry()
            self._has_age_at_entry = True
            return val

    @_mx_cy.ccall
    def sex(self) -> str:
        if self._has_sex:
            return self._v_sex
        else:
            val = self._v_sex = self._f_sex()
            self._has_sex = True
            return val

    @_mx_cy.ccall
    def rate_class(self) -> str:
        if self._has_rate_class:
            return self._v_rate_class
        else:
            val = self._v_rate_class = self._f_rate_class()
            self._has_rate_class = True
            return val

    @_mx_cy.ccall
    def sum_assured(self) -> _mx_cy.double:
        if self._has_sum_assured:
            return self._v_sum_assured
        else:
            val = self._v_sum_assured = self._f_sum_assured()
            self._has_sum_assured = True
            return val

    @_mx_cy.ccall
    def guarantee_age(self) -> _mx_cy.longlong:
        if self._has_guarantee_age:
            return self._v_guarantee_age
        else:
            val = self._v_guarantee_age = self._f_guarantee_age()
            self._has_guarantee_age = True
            return val

    @_mx_cy.ccall
    def premium_type(self) -> str:
        if self._has_premium_type:
            return self._v_premium_type
        else:
            val = self._v_premium_type = self._f_premium_type()
            self._has_premium_type = True
            return val

    @_mx_cy.ccall
    def premium_mode(self) -> str:
        if self._has_premium_mode:
            return self._v_premium_mode
        else:
            val = self._v_premium_mode = self._f_premium_mode()
            self._has_premium_mode = True
            return val

    @_mx_cy.ccall
    def premium_pp_ann(self) -> _mx_cy.double:
        if self._has_premium_pp_ann:
            return self._v_premium_pp_ann
        else:
            val = self._v_premium_pp_ann = self._f_premium_pp_ann()
            self._has_premium_pp_ann = True
            return val

    @_mx_cy.ccall
    def load_prem_rate(self) -> _mx_cy.double:
        if self._has_load_prem_rate:
            return self._v_load_prem_rate
        else:
            val = self._v_load_prem_rate = self._f_load_prem_rate()
            self._has_load_prem_rate = True
            return val

    @_mx_cy.ccall
    def av_pp_init(self) -> _mx_cy.double:
        if self._has_av_pp_init:
            return self._v_av_pp_init
        else:
            val = self._v_av_pp_init = self._f_av_pp_init()
            self._has_av_pp_init = True
            return val

    @_mx_cy.ccall
    def sg_pp_init(self) -> _mx_cy.double:
        if self._has_sg_pp_init:
            return self._v_sg_pp_init
        else:
            val = self._v_sg_pp_init = self._f_sg_pp_init()
            self._has_sg_pp_init = True
            return val

    @_mx_cy.ccall
    def loan_bal_init(self) -> _mx_cy.double:
        if self._has_loan_bal_init:
            return self._v_loan_bal_init
        else:
            val = self._v_loan_bal_init = self._f_loan_bal_init()
            self._has_loan_bal_init = True
            return val

    @_mx_cy.ccall
    def cum_prem_init(self) -> _mx_cy.double:
        if self._has_cum_prem_init:
            return self._v_cum_prem_init
        else:
            val = self._v_cum_prem_init = self._f_cum_prem_init()
            self._has_cum_prem_init = True
            return val

    @_mx_cy.ccall
    def pols_if_init(self) -> _mx_cy.double:
        if self._has_pols_if_init:
            return self._v_pols_if_init
        else:
            val = self._v_pols_if_init = self._f_pols_if_init()
            self._has_pols_if_init = True
            return val

    @_mx_cy.ccall
    def duration_mth_init(self) -> _mx_cy.longlong:
        if self._has_duration_mth_init:
            return self._v_duration_mth_init
        else:
            val = self._v_duration_mth_init = self._f_duration_mth_init()
            self._has_duration_mth_init = True
            return val

    @_mx_cy.ccall
    def has_surr_charge(self) -> _mx_cy.bint:
        if self._has_has_surr_charge:
            return self._v_has_surr_charge
        else:
            val = self._v_has_surr_charge = self._f_has_surr_charge()
            self._has_has_surr_charge = True
            return val

    @_mx_cy.ccall
    def surr_charge_id(self) -> str:
        if self._has_surr_charge_id:
            return self._v_surr_charge_id
        else:
            val = self._v_surr_charge_id = self._f_surr_charge_id()
            self._has_surr_charge_id = True
            return val

    @_mx_cy.ccall
    def rop_elected(self) -> _mx_cy.bint:
        if self._has_rop_elected:
            return self._v_rop_elected
        else:
            val = self._v_rop_elected = self._f_rop_elected()
            self._has_rop_elected = True
            return val

    @_mx_cy.ccall
    def coi_rate_dp(self) -> _mx_cy.longlong:
        if self._has_coi_rate_dp:
            return self._v_coi_rate_dp
        else:
            val = self._v_coi_rate_dp = self._f_coi_rate_dp()
            self._has_coi_rate_dp = True
            return val

    @_mx_cy.ccall
    def duration_mth(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 733):
            if self._has_duration_mth[t]:
                return self._v_duration_mth[t]
            else:
                val = self._f_duration_mth(t)
                self._v_duration_mth[t] = val
                self._has_duration_mth[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def duration(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 733):
            if self._has_duration[t]:
                return self._v_duration[t]
            else:
                val = self._f_duration(t)
                self._v_duration[t] = val
                self._has_duration[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def policy_year(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 733):
            if self._has_policy_year[t]:
                return self._v_policy_year[t]
            else:
                val = self._f_policy_year(t)
                self._v_policy_year[t] = val
                self._has_policy_year[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def age(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 733):
            if self._has_age[t]:
                return self._v_age[t]
            else:
                val = self._f_age(t)
                self._v_age[t] = val
                self._has_age[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def proj_len(self) -> _mx_cy.longlong:
        if self._has_proj_len:
            return self._v_proj_len
        else:
            val = self._v_proj_len = self._f_proj_len()
            self._has_proj_len = True
            return val

    @_mx_cy.ccall
    def sum_assured_at(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_sum_assured_at[t]:
                return self._v_sum_assured_at[t]
            else:
                val = self._f_sum_assured_at(t)
                self._v_sum_assured_at[t] = val
                self._has_sum_assured_at[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def units(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_units[t]:
                return self._v_units[t]
            else:
                val = self._f_units(t)
                self._v_units[t] = val
                self._has_units[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def crediting_rate_ann(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_crediting_rate_ann[t]:
                return self._v_crediting_rate_ann[t]
            else:
                val = self._f_crediting_rate_ann(t)
                self._v_crediting_rate_ann[t] = val
                self._has_crediting_rate_ann[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def inv_return_mth(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_inv_return_mth[t]:
                return self._v_inv_return_mth[t]
            else:
                val = self._f_inv_return_mth(t)
                self._v_inv_return_mth[t] = val
                self._has_inv_return_mth[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def guar_rate_mth(self) -> _mx_cy.double:
        if self._has_guar_rate_mth:
            return self._v_guar_rate_mth
        else:
            val = self._v_guar_rate_mth = self._f_guar_rate_mth()
            self._has_guar_rate_mth = True
            return val

    @_mx_cy.ccall
    def sg_rate_mth(self) -> _mx_cy.double:
        if self._has_sg_rate_mth:
            return self._v_sg_rate_mth
        else:
            val = self._v_sg_rate_mth = self._f_sg_rate_mth()
            self._has_sg_rate_mth = True
            return val

    @_mx_cy.ccall
    def naar_factor(self) -> _mx_cy.double:
        if self._has_naar_factor:
            return self._v_naar_factor
        else:
            val = self._v_naar_factor = self._f_naar_factor()
            self._has_naar_factor = True
            return val

    @_mx_cy.ccall
    def sg_naar_factor(self) -> _mx_cy.double:
        if self._has_sg_naar_factor:
            return self._v_sg_naar_factor
        else:
            val = self._v_sg_naar_factor = self._f_sg_naar_factor()
            self._has_sg_naar_factor = True
            return val

    @_mx_cy.ccall
    def loan_rate_mth(self) -> _mx_cy.double:
        if self._has_loan_rate_mth:
            return self._v_loan_rate_mth
        else:
            val = self._v_loan_rate_mth = self._f_loan_rate_mth()
            self._has_loan_rate_mth = True
            return val

    @_mx_cy.ccall
    def loan_cr_rate_mth(self) -> _mx_cy.double:
        if self._has_loan_cr_rate_mth:
            return self._v_loan_cr_rate_mth
        else:
            val = self._v_loan_cr_rate_mth = self._f_loan_cr_rate_mth()
            self._has_loan_cr_rate_mth = True
            return val

    @_mx_cy.ccall
    def premium_freq(self) -> _mx_cy.longlong:
        if self._has_premium_freq:
            return self._v_premium_freq
        else:
            val = self._v_premium_freq = self._f_premium_freq()
            self._has_premium_freq = True
            return val

    @_mx_cy.ccall
    def is_premium_mth(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        if (0 <= t < 733):
            if self._has_is_premium_mth[t]:
                return self._v_is_premium_mth[t]
            else:
                val = self._f_is_premium_mth(t)
                self._v_is_premium_mth[t] = val
                self._has_is_premium_mth[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def prem_persistency(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_prem_persistency[t]:
                return self._v_prem_persistency[t]
            else:
                val = self._f_prem_persistency(t)
                self._v_prem_persistency[t] = val
                self._has_prem_persistency[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def premium_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_premium_pp[t]:
                return self._v_premium_pp[t]
            else:
                val = self._f_premium_pp(t)
                self._v_premium_pp[t] = val
                self._has_premium_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def prem_to_av_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_prem_to_av_pp[t]:
                return self._v_prem_to_av_pp[t]
            else:
                val = self._f_prem_to_av_pp(t)
                self._v_prem_to_av_pp[t] = val
                self._has_prem_to_av_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def prem_to_sg_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_prem_to_sg_pp[t]:
                return self._v_prem_to_sg_pp[t]
            else:
                val = self._f_prem_to_sg_pp(t)
                self._v_prem_to_sg_pp[t] = val
                self._has_prem_to_sg_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def prem_to_av(self, t: object) -> object:
        if self._v_prem_to_av is None:
            self._v_prem_to_av = {}
        if t in self._v_prem_to_av:
            return self._v_prem_to_av[t]
        else:
            val = self._f_prem_to_av(t)
            self._v_prem_to_av[t] = val
            return val

    @_mx_cy.ccall
    def premiums(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_premiums[t]:
                return self._v_premiums[t]
            else:
                val = self._f_premiums(t)
                self._v_premiums[t] = val
                self._has_premiums[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def cum_prem_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_cum_prem_pp[t]:
                return self._v_cum_prem_pp[t]
            else:
                val = self._f_cum_prem_pp(t)
                self._v_cum_prem_pp[t] = val
                self._has_cum_prem_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def wd_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_wd_pp[t]:
                return self._v_wd_pp[t]
            else:
                val = self._f_wd_pp(t)
                self._v_wd_pp[t] = val
                self._has_wd_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def wd_fee_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_wd_fee_pp[t]:
                return self._v_wd_fee_pp[t]
            else:
                val = self._f_wd_fee_pp(t)
                self._v_wd_fee_pp[t] = val
                self._has_wd_fee_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def wd_fees(self, t: object) -> object:
        if self._v_wd_fees is None:
            self._v_wd_fees = {}
        if t in self._v_wd_fees:
            return self._v_wd_fees[t]
        else:
            val = self._f_wd_fees(t)
            self._v_wd_fees[t] = val
            return val

    @_mx_cy.ccall
    def corridor_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_corridor_factor[t]:
                return self._v_corridor_factor[t]
            else:
                val = self._f_corridor_factor(t)
                self._v_corridor_factor[t] = val
                self._has_corridor_factor[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def db_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_db_pp[t]:
                return self._v_db_pp[t]
            else:
                val = self._f_db_pp(t)
                self._v_db_pp[t] = val
                self._has_db_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def net_amt_at_risk(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_net_amt_at_risk[t]:
                return self._v_net_amt_at_risk[t]
            else:
                val = self._f_net_amt_at_risk(t)
                self._v_net_amt_at_risk[t] = val
                self._has_net_amt_at_risk[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def sg_net_amt_at_risk(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_sg_net_amt_at_risk[t]:
                return self._v_sg_net_amt_at_risk[t]
            else:
                val = self._f_sg_net_amt_at_risk(t)
                self._v_sg_net_amt_at_risk[t] = val
                self._has_sg_net_amt_at_risk[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def coi_rate_scale(self) -> object:
        if self._has_coi_rate_scale:
            return self._v_coi_rate_scale
        else:
            val = self._v_coi_rate_scale = self._f_coi_rate_scale()
            self._has_coi_rate_scale = True
            return val

    @_mx_cy.ccall
    def coi_rate_guar(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_coi_rate_guar[t]:
                return self._v_coi_rate_guar[t]
            else:
                val = self._f_coi_rate_guar(t)
                self._v_coi_rate_guar[t] = val
                self._has_coi_rate_guar[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def coi_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_coi_rate[t]:
                return self._v_coi_rate[t]
            else:
                val = self._f_coi_rate(t)
                self._v_coi_rate[t] = val
                self._has_coi_rate[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def sg_coi_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_sg_coi_rate[t]:
                return self._v_sg_coi_rate[t]
            else:
                val = self._f_sg_coi_rate(t)
                self._v_sg_coi_rate[t] = val
                self._has_sg_coi_rate[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def coi_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_coi_pp[t]:
                return self._v_coi_pp[t]
            else:
                val = self._f_coi_pp(t)
                self._v_coi_pp[t] = val
                self._has_coi_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def sg_coi_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_sg_coi_pp[t]:
                return self._v_sg_coi_pp[t]
            else:
                val = self._f_sg_coi_pp(t)
                self._v_sg_coi_pp[t] = val
                self._has_sg_coi_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def rider_charge_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_rider_charge_pp[t]:
                return self._v_rider_charge_pp[t]
            else:
                val = self._f_rider_charge_pp(t)
                self._v_rider_charge_pp[t] = val
                self._has_rider_charge_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def maint_fee_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_maint_fee_pp[t]:
                return self._v_maint_fee_pp[t]
            else:
                val = self._f_maint_fee_pp(t)
                self._v_maint_fee_pp[t] = val
                self._has_maint_fee_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def sg_maint_fee_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_sg_maint_fee_pp[t]:
                return self._v_sg_maint_fee_pp[t]
            else:
                val = self._f_sg_maint_fee_pp(t)
                self._v_sg_maint_fee_pp[t] = val
                self._has_sg_maint_fee_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def mth_deduction_pp(self, t: object) -> object:
        if self._v_mth_deduction_pp is None:
            self._v_mth_deduction_pp = {}
        if t in self._v_mth_deduction_pp:
            return self._v_mth_deduction_pp[t]
        else:
            val = self._f_mth_deduction_pp(t)
            self._v_mth_deduction_pp[t] = val
            return val

    @_mx_cy.ccall
    def sg_deduction_pp(self, t: object) -> object:
        if self._v_sg_deduction_pp is None:
            self._v_sg_deduction_pp = {}
        if t in self._v_sg_deduction_pp:
            return self._v_sg_deduction_pp[t]
        else:
            val = self._f_sg_deduction_pp(t)
            self._v_sg_deduction_pp[t] = val
            return val

    @_mx_cy.ccall
    def maint_fee_taken_pp(self, t: object) -> object:
        if self._v_maint_fee_taken_pp is None:
            self._v_maint_fee_taken_pp = {}
        if t in self._v_maint_fee_taken_pp:
            return self._v_maint_fee_taken_pp[t]
        else:
            val = self._f_maint_fee_taken_pp(t)
            self._v_maint_fee_taken_pp[t] = val
            return val

    @_mx_cy.ccall
    def coi_taken_pp(self, t: object) -> object:
        if self._v_coi_taken_pp is None:
            self._v_coi_taken_pp = {}
        if t in self._v_coi_taken_pp:
            return self._v_coi_taken_pp[t]
        else:
            val = self._f_coi_taken_pp(t)
            self._v_coi_taken_pp[t] = val
            return val

    @_mx_cy.ccall
    def mth_deduction_taken_pp(self, t: object) -> object:
        if self._v_mth_deduction_taken_pp is None:
            self._v_mth_deduction_taken_pp = {}
        if t in self._v_mth_deduction_taken_pp:
            return self._v_mth_deduction_taken_pp[t]
        else:
            val = self._f_mth_deduction_taken_pp(t)
            self._v_mth_deduction_taken_pp[t] = val
            return val

    @_mx_cy.ccall
    def mth_deduction_forgone_pp(self, t: object) -> object:
        if self._v_mth_deduction_forgone_pp is None:
            self._v_mth_deduction_forgone_pp = {}
        if t in self._v_mth_deduction_forgone_pp:
            return self._v_mth_deduction_forgone_pp[t]
        else:
            val = self._f_mth_deduction_forgone_pp(t)
            self._v_mth_deduction_forgone_pp[t] = val
            return val

    @_mx_cy.ccall
    def maint_fee(self, t: object) -> object:
        if self._v_maint_fee is None:
            self._v_maint_fee = {}
        if t in self._v_maint_fee:
            return self._v_maint_fee[t]
        else:
            val = self._f_maint_fee(t)
            self._v_maint_fee[t] = val
            return val

    @_mx_cy.ccall
    def coi(self, t: object) -> object:
        if self._v_coi is None:
            self._v_coi = {}
        if t in self._v_coi:
            return self._v_coi[t]
        else:
            val = self._f_coi(t)
            self._v_coi[t] = val
            return val

    @_mx_cy.ccall
    def mth_deduction(self, t: object) -> object:
        if self._v_mth_deduction is None:
            self._v_mth_deduction = {}
        if t in self._v_mth_deduction:
            return self._v_mth_deduction[t]
        else:
            val = self._f_mth_deduction(t)
            self._v_mth_deduction[t] = val
            return val

    @_mx_cy.ccall
    def mth_deduction_forgone(self, t: object) -> object:
        if self._v_mth_deduction_forgone is None:
            self._v_mth_deduction_forgone = {}
        if t in self._v_mth_deduction_forgone:
            return self._v_mth_deduction_forgone[t]
        else:
            val = self._f_mth_deduction_forgone(t)
            self._v_mth_deduction_forgone[t] = val
            return val

    @_mx_cy.ccall
    def av_pp_at(self, t: _mx_cy.longlong, timing: str) -> _mx_cy.double:
        if self._v_av_pp_at is None:
            self._v_av_pp_at = {}
        if (t, timing) in self._v_av_pp_at:
            return self._v_av_pp_at[(t, timing)]
        else:
            val = self._f_av_pp_at(t, timing)
            self._v_av_pp_at[(t, timing)] = val
            return val

    @_mx_cy.ccall
    def inv_income_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_inv_income_pp[t]:
                return self._v_inv_income_pp[t]
            else:
                val = self._f_inv_income_pp(t)
                self._v_inv_income_pp[t] = val
                self._has_inv_income_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def av_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_av_pp[t]:
                return self._v_av_pp[t]
            else:
                val = self._f_av_pp(t)
                self._v_av_pp[t] = val
                self._has_av_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def av_at(self, t: object, timing: object) -> object:
        if self._v_av_at is None:
            self._v_av_at = {}
        if (t, timing) in self._v_av_at:
            return self._v_av_at[(t, timing)]
        else:
            val = self._f_av_at(t, timing)
            self._v_av_at[(t, timing)] = val
            return val

    @_mx_cy.ccall
    def inv_income(self, t: object) -> object:
        if self._v_inv_income is None:
            self._v_inv_income = {}
        if t in self._v_inv_income:
            return self._v_inv_income[t]
        else:
            val = self._f_inv_income(t)
            self._v_inv_income[t] = val
            return val

    @_mx_cy.ccall
    def av_change(self, t: object) -> object:
        if self._v_av_change is None:
            self._v_av_change = {}
        if t in self._v_av_change:
            return self._v_av_change[t]
        else:
            val = self._f_av_change(t)
            self._v_av_change[t] = val
            return val

    @_mx_cy.ccall
    def loan_bal_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_loan_bal_pp[t]:
                return self._v_loan_bal_pp[t]
            else:
                val = self._f_loan_bal_pp(t)
                self._v_loan_bal_pp[t] = val
                self._has_loan_bal_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def sg_pp_at(self, t: _mx_cy.longlong, timing: str) -> _mx_cy.double:
        if self._v_sg_pp_at is None:
            self._v_sg_pp_at = {}
        if (t, timing) in self._v_sg_pp_at:
            return self._v_sg_pp_at[(t, timing)]
        else:
            val = self._f_sg_pp_at(t, timing)
            self._v_sg_pp_at[(t, timing)] = val
            return val

    @_mx_cy.ccall
    def sg_inv_income_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_sg_inv_income_pp[t]:
                return self._v_sg_inv_income_pp[t]
            else:
                val = self._f_sg_inv_income_pp(t)
                self._v_sg_inv_income_pp[t] = val
                self._has_sg_inv_income_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def sg_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_sg_pp[t]:
                return self._v_sg_pp[t]
            else:
                val = self._f_sg_pp(t)
                self._v_sg_pp[t] = val
                self._has_sg_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def sg_net_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_sg_net_pp[t]:
                return self._v_sg_net_pp[t]
            else:
                val = self._f_sg_net_pp(t)
                self._v_sg_net_pp[t] = val
                self._has_sg_net_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def is_guar_active(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        if (0 <= t < 733):
            if self._has_is_guar_active[t]:
                return self._v_is_guar_active[t]
            else:
                val = self._f_is_guar_active(t)
                self._v_is_guar_active[t] = val
                self._has_is_guar_active[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def is_guar_supported(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        if (0 <= t < 733):
            if self._has_is_guar_supported[t]:
                return self._v_is_guar_supported[t]
            else:
                val = self._f_is_guar_supported(t)
                self._v_is_guar_supported[t] = val
                self._has_is_guar_supported[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def catch_up_prem_pp(self, t: object) -> object:
        if self._v_catch_up_prem_pp is None:
            self._v_catch_up_prem_pp = {}
        if t in self._v_catch_up_prem_pp:
            return self._v_catch_up_prem_pp[t]
        else:
            val = self._f_catch_up_prem_pp(t)
            self._v_catch_up_prem_pp[t] = val
            return val

    @_mx_cy.ccall
    def surr_charge_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_surr_charge_rate[t]:
                return self._v_surr_charge_rate[t]
            else:
                val = self._f_surr_charge_rate(t)
                self._v_surr_charge_rate[t] = val
                self._has_surr_charge_rate[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def surr_charge_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_surr_charge_pp[t]:
                return self._v_surr_charge_pp[t]
            else:
                val = self._f_surr_charge_pp(t)
                self._v_surr_charge_pp[t] = val
                self._has_surr_charge_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def csv_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_csv_pp[t]:
                return self._v_csv_pp[t]
            else:
                val = self._f_csv_pp(t)
                self._v_csv_pp[t] = val
                self._has_csv_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def ncsv_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_ncsv_pp[t]:
                return self._v_ncsv_pp[t]
            else:
                val = self._f_ncsv_pp(t)
                self._v_ncsv_pp[t] = val
                self._has_ncsv_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def surr_charge(self, t: object) -> object:
        if self._v_surr_charge is None:
            self._v_surr_charge = {}
        if t in self._v_surr_charge:
            return self._v_surr_charge[t]
        else:
            val = self._f_surr_charge(t)
            self._v_surr_charge[t] = val
            return val

    @_mx_cy.ccall
    def is_shortfall(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        if (0 <= t < 733):
            if self._has_is_shortfall[t]:
                return self._v_is_shortfall[t]
            else:
                val = self._f_is_shortfall(t)
                self._v_is_shortfall[t] = val
                self._has_is_shortfall[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def cure_premium_pp(self, t: object) -> object:
        if self._v_cure_premium_pp is None:
            self._v_cure_premium_pp = {}
        if t in self._v_cure_premium_pp:
            return self._v_cure_premium_pp[t]
        else:
            val = self._f_cure_premium_pp(t)
            self._v_cure_premium_pp[t] = val
            return val

    @_mx_cy.ccall
    def grace_mth(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 733):
            if self._has_grace_mth[t]:
                return self._v_grace_mth[t]
            else:
                val = self._f_grace_mth(t)
                self._v_grace_mth[t] = val
                self._has_grace_mth[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def is_lapsed(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        if (0 <= t < 733):
            if self._has_is_lapsed[t]:
                return self._v_is_lapsed[t]
            else:
                val = self._f_is_lapsed(t)
                self._v_is_lapsed[t] = val
                self._has_is_lapsed[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def status(self, t: object) -> object:
        if self._v_status is None:
            self._v_status = {}
        if t in self._v_status:
            return self._v_status[t]
        else:
            val = self._f_status(t)
            self._v_status[t] = val
            return val

    @_mx_cy.ccall
    def rop_anniversary(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 733):
            if self._has_rop_anniversary[t]:
                return self._v_rop_anniversary[t]
            else:
                val = self._f_rop_anniversary(t)
                self._v_rop_anniversary[t] = val
                self._has_rop_anniversary[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def rop_ratio(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_rop_ratio[t]:
                return self._v_rop_ratio[t]
            else:
                val = self._f_rop_ratio(t)
                self._v_rop_ratio[t] = val
                self._has_rop_ratio[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def rop_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_rop_rate[t]:
                return self._v_rop_rate[t]
            else:
                val = self._f_rop_rate(t)
                self._v_rop_rate[t] = val
                self._has_rop_rate[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def class_factor(self) -> _mx_cy.double:
        if self._has_class_factor:
            return self._v_class_factor
        else:
            val = self._v_class_factor = self._f_class_factor()
            self._has_class_factor = True
            return val

    @_mx_cy.ccall
    def mort_improve_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_mort_improve_rate[t]:
                return self._v_mort_improve_rate[t]
            else:
                val = self._f_mort_improve_rate(t)
                self._v_mort_improve_rate[t] = val
                self._has_mort_improve_rate[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def mort_improve_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_mort_improve_factor[t]:
                return self._v_mort_improve_factor[t]
            else:
                val = self._f_mort_improve_factor(t)
                self._v_mort_improve_factor[t] = val
                self._has_mort_improve_factor[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def mort_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_mort_rate[t]:
                return self._v_mort_rate[t]
            else:
                val = self._f_mort_rate(t)
                self._v_mort_rate[t] = val
                self._has_mort_rate[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def mort_rate_mth(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_mort_rate_mth[t]:
                return self._v_mort_rate_mth[t]
            else:
                val = self._f_mort_rate_mth(t)
                self._v_mort_rate_mth[t] = val
                self._has_mort_rate_mth[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def lapse_rate_base(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_lapse_rate_base[t]:
                return self._v_lapse_rate_base[t]
            else:
                val = self._f_lapse_rate_base(t)
                self._v_lapse_rate_base[t] = val
                self._has_lapse_rate_base[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def lapse_rate_guar_mult(self) -> _mx_cy.double:
        if self._has_lapse_rate_guar_mult:
            return self._v_lapse_rate_guar_mult
        else:
            val = self._v_lapse_rate_guar_mult = self._f_lapse_rate_guar_mult()
            self._has_lapse_rate_guar_mult = True
            return val

    @_mx_cy.ccall
    def lapse_rate_pattern_mult(self) -> _mx_cy.double:
        if self._has_lapse_rate_pattern_mult:
            return self._v_lapse_rate_pattern_mult
        else:
            val = self._v_lapse_rate_pattern_mult = self._f_lapse_rate_pattern_mult()
            self._has_lapse_rate_pattern_mult = True
            return val

    @_mx_cy.ccall
    def lapse_rate_dyn_mult(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_lapse_rate_dyn_mult[t]:
                return self._v_lapse_rate_dyn_mult[t]
            else:
                val = self._f_lapse_rate_dyn_mult(t)
                self._v_lapse_rate_dyn_mult[t] = val
                self._has_lapse_rate_dyn_mult[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def lapse_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_lapse_rate[t]:
                return self._v_lapse_rate[t]
            else:
                val = self._f_lapse_rate(t)
                self._v_lapse_rate[t] = val
                self._has_lapse_rate[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def lapse_rate_mth(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_lapse_rate_mth[t]:
                return self._v_lapse_rate_mth[t]
            else:
                val = self._f_lapse_rate_mth(t)
                self._v_lapse_rate_mth[t] = val
                self._has_lapse_rate_mth[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_if(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_pols_if[t]:
                return self._v_pols_if[t]
            else:
                val = self._f_pols_if(t)
                self._v_pols_if[t] = val
                self._has_pols_if[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_if_at(self, t: object, timing: object) -> object:
        if self._v_pols_if_at is None:
            self._v_pols_if_at = {}
        if (t, timing) in self._v_pols_if_at:
            return self._v_pols_if_at[(t, timing)]
        else:
            val = self._f_pols_if_at(t, timing)
            self._v_pols_if_at[(t, timing)] = val
            return val

    @_mx_cy.ccall
    def pols_death(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_pols_death[t]:
                return self._v_pols_death[t]
            else:
                val = self._f_pols_death(t)
                self._v_pols_death[t] = val
                self._has_pols_death[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_lapse(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_pols_lapse[t]:
                return self._v_pols_lapse[t]
            else:
                val = self._f_pols_lapse(t)
                self._v_pols_lapse[t] = val
                self._has_pols_lapse[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_rop(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_pols_rop[t]:
                return self._v_pols_rop[t]
            else:
                val = self._f_pols_rop(t)
                self._v_pols_rop[t] = val
                self._has_pols_rop[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_lapse_grace(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_pols_lapse_grace[t]:
                return self._v_pols_lapse_grace[t]
            else:
                val = self._f_pols_lapse_grace(t)
                self._v_pols_lapse_grace[t] = val
                self._has_pols_lapse_grace[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_maturity(self, t: object) -> object:
        if self._v_pols_maturity is None:
            self._v_pols_maturity = {}
        if t in self._v_pols_maturity:
            return self._v_pols_maturity[t]
        else:
            val = self._f_pols_maturity(t)
            self._v_pols_maturity[t] = val
            return val

    @_mx_cy.ccall
    def claim_pp(self, t: _mx_cy.longlong, kind: str) -> _mx_cy.double:
        if self._v_claim_pp is None:
            self._v_claim_pp = {}
        if (t, kind) in self._v_claim_pp:
            return self._v_claim_pp[(t, kind)]
        else:
            val = self._f_claim_pp(t, kind)
            self._v_claim_pp[(t, kind)] = val
            return val

    @_mx_cy.ccall
    def claims_from_av(self, t: object, kind: object) -> object:
        if self._v_claims_from_av is None:
            self._v_claims_from_av = {}
        if (t, kind) in self._v_claims_from_av:
            return self._v_claims_from_av[(t, kind)]
        else:
            val = self._f_claims_from_av(t, kind)
            self._v_claims_from_av[(t, kind)] = val
            return val

    @_mx_cy.ccall
    def claims_over_av(self, t: object) -> object:
        if self._v_claims_over_av is None:
            self._v_claims_over_av = {}
        if t in self._v_claims_over_av:
            return self._v_claims_over_av[t]
        else:
            val = self._f_claims_over_av(t)
            self._v_claims_over_av[t] = val
            return val

    @_mx_cy.ccall
    def claims(self, t: _mx_cy.longlong, kind: object=None) -> _mx_cy.double:
        if self._v_claims is None:
            self._v_claims = {}
        if (t, kind) in self._v_claims:
            return self._v_claims[(t, kind)]
        else:
            val = self._f_claims(t, kind)
            self._v_claims[(t, kind)] = val
            return val

    @_mx_cy.ccall
    def withdrawals(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_withdrawals[t]:
                return self._v_withdrawals[t]
            else:
                val = self._f_withdrawals(t)
                self._v_withdrawals[t] = val
                self._has_withdrawals[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def inflation_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_inflation_factor[t]:
                return self._v_inflation_factor[t]
            else:
                val = self._f_inflation_factor(t)
                self._v_inflation_factor[t] = val
                self._has_inflation_factor[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def expenses(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_expenses[t]:
                return self._v_expenses[t]
            else:
                val = self._f_expenses(t)
                self._v_expenses[t] = val
                self._has_expenses[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def premium_taxes(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_premium_taxes[t]:
                return self._v_premium_taxes[t]
            else:
                val = self._f_premium_taxes(t)
                self._v_premium_taxes[t] = val
                self._has_premium_taxes[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def margin_expense(self, t: object) -> object:
        if self._v_margin_expense is None:
            self._v_margin_expense = {}
        if t in self._v_margin_expense:
            return self._v_margin_expense[t]
        else:
            val = self._f_margin_expense(t)
            self._v_margin_expense[t] = val
            return val

    @_mx_cy.ccall
    def margin_mortality(self, t: object) -> object:
        if self._v_margin_mortality is None:
            self._v_margin_mortality = {}
        if t in self._v_margin_mortality:
            return self._v_margin_mortality[t]
        else:
            val = self._f_margin_mortality(t)
            self._v_margin_mortality[t] = val
            return val

    @_mx_cy.ccall
    def margin_rop(self, t: object) -> object:
        if self._v_margin_rop is None:
            self._v_margin_rop = {}
        if t in self._v_margin_rop:
            return self._v_margin_rop[t]
        else:
            val = self._f_margin_rop(t)
            self._v_margin_rop[t] = val
            return val

    @_mx_cy.ccall
    def net_cf(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 733):
            if self._has_net_cf[t]:
                return self._v_net_cf[t]
            else:
                val = self._f_net_cf(t)
                self._v_net_cf[t] = val
                self._has_net_cf[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def solve_len(self) -> object:
        if self._has_solve_len:
            return self._v_solve_len
        else:
            val = self._v_solve_len = self._f_solve_len()
            self._has_solve_len = True
            return val

    @_mx_cy.ccall
    def sg_pp_solve(self, t: object, prem: object) -> object:
        if self._v_sg_pp_solve is None:
            self._v_sg_pp_solve = {}
        if (t, prem) in self._v_sg_pp_solve:
            return self._v_sg_pp_solve[(t, prem)]
        else:
            val = self._f_sg_pp_solve(t, prem)
            self._v_sg_pp_solve[(t, prem)] = val
            return val

    @_mx_cy.ccall
    def guar_min_sg(self, prem: object) -> object:
        if self._v_guar_min_sg is None:
            self._v_guar_min_sg = {}
        if prem in self._v_guar_min_sg:
            return self._v_guar_min_sg[prem]
        else:
            val = self._f_guar_min_sg(prem)
            self._v_guar_min_sg[prem] = val
            return val

    @_mx_cy.ccall
    def no_lapse_premium(self) -> object:
        if self._has_no_lapse_premium:
            return self._v_no_lapse_premium
        else:
            val = self._v_no_lapse_premium = self._f_no_lapse_premium()
            self._has_no_lapse_premium = True
            return val

    @_mx_cy.ccall
    def check_av_roll_fwd(self) -> object:
        if self._has_check_av_roll_fwd:
            return self._v_check_av_roll_fwd
        else:
            val = self._v_check_av_roll_fwd = self._f_check_av_roll_fwd()
            self._has_check_av_roll_fwd = True
            return val

    @_mx_cy.ccall
    def check_sg_roll_fwd(self) -> object:
        if self._has_check_sg_roll_fwd:
            return self._v_check_sg_roll_fwd
        else:
            val = self._v_check_sg_roll_fwd = self._f_check_sg_roll_fwd()
            self._has_check_sg_roll_fwd = True
            return val

    @_mx_cy.ccall
    def check_margin(self) -> object:
        if self._has_check_margin:
            return self._v_check_margin
        else:
            val = self._v_check_margin = self._f_check_margin()
            self._has_check_margin = True
            return val

    @_mx_cy.ccall
    def result_cf(self) -> object:
        if self._has_result_cf:
            return self._v_result_cf
        else:
            val = self._v_result_cf = self._f_result_cf()
            self._has_result_cf = True
            return val

    @_mx_cy.ccall
    def result_pols(self) -> object:
        if self._has_result_pols:
            return self._v_result_pols
        else:
            val = self._v_result_pols = self._f_result_pols()
            self._has_result_pols = True
            return val

    @_mx_cy.ccall
    def result_av(self) -> object:
        if self._has_result_av:
            return self._v_result_av
        else:
            val = self._v_result_av = self._f_result_av()
            self._has_result_av = True
            return val

    @_mx_cy.ccall
    def result_guar(self) -> object:
        if self._has_result_guar:
            return self._v_result_guar
        else:
            val = self._v_result_guar = self._f_result_guar()
            self._has_result_guar = True
            return val

    @_mx_cy.ccall
    def bench_net_cf(self) -> _mx_cy.double:
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

    def __call__(self, point_id: _mx_cy.longlong):
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


