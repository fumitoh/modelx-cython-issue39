"""Generated static fast-recursive reference runtime."""

class FastRecursiveRuntime:

    def __init__(self, ctx=None):
        self.ctx = ctx
        self.cache = [dict() for _ in range(57)]

    def bind(self, ctx):
        self.ctx = ctx
        for c in self.cache:
            c.clear()
        return self

def _calc_age(rt, t, life=1):
    """The attained age (ANB) of ``life`` at the start of policy year t."""
    return fr_age_at_entry(rt, life) + t - 1

def fr_age(rt, t, life=1):
    c = rt.cache[0]
    key = (t, life)
    if key in c:
        return c[key]
    val = _calc_age(rt, t, life)
    c[key] = val
    return val

def _calc_age_at_entry(rt, life=1):
    """x: the issue age (ANB) of the first (``life = 1``) or second life.

        Age nearest birthday at entry, plus a curtate policy year **[std]**: the fetched
        product documents state no age basis, and the UK assured lives tables are select
        tables indexed that way.
        """
    if life == 1:
        return int(fr_model_point(rt)['age_at_entry'])
    if life == 2 and fr_is_joint(rt):
        return int(fr_model_point(rt)['joint_age'])
    raise ValueError('invalid life')

def fr_age_at_entry(rt, life=1):
    c = rt.cache[1]
    key = life
    if key in c:
        return c[key]
    val = _calc_age_at_entry(rt, life)
    c[key] = val
    return val

def _calc_annuity_certain_factor(rt, m):
    """a(m): the m-month annuity-certain factor at the FIB commutation rate **[std]**.

        ``[1 - (1+r_c)^(-m/12)] / [(1+r_c)^(1/12) - 1]``, instalments in arrears.  Used
        only by the commutation module.
        """
    if m <= 0:
        return 0.0
    j = rt.ctx.fib_commute_disc_rate
    if j == 0.0:
        return float(m)
    return (1.0 - (1.0 + j) ** (-m / 12.0)) / ((1.0 + j) ** (1.0 / 12.0) - 1.0)

def fr_annuity_certain_factor(rt, m):
    c = rt.cache[2]
    key = m
    if key in c:
        return c[key]
    val = _calc_annuity_certain_factor(rt, m)
    c[key] = val
    return val

def _calc_bench_net_cf(rt):
    return sum((fr_net_cf(rt, t) for t in range(fr_proj_start(rt), fr_proj_len(rt) + 1)))

def fr_bench_net_cf(rt):
    c = rt.cache[3]
    key = None
    if key in c:
        return c[key]
    val = _calc_bench_net_cf(rt)
    c[key] = val
    return val

def _calc_benefit_pp(rt, t):
    """DB(t): the death and terminal illness benefit per policy in policy year t.

        Level: ``SA0 idx(t)``.  Decreasing: the **mid-year** balance ``B(12(t-1) + 6)``
        **[std]**, the annual grid's reading of a schedule that steps down monthly.  FIB:
        the commuted value of the instalment stream, which is what a commuted claim pays;
        an uncommuted FIB claim has no lump sum at all and goes through
        ``claims(t, "FIB")`` instead.
        """
    s = fr_shape(rt)
    if s == 'level':
        return fr_sum_assured(rt) * fr_idx_factor(rt, t)
    if s == 'decreasing':
        return fr_benefit_sched(rt, 12 * (t - 1) + 6)
    return fr_fib_commute_pp(rt, t)

def fr_benefit_pp(rt, t):
    c = rt.cache[4]
    key = t
    if key in c:
        return c[key]
    val = _calc_benefit_pp(rt, t)
    c[key] = val
    return val

def _calc_benefit_sched(rt, k):
    """B(k): the decreasing shape's benefit after k months [S1][S6][S8].

        ``SA0 [(1+j_m)^N - (1+j_m)^k] / [(1+j_m)^N - 1]``, a mortgage-style amortization
        from ``B(0) = SA0`` to ``B(N) = 0``.  A zero schedule rate degenerates to straight
        line, which the closed form cannot express.
        """
    n_m = fr_term_mths(rt)
    jm = fr_sched_rate_mth(rt)
    if jm == 0.0:
        return fr_sum_assured(rt) * (n_m - k) / n_m
    return fr_sum_assured(rt) * ((1.0 + jm) ** n_m - (1.0 + jm) ** k) / ((1.0 + jm) ** n_m - 1.0)

def fr_benefit_sched(rt, k):
    c = rt.cache[5]
    key = k
    if key in c:
        return c[key]
    val = _calc_benefit_sched(rt, k)
    c[key] = val
    return val

def _calc_claim_expenses(rt, t):
    """ec D(t): the claim handling expense on the year's death and TI claims **[std]**.

        £250 per claim, uninflated.  Kept out of :func:`expenses` because the notes' worked
        example prints the two as separate columns.
        """
    return rt.ctx.expense_claim * fr_pols_death(rt, t)

def fr_claim_expenses(rt, t):
    c = rt.cache[6]
    key = t
    if key in c:
        return c[key]
    val = _calc_claim_expenses(rt, t)
    c[key] = val
    return val

def _calc_claims(rt, t, kind=None):
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
        return sum((fr_claims(rt, t, k) for k in ('DEATH', 'FIB', 'LAPSE')))
    if kind == 'DEATH':
        if fr_shape(rt) == 'fib':
            return fr_fib_commute_rate(rt) * fr_benefit_pp(rt, t) * fr_pols_death(rt, t)
        return fr_benefit_pp(rt, t) * fr_pols_death(rt, t)
    if kind == 'FIB':
        if fr_shape(rt) != 'fib':
            return 0.0
        return (1.0 - fr_fib_commute_rate(rt)) * fr_fib_income(rt) * (6.0 * fr_pols_death(rt, t) + 12.0 * fr_fib_cum(rt, t))
    if kind == 'LAPSE':
        return 0.0
    raise ValueError('invalid kind')

def fr_claims(rt, t, kind=None):
    c = rt.cache[7]
    key = (t, kind)
    if key in c:
        return c[key]
    val = _calc_claims(rt, t, kind)
    c[key] = val
    return val

def _calc_comm_clawback(rt, t):
    """Initial commission recovered on lapses inside the clawback window **[std]**.

        ``c0 (clawback_mths - 12t)/clawback_mths`` per lapsed policy, linear in months in
        force.  Off in the base run (``clawback_mths`` is 0); set it to 48 for the
        notes' four-year rule.  Clawback periods of two to four years are evidenced [R9];
        the linear formula is a standardization.  Inside the window it reverses the sign of
        the early-lapse sensitivity, which is the point of carrying it.
        """
    if rt.ctx.clawback_mths <= 0:
        return 0.0
    mths = 12 * t
    if mths >= rt.ctx.clawback_mths:
        return 0.0
    return fr_comm_init_pp(rt) * (rt.ctx.clawback_mths - mths) / rt.ctx.clawback_mths * fr_pols_lapse(rt, t)

def fr_comm_clawback(rt, t):
    c = rt.cache[8]
    key = t
    if key in c:
        return c[key]
    val = _calc_comm_clawback(rt, t)
    c[key] = val
    return val

def _calc_comm_init_pp(rt):
    """c0: initial commission per policy issued **[std]**.

        150% of the annualized premium, paid upfront at issue.  Roughly 96% of protection
        commission is paid upfront [R9], which with the acquisition expense is what
        produces the deep year-one new business strain in the worked example.
        """
    return rt.ctx.comm_init_rate * fr_premium_pp(rt, 1)

def fr_comm_init_pp(rt):
    c = rt.cache[9]
    key = None
    if key in c:
        return c[key]
    val = _calc_comm_init_pp(rt)
    c[key] = val
    return val

def _calc_commissions(rt, t):
    """Commission outgo in policy year t **[std]**, net of any clawback recovered.

        The initial commission in policy year 1, then 2.5% of premium income from policy
        year 2.  Both are levels chosen for the reference implementation; only the upfront
        *pattern* is evidenced [R9].
        """
    init = fr_comm_init_pp(rt) * fr_pols_if(rt, t) if t == 1 else 0.0
    renew = rt.ctx.comm_renewal_rate * fr_premiums(rt, t) if t >= 2 else 0.0
    return init + renew - fr_comm_clawback(rt, t)

def fr_commissions(rt, t):
    c = rt.cache[10]
    key = t
    if key in c:
        return c[key]
    val = _calc_commissions(rt, t)
    c[key] = val
    return val

def _calc_duration(rt, t):
    """Completed years since entry at the start of policy year t: ``t - 1``.

        The select duration, which is what the UK assured lives tables are indexed by
        alongside attained age.
        """
    return t - 1

def fr_duration(rt, t):
    c = rt.cache[11]
    key = t
    if key in c:
        return c[key]
    val = _calc_duration(rt, t)
    c[key] = val
    return val

def _calc_duration_inforce(rt):
    """Completed policy years already elapsed when the projection starts; 0 at issue."""
    return int(fr_model_point(rt)['duration_inforce'])

def fr_duration_inforce(rt):
    c = rt.cache[12]
    key = None
    if key in c:
        return c[key]
    val = _calc_duration_inforce(rt)
    c[key] = val
    return val

def _calc_expenses(rt, t):
    """E0 and e(t): acquisition and inflating maintenance expense in year t **[std]**.

        £150 per policy at issue, then £30 per policy per year inflating at 3%, both at the
        start of the year.  An in-force model point starts after policy year 1 and never
        sees the acquisition charge.  Premiums as low as £5/month against a £30 maintenance
        expense make this assumption solvency-relevant on small-sum-assured blocks, which is
        why the notes rate expense inflation a first-order lever despite its size.
        """
    acq = rt.ctx.expense_acq * fr_pols_if(rt, t) if t == 1 else 0.0
    return acq + rt.ctx.expense_maint * fr_inflation_factor(rt, t) * fr_pols_if(rt, t)

def fr_expenses(rt, t):
    c = rt.cache[13]
    key = t
    if key in c:
        return c[key]
    val = _calc_expenses(rt, t)
    c[key] = val
    return val

def _calc_fib_commute_pp(rt, t):
    """CV: the commuted value of one FIB stream arising from a death in year t **[std]**.

        ``I a(N - k)`` at the mid-year death month ``k = 12(t-1) + 6``, so it falls to zero
        as the term runs out.  Zero on the level and decreasing shapes.
        """
    if fr_shape(rt) != 'fib':
        return 0.0
    return fr_fib_income(rt) * fr_annuity_certain_factor(rt, fr_term_mths(rt) - (12 * (t - 1) + 6))

def fr_fib_commute_pp(rt, t):
    c = rt.cache[14]
    key = t
    if key in c:
        return c[key]
    val = _calc_fib_commute_pp(rt, t)
    c[key] = val
    return val

def _calc_fib_commute_rate(rt):
    """The proportion of FIB claims commuted to a lump sum **[std]**; 0 in the base run.

        The insurer may replace the remaining instalments with a lump sum determined
        "fairly and reasonably" [S6][S8]; no insurer publishes the basis, so both the
        take-up and the discount rate ``fib_commute_disc_rate`` are standardizations.
        """
    return float(fr_model_point(rt)['fib_commute_rate'])

def fr_fib_commute_rate(rt):
    c = rt.cache[15]
    key = None
    if key in c:
        return c[key]
    val = _calc_fib_commute_rate(rt)
    c[key] = val
    return val

def _calc_fib_cum(rt, t):
    """FIBcum(t): the expected FIB streams already in payment at the start of year t.

        ``sum of D(s) for s < t``.  **Not decremented** by mortality or lapse: once a claim
        is admitted the instalments are an annuity-certain to the end of the term whatever
        happens to any life [S6][S8].  Only *new* claims carry ``l(t)``.
        """
    if t <= fr_proj_start(rt):
        return 0.0
    return fr_fib_cum(rt, t - 1) + fr_pols_death(rt, t - 1)

def fr_fib_cum(rt, t):
    c = rt.cache[16]
    key = t
    if key in c:
        return c[key]
    val = _calc_fib_cum(rt, t)
    c[key] = val
    return val

def _calc_fib_income(rt):
    """I: the family income benefit, per month, on the ``fib`` shape [S2][S6][S8]."""
    return float(fr_model_point(rt)['fib_income'])

def fr_fib_income(rt):
    c = rt.cache[17]
    key = None
    if key in c:
        return c[key]
    val = _calc_fib_income(rt)
    c[key] = val
    return val

def _calc_idx_factor(rt, t):
    """idx(t): the cumulative **cover** indexation factor at the start of policy year t.

        1 in the first projected year and whenever the option is not elected.
        """
    if not fr_indexation(rt) or t <= fr_proj_start(rt):
        return 1.0
    return fr_idx_factor(rt, t - 1) * (1.0 + fr_idx_increase(rt))

def fr_idx_factor(rt, t):
    c = rt.cache[18]
    key = t
    if key in c:
        return c[key]
    val = _calc_idx_factor(rt, t)
    c[key] = val
    return val

def _calc_idx_increase(rt):
    """The cover increase offered at each anniversary under the indexation option.

        ``min(max(RPI, 0), 10%)`` [S1][S2][S6][S7], times ``idx_accept_rate``.  The
        notes' base run is deterministic and always accepts, which is what the shipped
        ``idx_accept_rate = 1`` means; their 80% take-up **[std]** would be a mixture of
        paths, and scaling the increase instead is a deterministic approximation to it.

        One consequence worth stating: with acceptance certain, the rule removing the option
        after three consecutive declines [S1][S6] (two at one insurer [S8]) is never
        reached, so it is not implemented.
        """
    return min(max(rt.ctx.rpi_rate, 0.0), rt.ctx.idx_cover_cap) * rt.ctx.idx_accept_rate

def fr_idx_increase(rt):
    c = rt.cache[19]
    key = None
    if key in c:
        return c[key]
    val = _calc_idx_increase(rt)
    c[key] = val
    return val

def _calc_idx_prem_factor(rt, t):
    """idx_p(t): the cumulative **premium** indexation factor at the start of year t.

        The premium rises by ``min(1.5 x increase, 15%)`` for a cover increase of
        ``increase`` [S1][S2][S6].  The 1.5 multiplier is what makes an accepted increase
        premium-margin-accretive if mortality is proportional to cover - and what reverses
        the sign of that conclusion if acceptance is selective, impaired lives accepting
        while healthy ones decline **[std]** concern.  No public take-up data exists.
        """
    if not fr_indexation(rt) or t <= fr_proj_start(rt):
        return 1.0
    return fr_idx_prem_factor(rt, t - 1) * (1.0 + min(rt.ctx.idx_prem_mult * fr_idx_increase(rt), rt.ctx.idx_prem_cap))

def fr_idx_prem_factor(rt, t):
    c = rt.cache[20]
    key = t
    if key in c:
        return c[key]
    val = _calc_idx_prem_factor(rt, t)
    c[key] = val
    return val

def _calc_indexation(rt):
    """Whether the RPI indexation option is elected [S1][S2][S6][S7].

        Restricted to the level shape **[std scope]**: no fetched insurer offers indexed
        decreasing cover, and the notes do not combine indexation with the FIB schedule
        either.
        """
    v = bool(fr_model_point(rt)['indexation'])
    if v and fr_shape(rt) != 'level':
        raise ValueError('indexation is modelled on the level shape only')
    return v

def fr_indexation(rt):
    c = rt.cache[21]
    key = None
    if key in c:
        return c[key]
    val = _calc_indexation(rt)
    c[key] = val
    return val

def _calc_inflation_factor(rt, t):
    """The expense inflation factor in policy year t: ``(1 + pi)^(t-1)`` **[std]**."""
    return (1.0 + rt.ctx.inflation_rate) ** (t - 1)

def fr_inflation_factor(rt, t):
    c = rt.cache[22]
    key = t
    if key in c:
        return c[key]
    val = _calc_inflation_factor(rt, t)
    c[key] = val
    return val

def _calc_is_joint(rt):
    """True when the policy covers two lives on a first-death basis.

        The policy pays once and ends; separation and replacement options create *new*
        policies and are out of scope **[std scope]**.
        """
    return bool(fr_model_point(rt)['joint_first_death'])

def fr_is_joint(rt):
    c = rt.cache[23]
    key = None
    if key in c:
        return c[key]
    val = _calc_is_joint(rt)
    c[key] = val
    return val

def _calc_lapse_cum(rt, t):
    """w_cum(t): the cumulative lapse proportion of the original cohort before year t.

        A proportion of ``pols_if_init()``, not a running total of :func:`lapse_rate`, and
        it drives a loading on **mortality** rather than on lapse.  Zero in the first
        projected year.
        """
    if t <= fr_proj_start(rt):
        return 0.0
    return fr_lapse_cum(rt, t - 1) + fr_pols_lapse(rt, t - 1) / fr_pols_if_init(rt)

def fr_lapse_cum(rt, t):
    c = rt.cache[24]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_cum(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate(rt, t):
    """w(t): the annual lapse rate applied at the end of policy year t.

        The table rate times the rebroking multiplier, capped at 1.  A lapse pays nothing:
        there is no surrender or paid-up value at any duration [S1][S6][S8][R8].
        """
    return min(1.0, fr_lapse_rate_base(rt, t) * fr_rebroke_factor(rt, t))

def fr_lapse_rate(rt, t):
    c = rt.cache[25]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate_base(rt, t):
    """The table lapse rate in policy year t **[std]**, before any rebroking multiplier.

        10 / 8 / 7 / 5 / 6 / 4 percent, anchored to the FCA's 5% average in-force lapse
        rate for pure protection and to the spike pattern just after the two- and four-year
        commission clawback periods end [R9].  A full duration curve is not public and the
        levels are standardized calibrations.  Policy years beyond the table take its last
        row.
        """
    tbl = rt.ctx.data.lapse_table()
    return float(tbl.loc[min(t, int(tbl.index.max())), 'lapse_rate'])

def fr_lapse_rate_base(rt, t):
    c = rt.cache[26]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate_base(rt, t)
    c[key] = val
    return val

def _calc_model_point(rt):
    """The selected model point as a Series."""
    return rt.ctx.data.model_point_table().loc[rt.ctx.point_id]

def fr_model_point(rt):
    c = rt.cache[27]
    key = None
    if key in c:
        return c[key]
    val = _calc_model_point(rt)
    c[key] = val
    return val

def _calc_mort_basis(rt):
    """Whether the mortality table is read as the *applied* rate or as an *ultimate* one.

        *applied* **[std]** takes ``mort_table.csv`` as the rate actually applied, which is
        how the notes quote their illustrative worked-example vector; *select* multiplies
        it by :func:`select_factor` and by ``mort_scale``, the notes' proxy for the
        unavailable subscriber tables.  See the Space docstring for why both are shipped.
        """
    v = fr_model_point(rt)['mort_basis']
    if v not in ('applied', 'select'):
        raise ValueError('invalid mort_basis')
    return v

def fr_mort_basis(rt):
    c = rt.cache[28]
    key = None
    if key in c:
        return c[key]
    val = _calc_mort_basis(rt)
    c[key] = val
    return val

def _calc_mort_rate(rt, t):
    """q(t): the mortality (incl. TI) decrement applied to the *policy* in year t.

        The single life's rate on a single-life policy.  On a joint first-death policy it
        is the joint decrement ``1 - (1 - q_1)(1 - q_2)`` **[std]** on one policy, which
        pays once and ends [S1][S6]; modelling the two lives as separate policies would pay
        twice.
        """
    q1 = fr_mort_rate_life(rt, t, 1)
    if not fr_is_joint(rt):
        return q1
    q2 = fr_mort_rate_life(rt, t, 2)
    return 1.0 - (1.0 - q1) * (1.0 - q2)

def fr_mort_rate(rt, t):
    c = rt.cache[29]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate(rt, t)
    c[key] = val
    return val

def _calc_mort_rate_base(rt, t, life=1):
    """The mortality table rate for ``life`` at its attained age in policy year t.

        Includes terminal illness, which is an acceleration of the death benefit rather
        than a separate cover [S1][S6][S8]; the 16-Series tables the shipped table proxies
        are graduated on that basis [R10].
        """
    return float(rt.ctx.data.mort_table().loc[(fr_sex(rt, life), fr_smoker(rt, life), fr_age(rt, t, life)), 'mort_rate'])

def fr_mort_rate_base(rt, t, life=1):
    c = rt.cache[30]
    key = (t, life)
    if key in c:
        return c[key]
    val = _calc_mort_rate_base(rt, t, life)
    c[key] = val
    return val

def _calc_mort_rate_life(rt, t, life=1):
    """The mortality (incl. TI) rate applied to ``life`` in policy year t.

        The table rate, then on the *select* basis the select factor and the **[std]** 75%
        proxy scaling, then the selective-lapsation loading.  Capped at 1.
        """
    q = fr_mort_rate_base(rt, t, life)
    if fr_mort_basis(rt) == 'select':
        q = q * fr_select_factor(rt, t) * rt.ctx.mort_scale
    return min(1.0, q * fr_sel_lapse_factor(rt, t))

def fr_mort_rate_life(rt, t, life=1):
    c = rt.cache[31]
    key = (t, life)
    if key in c:
        return c[key]
    val = _calc_mort_rate_life(rt, t, life)
    c[key] = val
    return val

def _calc_net_cf(rt, t):
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
    return fr_premiums(rt, t) - fr_claims(rt, t) - fr_claim_expenses(rt, t) - fr_expenses(rt, t) - fr_commissions(rt, t)

def fr_net_cf(rt, t):
    c = rt.cache[32]
    key = t
    if key in c:
        return c[key]
    val = _calc_net_cf(rt, t)
    c[key] = val
    return val

def _calc_policy_term(rt):
    """n: the term in years; 1-50 level, 5-50 decreasing, 5-40 FIB [S1][S6][S8]."""
    return int(fr_model_point(rt)['policy_term'])

def fr_policy_term(rt):
    c = rt.cache[33]
    key = None
    if key in c:
        return c[key]
    val = _calc_policy_term(rt)
    c[key] = val
    return val

def _calc_pols_death(rt, t):
    """D(t) = l(t) q(t): expected death and terminal illness claims in policy year t.

        One decrement covering both: terminal illness accelerates the death benefit rather
        than adding to it [S1][S6][S8].
        """
    return fr_pols_if(rt, t) * fr_mort_rate(rt, t)

def fr_pols_death(rt, t):
    c = rt.cache[34]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_death(rt, t)
    c[key] = val
    return val

def _calc_pols_if(rt, t):
    """l(t): the number of policies in force at the **start** of policy year t.

        ``pols_if_init()`` in the first projected year, then the notes' recursion
        ``l(t+1) = l(t)(1 - q(t))(1 - w(t))``.  This is the weight on every cash flow of
        the same ``result_cf()`` row.  Zero outside ``proj_start() .. proj_len()``: the
        cover has not started or has expired.
        """
    if t < fr_proj_start(rt) or t > fr_proj_len(rt):
        return 0.0
    if t == fr_proj_start(rt):
        return fr_pols_if_init(rt)
    return fr_pols_if_at(rt, t - 1, 'AFT_DECR')

def fr_pols_if(rt, t):
    c = rt.cache[35]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_if(rt, t)
    c[key] = val
    return val

def _calc_pols_if_at(rt, t, timing):
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
    if timing == 'BEF_DECR':
        return fr_pols_if(rt, t)
    if timing == 'BEF_LAPSE':
        return fr_pols_if(rt, t) * (1.0 - fr_mort_rate(rt, t))
    if timing == 'AFT_DECR':
        if t < fr_proj_start(rt) or t >= fr_proj_len(rt):
            return 0.0
        return fr_pols_if_at(rt, t, 'BEF_LAPSE') * (1.0 - fr_lapse_rate(rt, t))
    raise ValueError('invalid timing')

def fr_pols_if_at(rt, t, timing):
    c = rt.cache[36]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_pols_if_at(rt, t, timing)
    c[key] = val
    return val

def _calc_pols_if_init(rt):
    """Initial number of policies in force; 1.0 on a single-policy model point."""
    return float(fr_model_point(rt)['pols_if_init'])

def fr_pols_if_init(rt):
    c = rt.cache[37]
    key = None
    if key in c:
        return c[key]
    val = _calc_pols_if_init(rt)
    c[key] = val
    return val

def _calc_pols_lapse(rt, t):
    """Lapses at the end of policy year t, taken from the survivors of mortality.

        Pays nothing - there is no surrender value [S6][R8] - so this moves
        :func:`pols_if` and nothing else.
        """
    return fr_pols_if_at(rt, t, 'BEF_LAPSE') * fr_lapse_rate(rt, t)

def fr_pols_lapse(rt, t):
    c = rt.cache[38]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_lapse(rt, t)
    c[key] = val
    return val

def _calc_pols_payer(rt, t):
    """The number of in-force policies actually paying premium in policy year t.

        ``l(t)`` less the waived fraction.  Equal to :func:`pols_if` unless the waiver of
        premium rider is in force.
        """
    return fr_pols_if(rt, t) * (1.0 - fr_wop_waived_frac(rt, t))

def fr_pols_payer(rt, t):
    c = rt.cache[39]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_payer(rt, t)
    c[key] = val
    return val

def _calc_premium_mth_pp(rt):
    """P_m: the guaranteed monthly premium per policy **[std]**.

        A pure modelling value.  No UK insurer publishes premium rate tables - pricing is
        quote-driven and only the £5/month minimum is public [S5] - so any reference
        premium basis is constructed rather than observed.  It is guaranteed level for the
        full term [S2][S6][S9], which is what puts every year of premium inside the
        Solvency UK contract boundary [R3].
        """
    return float(fr_model_point(rt)['premium_mth'])

def fr_premium_mth_pp(rt):
    c = rt.cache[40]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_mth_pp(rt)
    c[key] = val
    return val

def _calc_premium_pp(rt, t):
    """P_a idx_p(t): the annualized gross premium per policy in policy year t.

        ``12 P_m``, indexed if the option is elected, and loaded by
        ``wop_prem_loading`` where the waiver rider is in force - a **[std]**
        placeholder, since the rider's extra premium is not published either.
        """
    p = 12.0 * fr_premium_mth_pp(rt) * fr_idx_prem_factor(rt, t)
    return p * (1.0 + rt.ctx.wop_prem_loading) if fr_wop(rt) else p

def fr_premium_pp(rt, t):
    c = rt.cache[41]
    key = t
    if key in c:
        return c[key]
    val = _calc_premium_pp(rt, t)
    c[key] = val
    return val

def _calc_premiums(rt, t):
    """Premium income at the start of policy year t, an inflow.

        Carried on :func:`pols_payer`, never on the FIB ledger: premiums stop at death
        while family income benefit instalments continue.  Annual in advance with no
        allowance for premiums ceasing at a mid-year death or lapse, which slightly
        overstates income - the known bias of this convention **[std]**, offset by the
        mid-year benefit timing of the decreasing shape.
        """
    return fr_premium_pp(rt, t) * fr_pols_payer(rt, t)

def fr_premiums(rt, t):
    c = rt.cache[42]
    key = t
    if key in c:
        return c[key]
    val = _calc_premiums(rt, t)
    c[key] = val
    return val

def _calc_proj_len(rt):
    """Projection length in policy years: the term, exactly.

        Cover ceases at the end of the term with no maturity value, no renewal and no
        conversion [S1][S2][S6][S8][R8], so the horizon is ``n`` and there is nothing after
        it - the structural contrast with ``Term_US_A``, which runs on to attained age 95.
        """
    return fr_policy_term(rt)

def fr_proj_len(rt):
    c = rt.cache[43]
    key = None
    if key in c:
        return c[key]
    val = _calc_proj_len(rt)
    c[key] = val
    return val

def _calc_proj_start(rt):
    """The first projected policy year: ``duration_inforce() + 1``.

        1 at issue, so the acquisition expense and the initial commission fall inside the
        projection; an in-force model point starts later and never sees either.
        """
    return fr_duration_inforce(rt) + 1

def fr_proj_start(rt):
    c = rt.cache[44]
    key = None
    if key in c:
        return c[key]
    val = _calc_proj_start(rt)
    c[key] = val
    return val

def _calc_rebroke_factor(rt, t):
    """M_reb(t): the rebroking multiplier on the lapse rate **[std]**; 1 in the base run.

        ``min(rebroke_cap, max(1, P_inforce / P_market))``.  Premiums are guaranteed, so
        there is no premium-shock lapse to model; the economic driver is rebroking when
        market premiums for the attained age fall below the in-force premium.
        ``premium_market_ratio`` is a flat scalar, so the multiplier is level in ``t`` -
        a market premium path would be another input table.
        """
    return min(rt.ctx.rebroke_cap, max(1.0, rt.ctx.premium_market_ratio))

def fr_rebroke_factor(rt, t):
    c = rt.cache[45]
    key = t
    if key in c:
        return c[key]
    val = _calc_rebroke_factor(rt, t)
    c[key] = val
    return val

def _calc_sched_rate(rt):
    """j: the decreasing shape's schedule rate p.a. **[std]**, 6% on the shipped points.

        Contractual, not experience: the client selects it at outset and the benefit
        amortizes at it whatever happens to interest rates [S1][S6][S8].  The risk it
        carries is therefore specification error - mis-implementing the amortization or the
        monthly convention - rather than assumption error.
        """
    return float(fr_model_point(rt)['sched_rate'])

def fr_sched_rate(rt):
    c = rt.cache[46]
    key = None
    if key in c:
        return c[key]
    val = _calc_sched_rate(rt)
    c[key] = val
    return val

def _calc_sched_rate_mth(rt):
    """j_m = (1+j)^(1/12) - 1: the decreasing schedule's monthly rate **[std]**.

        The effective convention, not a nominal ``j/12``.  The two give slightly different
        schedules, so the convention has to be stated; ``benefit_sched(60) = £134,588`` on
        the anchor cell is the notes' validation anchor for an implementation.
        """
    return (1.0 + fr_sched_rate(rt)) ** (1.0 / 12.0) - 1.0

def fr_sched_rate_mth(rt):
    c = rt.cache[47]
    key = None
    if key in c:
        return c[key]
    val = _calc_sched_rate_mth(rt)
    c[key] = val
    return val

def _calc_sel_lapse_factor(rt, t):
    """The selective-lapsation loading on mortality in policy year t **[std]**.

        ``1 + lambda max(0, w_cum(t) - w_ref)``.  Lapsers are healthier than persisters, so
        a block that has already shed a large proportion of its lives carries impaired
        mortality on the remainder - guaranteed premiums plus healthy-life rebroking make
        this a structural feature of UK term rather than an incidental one.  Off in the base
        run (``sel_lapse_lambda = 0``), where it returns 1 in every year.
        """
    return 1.0 + rt.ctx.sel_lapse_lambda * max(0.0, fr_lapse_cum(rt, t) - rt.ctx.sel_lapse_ref)

def fr_sel_lapse_factor(rt, t):
    c = rt.cache[48]
    key = t
    if key in c:
        return c[key]
    val = _calc_sel_lapse_factor(rt, t)
    c[key] = val
    return val

def _calc_select_factor(rt, t):
    """The select-duration factor applying in policy year t **[std]**.

        A 5-year select period, the structure of TMNL16/TFNL16 [R12], with the factor
        grading from 0.55 at duration 0 to 1.00 at and beyond ``select_period``.  Read
        only on the *select* mortality basis; the *applied* basis takes the table as it
        stands.  The values are a standardization - the real tables are subscriber-only
        [R11] - and a licensed basis drops in by replacing the CSV.
        """
    d = min(fr_duration(rt, t), rt.ctx.select_period)
    return float(rt.ctx.data.select_factor_table().loc[d, 'factor'])

def fr_select_factor(rt, t):
    c = rt.cache[49]
    key = t
    if key in c:
        return c[key]
    val = _calc_select_factor(rt, t)
    c[key] = val
    return val

def _calc_sex(rt, life=1):
    """The sex (M / F) of the first or second life."""
    if life == 1:
        return fr_model_point(rt)['sex']
    if life == 2 and fr_is_joint(rt):
        return fr_model_point(rt)['joint_sex']
    raise ValueError('invalid life')

def fr_sex(rt, life=1):
    c = rt.cache[50]
    key = life
    if key in c:
        return c[key]
    val = _calc_sex(rt, life)
    c[key] = val
    return val

def _calc_shape(rt):
    """The benefit shape: ``level``, ``decreasing`` or ``fib`` [S1][S2][S6][S8]."""
    v = fr_model_point(rt)['shape']
    if v not in ('level', 'decreasing', 'fib'):
        raise ValueError('invalid shape')
    return v

def fr_shape(rt):
    c = rt.cache[51]
    key = None
    if key in c:
        return c[key]
    val = _calc_shape(rt)
    c[key] = val
    return val

def _calc_smoker(rt, life=1):
    """The smoker status (N / S) of the first or second life."""
    if life == 1:
        return fr_model_point(rt)['smoker']
    if life == 2 and fr_is_joint(rt):
        return fr_model_point(rt)['joint_smoker']
    raise ValueError('invalid life')

def fr_smoker(rt, life=1):
    c = rt.cache[52]
    key = life
    if key in c:
        return c[key]
    val = _calc_smoker(rt, life)
    c[key] = val
    return val

def _calc_sum_assured(rt):
    """SA0: the initial sum assured of the level and decreasing shapes [S1][S6]."""
    return float(fr_model_point(rt)['sum_assured'])

def fr_sum_assured(rt):
    c = rt.cache[53]
    key = None
    if key in c:
        return c[key]
    val = _calc_sum_assured(rt)
    c[key] = val
    return val

def _calc_term_mths(rt):
    """N = 12n: the term in months, the horizon of the benefit schedules."""
    return 12 * fr_policy_term(rt)

def fr_term_mths(rt):
    c = rt.cache[54]
    key = None
    if key in c:
        return c[key]
    val = _calc_term_mths(rt)
    c[key] = val
    return val

def _calc_wop(rt):
    """Whether the waiver of premium rider is in force [S1]; false in the base run."""
    return bool(fr_model_point(rt)['wop'])

def fr_wop(rt):
    c = rt.cache[55]
    key = None
    if key in c:
        return c[key]
    val = _calc_wop(rt)
    c[key] = val
    return val

def _calc_wop_waived_frac(rt, t):
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
    if not fr_wop(rt) or t <= fr_proj_start(rt):
        return 0.0
    u = fr_wop_waived_frac(rt, t - 1)
    return u * (1.0 - rt.ctx.wop_rec_rate) + (1.0 - u) * rt.ctx.wop_inc_rate

def fr_wop_waived_frac(rt, t):
    c = rt.cache[56]
    key = t
    if key in c:
        return c[key]
    val = _calc_wop_waived_frac(rt, t)
    c[key] = val
    return val

def evaluate(rt, ctx):
    rt.bind(ctx)
    return fr_bench_net_cf(rt)
