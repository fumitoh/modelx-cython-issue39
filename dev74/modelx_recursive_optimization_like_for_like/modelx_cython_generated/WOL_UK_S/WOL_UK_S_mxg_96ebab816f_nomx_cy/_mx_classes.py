from cython.cimports.WOL_UK_S_mxg_96ebab816f_nomx_cy import _mx_sys
import cython as _mx_cy
from . import _mx_sys



_v_cells_names_Data = [
    'input_dir',
    'model_point_table',
    'mort_table',
    'lapse_table',
]
_v_space_params_Data = []


@_mx_cy.cclass
class _c_Data(_mx_sys.BaseSpace):
    
    _v_input_dir: object
    _has_input_dir: _mx_cy.bint
    _v_model_point_table: object
    _has_model_point_table: _mx_cy.bint
    _v_mort_table: object
    _has_mort_table: _mx_cy.bint
    _v_lapse_table: object
    _has_lapse_table: _mx_cy.bint
    
    model_point_file: str
    mort_table_file: str
    lapse_table_file: str
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
        self.mort_table_file = 'mort_table.csv'
        self.lapse_table_file = 'lapse_table.csv'
        self.pd = _mx_sys.import_module('pandas')

    @_mx_cy.ccall
    def _mx_copy_refs(self, base, base_root):
        
        base_: _c_Data = _mx_cy.cast(_c_Data, base)

        # Reference assignment
        self.model_point_file = base_.model_point_file
        self.mort_table_file = base_.mort_table_file
        self.lapse_table_file = base_.lapse_table_file
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
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.model_point_file, index_col="point_id")        # noqa: F821

    @_mx_cy.cfunc
    def _f_mort_table(self) -> object:
        """The annual mortality rates, read from *mort_table.csv*.

        Keyed by basis (``population`` or ``assured``), sex, smoker status and age last
        birthday, and capped at 1.  Both bases are **[std]** proxies: the ``population``
        rates are shaped like the ONS national life tables and anchored so that the O50
        cell's loaded rate is the notes' walk-through basis exactly, and the ``assured``
        rates are shaped like the "00" Series permanent assurance tables.  Neither is a
        published table, and the file's ``provenance`` column says which cells are anchors
        and which come from a sex or smoker factor.  Sorted on read, because
        ``Projection.mort_rate`` indexes into it.
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.mort_table_file,                               # noqa: F821
            index_col=["basis", "sex", "smoker", "age"]).sort_index()

    @_mx_cy.cfunc
    def _f_lapse_table(self) -> object:
        """The annual lapse rates by cell and policy year, from *lapse_table.csv*.

        The two cells carry different tables: the guaranteed-acceptance one lapses faster
        early, on affordability attrition.  Both are **[std]** drafting constructions - no
        public UK whole of life lapse study was retrieved - and on a product with no
        surrender value they are the single largest lever on the liability.
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.lapse_table_file,                              # noqa: F821
            index_col=["cell", "policy_year"]).sort_index()


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
    def mort_table(self) -> object:
        if self._has_mort_table:
            return self._v_mort_table
        else:
            val = self._v_mort_table = self._f_mort_table()
            self._has_mort_table = True
            return val

    @_mx_cy.ccall
    def lapse_table(self) -> object:
        if self._has_lapse_table:
            return self._v_lapse_table
        else:
            val = self._v_lapse_table = self._f_lapse_table()
            self._has_lapse_table = True
            return val










_v_cells_names_Projection = [
    'model_point',
    'cell',
    'age_at_entry',
    'sex',
    'smoker',
    'sum_assured',
    'premium_mth',
    'escalation',
    'cessation_mths',
    'moratorium_mths',
    'adb_multiplier',
    'pu_variant',
    'pols_if_init',
    'proj_len',
    'duration',
    'duration_mth',
    'policy_year',
    'age',
    'mort_basis',
    'mort_loading',
    'mort_improve_factor',
    'mort_rate',
    'mort_rate_mth',
    'esc_cover_step',
    'esc_prem_step',
    'cover_pp',
    'premium_pp',
    'prem_cum_pp',
    'in_moratorium',
    'payments_made',
    'payments_expected',
    'pu_eligible',
    'crossover_mth',
    'lapse_rate_base',
    'lapse_rate',
    'lapse_rate_mth',
    'pols_if',
    'pols_pu',
    'pu_benefit',
    'pols_all',
    'pols_if_at',
    'pols_death',
    'pols_death_pu',
    'pols_exit',
    'pols_convert',
    'pols_lapse',
    'pols_maturity',
    'benefit_pp',
    'premiums',
    'claims',
    'expense_acq_pp',
    'expense_maint_pp',
    'inflation_factor',
    'expenses',
    'commissions',
    'net_cf',
    'check_pols_roll_fwd_resid',
    'check_pols_roll_fwd',
    'check_truncation',
    'result_cf',
    'result_pols',
    'bench_net_cf',
]
_v_space_params_Projection = [
    'point_id',
]


@_mx_cy.cclass
class _c_Projection(_mx_sys.BaseSpace):
    
    _v_model_point: object
    _has_model_point: _mx_cy.bint
    _v_cell: str
    _has_cell: _mx_cy.bint
    _v_age_at_entry: _mx_cy.longlong
    _has_age_at_entry: _mx_cy.bint
    _v_sex: str
    _has_sex: _mx_cy.bint
    _v_smoker: str
    _has_smoker: _mx_cy.bint
    _v_sum_assured: _mx_cy.double
    _has_sum_assured: _mx_cy.bint
    _v_premium_mth: _mx_cy.double
    _has_premium_mth: _mx_cy.bint
    _v_escalation: str
    _has_escalation: _mx_cy.bint
    _v_cessation_mths: _mx_cy.longlong
    _has_cessation_mths: _mx_cy.bint
    _v_moratorium_mths: _mx_cy.longlong
    _has_moratorium_mths: _mx_cy.bint
    _v_adb_multiplier: _mx_cy.double
    _has_adb_multiplier: _mx_cy.bint
    _v_pu_variant: _mx_cy.bint
    _has_pu_variant: _mx_cy.bint
    _v_pols_if_init: _mx_cy.double
    _has_pols_if_init: _mx_cy.bint
    _v_proj_len: _mx_cy.longlong
    _has_proj_len: _mx_cy.bint
    _v_duration: _mx_cy.longlong[961]
    _has_duration: _mx_cy.bint[961]
    _v_duration_mth: dict
    _v_policy_year: _mx_cy.longlong[961]
    _has_policy_year: _mx_cy.bint[961]
    _v_age: _mx_cy.longlong[961]
    _has_age: _mx_cy.bint[961]
    _v_mort_basis: str
    _has_mort_basis: _mx_cy.bint
    _v_mort_loading: _mx_cy.double
    _has_mort_loading: _mx_cy.bint
    _v_mort_improve_factor: _mx_cy.double[961]
    _has_mort_improve_factor: _mx_cy.bint[961]
    _v_mort_rate: _mx_cy.double[961]
    _has_mort_rate: _mx_cy.bint[961]
    _v_mort_rate_mth: _mx_cy.double[961]
    _has_mort_rate_mth: _mx_cy.bint[961]
    _v_esc_cover_step: _mx_cy.double
    _has_esc_cover_step: _mx_cy.bint
    _v_esc_prem_step: _mx_cy.double
    _has_esc_prem_step: _mx_cy.bint
    _v_cover_pp: _mx_cy.double[961]
    _has_cover_pp: _mx_cy.bint[961]
    _v_premium_pp: _mx_cy.double[961]
    _has_premium_pp: _mx_cy.bint[961]
    _v_prem_cum_pp: _mx_cy.double[961]
    _has_prem_cum_pp: _mx_cy.bint[961]
    _v_in_moratorium: _mx_cy.bint[961]
    _has_in_moratorium: _mx_cy.bint[961]
    _v_payments_made: _mx_cy.longlong[961]
    _has_payments_made: _mx_cy.bint[961]
    _v_payments_expected: _mx_cy.longlong
    _has_payments_expected: _mx_cy.bint
    _v_pu_eligible: _mx_cy.bint[961]
    _has_pu_eligible: _mx_cy.bint[961]
    _v_crossover_mth: object
    _has_crossover_mth: _mx_cy.bint
    _v_lapse_rate_base: _mx_cy.double[961]
    _has_lapse_rate_base: _mx_cy.bint[961]
    _v_lapse_rate: _mx_cy.double[961]
    _has_lapse_rate: _mx_cy.bint[961]
    _v_lapse_rate_mth: _mx_cy.double[961]
    _has_lapse_rate_mth: _mx_cy.bint[961]
    _v_pols_if: _mx_cy.double[961]
    _has_pols_if: _mx_cy.bint[961]
    _v_pols_pu: _mx_cy.double[961]
    _has_pols_pu: _mx_cy.bint[961]
    _v_pu_benefit: _mx_cy.double[961]
    _has_pu_benefit: _mx_cy.bint[961]
    _v_pols_all: _mx_cy.double[961]
    _has_pols_all: _mx_cy.bint[961]
    _v_pols_if_at: dict
    _v_pols_death: _mx_cy.double[961]
    _has_pols_death: _mx_cy.bint[961]
    _v_pols_death_pu: dict
    _v_pols_exit: _mx_cy.double[961]
    _has_pols_exit: _mx_cy.bint[961]
    _v_pols_convert: _mx_cy.double[961]
    _has_pols_convert: _mx_cy.bint[961]
    _v_pols_lapse: dict
    _v_pols_maturity: dict
    _v_benefit_pp: dict
    _v_premiums: _mx_cy.double[961]
    _has_premiums: _mx_cy.bint[961]
    _v_claims: dict
    _v_expense_acq_pp: _mx_cy.double
    _has_expense_acq_pp: _mx_cy.bint
    _v_expense_maint_pp: _mx_cy.double
    _has_expense_maint_pp: _mx_cy.bint
    _v_inflation_factor: _mx_cy.double[961]
    _has_inflation_factor: _mx_cy.bint[961]
    _v_expenses: _mx_cy.double[961]
    _has_expenses: _mx_cy.bint[961]
    _v_commissions: _mx_cy.double[961]
    _has_commissions: _mx_cy.bint[961]
    _v_net_cf: _mx_cy.double[961]
    _has_net_cf: _mx_cy.bint[961]
    _v_check_pols_roll_fwd_resid: dict
    _v_check_pols_roll_fwd: object
    _has_check_pols_roll_fwd: _mx_cy.bint
    _v_check_truncation: object
    _has_check_truncation: _mx_cy.bint
    _v_result_cf: object
    _has_result_cf: _mx_cy.bint
    _v_result_pols: object
    _has_result_pols: _mx_cy.bint
    _v_bench_net_cf: _mx_cy.double
    _has_bench_net_cf: _mx_cy.bint
    
    data: _c_Data
    point_id: _mx_cy.longlong
    omega_age: _mx_cy.longlong
    mort_loading_o50: _mx_cy.double
    mort_loading_uw: _mx_cy.double
    mort_improvement: _mx_cy.double
    acc_share: _mx_cy.double
    suicide_share: _mx_cy.double
    suicide_mths: _mx_cy.longlong
    rpi_rate: _mx_cy.double
    esc_fixed_cover: _mx_cy.double
    esc_fixed_prem: _mx_cy.double
    esc_rpi_cover_cap: _mx_cy.double
    esc_rpi_prem_mult: _mx_cy.double
    esc_rpi_prem_cap: _mx_cy.double
    esc_take_up: _mx_cy.double
    lapse_crossover_beta: _mx_cy.double
    expense_acq_o50: _mx_cy.double
    expense_acq_uw: _mx_cy.double
    expense_maint_o50: _mx_cy.double
    expense_maint_uw: _mx_cy.double
    inflation_rate: _mx_cy.double
    comm_init_rate: _mx_cy.double
    pd: object

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
        self.omega_age = 120
        self.mort_loading_o50 = 1.2
        self.mort_loading_uw = 1.0
        self.mort_improvement = 0.0
        self.acc_share = 0.03
        self.suicide_share = 0.01
        self.suicide_mths = 12
        self.rpi_rate = 0.03
        self.esc_fixed_cover = 0.05
        self.esc_fixed_prem = 0.1
        self.esc_rpi_cover_cap = 0.1
        self.esc_rpi_prem_mult = 1.5
        self.esc_rpi_prem_cap = 0.15
        self.esc_take_up = 1.0
        self.lapse_crossover_beta = 0.0
        self.expense_acq_o50 = 150.0
        self.expense_acq_uw = 300.0
        self.expense_maint_o50 = 30.0
        self.expense_maint_uw = 50.0
        self.inflation_rate = 0.03
        self.comm_init_rate = 0.25
        self.pd = _mx_sys.import_module('pandas')

    @_mx_cy.ccall
    def _mx_copy_refs(self, base, base_root):
        
        base_: _c_Projection = _mx_cy.cast(_c_Projection, base)

        # Reference assignment
        self.data = self._parent.Data if base_.data._mx_is_in(base_root) else base_.data
        self.point_id = base_.point_id
        self.omega_age = base_.omega_age
        self.mort_loading_o50 = base_.mort_loading_o50
        self.mort_loading_uw = base_.mort_loading_uw
        self.mort_improvement = base_.mort_improvement
        self.acc_share = base_.acc_share
        self.suicide_share = base_.suicide_share
        self.suicide_mths = base_.suicide_mths
        self.rpi_rate = base_.rpi_rate
        self.esc_fixed_cover = base_.esc_fixed_cover
        self.esc_fixed_prem = base_.esc_fixed_prem
        self.esc_rpi_cover_cap = base_.esc_rpi_cover_cap
        self.esc_rpi_prem_mult = base_.esc_rpi_prem_mult
        self.esc_rpi_prem_cap = base_.esc_rpi_prem_cap
        self.esc_take_up = base_.esc_take_up
        self.lapse_crossover_beta = base_.lapse_crossover_beta
        self.expense_acq_o50 = base_.expense_acq_o50
        self.expense_acq_uw = base_.expense_acq_uw
        self.expense_maint_o50 = base_.expense_maint_o50
        self.expense_maint_uw = base_.expense_maint_uw
        self.inflation_rate = base_.inflation_rate
        self.comm_init_rate = base_.comm_init_rate
        self.pd = base_.pd

    @_mx_cy.cfunc
    def _f_model_point(self) -> object:
        """The selected model point as a Series."""
        return self.data.model_point_table().loc[self.point_id]                    # noqa: F821

    @_mx_cy.cfunc
    def _f_cell(self) -> str:
        """``O50`` (over-50s guaranteed acceptance) or ``UW`` (underwritten guaranteed).

        The two cells share this engine and not their mortality basis, their lapse table,
        their expense levels or their benefit rules.  See the Space docstring.
        """
        v = self.model_point()["cell"]
        if v not in ("O50", "UW"):
            raise ValueError("invalid cell")
        return v

    @_mx_cy.cfunc
    def _f_age_at_entry(self) -> _mx_cy.longlong:
        """The entry age of the selected model point, **age last birthday**.

        ALB rather than the age nearest birthday every other model in this library uses:
        the underwritten cell's specimen defines entry age x as "before the (x+1)th
        birthday", which is ALB, and the over-50s documents price on "age at outset" without
        stating a basis **[std]**.  All age lookups here are on that one basis.
        """
        return int(self.model_point()["entry_age"])

    @_mx_cy.cfunc
    def _f_sex(self) -> str:
        """The sex (M / F) of the selected model point.

        Carried for the basis lookup.  The over-50s documents state age and smoker status as
        the rate factors and do not rate by sex, so on that cell this drives the shipped
        **[std]** proxy table and nothing contractual.
        """
        return self.model_point()["sex"]

    @_mx_cy.cfunc
    def _f_smoker(self) -> str:
        """The smoker status (NS / S).

        The underwritten specimen distinguishes three smoking states; they are collapsed to
        two here **[std]**.
        """
        return self.model_point()["smoker"]

    @_mx_cy.cfunc
    def _f_sum_assured(self) -> _mx_cy.double:
        """SA: the sum assured or cash sum at outset.

        :func:`cover_pp` is the amount in force in a given month, which differs from this on
        the escalating variants.
        """
        return float(self.model_point()["sum_assured"])

    @_mx_cy.cfunc
    def _f_premium_mth(self) -> _mx_cy.double:
        """P: the monthly premium at outset, guaranteed never to increase.

        A model point input, not a rate-table lookup: no insurer publishes whole of life
        premium rate tables, so any shipped scale would be a **[std]** snapshot calibrated
        to the handful of public quote anchors.
        """
        return float(self.model_point()["premium_mth"])

    @_mx_cy.cfunc
    def _f_escalation(self) -> str:
        """``level``, ``fixed_5pct`` (the UW increasing-cover variant) or ``rpi``.

        The underwritten variant raises cover 5% and premium 10% a year - two percent of
        premium for each one percent of cover - and the over-50s RPI variant raises the cash
        sum by RPI capped at 10% and the premium by 1.5 x RPI capped at 15%.
        """
        v = self.model_point()["escalation"]
        if v not in ("level", "fixed_5pct", "rpi"):
            raise ValueError("invalid escalation")
        return v

    @_mx_cy.cfunc
    def _f_cessation_mths(self) -> _mx_cy.longlong:
        """T_cess: months from outset to premium cessation; 0 means premiums for life.

        The over-50s cells cease at the anniversary on or after the 90th birthday **[std]**
        and cover continues; the underwritten cell has no cessation at all.
        """
        return int(self.model_point()["cessation_months"])

    @_mx_cy.cfunc
    def _f_moratorium_mths(self) -> _mx_cy.longlong:
        """The over-50s moratorium in months, 12; zero on the underwritten cell.

        The underwritten cell has a suicide clause over the same window instead, which is a
        different rule with a different denominator - see :func:`benefit_pp`.
        """
        return int(self.model_point()["moratorium_months"])

    @_mx_cy.cfunc
    def _f_adb_multiplier(self) -> _mx_cy.double:
        """k_adb: the accidental death multiplier past the moratorium, 1 or 2.

        The 2 is one insurer's variant and applies to **accidental** death **on and after
        the first anniversary** only.  Inside the moratorium the accidental benefit is
        already the full cash sum, so doubling it there - or applying the multiplier to all
        deaths - overstates outgo.
        """
        return 2.0 if bool(self.model_point()["variant_adb_2x"]) else 1.0

    @_mx_cy.cfunc
    def _f_pu_variant(self) -> _mx_cy.bint:
        """Whether the pro-rata paid-up variant applies.

        Once half the expected payments have been made, a would-be lapse converts to a
        paid-up policy instead of forfeiting everything.  Requires a premium cessation date,
        since ``N_expected`` is measured to it; the underwritten cell has none, so the
        combination raises rather than dividing by zero.
        """
        v = bool(self.model_point()["variant_paid_up"])
        if v and self.cessation_mths() <= 0:
            raise ValueError("the pro-rata paid-up value needs a premium cessation date")
        return v

    @_mx_cy.cfunc
    def _f_pols_if_init(self) -> _mx_cy.double:
        """Initial number of policies in force; 1.0 on a single-policy model point."""
        return float(self.model_point()["pols_if_init"])

    @_mx_cy.cfunc
    def _f_proj_len(self) -> _mx_cy.longlong:
        """Projection length in months: ``12 x (omega_age - entry_age)``.

        Whole of life has no maturity date, so the horizon is a **limiting age** rather than
        a contractual one.  The shipped mortality tables reach 1 well before ``omega_age``,
        so the population is exhausted inside the projection rather than truncated by it;
        :func:`check_truncation` asserts that, because a limiting age set too low would
        silently drop liability off the end.
        """
        return 12 * (self.omega_age - self.age_at_entry())                         # noqa: F821

    @_mx_cy.cfunc
    def _f_duration(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """Completed policy years at the start of month t: ``(t - 1) // 12``."""
        return (t - 1) // 12

    @_mx_cy.cfunc
    def _f_duration_mth(self, t: object) -> object:
        """Months elapsed from outset at the end of month t; equal to t.

        ``t`` is 1-based, so the identity is trivial - the cells exists so the monthly
        models in this library share one vocabulary.
        """
        return t

    @_mx_cy.cfunc
    def _f_policy_year(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """y = floor((t-1)/12) + 1: the policy year containing month t; 1 for t = 1..12."""
        return self.duration(t) + 1

    @_mx_cy.cfunc
    def _f_age(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """a(t): the attained age (ALB) in the policy year containing month t."""
        return self.age_at_entry() + self.duration(t)

    @_mx_cy.cfunc
    def _f_mort_basis(self) -> str:
        """The mortality basis the cell takes: ``population`` for O50, ``assured`` for UW.

        Derived from :func:`cell` rather than left as a free parameter, because feeding
        either cell the other's basis produces plausible-looking but wrong margins.  See the
        Space docstring.
        """
        return "population" if self.cell() == "O50" else "assured"

    @_mx_cy.cfunc
    def _f_mort_loading(self) -> _mx_cy.double:
        """The anti-selection loading on the table rate: 120% for O50, 100% for UW **[std]**.

        Guaranteed acceptance removes underwriting, so the pool cannot be better than the
        population and self-selects worse.  No insurer discloses its guaranteed-acceptance
        pricing basis, so the loading is a placeholder to be calibrated - and a deliberately
        modest one, since population mortality is already heavier than insured experience.
        """
        return self.mort_loading_o50 if self.cell() == "O50" else self.mort_loading_uw  # noqa: F821

    @_mx_cy.cfunc
    def _f_mort_improve_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The mortality improvement factor in month t; 1 in the base run **[std]**.

        ``(1 - improvement)^(y - 1)``.  The market-standard expression is a CMI projections
        model with a chosen long-term rate, but that model is subscriber-restricted, so a
        flat annual improvement is the **[std]** sensitivity proxy.  Improvements lengthen
        exactly the part of the liability that is pure outgo - past the crossover and past
        premium cessation - so this is not a second-order dial on this product.
        """
        return (1.0 - self.mort_improvement) ** (self.policy_year(t) - 1)          # noqa: F821

    @_mx_cy.cfunc
    def _f_mort_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """q(y): the annual mortality rate applied in the policy year containing month t.

        The cell's table rate at the attained age, times the anti-selection loading and the
        improvement factor, capped at 1.  Both shipped bases are **[std]** proxies shaped
        like the tables the notes name and are not published tables.
        """
        q = float(self.data.mort_table().loc[                                 # noqa: F821
            (self.mort_basis(), self.sex(), self.smoker(), self.age(t)), "mort_rate"])
        return min(1.0, q * self.mort_loading() * self.mort_improve_factor(t))

    @_mx_cy.cfunc
    def _f_mort_rate_mth(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """q_m(y) = 1 - (1 - q)^(1/12): the monthly mortality rate **[std]**."""
        return 1.0 - (1.0 - self.mort_rate(t)) ** (1.0 / 12.0)

    @_mx_cy.cfunc
    def _f_esc_cover_step(self) -> _mx_cy.double:
        """The annual increase in the sum assured under the escalation variant.

        5% on the underwritten increasing-cover variant, and RPI floored at 0 and capped at
        10% on the over-50s RPI variant.  Scaled by ``esc_take_up``, which is 1 in the
        base run: holders may decline an increase, with three declines removing the option,
        but a deterministic run cannot represent a take-up probability, so full take-up is
        assumed and the decline rule is not implemented.
        """
        e = self.escalation()
        if e == "level":
            return 0.0
        if e == "fixed_5pct":
            return self.esc_fixed_cover * self.esc_take_up                         # noqa: F821
        return min(max(self.rpi_rate, 0.0), self.esc_rpi_cover_cap) * self.esc_take_up  # noqa: F821

    @_mx_cy.cfunc
    def _f_esc_prem_step(self) -> _mx_cy.double:
        """The annual increase in the premium under the escalation variant.

        10% on the underwritten variant - two percent of premium for each one percent of
        cover - and ``1.5 x RPI`` capped at 15% on the over-50s RPI variant.  Floored at 0:
        the source defines an increase only, with no decrease **[std]**.
        """
        e = self.escalation()
        if e == "level":
            return 0.0
        if e == "fixed_5pct":
            return self.esc_fixed_prem * self.esc_take_up                          # noqa: F821
        return min(max(self.esc_rpi_prem_mult * self.rpi_rate, 0.0),               # noqa: F821
                   self.esc_rpi_prem_cap) * self.esc_take_up                       # noqa: F821

    @_mx_cy.cfunc
    def _f_cover_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """SA(t): the sum assured or cash sum in force in month t.

        Steps at policy anniversaries.  On the RPI variant the cash sum **continues to
        index after premiums cease at 90**, which is why this carries no cessation test -
        the premium step, being applied to a zero premium, stops of its own accord.
        """
        return self.sum_assured() * (1.0 + self.esc_cover_step()) ** (self.policy_year(t) - 1)

    @_mx_cy.cfunc
    def _f_premium_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """P(t): the monthly premium due at the beginning of month t.

        Zero once the premium cessation month has passed, and zero on a paid-up policy -
        which is carried as a separate population strand rather than as a premium of zero,
        so it does not appear here.
        """
        if self.cessation_mths() > 0 and t > self.cessation_mths():
            return 0.0
        return self.premium_mth() * (1.0 + self.esc_prem_step()) ** (self.policy_year(t) - 1)

    @_mx_cy.cfunc
    def _f_prem_cum_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """CumPrem(t): cumulative premiums paid per policy to the end of month t.

        The premium falls at the beginning of the month and death at the end, so a death in
        month t has had the month-t premium paid on it - which is why the moratorium refund
        at ``t = 1`` is one month's premium and not nothing.  This is the **refund base**: a
        year-one non-accidental claim pays cumulative premiums paid, not the cash sum and
        not an annualized premium.
        """
        if t <= 0:
            return 0.0
        return self.prem_cum_pp(t - 1) + self.premium_pp(t)

    @_mx_cy.cfunc
    def _f_in_moratorium(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        """Whether month t falls inside the over-50s moratorium; always False on the UW cell."""
        return t <= self.moratorium_mths()

    @_mx_cy.cfunc
    def _f_payments_made(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        """N_paid(t): the number of monthly payments made by the end of month t."""
        if self.cessation_mths() <= 0:
            return t
        return min(t, self.cessation_mths())

    @_mx_cy.cfunc
    def _f_payments_expected(self) -> _mx_cy.longlong:
        """N_expected: the payments expected over the premium-paying period.

        The pro-rata paid-up denominator, so it is the cessation month; zero where premiums
        are payable for life, in which case the variant does not apply.
        """
        return self.cessation_mths()

    @_mx_cy.cfunc
    def _f_pu_eligible(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        """Whether a would-be lapse in month t converts to paid-up instead of terminating.

        The pro-rata paid-up rule: at least half the expected payments must have been made
        [S9].  Before that halfway point a lapse is a total loss and the base lapse rate
        applies; after it, forfeiture is strictly dominated, so **all** would-be lapses are
        assumed to convert **[std]**.
        """
        if not self.pu_variant():
            return False
        return self.payments_made(t) >= self.payments_expected() / 2.0

    @_mx_cy.cfunc
    def _f_crossover_mth(self) -> object:
        """t*: the first month in which cumulative premiums exceed the cover in force.

        ``floor(SA/P) + 1`` under level premiums - 167 months, thirteen years and eleven
        months, on the anchor cell, which is the FCA's stylised example exactly - but
        searched rather than closed-form so that an escalating variant still resolves.
        Returns 0 where the crossover never happens, which is the case whenever the cash sum
        exceeds the total premiums payable to cessation.

        Reported, not acted on: the crossover-aware lapse module that would raise lapse past
        the tipping point is a pure stress dial and is off in the base run.
        """
        last = self.cessation_mths() if self.cessation_mths() > 0 else self.proj_len()
        for t in range(1, last + 1):
            if self.prem_cum_pp(t) > self.cover_pp(t):
                return t
        return 0

    @_mx_cy.cfunc
    def _f_lapse_rate_base(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The table annual lapse rate in month t **[std]**, before the crossover stress.

        Read from the cell's own row of the lapse table; policy years beyond the table take
        its last row.  Both tables are drafting constructions - no public UK whole of life
        lapse study was retrieved - and on a product with no surrender value they are the
        single largest lever on the liability.
        """
        tbl = self.data.lapse_table().loc[self.cell()]                             # noqa: F821
        y = self.policy_year(t)
        return float(tbl.loc[min(y, int(tbl.index.max())), "lapse_rate"])

    @_mx_cy.cfunc
    def _f_lapse_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """w(y): the annual lapse rate applying at the end of month t.

        **Zero once premiums have ceased**: there is nothing left to stop paying, and
        applying a lapse decrement there silently destroys liability - the notes list it as
        a pitfall.  Otherwise the table rate, optionally stressed by
        ``1 + beta`` past the crossover, which is off in the base run.
        """
        if self.cessation_mths() > 0 and t > self.cessation_mths():
            return 0.0
        w = self.lapse_rate_base(t)
        if self.lapse_crossover_beta > 0.0 and self.prem_cum_pp(t) > self.cover_pp(t):  # noqa: F821
            w = w * (1.0 + self.lapse_crossover_beta)                         # noqa: F821
        return min(1.0, w)

    @_mx_cy.cfunc
    def _f_lapse_rate_mth(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """w_m(y) = 1 - (1 - w)^(1/12): the monthly lapse rate **[std]**."""
        return 1.0 - (1.0 - self.lapse_rate(t)) ** (1.0 / 12.0)

    @_mx_cy.cfunc
    def _f_pols_if(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """l(t-1): full-cover policies in force at the **start** of policy month t.

        The notes' in-force probability, and the column their worked-example table prints.
        Paid-up policies are **not** counted here: they are a separate strand,
        :func:`pols_pu`, because their benefit is a reduced amount.  On every model point
        without the pro-rata paid-up variant the two coincide with :func:`pols_all`.
        """
        if t < 1 or t > self.proj_len():
            return 0.0
        if t == 1:
            return self.pols_if_init()
        return (self.pols_if(t - 1) * (1.0 - self.mort_rate_mth(t - 1))
                * (1.0 - self.lapse_rate_mth(t - 1)))

    @_mx_cy.cfunc
    def _f_pols_pu(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Paid-up policies in force at the start of month t.

        Zero without the pro-rata paid-up variant.  Paid-up policies pay no premium, carry no
        lapse decrement and do not escalate, so they roll forward on mortality alone and take
        conversions in from the full-cover strand.
        """
        if t < 1 or t > self.proj_len() or not self.pu_variant():
            return 0.0
        if t == 1:
            return 0.0
        return self.pols_pu(t - 1) * (1.0 - self.mort_rate_mth(t - 1)) + self.pols_convert(t - 1)

    @_mx_cy.cfunc
    def _f_pu_benefit(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The aggregate paid-up cover in force at the start of month t.

        Carrying the aggregate benefit alongside the count is what removes the need for a
        per-conversion cohort dimension: the paid-up payout depends on when the policy
        converted, but every paid-up policy thereafter rolls forward on the same survival
        factor, so the sum of their payouts satisfies the same recursion as the count.
        Death outgo on the strand is then ``pu_benefit(t) x q_m(t)``.
        """
        if t < 1 or t > self.proj_len() or not self.pu_variant():
            return 0.0
        if t == 1:
            return 0.0
        return (self.pu_benefit(t - 1) * (1.0 - self.mort_rate_mth(t - 1))
                + self.pols_convert(t - 1) * self.benefit_pp(t - 1, "PAID_UP"))

    @_mx_cy.cfunc
    def _f_pols_all(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """All policies in force at the start of month t: full cover plus paid-up.

        The weight on the maintenance expense, and the count the roll-forward closes on.
        """
        return self.pols_if(t) + self.pols_pu(t)

    @_mx_cy.cfunc
    def _f_pols_if_at(self, t: _mx_cy.longlong, timing: str) -> _mx_cy.double:
        """The number of full-cover policies in force at a point inside month t.

        ``"BEF_DECR"``
            the start of the month, before any decrement; :func:`pols_if`.

        ``"BEF_LAPSE"``
            after deaths, before lapses - the notes' processing order is
            **death before lapse** **[std]**.

        ``"AFT_DECR"``
            the notes' ``l(t)``, the end-of-month count.
        """
        if timing == "BEF_DECR":
            return self.pols_if(t)
        if timing == "BEF_LAPSE":
            return self.pols_if(t) * (1.0 - self.mort_rate_mth(t))
        if timing == "AFT_DECR":
            if t < 1 or t >= self.proj_len():
                return 0.0
            return self.pols_if(t + 1)
        raise ValueError("invalid timing")

    @_mx_cy.cfunc
    def _f_pols_death(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Deaths on full cover at the end of month t, against the start-of-month in-force."""
        return self.pols_if(t) * self.mort_rate_mth(t)

    @_mx_cy.cfunc
    def _f_pols_death_pu(self, t: object) -> object:
        """Deaths on paid-up cover at the end of month t; zero without the pro-rata paid-up value."""
        return self.pols_pu(t) * self.mort_rate_mth(t)

    @_mx_cy.cfunc
    def _f_pols_exit(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Would-be lapses at the end of month t, taken from the survivors of mortality.

        What happens to them depends on :func:`pu_eligible`: they either terminate for
        nothing or convert to paid-up.
        """
        return self.pols_if_at(t, "BEF_LAPSE") * self.lapse_rate_mth(t)

    @_mx_cy.cfunc
    def _f_pols_convert(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Would-be lapses converted to paid-up at the end of month t.

        All of them once the pro-rata paid-up halfway point is passed **[std]**, none before
        it, and none at all without the variant.  A state change, not a cash flow.
        """
        return self.pols_exit(t) if self.pu_eligible(t) else 0.0

    @_mx_cy.cfunc
    def _f_pols_lapse(self, t: object) -> object:
        """Lapses that actually terminate the policy at the end of month t.

        **Pays nothing.** There is no surrender value at any duration on either cell, so
        this moves :func:`pols_if` and produces no cash flow whatever - which is the
        arithmetic meaning of a lapse-supported product.
        """
        return self.pols_exit(t) - self.pols_convert(t)

    @_mx_cy.cfunc
    def _f_pols_maturity(self, t: object) -> object:
        """Policies still in force when the projection is truncated at the limiting age.

        Not a maturity - whole of life has none - and not a benefit: it pays nothing.  It is
        the truncation residual, non-zero only in the last projected month, and it exists so
        that the roll-forward closes there.  :func:`check_truncation` asserts it is
        negligible, which is the substantive statement: a limiting age set too low would
        drop liability off the end of the projection instead.
        """
        if t != self.proj_len():
            return 0.0
        return (self.pols_all(t) - self.pols_death(t) - self.pols_death_pu(t) - self.pols_lapse(t))

    @_mx_cy.cfunc
    def _f_benefit_pp(self, t: _mx_cy.longlong, kind: str) -> _mx_cy.double:
        """The benefit amount per policy in month t, by kind.

        ``"NON_ACC"``
            the non-accidental death benefit.  On the O50 cell it is
            ``CumPrem(t)`` inside the moratorium and the cash sum after it; on
            the UW cell it is the sum assured, with the suicide refund handled
            under ``"DEATH"``.

        ``"ACC"``
            the accidental death benefit: the full cash sum from day one, and
            ``k_adb`` times it past the moratorium.  On the UW cell there is no
            accidental split, so this is the sum assured.

        ``"DEATH"``
            the expected benefit per death on the full-cover strand, blending the
            two above by the accidental share on O50, and the sum assured with
            the suicide refund by the suicide share inside the first twelve
            months on UW.  This is what :func:`claims` multiplies by.

        ``"PAID_UP"``
            the pro-rata paid-up payout for a policy converting in month t,
            ``SA x N_paid / N_expected``.  Zero without the variant.
        """
        if kind == "NON_ACC":
            if self.cell() == "O50" and self.in_moratorium(t):
                return self.prem_cum_pp(t)
            return self.cover_pp(t)
        if kind == "ACC":
            if self.cell() != "O50":
                return self.cover_pp(t)
            if self.in_moratorium(t):
                return self.cover_pp(t)
            return self.adb_multiplier() * self.cover_pp(t)
        if kind == "DEATH":
            if self.cell() == "O50":
                return ((1.0 - self.acc_share) * self.benefit_pp(t, "NON_ACC")     # noqa: F821
                        + self.acc_share * self.benefit_pp(t, "ACC"))              # noqa: F821
            if t <= self.suicide_mths:                                        # noqa: F821
                return ((1.0 - self.suicide_share) * self.cover_pp(t)              # noqa: F821
                        + self.suicide_share * self.prem_cum_pp(t))                # noqa: F821
            return self.cover_pp(t)
        if kind == "PAID_UP":
            if not self.pu_variant():
                return 0.0
            return self.cover_pp(t) * self.payments_made(t) / self.payments_expected()
        raise ValueError("invalid kind")

    @_mx_cy.cfunc
    def _f_premiums(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """E[premium](t): premium income at the beginning of month t, an inflow.

        Carried on the full-cover strand only: paid-up policies pay nothing, and neither do
        over-50s policies past cessation, where :func:`premium_pp` is already zero.
        """
        return self.premium_pp(t) * self.pols_if(t)

    @_mx_cy.cfunc
    def _f_claims(self, t: _mx_cy.longlong, kind: object=None) -> _mx_cy.double:
        """Death outgo in month t, by kind; the total when kind is omitted.

        ``"DEATH"``
            outgo on the full-cover strand, ``deaths x benefit_pp(t, "DEATH")``.

        ``"DEATH_PU"``
            outgo on the paid-up strand, ``pu_benefit(t) x q_m(t)`` - the
            aggregate paid-up cover times the monthly mortality rate, which is
            why the strand carries a benefit total as well as a count.

        ``"LAPSE"``
            zero, always.  There is no surrender value at any time on either
            cell; the kind exists so the zero is stated rather than inferred.
        """
        if kind is None:
            return sum(self.claims(t, k) for k in ("DEATH", "DEATH_PU", "LAPSE"))
        if kind == "DEATH":
            return self.pols_death(t) * self.benefit_pp(t, "DEATH")
        if kind == "DEATH_PU":
            return self.pu_benefit(t) * self.mort_rate_mth(t)
        if kind == "LAPSE":
            return 0.0
        raise ValueError("invalid kind")

    @_mx_cy.cfunc
    def _f_expense_acq_pp(self) -> _mx_cy.double:
        """The acquisition expense per policy at issue **[std]**: £150 on O50, £300 on UW."""
        return self.expense_acq_o50 if self.cell() == "O50" else self.expense_acq_uw    # noqa: F821

    @_mx_cy.cfunc
    def _f_expense_maint_pp(self) -> _mx_cy.double:
        """The annual maintenance expense per policy **[std]**: £30 on O50, £50 on UW.

        Premiums are level and small - £30 a month on the anchor cell - while this inflates,
        so the expense margin erodes mechanically over a twenty-year-plus horizon.  A
        per-policy expense error compounds accordingly.
        """
        return self.expense_maint_o50 if self.cell() == "O50" else self.expense_maint_uw  # noqa: F821

    @_mx_cy.cfunc
    def _f_inflation_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """The expense inflation factor in month t: ``(1 + pi)^(y - 1)`` **[std]**.

        Steps on policy anniversaries, not monthly, which is how the notes write it.
        """
        return (1.0 + self.inflation_rate) ** (self.policy_year(t) - 1)            # noqa: F821

    @_mx_cy.cfunc
    def _f_expenses(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Acquisition and maintenance expense in month t **[std]**.

        The acquisition charge falls once, at issue.  Maintenance is carried on
        :func:`pols_all`, so a paid-up policy still costs money to administer even though it
        pays no premium - which is part of why the pro-rata paid-up variant is expensive.
        """
        acq = self.expense_acq_pp() * self.pols_if(t) if t == 1 else 0.0
        return acq + self.expense_maint_pp() / 12.0 * self.inflation_factor(t) * self.pols_all(t)

    @_mx_cy.cfunc
    def _f_commissions(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """Initial commission in month t **[std]**: a share of the first year's premiums.

        The existence of commission is sourced - an intermediary is "paid by commission as a
        percentage of total annual premium" - and the level is a standardization.
        """
        if self.policy_year(t) > 1:
            return 0.0
        return self.comm_init_rate * self.premiums(t)                              # noqa: F821

    @_mx_cy.cfunc
    def _f_net_cf(self, t: _mx_cy.longlong) -> _mx_cy.double:
        """CF(t): the net cash flow of month t, **income positive**.

        Premiums less death outgo, expenses and commission.  The notes' own sign and the
        library-wide one, so there is no outgo-positive ``liability_cf`` companion.

        Note that the notes' worked-example table prints premium income and death outgo as
        separate positive columns and omits expenses "for clarity", so ``net_cf`` will not
        equal any column of that table.  Lapse contributes nothing at all: it moves
        :func:`pols_if` and pays no cash.
        """
        return self.premiums(t) - self.claims(t) - self.expenses(t) - self.commissions(t)

    @_mx_cy.cfunc
    def _f_check_pols_roll_fwd_resid(self, t: object) -> object:
        """The in-force roll-forward residual in month t; zero everywhere.

        ``pols_all(t) - pols_all(t+1)`` less deaths from both strands, lapses that actually
        terminate, and the truncation residual in the last month.  Conversions to paid-up
        are absent because they move policies *between* strands rather than out of the
        population - which is the point of running the check on the total.
        """
        return (self.pols_all(t) - self.pols_all(t + 1)
                - self.pols_death(t) - self.pols_death_pu(t) - self.pols_lapse(t)
                - self.pols_maturity(t))

    @_mx_cy.cfunc
    def _f_check_pols_roll_fwd(self) -> object:
        """True when the in-force roll-forward closes in every projected month.

        The library-wide form of a roll-forward check: no argument, one bool over all t, so
        one test can call it across every model.  :func:`check_pols_roll_fwd_resid` gives
        the signed residual of the month that failed.  The tolerance scales with
        ``pols_if_init()``, since the residual accumulates rounding on that many policies.
        """
        return all(abs(self.check_pols_roll_fwd_resid(t)) <= 1e-10 * max(self.pols_if_init(), 1.0)
                   for t in range(1, self.proj_len() + 1))

    @_mx_cy.cfunc
    def _f_check_truncation(self) -> object:
        """True when the population left at the limiting age is negligible.

        Whole of life has no maturity date, so the projection ends at a limiting age rather
        than at a contractual one, and anything still in force there is liability dropped
        off the end.  The shipped mortality tables reach 1 well before ``omega_age``, so the
        residual should be vanishing; if it is not, the limiting age is too low and the
        model is understating the tail rather than merely rounding it.
        """
        return self.pols_maturity(self.proj_len()) <= 1e-9 * max(self.pols_if_init(), 1.0)

    @_mx_cy.cfunc
    def _f_result_cf(self) -> object:
        """Result table of cashflows, indexed by policy month t.

        ``pols_if`` is the full-cover count at the start of the month, which is the weight
        on premium income and on full-cover death outgo; ``pols_pu`` is the paid-up strand,
        empty on every model point without the pro-rata paid-up variant.  ``claims_lapse`` is
        a column of zeros by product design - there is no surrender value - and is published
        rather than dropped.
        """
        ts = list(range(1, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "pols_if": [self.pols_if(t) for t in ts],
                "pols_pu": [self.pols_pu(t) for t in ts],
                "premiums": [self.premiums(t) for t in ts],
                "claims_death": [self.claims(t, "DEATH") for t in ts],
                "claims_death_pu": [self.claims(t, "DEATH_PU") for t in ts],
                "claims_lapse": [self.claims(t, "LAPSE") for t in ts],
                "expenses": [self.expenses(t) for t in ts],
                "commissions": [self.commissions(t) for t in ts],
                "net_cf": [self.net_cf(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    @_mx_cy.cfunc
    def _f_result_pols(self) -> object:
        """Result table of policy counts, benefits and rates, indexed by policy month t."""
        ts = list(range(1, self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "pols_if": [self.pols_if(t) for t in ts],
                "pols_pu": [self.pols_pu(t) for t in ts],
                "pols_death": [self.pols_death(t) for t in ts],
                "pols_lapse": [self.pols_lapse(t) for t in ts],
                "pols_convert": [self.pols_convert(t) for t in ts],
                "prem_cum_pp": [self.prem_cum_pp(t) for t in ts],
                "cover_pp": [self.cover_pp(t) for t in ts],
                "benefit_death_pp": [self.benefit_pp(t, "DEATH") for t in ts],
                "mort_rate": [self.mort_rate(t) for t in ts],
                "lapse_rate": [self.lapse_rate(t) for t in ts],
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
    def cell(self) -> str:
        if self._has_cell:
            return self._v_cell
        else:
            val = self._v_cell = self._f_cell()
            self._has_cell = True
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
    def smoker(self) -> str:
        if self._has_smoker:
            return self._v_smoker
        else:
            val = self._v_smoker = self._f_smoker()
            self._has_smoker = True
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
    def premium_mth(self) -> _mx_cy.double:
        if self._has_premium_mth:
            return self._v_premium_mth
        else:
            val = self._v_premium_mth = self._f_premium_mth()
            self._has_premium_mth = True
            return val

    @_mx_cy.ccall
    def escalation(self) -> str:
        if self._has_escalation:
            return self._v_escalation
        else:
            val = self._v_escalation = self._f_escalation()
            self._has_escalation = True
            return val

    @_mx_cy.ccall
    def cessation_mths(self) -> _mx_cy.longlong:
        if self._has_cessation_mths:
            return self._v_cessation_mths
        else:
            val = self._v_cessation_mths = self._f_cessation_mths()
            self._has_cessation_mths = True
            return val

    @_mx_cy.ccall
    def moratorium_mths(self) -> _mx_cy.longlong:
        if self._has_moratorium_mths:
            return self._v_moratorium_mths
        else:
            val = self._v_moratorium_mths = self._f_moratorium_mths()
            self._has_moratorium_mths = True
            return val

    @_mx_cy.ccall
    def adb_multiplier(self) -> _mx_cy.double:
        if self._has_adb_multiplier:
            return self._v_adb_multiplier
        else:
            val = self._v_adb_multiplier = self._f_adb_multiplier()
            self._has_adb_multiplier = True
            return val

    @_mx_cy.ccall
    def pu_variant(self) -> _mx_cy.bint:
        if self._has_pu_variant:
            return self._v_pu_variant
        else:
            val = self._v_pu_variant = self._f_pu_variant()
            self._has_pu_variant = True
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
    def proj_len(self) -> _mx_cy.longlong:
        if self._has_proj_len:
            return self._v_proj_len
        else:
            val = self._v_proj_len = self._f_proj_len()
            self._has_proj_len = True
            return val

    @_mx_cy.ccall
    def duration(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 961):
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
    def duration_mth(self, t: object) -> object:
        if self._v_duration_mth is None:
            self._v_duration_mth = {}
        if t in self._v_duration_mth:
            return self._v_duration_mth[t]
        else:
            val = self._f_duration_mth(t)
            self._v_duration_mth[t] = val
            return val

    @_mx_cy.ccall
    def policy_year(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 961):
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
        if (0 <= t < 961):
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
    def mort_basis(self) -> str:
        if self._has_mort_basis:
            return self._v_mort_basis
        else:
            val = self._v_mort_basis = self._f_mort_basis()
            self._has_mort_basis = True
            return val

    @_mx_cy.ccall
    def mort_loading(self) -> _mx_cy.double:
        if self._has_mort_loading:
            return self._v_mort_loading
        else:
            val = self._v_mort_loading = self._f_mort_loading()
            self._has_mort_loading = True
            return val

    @_mx_cy.ccall
    def mort_improve_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
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
        if (0 <= t < 961):
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
        if (0 <= t < 961):
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
    def esc_cover_step(self) -> _mx_cy.double:
        if self._has_esc_cover_step:
            return self._v_esc_cover_step
        else:
            val = self._v_esc_cover_step = self._f_esc_cover_step()
            self._has_esc_cover_step = True
            return val

    @_mx_cy.ccall
    def esc_prem_step(self) -> _mx_cy.double:
        if self._has_esc_prem_step:
            return self._v_esc_prem_step
        else:
            val = self._v_esc_prem_step = self._f_esc_prem_step()
            self._has_esc_prem_step = True
            return val

    @_mx_cy.ccall
    def cover_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
            if self._has_cover_pp[t]:
                return self._v_cover_pp[t]
            else:
                val = self._f_cover_pp(t)
                self._v_cover_pp[t] = val
                self._has_cover_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def premium_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
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
    def prem_cum_pp(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
            if self._has_prem_cum_pp[t]:
                return self._v_prem_cum_pp[t]
            else:
                val = self._f_prem_cum_pp(t)
                self._v_prem_cum_pp[t] = val
                self._has_prem_cum_pp[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def in_moratorium(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        if (0 <= t < 961):
            if self._has_in_moratorium[t]:
                return self._v_in_moratorium[t]
            else:
                val = self._f_in_moratorium(t)
                self._v_in_moratorium[t] = val
                self._has_in_moratorium[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def payments_made(self, t: _mx_cy.longlong) -> _mx_cy.longlong:
        if (0 <= t < 961):
            if self._has_payments_made[t]:
                return self._v_payments_made[t]
            else:
                val = self._f_payments_made(t)
                self._v_payments_made[t] = val
                self._has_payments_made[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def payments_expected(self) -> _mx_cy.longlong:
        if self._has_payments_expected:
            return self._v_payments_expected
        else:
            val = self._v_payments_expected = self._f_payments_expected()
            self._has_payments_expected = True
            return val

    @_mx_cy.ccall
    def pu_eligible(self, t: _mx_cy.longlong) -> _mx_cy.bint:
        if (0 <= t < 961):
            if self._has_pu_eligible[t]:
                return self._v_pu_eligible[t]
            else:
                val = self._f_pu_eligible(t)
                self._v_pu_eligible[t] = val
                self._has_pu_eligible[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def crossover_mth(self) -> object:
        if self._has_crossover_mth:
            return self._v_crossover_mth
        else:
            val = self._v_crossover_mth = self._f_crossover_mth()
            self._has_crossover_mth = True
            return val

    @_mx_cy.ccall
    def lapse_rate_base(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
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
    def lapse_rate(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
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
        if (0 <= t < 961):
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
        if (0 <= t < 961):
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
    def pols_pu(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
            if self._has_pols_pu[t]:
                return self._v_pols_pu[t]
            else:
                val = self._f_pols_pu(t)
                self._v_pols_pu[t] = val
                self._has_pols_pu[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pu_benefit(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
            if self._has_pu_benefit[t]:
                return self._v_pu_benefit[t]
            else:
                val = self._f_pu_benefit(t)
                self._v_pu_benefit[t] = val
                self._has_pu_benefit[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_all(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
            if self._has_pols_all[t]:
                return self._v_pols_all[t]
            else:
                val = self._f_pols_all(t)
                self._v_pols_all[t] = val
                self._has_pols_all[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_if_at(self, t: _mx_cy.longlong, timing: str) -> _mx_cy.double:
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
        if (0 <= t < 961):
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
    def pols_death_pu(self, t: object) -> object:
        if self._v_pols_death_pu is None:
            self._v_pols_death_pu = {}
        if t in self._v_pols_death_pu:
            return self._v_pols_death_pu[t]
        else:
            val = self._f_pols_death_pu(t)
            self._v_pols_death_pu[t] = val
            return val

    @_mx_cy.ccall
    def pols_exit(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
            if self._has_pols_exit[t]:
                return self._v_pols_exit[t]
            else:
                val = self._f_pols_exit(t)
                self._v_pols_exit[t] = val
                self._has_pols_exit[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_convert(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
            if self._has_pols_convert[t]:
                return self._v_pols_convert[t]
            else:
                val = self._f_pols_convert(t)
                self._v_pols_convert[t] = val
                self._has_pols_convert[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def pols_lapse(self, t: object) -> object:
        if self._v_pols_lapse is None:
            self._v_pols_lapse = {}
        if t in self._v_pols_lapse:
            return self._v_pols_lapse[t]
        else:
            val = self._f_pols_lapse(t)
            self._v_pols_lapse[t] = val
            return val

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
    def benefit_pp(self, t: _mx_cy.longlong, kind: str) -> _mx_cy.double:
        if self._v_benefit_pp is None:
            self._v_benefit_pp = {}
        if (t, kind) in self._v_benefit_pp:
            return self._v_benefit_pp[(t, kind)]
        else:
            val = self._f_benefit_pp(t, kind)
            self._v_benefit_pp[(t, kind)] = val
            return val

    @_mx_cy.ccall
    def premiums(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
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
    def expense_acq_pp(self) -> _mx_cy.double:
        if self._has_expense_acq_pp:
            return self._v_expense_acq_pp
        else:
            val = self._v_expense_acq_pp = self._f_expense_acq_pp()
            self._has_expense_acq_pp = True
            return val

    @_mx_cy.ccall
    def expense_maint_pp(self) -> _mx_cy.double:
        if self._has_expense_maint_pp:
            return self._v_expense_maint_pp
        else:
            val = self._v_expense_maint_pp = self._f_expense_maint_pp()
            self._has_expense_maint_pp = True
            return val

    @_mx_cy.ccall
    def inflation_factor(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
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
        if (0 <= t < 961):
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
    def commissions(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
            if self._has_commissions[t]:
                return self._v_commissions[t]
            else:
                val = self._f_commissions(t)
                self._v_commissions[t] = val
                self._has_commissions[t] = True
                return val
        else:
            raise IndexError("array index out of range")

    @_mx_cy.ccall
    def net_cf(self, t: _mx_cy.longlong) -> _mx_cy.double:
        if (0 <= t < 961):
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
    def check_pols_roll_fwd_resid(self, t: object) -> object:
        if self._v_check_pols_roll_fwd_resid is None:
            self._v_check_pols_roll_fwd_resid = {}
        if t in self._v_check_pols_roll_fwd_resid:
            return self._v_check_pols_roll_fwd_resid[t]
        else:
            val = self._f_check_pols_roll_fwd_resid(t)
            self._v_check_pols_roll_fwd_resid[t] = val
            return val

    @_mx_cy.ccall
    def check_pols_roll_fwd(self) -> object:
        if self._has_check_pols_roll_fwd:
            return self._v_check_pols_roll_fwd
        else:
            val = self._v_check_pols_roll_fwd = self._f_check_pols_roll_fwd()
            self._has_check_pols_roll_fwd = True
            return val

    @_mx_cy.ccall
    def check_truncation(self) -> object:
        if self._has_check_truncation:
            return self._v_check_truncation
        else:
            val = self._v_check_truncation = self._f_check_truncation()
            self._has_check_truncation = True
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


