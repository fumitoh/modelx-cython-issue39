# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False

"""Generated static fast-recursive reference runtime."""

class FastRecursiveRuntime:

    def __init__(self, ctx=None):
        self.ctx = ctx
        self.cache = [dict() for _ in range(35)]

    def bind(self, ctx):
        self.ctx = ctx
        for c in self.cache:
            c.clear()
        return self

cdef object _calc_age(rt, t):
    """The attained age at time t.

        Defined as::

            age_at_entry() + duration(t)

        .. seealso::

            * :func:`age_at_entry`
            * :func:`duration`

        """
    return fr_age_at_entry(rt) + fr_duration(rt, t)

cdef object fr_age(rt, t):
    c = rt.cache[0]
    key = t
    if key in c:
        return c[key]
    val = _calc_age(rt, t)
    c[key] = val
    return val

cdef object _calc_age_at_entry(rt):
    """The age at entry of the selected model point

        The element labeled ``age_at_entry`` of the Series returned by
        :func:`model_point`.
        """
    return fr_model_point(rt)['age_at_entry']

cdef object fr_age_at_entry(rt):
    c = rt.cache[1]
    key = None
    if key in c:
        return c[key]
    val = _calc_age_at_entry(rt)
    c[key] = val
    return val

cdef object _calc_claim_pp(rt, t):
    """Claim per policy

        The claim amount per plicy. Defaults to :func:`sum_assured`.
        """
    return fr_sum_assured(rt)

cdef object fr_claim_pp(rt, t):
    c = rt.cache[2]
    key = t
    if key in c:
        return c[key]
    val = _calc_claim_pp(rt, t)
    c[key] = val
    return val

cdef object _calc_claims(rt, t):
    """Claims

        Claims during the period from ``t`` to ``t+1`` defined as::

            claim_pp(t) * pols_death(t)

        .. seealso::

            * :func:`claim_pp`
            * :func:`pols_death`

        """
    return fr_claim_pp(rt, t) * fr_pols_death(rt, t)

cdef object fr_claims(rt, t):
    c = rt.cache[3]
    key = t
    if key in c:
        return c[key]
    val = _calc_claims(rt, t)
    c[key] = val
    return val

cdef object _calc_commissions(rt, t):
    """Commissions

        By default, 100% premiums for the first year, 0 otherwise.

        .. seealso::

            * :func:`premiums`
            * :func:`duration`

        """
    return fr_premiums(rt, t) if fr_duration(rt, t) == 0 else 0

cdef object fr_commissions(rt, t):
    c = rt.cache[4]
    key = t
    if key in c:
        return c[key]
    val = _calc_commissions(rt, t)
    c[key] = val
    return val

cdef object _calc_disc_factors(rt):
    """Discount factors.

        Vector of the discount factors as a Numpy array. Used for calculating
        the present values of cashflows.

        .. seealso::

            :func:`disc_rate_mth`
        """
    return rt.ctx.np.array(list(((1 + fr_disc_rate_mth(rt)[t]) ** (-t) for t in range(fr_proj_len(rt)))))

cdef object fr_disc_factors(rt):
    c = rt.cache[5]
    key = None
    if key in c:
        return c[key]
    val = _calc_disc_factors(rt)
    c[key] = val
    return val

cdef object _calc_disc_rate_mth(rt):
    """Monthly discount rate

        Nummpy array of monthly discount rates from time 0 to :func:`proj_len` - 1
        defined as::

            (1 + disc_rate_ann)**(1/12) - 1

        .. seealso::

            :func:`disc_rate_ann`

        """
    return rt.ctx.np.array(list(((1 + rt.ctx.disc_rate_ann[t // 12]) ** (1 / 12) - 1 for t in range(fr_proj_len(rt)))))

cdef object fr_disc_rate_mth(rt):
    c = rt.cache[6]
    key = None
    if key in c:
        return c[key]
    val = _calc_disc_rate_mth(rt)
    c[key] = val
    return val

cdef object _calc_duration(rt, t):
    """Duration in force in years"""
    return t // 12

cdef object fr_duration(rt, t):
    c = rt.cache[7]
    key = t
    if key in c:
        return c[key]
    val = _calc_duration(rt, t)
    c[key] = val
    return val

cdef object _calc_expense_acq(rt):
    """Acquisition expense per policy

        ``300`` by default.
        """
    return 300

cdef object fr_expense_acq(rt):
    c = rt.cache[8]
    key = None
    if key in c:
        return c[key]
    val = _calc_expense_acq(rt)
    c[key] = val
    return val

cdef object _calc_expense_maint(rt):
    """Annual maintenance expense per policy

        ``60`` by default.
        """
    return 60

cdef object fr_expense_maint(rt):
    c = rt.cache[9]
    key = None
    if key in c:
        return c[key]
    val = _calc_expense_maint(rt)
    c[key] = val
    return val

cdef object _calc_expenses(rt, t):
    """Acquisition and maintenance expenses

        Expense cashflow during the period from ``t`` to ``t+1``.
        For any ``t``, the maintenance expense is recognized,
        which is defined as::

            pols_if(t) * expense_maint()/12 * inflation_factor(t)

        At ``t=0`` only, the acquisition expense,
        defined as :func:`expense_acq`, is recognized.

        .. seealso::

            * :func:`pols_if`
            * :func:`expense_maint`
            * :func:`inflation_factor`

        .. versionchanged:: 0.2.0
           The maintenance expense is also recognized for ``t=0``.

        """
    maint = fr_pols_if(rt, t) * fr_expense_maint(rt) / 12 * fr_inflation_factor(rt, t)
    if t == 0:
        return fr_expense_acq(rt) + maint
    else:
        return maint

cdef object fr_expenses(rt, t):
    c = rt.cache[10]
    key = t
    if key in c:
        return c[key]
    val = _calc_expenses(rt, t)
    c[key] = val
    return val

cdef object _calc_inflation_factor(rt, t):
    """The inflation factor at time t

        .. seealso::

            * :func:`inflation_rate`

        """
    return (1 + fr_inflation_rate(rt)) ** (t / 12)

cdef object fr_inflation_factor(rt, t):
    c = rt.cache[11]
    key = t
    if key in c:
        return c[key]
    val = _calc_inflation_factor(rt, t)
    c[key] = val
    return val

cdef object _calc_inflation_rate(rt):
    """Inflation rate"""
    return 0.01

cdef object fr_inflation_rate(rt):
    c = rt.cache[12]
    key = None
    if key in c:
        return c[key]
    val = _calc_inflation_rate(rt)
    c[key] = val
    return val

cdef object _calc_lapse_rate(rt, t):
    """Lapse rate

        By default, the lapse rate assumption is defined by duration as::

            max(0.1 - 0.02 * duration(t), 0.02)

        .. seealso::

            :func:`duration`

        """
    return max(0.1 - 0.02 * fr_duration(rt, t), 0.02)

cdef object fr_lapse_rate(rt, t):
    c = rt.cache[13]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate(rt, t)
    c[key] = val
    return val

cdef object _calc_loading_prem(rt):
    """Loading per premium

        ``0.5`` by default.

        .. seealso::

            * :func:`premium_pp`

        """
    return 0.5

cdef object fr_loading_prem(rt):
    c = rt.cache[14]
    key = None
    if key in c:
        return c[key]
    val = _calc_loading_prem(rt)
    c[key] = val
    return val

cdef object _calc_model_point(rt):
    """The selected model point as a Series

        :func:`model_point` looks up :attr:`model_point_table`, and
        returns as a Series the row whose label is the value of
        :attr:`point_id`.

        Example:
            In the code below ``Projection`` refers to
            the :mod:`~basiclife.BasicTerm_S.Projection` space::

                >>> Projection.point_id
                1

                >>> Projection.model_point()
                age_at_entry        47
                sex                  M
                policy_term         10
                policy_count         1
                sum_assured     622000
                Name: 1, dtype: object

                >>> Projection.point_id = 2

                >>> Projection.model_point()
                age_at_entry        29
                sex                  M
                policy_term         20
                policy_count         1
                sum_assured     752000
                Name: 2, dtype: object

        """
    return rt.ctx.model_point_table.loc[rt.ctx.point_id]

cdef object fr_model_point(rt):
    c = rt.cache[15]
    key = None
    if key in c:
        return c[key]
    val = _calc_model_point(rt)
    c[key] = val
    return val

cdef object _calc_mort_rate(rt, t):
    """Mortality rate to be applied at time t

        .. seealso::

           * :attr:`mort_table`
           * :func:`mort_rate_mth`

        """
    return rt.ctx.mort_table[str(max(min(5, fr_duration(rt, t)), 0))][fr_age(rt, t)]

cdef object fr_mort_rate(rt, t):
    c = rt.cache[16]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate(rt, t)
    c[key] = val
    return val

cdef object _calc_mort_rate_mth(rt, t):
    """Monthly mortality rate to be applied at time t

        .. seealso::

           * :attr:`mort_table`
           * :func:`mort_rate`

        """
    return 1 - (1 - fr_mort_rate(rt, t)) ** (1 / 12)

cdef object fr_mort_rate_mth(rt, t):
    c = rt.cache[17]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate_mth(rt, t)
    c[key] = val
    return val

cdef object _calc_net_premium_pp(rt):
    """Net premium per policy

        The net premium per policy is defined so that
        the present value of net premiums equates to the present value of
        claims::

            pv_claims() / pv_pols_if()

        .. seealso::

            * :func:`pv_claims`
            * :func:`pv_pols_if`

        """
    return fr_pv_claims(rt) / fr_pv_pols_if(rt)

cdef object fr_net_premium_pp(rt):
    c = rt.cache[18]
    key = None
    if key in c:
        return c[key]
    val = _calc_net_premium_pp(rt)
    c[key] = val
    return val

cdef object _calc_policy_term(rt):
    """The policy term of the selected model point.

        The element labeled ``policy_term`` of the Series returned by
        :func:`model_point`.
        """
    return fr_model_point(rt)['policy_term']

cdef object fr_policy_term(rt):
    c = rt.cache[19]
    key = None
    if key in c:
        return c[key]
    val = _calc_policy_term(rt)
    c[key] = val
    return val

cdef object _calc_pols_death(rt, t):
    """Number of death occurring at time t"""
    return fr_pols_if(rt, t) * fr_mort_rate_mth(rt, t)

cdef object fr_pols_death(rt, t):
    c = rt.cache[20]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_death(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_if(rt, t):
    """Number of policies in-force

        Number of in-force policies calculated recursively.
        The initial value is read from :func:`pols_if_init`.
        Subsequent values are defined recursively as::

            pols_if(t-1) - pols_lapse(t-1) - pols_death(t-1) - pols_maturity(t)

        .. seealso::
            * :func:`pols_lapse`
            * :func:`pols_death`
            * :func:`pols_maturity`

        """
    if t == 0:
        return fr_pols_if_init(rt)
    elif t > fr_policy_term(rt) * 12:
        return 0
    else:
        return fr_pols_if(rt, t - 1) - fr_pols_lapse(rt, t - 1) - fr_pols_death(rt, t - 1) - fr_pols_maturity(rt, t)

cdef object fr_pols_if(rt, t):
    c = rt.cache[21]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_if(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_if_init(rt):
    """Initial Number of Policies In-force

        Number of in-force policies at time 0 referenced from :func:`pols_if`.
        Defaults to 1.
        """
    return 1

cdef object fr_pols_if_init(rt):
    c = rt.cache[22]
    key = None
    if key in c:
        return c[key]
    val = _calc_pols_if_init(rt)
    c[key] = val
    return val

cdef object _calc_pols_lapse(rt, t):
    """Number of lapse occurring at time t

        .. seealso::
            * :func:`pols_if`
            * :func:`lapse_rate`

        """
    return (fr_pols_if(rt, t) - fr_pols_death(rt, t)) * (1 - (1 - fr_lapse_rate(rt, t)) ** (1 / 12))

cdef object fr_pols_lapse(rt, t):
    c = rt.cache[23]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_lapse(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_maturity(rt, t):
    """Number of maturing policies

        The policy maturity occurs at ``t == 12 * policy_term()``,
        after death and lapse during the last period::

            pols_if(t-1) - pols_lapse(t-1) - pols_death(t-1)

        otherwise ``0``.
        """
    if t == fr_policy_term(rt) * 12:
        return fr_pols_if(rt, t - 1) - fr_pols_lapse(rt, t - 1) - fr_pols_death(rt, t - 1)
    else:
        return 0

cdef object fr_pols_maturity(rt, t):
    c = rt.cache[24]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_maturity(rt, t)
    c[key] = val
    return val

cdef object _calc_premium_pp(rt):
    """Monthly premium per policy

        Monthly premium amount per policy defined as::

            round((1 + loading_prem()) * net_premium(), 2)

        .. versionchanged:: 0.2.0
           The ``t`` parameter is removed.

        .. seealso::

            * :func:`loading_prem`
            * :func:`net_premium_pp`

        """
    return round((1 + fr_loading_prem(rt)) * fr_net_premium_pp(rt), 2)

cdef object fr_premium_pp(rt):
    c = rt.cache[25]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_pp(rt)
    c[key] = val
    return val

cdef object _calc_premiums(rt, t):
    """Premium income

        Premium income during the period from ``t`` to ``t+1`` defined as::

            premium_pp(t) * pols_if(t)

        .. seealso::

            * :func:`premium_pp`
            * :func:`pols_if`

        """
    return fr_premium_pp(rt) * fr_pols_if(rt, t)

cdef object fr_premiums(rt, t):
    c = rt.cache[26]
    key = t
    if key in c:
        return c[key]
    val = _calc_premiums(rt, t)
    c[key] = val
    return val

cdef object _calc_proj_len(rt):
    """Projection length in months

        Projection length in months defined as::

            12 * policy_term() + 1

        .. seealso::

            :func:`policy_term`

        """
    return 12 * fr_policy_term(rt) + 1

cdef object fr_proj_len(rt):
    c = rt.cache[27]
    key = None
    if key in c:
        return c[key]
    val = _calc_proj_len(rt)
    c[key] = val
    return val

cdef object _calc_pv_claims(rt):
    """Present value of claims

        .. seealso::

            * :func:`claims`

        """
    return sum(list((fr_claims(rt, t) for t in range(fr_proj_len(rt)))) * fr_disc_factors(rt)[:fr_proj_len(rt)])

cdef object fr_pv_claims(rt):
    c = rt.cache[28]
    key = None
    if key in c:
        return c[key]
    val = _calc_pv_claims(rt)
    c[key] = val
    return val

cdef object _calc_pv_commissions(rt):
    """Present value of commissions

        .. seealso::

            * :func:`expenses`

        """
    return sum(list((fr_commissions(rt, t) for t in range(fr_proj_len(rt)))) * fr_disc_factors(rt)[:fr_proj_len(rt)])

cdef object fr_pv_commissions(rt):
    c = rt.cache[29]
    key = None
    if key in c:
        return c[key]
    val = _calc_pv_commissions(rt)
    c[key] = val
    return val

cdef object _calc_pv_expenses(rt):
    """Present value of expenses

        .. seealso::

            * :func:`expenses`

        """
    return sum(list((fr_expenses(rt, t) for t in range(fr_proj_len(rt)))) * fr_disc_factors(rt)[:fr_proj_len(rt)])

cdef object fr_pv_expenses(rt):
    c = rt.cache[30]
    key = None
    if key in c:
        return c[key]
    val = _calc_pv_expenses(rt)
    c[key] = val
    return val

cdef object _calc_pv_net_cf(rt):
    """Present value of net cashflows.

        Defined as::

            pv_premiums() - pv_claims() - pv_expenses() - pv_commissions()

        .. seealso::

            * :func:`pv_premiums`
            * :func:`pv_claims`
            * :func:`pv_expenses`
            * :func:`pv_commissions`

        """
    return fr_pv_premiums(rt) - fr_pv_claims(rt) - fr_pv_expenses(rt) - fr_pv_commissions(rt)

cdef object fr_pv_net_cf(rt):
    c = rt.cache[31]
    key = None
    if key in c:
        return c[key]
    val = _calc_pv_net_cf(rt)
    c[key] = val
    return val

cdef object _calc_pv_pols_if(rt):
    """Present value of policies in-force

        The discounted sum of the number of in-force policies at each month.
        It is used as the annuity factor for calculating :func:`net_premium_pp`.

        """
    return sum(list((fr_pols_if(rt, t) for t in range(fr_proj_len(rt)))) * fr_disc_factors(rt)[:fr_proj_len(rt)])

cdef object fr_pv_pols_if(rt):
    c = rt.cache[32]
    key = None
    if key in c:
        return c[key]
    val = _calc_pv_pols_if(rt)
    c[key] = val
    return val

cdef object _calc_pv_premiums(rt):
    """Present value of premiums

        .. seealso::

            * :func:`premiums`

        """
    return sum(list((fr_premiums(rt, t) for t in range(fr_proj_len(rt)))) * fr_disc_factors(rt)[:fr_proj_len(rt)])

cdef object fr_pv_premiums(rt):
    c = rt.cache[33]
    key = None
    if key in c:
        return c[key]
    val = _calc_pv_premiums(rt)
    c[key] = val
    return val

cdef object _calc_sum_assured(rt):
    """The sum assured of the selected model point

        The element labeled ``sum_assured`` of the Series returned by
        :func:`model_point`.
        """
    return fr_model_point(rt)['sum_assured']

cdef object fr_sum_assured(rt):
    c = rt.cache[34]
    key = None
    if key in c:
        return c[key]
    val = _calc_sum_assured(rt)
    c[key] = val
    return val

def evaluate(rt, ctx):
    rt.bind(ctx)
    return fr_pv_net_cf(rt)
