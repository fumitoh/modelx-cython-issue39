from . import _mx_sys



_v_cells_names_Data = [
    'input_dir',
    'model_point_table',
    'mort_table',
    'select_factor_table',
    'lapse_table',
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
        self._v_select_factor_table = None
        self._has_select_factor_table = False
        self._v_lapse_table = None
        self._has_lapse_table = False

    def _mx_assign_refs(self, io_data, pickle_data):

        # Reference assignment
        self.model_point_file = 'model_point_table.csv'
        self.mort_table_file = 'mort_table.csv'
        self.select_factor_file = 'select_factor_table.csv'
        self.lapse_table_file = 'lapse_table.csv'
        self.pd = _mx_sys.import_module('pandas')

    def _mx_copy_refs(self, base, base_root):

        # Reference assignment
        self.model_point_file = base.model_point_file
        self.mort_table_file = base.mort_table_file
        self.select_factor_file = base.select_factor_file
        self.lapse_table_file = base.lapse_table_file
        self.pd = base.pd

    def _f_input_dir(self):
        """The directory holding the input CSVs: the model folder's parent.

        Inputs are *external* files, not data stored inside the model, so the model
        folder is pure formulas.  The path is resolved at run time from where the model
        was read, following ``annuallife.TradLife_A``.
        """
        return self._model.path.parent                                        # noqa: F821

    def _f_model_point_table(self):
        """The model point table, read from *model_point_table.csv*."""
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.model_point_file, index_col="point_id")        # noqa: F821

    def _f_mort_table(self):
        """The mortality rates by sex, smoker status and age, from *mort_table.csv*.

        Read as the applied best-estimate rate on the ``applied`` mortality basis and as
        the ultimate rate on the ``select`` basis; see ``Projection.mort_basis``.
        """
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.mort_table_file,                               # noqa: F821
            index_col=["sex", "smoker", "age"])

    def _f_select_factor_table(self):
        """The select-duration factors, read from *select_factor_table.csv*."""
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.select_factor_file, index_col="duration")      # noqa: F821

    def _f_lapse_table(self):
        """The lapse rates by policy year, read from *lapse_table.csv*."""
        return self.pd.read_csv(                                              # noqa: F821
            self.input_dir() / self.lapse_table_file, index_col="policy_year")     # noqa: F821


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

    def select_factor_table(self):
        if self._has_select_factor_table:
            return self._v_select_factor_table
        else:
            val = self._v_select_factor_table = self._f_select_factor_table()
            self._has_select_factor_table = True
            return val

    def lapse_table(self):
        if self._has_lapse_table:
            return self._v_lapse_table
        else:
            val = self._v_lapse_table = self._f_lapse_table()
            self._has_lapse_table = True
            return val










_v_cells_names_Projection = [
    'model_point',
    'shape',
    'is_joint',
    'age_at_entry',
    'sex',
    'smoker',
    'policy_term',
    'sum_assured',
    'fib_income',
    'sched_rate',
    'indexation',
    'wop',
    'premium_mth_pp',
    'premium_mode',
    'mort_basis',
    'pols_if_init',
    'duration_inforce',
    'fib_commute_rate',
    'proj_start',
    'proj_len',
    'term_mths',
    'duration',
    'age',
    'select_factor',
    'mort_rate_base',
    'mort_rate_life',
    'mort_rate',
    'lapse_cum',
    'sel_lapse_factor',
    'lapse_rate_base',
    'rebroke_factor',
    'lapse_rate',
    'pols_if',
    'pols_if_at',
    'pols_death',
    'pols_lapse',
    'pols_maturity',
    'wop_waived_frac',
    'pols_payer',
    'idx_increase',
    'idx_factor',
    'idx_prem_factor',
    'premium_pp',
    'premiums',
    'sched_rate_mth',
    'benefit_sched',
    'annuity_certain_factor',
    'fib_commute_pp',
    'benefit_pp',
    'fib_cum',
    'claims',
    'claim_expenses',
    'inflation_factor',
    'expenses',
    'comm_init_pp',
    'comm_clawback',
    'commissions',
    'net_cf',
    'check_pols_roll_fwd_resid',
    'check_pols_roll_fwd',
    'check_fib_ledger_resid',
    'check_fib_ledger',
    'result_cf',
    'result_pols',
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
        self._v_shape = None
        self._has_shape = False
        self._v_is_joint = None
        self._has_is_joint = False
        self._v_age_at_entry = {}
        self._v_sex = {}
        self._v_smoker = {}
        self._v_policy_term = None
        self._has_policy_term = False
        self._v_sum_assured = None
        self._has_sum_assured = False
        self._v_fib_income = None
        self._has_fib_income = False
        self._v_sched_rate = None
        self._has_sched_rate = False
        self._v_indexation = None
        self._has_indexation = False
        self._v_wop = None
        self._has_wop = False
        self._v_premium_mth_pp = None
        self._has_premium_mth_pp = False
        self._v_premium_mode = None
        self._has_premium_mode = False
        self._v_mort_basis = None
        self._has_mort_basis = False
        self._v_pols_if_init = None
        self._has_pols_if_init = False
        self._v_duration_inforce = None
        self._has_duration_inforce = False
        self._v_fib_commute_rate = None
        self._has_fib_commute_rate = False
        self._v_proj_start = None
        self._has_proj_start = False
        self._v_proj_len = None
        self._has_proj_len = False
        self._v_term_mths = None
        self._has_term_mths = False
        self._v_duration = {}
        self._v_age = {}
        self._v_select_factor = {}
        self._v_mort_rate_base = {}
        self._v_mort_rate_life = {}
        self._v_mort_rate = {}
        self._v_lapse_cum = {}
        self._v_sel_lapse_factor = {}
        self._v_lapse_rate_base = {}
        self._v_rebroke_factor = {}
        self._v_lapse_rate = {}
        self._v_pols_if = {}
        self._v_pols_if_at = {}
        self._v_pols_death = {}
        self._v_pols_lapse = {}
        self._v_pols_maturity = {}
        self._v_wop_waived_frac = {}
        self._v_pols_payer = {}
        self._v_idx_increase = None
        self._has_idx_increase = False
        self._v_idx_factor = {}
        self._v_idx_prem_factor = {}
        self._v_premium_pp = {}
        self._v_premiums = {}
        self._v_sched_rate_mth = None
        self._has_sched_rate_mth = False
        self._v_benefit_sched = {}
        self._v_annuity_certain_factor = {}
        self._v_fib_commute_pp = {}
        self._v_benefit_pp = {}
        self._v_fib_cum = {}
        self._v_claims = {}
        self._v_claim_expenses = {}
        self._v_inflation_factor = {}
        self._v_expenses = {}
        self._v_comm_init_pp = None
        self._has_comm_init_pp = False
        self._v_comm_clawback = {}
        self._v_commissions = {}
        self._v_net_cf = {}
        self._v_check_pols_roll_fwd_resid = {}
        self._v_check_pols_roll_fwd = None
        self._has_check_pols_roll_fwd = False
        self._v_check_fib_ledger_resid = {}
        self._v_check_fib_ledger = None
        self._has_check_fib_ledger = False
        self._v_result_cf = None
        self._has_result_cf = False
        self._v_result_pols = None
        self._has_result_pols = False
        self._v_bench_net_cf = None
        self._has_bench_net_cf = False

    def _mx_assign_refs(self, io_data, pickle_data):

        # Reference assignment
        self.data = self._parent.Data
        self.point_id = 1
        self.select_period = 5
        self.mort_scale = 0.75
        self.sel_lapse_lambda = 0.0
        self.sel_lapse_ref = 0.2
        self.premium_market_ratio = 1.0
        self.rebroke_cap = 2.0
        self.rpi_rate = 0.03
        self.idx_cover_cap = 0.1
        self.idx_prem_mult = 1.5
        self.idx_prem_cap = 0.15
        self.idx_accept_rate = 1.0
        self.expense_acq = 150.0
        self.expense_maint = 30.0
        self.expense_claim = 250.0
        self.inflation_rate = 0.03
        self.comm_init_rate = 1.5
        self.comm_renewal_rate = 0.025
        self.clawback_mths = 0
        self.fib_commute_disc_rate = 0.03
        self.wop_inc_rate = 0.004
        self.wop_rec_rate = 0.35
        self.wop_prem_loading = 0.05
        self.pd = _mx_sys.import_module('pandas')

    def _mx_copy_refs(self, base, base_root):

        # Reference assignment
        self.data = self._parent.Data if base.data._mx_is_in(base_root) else base.data
        self.point_id = base.point_id
        self.select_period = base.select_period
        self.mort_scale = base.mort_scale
        self.sel_lapse_lambda = base.sel_lapse_lambda
        self.sel_lapse_ref = base.sel_lapse_ref
        self.premium_market_ratio = base.premium_market_ratio
        self.rebroke_cap = base.rebroke_cap
        self.rpi_rate = base.rpi_rate
        self.idx_cover_cap = base.idx_cover_cap
        self.idx_prem_mult = base.idx_prem_mult
        self.idx_prem_cap = base.idx_prem_cap
        self.idx_accept_rate = base.idx_accept_rate
        self.expense_acq = base.expense_acq
        self.expense_maint = base.expense_maint
        self.expense_claim = base.expense_claim
        self.inflation_rate = base.inflation_rate
        self.comm_init_rate = base.comm_init_rate
        self.comm_renewal_rate = base.comm_renewal_rate
        self.clawback_mths = base.clawback_mths
        self.fib_commute_disc_rate = base.fib_commute_disc_rate
        self.wop_inc_rate = base.wop_inc_rate
        self.wop_rec_rate = base.wop_rec_rate
        self.wop_prem_loading = base.wop_prem_loading
        self.pd = base.pd

    def _f_model_point(self):
        """The selected model point as a Series."""
        return self.data.model_point_table().loc[self.point_id]                    # noqa: F821

    def _f_shape(self):
        """The benefit shape: ``level``, ``decreasing`` or ``fib`` [S1][S2][S6][S8]."""
        v = self.model_point()["shape"]
        if v not in ("level", "decreasing", "fib"):
            raise ValueError("invalid shape")
        return v

    def _f_is_joint(self):
        """True when the policy covers two lives on a first-death basis.

        The policy pays once and ends; separation and replacement options create *new*
        policies and are out of scope **[std scope]**.
        """
        return bool(self.model_point()["joint_first_death"])

    def _f_age_at_entry(self, life=1):
        """x: the issue age (ANB) of the first (``life = 1``) or second life.

        Age nearest birthday at entry, plus a curtate policy year **[std]**: the fetched
        product documents state no age basis, and the UK assured lives tables are select
        tables indexed that way.
        """
        if life == 1:
            return int(self.model_point()["age_at_entry"])
        if life == 2 and self.is_joint():
            return int(self.model_point()["joint_age"])
        raise ValueError("invalid life")

    def _f_sex(self, life=1):
        """The sex (M / F) of the first or second life."""
        if life == 1:
            return self.model_point()["sex"]
        if life == 2 and self.is_joint():
            return self.model_point()["joint_sex"]
        raise ValueError("invalid life")

    def _f_smoker(self, life=1):
        """The smoker status (N / S) of the first or second life."""
        if life == 1:
            return self.model_point()["smoker"]
        if life == 2 and self.is_joint():
            return self.model_point()["joint_smoker"]
        raise ValueError("invalid life")

    def _f_policy_term(self):
        """n: the term in years; 1-50 level, 5-50 decreasing, 5-40 FIB [S1][S6][S8]."""
        return int(self.model_point()["policy_term"])

    def _f_sum_assured(self):
        """SA0: the initial sum assured of the level and decreasing shapes [S1][S6]."""
        return float(self.model_point()["sum_assured"])

    def _f_fib_income(self):
        """I: the family income benefit, per month, on the ``fib`` shape [S2][S6][S8]."""
        return float(self.model_point()["fib_income"])

    def _f_sched_rate(self):
        """j: the decreasing shape's schedule rate p.a. **[std]**, 6% on the shipped points.

        Contractual, not experience: the client selects it at outset and the benefit
        amortizes at it whatever happens to interest rates [S1][S6][S8].  The risk it
        carries is therefore specification error - mis-implementing the amortization or the
        monthly convention - rather than assumption error.
        """
        return float(self.model_point()["sched_rate"])

    def _f_indexation(self):
        """Whether the RPI indexation option is elected [S1][S2][S6][S7].

        Restricted to the level shape **[std scope]**: no fetched insurer offers indexed
        decreasing cover, and the notes do not combine indexation with the FIB schedule
        either.
        """
        v = bool(self.model_point()["indexation"])
        if v and self.shape() != "level":
            raise ValueError("indexation is modelled on the level shape only")
        return v

    def _f_wop(self):
        """Whether the waiver of premium rider is in force [S1]; false in the base run."""
        return bool(self.model_point()["wop"])

    def _f_premium_mth_pp(self):
        """P_m: the guaranteed monthly premium per policy **[std]**.

        A pure modelling value.  No UK insurer publishes premium rate tables - pricing is
        quote-driven and only the £5/month minimum is public [S5] - so any reference
        premium basis is constructed rather than observed.  It is guaranteed level for the
        full term [S2][S6][S9], which is what puts every year of premium inside the
        Solvency UK contract boundary [R3].
        """
        return float(self.model_point()["premium_mth"])

    def _f_premium_mode(self):
        """Monthly or annual premium payment.

        Inert on the annual grid, which annualizes either way: ``P_a = 12 P_m``.  It is
        carried because the notes' monthly-grid variant distinguishes them, and that
        variant is not implemented.
        """
        return self.model_point()["premium_mode"]

    def _f_mort_basis(self):
        """Whether the mortality table is read as the *applied* rate or as an *ultimate* one.

        *applied* **[std]** takes ``mort_table.csv`` as the rate actually applied, which is
        how the notes quote their illustrative worked-example vector; *select* multiplies
        it by :func:`select_factor` and by ``mort_scale``, the notes' proxy for the
        unavailable subscriber tables.  See the Space docstring for why both are shipped.
        """
        v = self.model_point()["mort_basis"]
        if v not in ("applied", "select"):
            raise ValueError("invalid mort_basis")
        return v

    def _f_pols_if_init(self):
        """Initial number of policies in force; 1.0 on a single-policy model point."""
        return float(self.model_point()["pols_if_init"])

    def _f_duration_inforce(self):
        """Completed policy years already elapsed when the projection starts; 0 at issue."""
        return int(self.model_point()["duration_inforce"])

    def _f_fib_commute_rate(self):
        """The proportion of FIB claims commuted to a lump sum **[std]**; 0 in the base run.

        The insurer may replace the remaining instalments with a lump sum determined
        "fairly and reasonably" [S6][S8]; no insurer publishes the basis, so both the
        take-up and the discount rate ``fib_commute_disc_rate`` are standardizations.
        """
        return float(self.model_point()["fib_commute_rate"])

    def _f_proj_start(self):
        """The first projected policy year: ``duration_inforce() + 1``.

        1 at issue, so the acquisition expense and the initial commission fall inside the
        projection; an in-force model point starts later and never sees either.
        """
        return self.duration_inforce() + 1

    def _f_proj_len(self):
        """Projection length in policy years: the term, exactly.

        Cover ceases at the end of the term with no maturity value, no renewal and no
        conversion [S1][S2][S6][S8][R8], so the horizon is ``n`` and there is nothing after
        it - the structural contrast with ``Term_US_A``, which runs on to attained age 95.
        """
        return self.policy_term()

    def _f_term_mths(self):
        """N = 12n: the term in months, the horizon of the benefit schedules."""
        return 12 * self.policy_term()

    def _f_duration(self, t):
        """Completed years since entry at the start of policy year t: ``t - 1``.

        The select duration, which is what the UK assured lives tables are indexed by
        alongside attained age.
        """
        return t - 1

    def _f_age(self, t, life=1):
        """The attained age (ANB) of ``life`` at the start of policy year t."""
        return self.age_at_entry(life) + t - 1

    def _f_select_factor(self, t):
        """The select-duration factor applying in policy year t **[std]**.

        A 5-year select period, the structure of TMNL16/TFNL16 [R12], with the factor
        grading from 0.55 at duration 0 to 1.00 at and beyond ``select_period``.  Read
        only on the *select* mortality basis; the *applied* basis takes the table as it
        stands.  The values are a standardization - the real tables are subscriber-only
        [R11] - and a licensed basis drops in by replacing the CSV.
        """
        d = min(self.duration(t), self.select_period)                              # noqa: F821
        return float(self.data.select_factor_table().loc[d, "factor"])        # noqa: F821

    def _f_mort_rate_base(self, t, life=1):
        """The mortality table rate for ``life`` at its attained age in policy year t.

        Includes terminal illness, which is an acceleration of the death benefit rather
        than a separate cover [S1][S6][S8]; the 16-Series tables the shipped table proxies
        are graduated on that basis [R10].
        """
        return float(self.data.mort_table().loc[                              # noqa: F821
            (self.sex(life), self.smoker(life), self.age(t, life)), "mort_rate"])

    def _f_mort_rate_life(self, t, life=1):
        """The mortality (incl. TI) rate applied to ``life`` in policy year t.

        The table rate, then on the *select* basis the select factor and the **[std]** 75%
        proxy scaling, then the selective-lapsation loading.  Capped at 1.
        """
        q = self.mort_rate_base(t, life)
        if self.mort_basis() == "select":
            q = q * self.select_factor(t) * self.mort_scale                        # noqa: F821
        return min(1.0, q * self.sel_lapse_factor(t))

    def _f_mort_rate(self, t):
        """q(t): the mortality (incl. TI) decrement applied to the *policy* in year t.

        The single life's rate on a single-life policy.  On a joint first-death policy it
        is the joint decrement ``1 - (1 - q_1)(1 - q_2)`` **[std]** on one policy, which
        pays once and ends [S1][S6]; modelling the two lives as separate policies would pay
        twice.
        """
        q1 = self.mort_rate_life(t, 1)
        if not self.is_joint():
            return q1
        q2 = self.mort_rate_life(t, 2)
        return 1.0 - (1.0 - q1) * (1.0 - q2)

    def _f_lapse_cum(self, t):
        """w_cum(t): the cumulative lapse proportion of the original cohort before year t.

        A proportion of ``pols_if_init()``, not a running total of :func:`lapse_rate`, and
        it drives a loading on **mortality** rather than on lapse.  Zero in the first
        projected year.
        """
        if t <= self.proj_start():
            return 0.0
        return self.lapse_cum(t - 1) + self.pols_lapse(t - 1) / self.pols_if_init()

    def _f_sel_lapse_factor(self, t):
        """The selective-lapsation loading on mortality in policy year t **[std]**.

        ``1 + lambda max(0, w_cum(t) - w_ref)``.  Lapsers are healthier than persisters, so
        a block that has already shed a large proportion of its lives carries impaired
        mortality on the remainder - guaranteed premiums plus healthy-life rebroking make
        this a structural feature of UK term rather than an incidental one.  Off in the base
        run (``sel_lapse_lambda = 0``), where it returns 1 in every year.
        """
        return 1.0 + self.sel_lapse_lambda * max(                             # noqa: F821
            0.0, self.lapse_cum(t) - self.sel_lapse_ref)                           # noqa: F821

    def _f_lapse_rate_base(self, t):
        """The table lapse rate in policy year t **[std]**, before any rebroking multiplier.

        10 / 8 / 7 / 5 / 6 / 4 percent, anchored to the FCA's 5% average in-force lapse
        rate for pure protection and to the spike pattern just after the two- and four-year
        commission clawback periods end [R9].  A full duration curve is not public and the
        levels are standardized calibrations.  Policy years beyond the table take its last
        row.
        """
        tbl = self.data.lapse_table()                                         # noqa: F821
        return float(tbl.loc[min(t, int(tbl.index.max())), "lapse_rate"])

    def _f_rebroke_factor(self, t):
        """M_reb(t): the rebroking multiplier on the lapse rate **[std]**; 1 in the base run.

        ``min(rebroke_cap, max(1, P_inforce / P_market))``.  Premiums are guaranteed, so
        there is no premium-shock lapse to model; the economic driver is rebroking when
        market premiums for the attained age fall below the in-force premium.
        ``premium_market_ratio`` is a flat scalar, so the multiplier is level in ``t`` -
        a market premium path would be another input table.
        """
        return min(self.rebroke_cap, max(1.0, self.premium_market_ratio))          # noqa: F821

    def _f_lapse_rate(self, t):
        """w(t): the annual lapse rate applied at the end of policy year t.

        The table rate times the rebroking multiplier, capped at 1.  A lapse pays nothing:
        there is no surrender or paid-up value at any duration [S1][S6][S8][R8].
        """
        return min(1.0, self.lapse_rate_base(t) * self.rebroke_factor(t))

    def _f_pols_if(self, t):
        """l(t): the number of policies in force at the **start** of policy year t.

        ``pols_if_init()`` in the first projected year, then the notes' recursion
        ``l(t+1) = l(t)(1 - q(t))(1 - w(t))``.  This is the weight on every cash flow of
        the same ``result_cf()`` row.  Zero outside ``proj_start() .. proj_len()``: the
        cover has not started or has expired.
        """
        if t < self.proj_start() or t > self.proj_len():
            return 0.0
        if t == self.proj_start():
            return self.pols_if_init()
        return self.pols_if_at(t - 1, "AFT_DECR")

    def _f_pols_if_at(self, t, timing):
        """The number of policies in force at a point inside policy year t.

        ``"BEF_DECR"``
            l(t), the start of the year, before any decrement; the same number
            as :func:`pols_if` and the weight on that year's cash flows.

        ``"BEF_LAPSE"``
            after deaths, before lapses - the notes' processing order is
            **death before lapse** **[std order]**, so this is the population
            lapses are taken from.

        ``"AFT_DECR"``
            l(t+1), the end-of-year state: what is left once the year's deaths
            and lapses are taken, and zero from ``proj_len()`` on because the
            cover expires there.
        """
        if timing == "BEF_DECR":
            return self.pols_if(t)
        if timing == "BEF_LAPSE":
            return self.pols_if(t) * (1.0 - self.mort_rate(t))
        if timing == "AFT_DECR":
            if t < self.proj_start() or t >= self.proj_len():
                return 0.0
            return self.pols_if_at(t, "BEF_LAPSE") * (1.0 - self.lapse_rate(t))
        raise ValueError("invalid timing")

    def _f_pols_death(self, t):
        """D(t) = l(t) q(t): expected death and terminal illness claims in policy year t.

        One decrement covering both: terminal illness accelerates the death benefit rather
        than adding to it [S1][S6][S8].
        """
        return self.pols_if(t) * self.mort_rate(t)

    def _f_pols_lapse(self, t):
        """Lapses at the end of policy year t, taken from the survivors of mortality.

        Pays nothing - there is no surrender value [S6][R8] - so this moves
        :func:`pols_if` and nothing else.
        """
        return self.pols_if_at(t, "BEF_LAPSE") * self.lapse_rate(t)

    def _f_pols_maturity(self, t):
        """Policies whose cover expires at the end of the term; zero in every other year.

        Not a decrement and not a benefit - the contract simply runs out, with no maturity
        value [S1][S2][S6][S8][R8] - but needed for the in-force roll-forward to close; see
        the Space docstring and :func:`check_pols_roll_fwd`.
        """
        if t != self.proj_len():
            return 0.0
        return self.pols_if_at(t, "BEF_LAPSE") * (1.0 - self.lapse_rate(t))

    def _f_wop_waived_frac(self, t):
        """The fraction of in-force policies with premiums waived at the start of year t.

        A two-state incidence/recovery chain **[std]**,
        ``u(t+1) = u(t)(1 - rec) + (1 - u(t)) inc``, starting from ``u = 0``.  Both rates
        are placeholders: no public UK incidence basis for the waiver work-tasks
        definitions appears in the fetched sources.  Incidence in year ``t`` produces
        waiver from year ``t + 1``, which is the annual grid's reading of the 26-week
        deferred period [S1] **[std]**, and mortality and lapse are assumed independent of
        the waiver state **[std]** - which is what lets the waived population be carried as
        a fraction of the in-force rather than as its own decrement.  Zero unless the rider
        is in force.
        """
        if not self.wop() or t <= self.proj_start():
            return 0.0
        u = self.wop_waived_frac(t - 1)
        return u * (1.0 - self.wop_rec_rate) + (1.0 - u) * self.wop_inc_rate       # noqa: F821

    def _f_pols_payer(self, t):
        """The number of in-force policies actually paying premium in policy year t.

        ``l(t)`` less the waived fraction.  Equal to :func:`pols_if` unless the waiver of
        premium rider is in force.
        """
        return self.pols_if(t) * (1.0 - self.wop_waived_frac(t))

    def _f_idx_increase(self):
        """The cover increase offered at each anniversary under the indexation option.

        ``min(max(RPI, 0), 10%)`` [S1][S2][S6][S7], times ``idx_accept_rate``.  The
        notes' base run is deterministic and always accepts, which is what the shipped
        ``idx_accept_rate = 1`` means; their 80% take-up **[std]** would be a mixture of
        paths, and scaling the increase instead is a deterministic approximation to it.

        One consequence worth stating: with acceptance certain, the rule removing the option
        after three consecutive declines [S1][S6] (two at one insurer [S8]) is never
        reached, so it is not implemented.
        """
        return min(max(self.rpi_rate, 0.0), self.idx_cover_cap) * self.idx_accept_rate  # noqa: F821

    def _f_idx_factor(self, t):
        """idx(t): the cumulative **cover** indexation factor at the start of policy year t.

        1 in the first projected year and whenever the option is not elected.
        """
        if not self.indexation() or t <= self.proj_start():
            return 1.0
        return self.idx_factor(t - 1) * (1.0 + self.idx_increase())

    def _f_idx_prem_factor(self, t):
        """idx_p(t): the cumulative **premium** indexation factor at the start of year t.

        The premium rises by ``min(1.5 x increase, 15%)`` for a cover increase of
        ``increase`` [S1][S2][S6].  The 1.5 multiplier is what makes an accepted increase
        premium-margin-accretive if mortality is proportional to cover - and what reverses
        the sign of that conclusion if acceptance is selective, impaired lives accepting
        while healthy ones decline **[std]** concern.  No public take-up data exists.
        """
        if not self.indexation() or t <= self.proj_start():
            return 1.0
        return self.idx_prem_factor(t - 1) * (
            1.0 + min(self.idx_prem_mult * self.idx_increase(), self.idx_prem_cap))     # noqa: F821

    def _f_premium_pp(self, t):
        """P_a idx_p(t): the annualized gross premium per policy in policy year t.

        ``12 P_m``, indexed if the option is elected, and loaded by
        ``wop_prem_loading`` where the waiver rider is in force - a **[std]**
        placeholder, since the rider's extra premium is not published either.
        """
        p = 12.0 * self.premium_mth_pp() * self.idx_prem_factor(t)
        return p * (1.0 + self.wop_prem_loading) if self.wop() else p              # noqa: F821

    def _f_premiums(self, t):
        """Premium income at the start of policy year t, an inflow.

        Carried on :func:`pols_payer`, never on the FIB ledger: premiums stop at death
        while family income benefit instalments continue.  Annual in advance with no
        allowance for premiums ceasing at a mid-year death or lapse, which slightly
        overstates income - the known bias of this convention **[std]**, offset by the
        mid-year benefit timing of the decreasing shape.
        """
        return self.premium_pp(t) * self.pols_payer(t)

    def _f_sched_rate_mth(self):
        """j_m = (1+j)^(1/12) - 1: the decreasing schedule's monthly rate **[std]**.

        The effective convention, not a nominal ``j/12``.  The two give slightly different
        schedules, so the convention has to be stated; ``benefit_sched(60) = £134,588`` on
        the anchor cell is the notes' validation anchor for an implementation.
        """
        return (1.0 + self.sched_rate()) ** (1.0 / 12.0) - 1.0

    def _f_benefit_sched(self, k):
        """B(k): the decreasing shape's benefit after k months [S1][S6][S8].

        ``SA0 [(1+j_m)^N - (1+j_m)^k] / [(1+j_m)^N - 1]``, a mortgage-style amortization
        from ``B(0) = SA0`` to ``B(N) = 0``.  A zero schedule rate degenerates to straight
        line, which the closed form cannot express.
        """
        n_m = self.term_mths()
        jm = self.sched_rate_mth()
        if jm == 0.0:
            return self.sum_assured() * (n_m - k) / n_m
        return self.sum_assured() * (
            (1.0 + jm) ** n_m - (1.0 + jm) ** k) / ((1.0 + jm) ** n_m - 1.0)

    def _f_annuity_certain_factor(self, m):
        """a(m): the m-month annuity-certain factor at the FIB commutation rate **[std]**.

        ``[1 - (1+r_c)^(-m/12)] / [(1+r_c)^(1/12) - 1]``, instalments in arrears.  Used
        only by the commutation module.
        """
        if m <= 0:
            return 0.0
        j = self.fib_commute_disc_rate                                        # noqa: F821
        if j == 0.0:
            return float(m)
        return (1.0 - (1.0 + j) ** (-m / 12.0)) / ((1.0 + j) ** (1.0 / 12.0) - 1.0)

    def _f_fib_commute_pp(self, t):
        """CV: the commuted value of one FIB stream arising from a death in year t **[std]**.

        ``I a(N - k)`` at the mid-year death month ``k = 12(t-1) + 6``, so it falls to zero
        as the term runs out.  Zero on the level and decreasing shapes.
        """
        if self.shape() != "fib":
            return 0.0
        return self.fib_income() * self.annuity_certain_factor(self.term_mths() - (12 * (t - 1) + 6))

    def _f_benefit_pp(self, t):
        """DB(t): the death and terminal illness benefit per policy in policy year t.

        Level: ``SA0 idx(t)``.  Decreasing: the **mid-year** balance ``B(12(t-1) + 6)``
        **[std]**, the annual grid's reading of a schedule that steps down monthly.  FIB:
        the commuted value of the instalment stream, which is what a commuted claim pays;
        an uncommuted FIB claim has no lump sum at all and goes through
        ``claims(t, "FIB")`` instead.
        """
        s = self.shape()
        if s == "level":
            return self.sum_assured() * self.idx_factor(t)
        if s == "decreasing":
            return self.benefit_sched(12 * (t - 1) + 6)
        return self.fib_commute_pp(t)

    def _f_fib_cum(self, t):
        """FIBcum(t): the expected FIB streams already in payment at the start of year t.

        ``sum of D(s) for s < t``.  **Not decremented** by mortality or lapse: once a claim
        is admitted the instalments are an annuity-certain to the end of the term whatever
        happens to any life [S6][S8].  Only *new* claims carry ``l(t)``.
        """
        if t <= self.proj_start():
            return 0.0
        return self.fib_cum(t - 1) + self.pols_death(t - 1)

    def _f_claims(self, t, kind=None):
        """Benefit outgo in policy year t, by kind; the total when kind is omitted.

        ``"DEATH"``
            the lump sum paid at the end of the year of death: ``DB(t) D(t)`` on
            the level and decreasing shapes, and on the ``fib`` shape only the
            commuted proportion of the streams.

        ``"FIB"``
            the family income benefit instalments falling in year t,
            ``I [6 D(t) + 12 FIBcum(t)]`` net of the commuted proportion - six
            instalments in the year of a mid-year death, twelve in each later
            year.  Zero on the other two shapes.

        ``"LAPSE"``
            zero, always.  There is no surrender or paid-up value at any duration
            [S1][S6][S8][R8]; the kind exists so that the zero is stated rather
            than left to inference.  See the Space docstring.
        """
        if kind is None:
            return sum(self.claims(t, k) for k in ("DEATH", "FIB", "LAPSE"))
        if kind == "DEATH":
            if self.shape() == "fib":
                return self.fib_commute_rate() * self.benefit_pp(t) * self.pols_death(t)
            return self.benefit_pp(t) * self.pols_death(t)
        if kind == "FIB":
            if self.shape() != "fib":
                return 0.0
            return ((1.0 - self.fib_commute_rate()) * self.fib_income()
                    * (6.0 * self.pols_death(t) + 12.0 * self.fib_cum(t)))
        if kind == "LAPSE":
            return 0.0
        raise ValueError("invalid kind")

    def _f_claim_expenses(self, t):
        """ec D(t): the claim handling expense on the year's death and TI claims **[std]**.

        £250 per claim, uninflated.  Kept out of :func:`expenses` because the notes' worked
        example prints the two as separate columns.
        """
        return self.expense_claim * self.pols_death(t)                             # noqa: F821

    def _f_inflation_factor(self, t):
        """The expense inflation factor in policy year t: ``(1 + pi)^(t-1)`` **[std]**."""
        return (1.0 + self.inflation_rate) ** (t - 1)                         # noqa: F821

    def _f_expenses(self, t):
        """E0 and e(t): acquisition and inflating maintenance expense in year t **[std]**.

        £150 per policy at issue, then £30 per policy per year inflating at 3%, both at the
        start of the year.  An in-force model point starts after policy year 1 and never
        sees the acquisition charge.  Premiums as low as £5/month against a £30 maintenance
        expense make this assumption solvency-relevant on small-sum-assured blocks, which is
        why the notes rate expense inflation a first-order lever despite its size.
        """
        acq = self.expense_acq * self.pols_if(t) if t == 1 else 0.0                # noqa: F821
        return acq + self.expense_maint * self.inflation_factor(t) * self.pols_if(t)    # noqa: F821

    def _f_comm_init_pp(self):
        """c0: initial commission per policy issued **[std]**.

        150% of the annualized premium, paid upfront at issue.  Roughly 96% of protection
        commission is paid upfront [R9], which with the acquisition expense is what
        produces the deep year-one new business strain in the worked example.
        """
        return self.comm_init_rate * self.premium_pp(1)                            # noqa: F821

    def _f_comm_clawback(self, t):
        """Initial commission recovered on lapses inside the clawback window **[std]**.

        ``c0 (clawback_mths - 12t)/clawback_mths`` per lapsed policy, linear in months in
        force.  Off in the base run (``clawback_mths`` is 0); set it to 48 for the
        notes' four-year rule.  Clawback periods of two to four years are evidenced [R9];
        the linear formula is a standardization.  Inside the window it reverses the sign of
        the early-lapse sensitivity, which is the point of carrying it.
        """
        if self.clawback_mths <= 0:                                           # noqa: F821
            return 0.0
        mths = 12 * t
        if mths >= self.clawback_mths:                                        # noqa: F821
            return 0.0
        return (self.comm_init_pp() * (self.clawback_mths - mths)                  # noqa: F821
                / self.clawback_mths * self.pols_lapse(t))                         # noqa: F821

    def _f_commissions(self, t):
        """Commission outgo in policy year t **[std]**, net of any clawback recovered.

        The initial commission in policy year 1, then 2.5% of premium income from policy
        year 2.  Both are levels chosen for the reference implementation; only the upfront
        *pattern* is evidenced [R9].
        """
        init = self.comm_init_pp() * self.pols_if(t) if t == 1 else 0.0
        renew = self.comm_renewal_rate * self.premiums(t) if t >= 2 else 0.0       # noqa: F821
        return init + renew - self.comm_clawback(t)

    def _f_net_cf(self, t):
        """CF(t): the net cash flow of policy year t, **income positive**.

        Premiums less death and terminal illness claims, claim expense, maintenance and
        acquisition expense and commission.  The notes' own sign - they write ``+ = inflow``
        - which is also the library-wide convention, so unlike the whole life and payout
        annuity models there is no outgo-positive ``liability_cf`` companion to publish.

        The shape to expect on guaranteed term is a deep new business strain in year 1,
        upfront commission and acquisition expense against a single year's premium, then
        thin positive margins: the level premium prefunds rising mortality cost, so early
        lapses forfeit margin to the insurer and late ones relieve it.
        """
        return (self.premiums(t) - self.claims(t) - self.claim_expenses(t)
                - self.expenses(t) - self.commissions(t))

    def _f_check_pols_roll_fwd_resid(self, t):
        """The in-force roll-forward residual in policy year t; zero everywhere.

        ``pols_if(t) - pols_if(t+1) - deaths - lapses - expiries``.  Expiries are non-zero
        only in the final policy year, where the survivors neither die nor lapse: their
        cover runs out.  Without that term the last year appears to lose lives with no
        cause.
        """
        return (self.pols_if(t) - self.pols_if(t + 1)
                - self.pols_death(t) - self.pols_lapse(t) - self.pols_maturity(t))

    def _f_check_pols_roll_fwd(self):
        """True when the in-force roll-forward closes in every projected policy year.

        The library-wide form of a roll-forward check: no argument, one bool over all t, so
        one test can call it across every model.  :func:`check_pols_roll_fwd_resid` gives
        the signed residual of the year that failed.  The tolerance scales with
        ``pols_if_init()``, since the residual accumulates rounding on that many policies.
        """
        return all(abs(self.check_pols_roll_fwd_resid(t)) <= 1e-10 * max(self.pols_if_init(), 1.0)
                   for t in range(self.proj_start(), self.proj_len() + 1))

    def _f_check_fib_ledger_resid(self, t):
        """The family income benefit ledger residual in policy year t; zero everywhere.

        :func:`claims` ``(t, "FIB")`` less an independent rebuild of the same figure: six
        instalments for a death in year t and twelve for every death in an earlier year,
        summed straight off the death vector with no reference to the :func:`fib_cum`
        recursion.  A ledger that was decremented by mortality or lapse - the notes'
        pitfall - or one that paid only the year-of-death instalments would show up here.
        Zero by definition on the level and decreasing shapes, which have no ledger.
        """
        if self.shape() != "fib":
            return 0.0
        built = 6.0 * self.pols_death(t) + 12.0 * sum(
            self.pols_death(s) for s in range(self.proj_start(), t))
        return self.claims(t, "FIB") - (1.0 - self.fib_commute_rate()) * self.fib_income() * built

    def _f_check_fib_ledger(self):
        """True when the family income benefit ledger closes in every projected year.

        No argument, one bool over all t, the library-wide shape of a ``check_*`` cells;
        :func:`check_fib_ledger_resid` gives the signed residual of the year that failed.
        """
        return all(abs(self.check_fib_ledger_resid(t)) <= 1e-10 * max(self.pols_if_init(), 1.0)
                   for t in range(self.proj_start(), self.proj_len() + 1))

    def _f_result_cf(self):
        """Result table of cashflows, indexed by policy year t.

        ``pols_if`` is the start-of-year count, which is the weight applied to every cash
        flow on the same row.  ``net_cf`` carries the notes' own income-positive sign.
        ``claims_lapse`` is a column of zeros by product design - there is no surrender
        value - and is published rather than dropped; see the Space docstring.
        """
        ts = list(range(self.proj_start(), self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "pols_if": [self.pols_if(t) for t in ts],
                "premiums": [self.premiums(t) for t in ts],
                "claims_death": [self.claims(t, "DEATH") for t in ts],
                "claims_fib": [self.claims(t, "FIB") for t in ts],
                "claims_lapse": [self.claims(t, "LAPSE") for t in ts],
                "claim_expenses": [self.claim_expenses(t) for t in ts],
                "expenses": [self.expenses(t) for t in ts],
                "commissions": [self.commissions(t) for t in ts],
                "net_cf": [self.net_cf(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    def _f_result_pols(self):
        """Result table of policy counts and decrement rates, indexed by policy year t."""
        ts = list(range(self.proj_start(), self.proj_len() + 1))
        return self.pd.DataFrame(                                             # noqa: F821
            {
                "pols_if": [self.pols_if(t) for t in ts],
                "pols_death": [self.pols_death(t) for t in ts],
                "pols_lapse": [self.pols_lapse(t) for t in ts],
                "pols_maturity": [self.pols_maturity(t) for t in ts],
                "pols_payer": [self.pols_payer(t) for t in ts],
                "fib_cum": [self.fib_cum(t) for t in ts],
                "mort_rate": [self.mort_rate(t) for t in ts],
                "lapse_rate": [self.lapse_rate(t) for t in ts],
            },
            index=self.pd.Index(ts, name="t"),                                # noqa: F821
        )

    def _f_bench_net_cf(self):
        return sum(self.net_cf(t) for t in range(self.proj_start(), self.proj_len() + 1))


    def model_point(self):
        if self._has_model_point:
            return self._v_model_point
        else:
            val = self._v_model_point = self._f_model_point()
            self._has_model_point = True
            return val

    def shape(self):
        if self._has_shape:
            return self._v_shape
        else:
            val = self._v_shape = self._f_shape()
            self._has_shape = True
            return val

    def is_joint(self):
        if self._has_is_joint:
            return self._v_is_joint
        else:
            val = self._v_is_joint = self._f_is_joint()
            self._has_is_joint = True
            return val

    def age_at_entry(self, life=1):
        if life in self._v_age_at_entry:
            return self._v_age_at_entry[life]
        else:
            val = self._f_age_at_entry(life)
            self._v_age_at_entry[life] = val
            return val

    def sex(self, life=1):
        if life in self._v_sex:
            return self._v_sex[life]
        else:
            val = self._f_sex(life)
            self._v_sex[life] = val
            return val

    def smoker(self, life=1):
        if life in self._v_smoker:
            return self._v_smoker[life]
        else:
            val = self._f_smoker(life)
            self._v_smoker[life] = val
            return val

    def policy_term(self):
        if self._has_policy_term:
            return self._v_policy_term
        else:
            val = self._v_policy_term = self._f_policy_term()
            self._has_policy_term = True
            return val

    def sum_assured(self):
        if self._has_sum_assured:
            return self._v_sum_assured
        else:
            val = self._v_sum_assured = self._f_sum_assured()
            self._has_sum_assured = True
            return val

    def fib_income(self):
        if self._has_fib_income:
            return self._v_fib_income
        else:
            val = self._v_fib_income = self._f_fib_income()
            self._has_fib_income = True
            return val

    def sched_rate(self):
        if self._has_sched_rate:
            return self._v_sched_rate
        else:
            val = self._v_sched_rate = self._f_sched_rate()
            self._has_sched_rate = True
            return val

    def indexation(self):
        if self._has_indexation:
            return self._v_indexation
        else:
            val = self._v_indexation = self._f_indexation()
            self._has_indexation = True
            return val

    def wop(self):
        if self._has_wop:
            return self._v_wop
        else:
            val = self._v_wop = self._f_wop()
            self._has_wop = True
            return val

    def premium_mth_pp(self):
        if self._has_premium_mth_pp:
            return self._v_premium_mth_pp
        else:
            val = self._v_premium_mth_pp = self._f_premium_mth_pp()
            self._has_premium_mth_pp = True
            return val

    def premium_mode(self):
        if self._has_premium_mode:
            return self._v_premium_mode
        else:
            val = self._v_premium_mode = self._f_premium_mode()
            self._has_premium_mode = True
            return val

    def mort_basis(self):
        if self._has_mort_basis:
            return self._v_mort_basis
        else:
            val = self._v_mort_basis = self._f_mort_basis()
            self._has_mort_basis = True
            return val

    def pols_if_init(self):
        if self._has_pols_if_init:
            return self._v_pols_if_init
        else:
            val = self._v_pols_if_init = self._f_pols_if_init()
            self._has_pols_if_init = True
            return val

    def duration_inforce(self):
        if self._has_duration_inforce:
            return self._v_duration_inforce
        else:
            val = self._v_duration_inforce = self._f_duration_inforce()
            self._has_duration_inforce = True
            return val

    def fib_commute_rate(self):
        if self._has_fib_commute_rate:
            return self._v_fib_commute_rate
        else:
            val = self._v_fib_commute_rate = self._f_fib_commute_rate()
            self._has_fib_commute_rate = True
            return val

    def proj_start(self):
        if self._has_proj_start:
            return self._v_proj_start
        else:
            val = self._v_proj_start = self._f_proj_start()
            self._has_proj_start = True
            return val

    def proj_len(self):
        if self._has_proj_len:
            return self._v_proj_len
        else:
            val = self._v_proj_len = self._f_proj_len()
            self._has_proj_len = True
            return val

    def term_mths(self):
        if self._has_term_mths:
            return self._v_term_mths
        else:
            val = self._v_term_mths = self._f_term_mths()
            self._has_term_mths = True
            return val

    def duration(self, t):
        if t in self._v_duration:
            return self._v_duration[t]
        else:
            val = self._f_duration(t)
            self._v_duration[t] = val
            return val

    def age(self, t, life=1):
        if (t, life) in self._v_age:
            return self._v_age[(t, life)]
        else:
            val = self._f_age(t, life)
            self._v_age[(t, life)] = val
            return val

    def select_factor(self, t):
        if t in self._v_select_factor:
            return self._v_select_factor[t]
        else:
            val = self._f_select_factor(t)
            self._v_select_factor[t] = val
            return val

    def mort_rate_base(self, t, life=1):
        if (t, life) in self._v_mort_rate_base:
            return self._v_mort_rate_base[(t, life)]
        else:
            val = self._f_mort_rate_base(t, life)
            self._v_mort_rate_base[(t, life)] = val
            return val

    def mort_rate_life(self, t, life=1):
        if (t, life) in self._v_mort_rate_life:
            return self._v_mort_rate_life[(t, life)]
        else:
            val = self._f_mort_rate_life(t, life)
            self._v_mort_rate_life[(t, life)] = val
            return val

    def mort_rate(self, t):
        if t in self._v_mort_rate:
            return self._v_mort_rate[t]
        else:
            val = self._f_mort_rate(t)
            self._v_mort_rate[t] = val
            return val

    def lapse_cum(self, t):
        if t in self._v_lapse_cum:
            return self._v_lapse_cum[t]
        else:
            val = self._f_lapse_cum(t)
            self._v_lapse_cum[t] = val
            return val

    def sel_lapse_factor(self, t):
        if t in self._v_sel_lapse_factor:
            return self._v_sel_lapse_factor[t]
        else:
            val = self._f_sel_lapse_factor(t)
            self._v_sel_lapse_factor[t] = val
            return val

    def lapse_rate_base(self, t):
        if t in self._v_lapse_rate_base:
            return self._v_lapse_rate_base[t]
        else:
            val = self._f_lapse_rate_base(t)
            self._v_lapse_rate_base[t] = val
            return val

    def rebroke_factor(self, t):
        if t in self._v_rebroke_factor:
            return self._v_rebroke_factor[t]
        else:
            val = self._f_rebroke_factor(t)
            self._v_rebroke_factor[t] = val
            return val

    def lapse_rate(self, t):
        if t in self._v_lapse_rate:
            return self._v_lapse_rate[t]
        else:
            val = self._f_lapse_rate(t)
            self._v_lapse_rate[t] = val
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

    def wop_waived_frac(self, t):
        if t in self._v_wop_waived_frac:
            return self._v_wop_waived_frac[t]
        else:
            val = self._f_wop_waived_frac(t)
            self._v_wop_waived_frac[t] = val
            return val

    def pols_payer(self, t):
        if t in self._v_pols_payer:
            return self._v_pols_payer[t]
        else:
            val = self._f_pols_payer(t)
            self._v_pols_payer[t] = val
            return val

    def idx_increase(self):
        if self._has_idx_increase:
            return self._v_idx_increase
        else:
            val = self._v_idx_increase = self._f_idx_increase()
            self._has_idx_increase = True
            return val

    def idx_factor(self, t):
        if t in self._v_idx_factor:
            return self._v_idx_factor[t]
        else:
            val = self._f_idx_factor(t)
            self._v_idx_factor[t] = val
            return val

    def idx_prem_factor(self, t):
        if t in self._v_idx_prem_factor:
            return self._v_idx_prem_factor[t]
        else:
            val = self._f_idx_prem_factor(t)
            self._v_idx_prem_factor[t] = val
            return val

    def premium_pp(self, t):
        if t in self._v_premium_pp:
            return self._v_premium_pp[t]
        else:
            val = self._f_premium_pp(t)
            self._v_premium_pp[t] = val
            return val

    def premiums(self, t):
        if t in self._v_premiums:
            return self._v_premiums[t]
        else:
            val = self._f_premiums(t)
            self._v_premiums[t] = val
            return val

    def sched_rate_mth(self):
        if self._has_sched_rate_mth:
            return self._v_sched_rate_mth
        else:
            val = self._v_sched_rate_mth = self._f_sched_rate_mth()
            self._has_sched_rate_mth = True
            return val

    def benefit_sched(self, k):
        if k in self._v_benefit_sched:
            return self._v_benefit_sched[k]
        else:
            val = self._f_benefit_sched(k)
            self._v_benefit_sched[k] = val
            return val

    def annuity_certain_factor(self, m):
        if m in self._v_annuity_certain_factor:
            return self._v_annuity_certain_factor[m]
        else:
            val = self._f_annuity_certain_factor(m)
            self._v_annuity_certain_factor[m] = val
            return val

    def fib_commute_pp(self, t):
        if t in self._v_fib_commute_pp:
            return self._v_fib_commute_pp[t]
        else:
            val = self._f_fib_commute_pp(t)
            self._v_fib_commute_pp[t] = val
            return val

    def benefit_pp(self, t):
        if t in self._v_benefit_pp:
            return self._v_benefit_pp[t]
        else:
            val = self._f_benefit_pp(t)
            self._v_benefit_pp[t] = val
            return val

    def fib_cum(self, t):
        if t in self._v_fib_cum:
            return self._v_fib_cum[t]
        else:
            val = self._f_fib_cum(t)
            self._v_fib_cum[t] = val
            return val

    def claims(self, t, kind=None):
        if (t, kind) in self._v_claims:
            return self._v_claims[(t, kind)]
        else:
            val = self._f_claims(t, kind)
            self._v_claims[(t, kind)] = val
            return val

    def claim_expenses(self, t):
        if t in self._v_claim_expenses:
            return self._v_claim_expenses[t]
        else:
            val = self._f_claim_expenses(t)
            self._v_claim_expenses[t] = val
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

    def comm_init_pp(self):
        if self._has_comm_init_pp:
            return self._v_comm_init_pp
        else:
            val = self._v_comm_init_pp = self._f_comm_init_pp()
            self._has_comm_init_pp = True
            return val

    def comm_clawback(self, t):
        if t in self._v_comm_clawback:
            return self._v_comm_clawback[t]
        else:
            val = self._f_comm_clawback(t)
            self._v_comm_clawback[t] = val
            return val

    def commissions(self, t):
        if t in self._v_commissions:
            return self._v_commissions[t]
        else:
            val = self._f_commissions(t)
            self._v_commissions[t] = val
            return val

    def net_cf(self, t):
        if t in self._v_net_cf:
            return self._v_net_cf[t]
        else:
            val = self._f_net_cf(t)
            self._v_net_cf[t] = val
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

    def check_fib_ledger_resid(self, t):
        if t in self._v_check_fib_ledger_resid:
            return self._v_check_fib_ledger_resid[t]
        else:
            val = self._f_check_fib_ledger_resid(t)
            self._v_check_fib_ledger_resid[t] = val
            return val

    def check_fib_ledger(self):
        if self._has_check_fib_ledger:
            return self._v_check_fib_ledger
        else:
            val = self._v_check_fib_ledger = self._f_check_fib_ledger()
            self._has_check_fib_ledger = True
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


