# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False

"""Generated static fast-recursive reference runtime."""

class FastRecursiveRuntime:

    def __init__(self, ctx=None):
        self.ctx = ctx
        self.cache = [dict() for _ in range(52)]

    def bind(self, ctx):
        self.ctx = ctx
        for c in self.cache:
            c.clear()
        return self

cdef object _calc_adb_multiplier(rt):
    """k_adb: the accidental death multiplier past the moratorium, 1 or 2.

        The 2 is one insurer's variant and applies to **accidental** death **on and after
        the first anniversary** only.  Inside the moratorium the accidental benefit is
        already the full cash sum, so doubling it there - or applying the multiplier to all
        deaths - overstates outgo.
        """
    return 2.0 if bool(fr_model_point(rt)['variant_adb_2x']) else 1.0

cdef object fr_adb_multiplier(rt):
    c = rt.cache[0]
    key = None
    if key in c:
        return c[key]
    val = _calc_adb_multiplier(rt)
    c[key] = val
    return val

cdef object _calc_age(rt, t):
    """a(t): the attained age (ALB) in the policy year containing month t."""
    return fr_age_at_entry(rt) + fr_duration(rt, t)

cdef object fr_age(rt, t):
    c = rt.cache[1]
    key = t
    if key in c:
        return c[key]
    val = _calc_age(rt, t)
    c[key] = val
    return val

cdef object _calc_age_at_entry(rt):
    """The entry age of the selected model point, **age last birthday**.

        ALB rather than the age nearest birthday every other model in this library uses:
        the underwritten cell's specimen defines entry age x as "before the (x+1)th
        birthday", which is ALB, and the over-50s documents price on "age at outset" without
        stating a basis **[std]**.  All age lookups here are on that one basis.
        """
    return int(fr_model_point(rt)['entry_age'])

cdef object fr_age_at_entry(rt):
    c = rt.cache[2]
    key = None
    if key in c:
        return c[key]
    val = _calc_age_at_entry(rt)
    c[key] = val
    return val

cdef object _calc_bench_net_cf(rt):
    return sum((fr_net_cf(rt, t) for t in range(1, fr_proj_len(rt) + 1)))

cdef object fr_bench_net_cf(rt):
    c = rt.cache[3]
    key = None
    if key in c:
        return c[key]
    val = _calc_bench_net_cf(rt)
    c[key] = val
    return val

cdef object _calc_benefit_pp(rt, t, kind):
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
    if kind == 'NON_ACC':
        if fr_cell(rt) == 'O50' and fr_in_moratorium(rt, t):
            return fr_prem_cum_pp(rt, t)
        return fr_cover_pp(rt, t)
    if kind == 'ACC':
        if fr_cell(rt) != 'O50':
            return fr_cover_pp(rt, t)
        if fr_in_moratorium(rt, t):
            return fr_cover_pp(rt, t)
        return fr_adb_multiplier(rt) * fr_cover_pp(rt, t)
    if kind == 'DEATH':
        if fr_cell(rt) == 'O50':
            return (1.0 - rt.ctx.acc_share) * fr_benefit_pp(rt, t, 'NON_ACC') + rt.ctx.acc_share * fr_benefit_pp(rt, t, 'ACC')
        if t <= rt.ctx.suicide_mths:
            return (1.0 - rt.ctx.suicide_share) * fr_cover_pp(rt, t) + rt.ctx.suicide_share * fr_prem_cum_pp(rt, t)
        return fr_cover_pp(rt, t)
    if kind == 'PAID_UP':
        if not fr_pu_variant(rt):
            return 0.0
        return fr_cover_pp(rt, t) * fr_payments_made(rt, t) / fr_payments_expected(rt)
    raise ValueError('invalid kind')

cdef object fr_benefit_pp(rt, t, kind):
    c = rt.cache[4]
    key = (t, kind)
    if key in c:
        return c[key]
    val = _calc_benefit_pp(rt, t, kind)
    c[key] = val
    return val

cdef object _calc_cell(rt):
    """``O50`` (over-50s guaranteed acceptance) or ``UW`` (underwritten guaranteed).

        The two cells share this engine and not their mortality basis, their lapse table,
        their expense levels or their benefit rules.  See the Space docstring.
        """
    v = fr_model_point(rt)['cell']
    if v not in ('O50', 'UW'):
        raise ValueError('invalid cell')
    return v

cdef object fr_cell(rt):
    c = rt.cache[5]
    key = None
    if key in c:
        return c[key]
    val = _calc_cell(rt)
    c[key] = val
    return val

cdef object _calc_cessation_mths(rt):
    """T_cess: months from outset to premium cessation; 0 means premiums for life.

        The over-50s cells cease at the anniversary on or after the 90th birthday **[std]**
        and cover continues; the underwritten cell has no cessation at all.
        """
    return int(fr_model_point(rt)['cessation_months'])

cdef object fr_cessation_mths(rt):
    c = rt.cache[6]
    key = None
    if key in c:
        return c[key]
    val = _calc_cessation_mths(rt)
    c[key] = val
    return val

cdef object _calc_claims(rt, t, kind=None):
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
        return sum((fr_claims(rt, t, k) for k in ('DEATH', 'DEATH_PU', 'LAPSE')))
    if kind == 'DEATH':
        return fr_pols_death(rt, t) * fr_benefit_pp(rt, t, 'DEATH')
    if kind == 'DEATH_PU':
        return fr_pu_benefit(rt, t) * fr_mort_rate_mth(rt, t)
    if kind == 'LAPSE':
        return 0.0
    raise ValueError('invalid kind')

cdef object fr_claims(rt, t, kind=None):
    c = rt.cache[7]
    key = (t, kind)
    if key in c:
        return c[key]
    val = _calc_claims(rt, t, kind)
    c[key] = val
    return val

cdef object _calc_commissions(rt, t):
    """Initial commission in month t **[std]**: a share of the first year's premiums.

        The existence of commission is sourced - an intermediary is "paid by commission as a
        percentage of total annual premium" - and the level is a standardization.
        """
    if fr_policy_year(rt, t) > 1:
        return 0.0
    return rt.ctx.comm_init_rate * fr_premiums(rt, t)

cdef object fr_commissions(rt, t):
    c = rt.cache[8]
    key = t
    if key in c:
        return c[key]
    val = _calc_commissions(rt, t)
    c[key] = val
    return val

cdef object _calc_cover_pp(rt, t):
    """SA(t): the sum assured or cash sum in force in month t.

        Steps at policy anniversaries.  On the RPI variant the cash sum **continues to
        index after premiums cease at 90**, which is why this carries no cessation test -
        the premium step, being applied to a zero premium, stops of its own accord.
        """
    return fr_sum_assured(rt) * (1.0 + fr_esc_cover_step(rt)) ** (fr_policy_year(rt, t) - 1)

cdef object fr_cover_pp(rt, t):
    c = rt.cache[9]
    key = t
    if key in c:
        return c[key]
    val = _calc_cover_pp(rt, t)
    c[key] = val
    return val

cdef object _calc_duration(rt, t):
    """Completed policy years at the start of month t: ``(t - 1) // 12``."""
    return (t - 1) // 12

cdef object fr_duration(rt, t):
    c = rt.cache[10]
    key = t
    if key in c:
        return c[key]
    val = _calc_duration(rt, t)
    c[key] = val
    return val

cdef object _calc_esc_cover_step(rt):
    """The annual increase in the sum assured under the escalation variant.

        5% on the underwritten increasing-cover variant, and RPI floored at 0 and capped at
        10% on the over-50s RPI variant.  Scaled by ``esc_take_up``, which is 1 in the
        base run: holders may decline an increase, with three declines removing the option,
        but a deterministic run cannot represent a take-up probability, so full take-up is
        assumed and the decline rule is not implemented.
        """
    e = fr_escalation(rt)
    if e == 'level':
        return 0.0
    if e == 'fixed_5pct':
        return rt.ctx.esc_fixed_cover * rt.ctx.esc_take_up
    return min(max(rt.ctx.rpi_rate, 0.0), rt.ctx.esc_rpi_cover_cap) * rt.ctx.esc_take_up

cdef object fr_esc_cover_step(rt):
    c = rt.cache[11]
    key = None
    if key in c:
        return c[key]
    val = _calc_esc_cover_step(rt)
    c[key] = val
    return val

cdef object _calc_esc_prem_step(rt):
    """The annual increase in the premium under the escalation variant.

        10% on the underwritten variant - two percent of premium for each one percent of
        cover - and ``1.5 x RPI`` capped at 15% on the over-50s RPI variant.  Floored at 0:
        the source defines an increase only, with no decrease **[std]**.
        """
    e = fr_escalation(rt)
    if e == 'level':
        return 0.0
    if e == 'fixed_5pct':
        return rt.ctx.esc_fixed_prem * rt.ctx.esc_take_up
    return min(max(rt.ctx.esc_rpi_prem_mult * rt.ctx.rpi_rate, 0.0), rt.ctx.esc_rpi_prem_cap) * rt.ctx.esc_take_up

cdef object fr_esc_prem_step(rt):
    c = rt.cache[12]
    key = None
    if key in c:
        return c[key]
    val = _calc_esc_prem_step(rt)
    c[key] = val
    return val

cdef object _calc_escalation(rt):
    """``level``, ``fixed_5pct`` (the UW increasing-cover variant) or ``rpi``.

        The underwritten variant raises cover 5% and premium 10% a year - two percent of
        premium for each one percent of cover - and the over-50s RPI variant raises the cash
        sum by RPI capped at 10% and the premium by 1.5 x RPI capped at 15%.
        """
    v = fr_model_point(rt)['escalation']
    if v not in ('level', 'fixed_5pct', 'rpi'):
        raise ValueError('invalid escalation')
    return v

cdef object fr_escalation(rt):
    c = rt.cache[13]
    key = None
    if key in c:
        return c[key]
    val = _calc_escalation(rt)
    c[key] = val
    return val

cdef object _calc_expense_acq_pp(rt):
    """The acquisition expense per policy at issue **[std]**: £150 on O50, £300 on UW."""
    return rt.ctx.expense_acq_o50 if fr_cell(rt) == 'O50' else rt.ctx.expense_acq_uw

cdef object fr_expense_acq_pp(rt):
    c = rt.cache[14]
    key = None
    if key in c:
        return c[key]
    val = _calc_expense_acq_pp(rt)
    c[key] = val
    return val

cdef object _calc_expense_maint_pp(rt):
    """The annual maintenance expense per policy **[std]**: £30 on O50, £50 on UW.

        Premiums are level and small - £30 a month on the anchor cell - while this inflates,
        so the expense margin erodes mechanically over a twenty-year-plus horizon.  A
        per-policy expense error compounds accordingly.
        """
    return rt.ctx.expense_maint_o50 if fr_cell(rt) == 'O50' else rt.ctx.expense_maint_uw

cdef object fr_expense_maint_pp(rt):
    c = rt.cache[15]
    key = None
    if key in c:
        return c[key]
    val = _calc_expense_maint_pp(rt)
    c[key] = val
    return val

cdef object _calc_expenses(rt, t):
    """Acquisition and maintenance expense in month t **[std]**.

        The acquisition charge falls once, at issue.  Maintenance is carried on
        :func:`pols_all`, so a paid-up policy still costs money to administer even though it
        pays no premium - which is part of why the pro-rata paid-up variant is expensive.
        """
    acq = fr_expense_acq_pp(rt) * fr_pols_if(rt, t) if t == 1 else 0.0
    return acq + fr_expense_maint_pp(rt) / 12.0 * fr_inflation_factor(rt, t) * fr_pols_all(rt, t)

cdef object fr_expenses(rt, t):
    c = rt.cache[16]
    key = t
    if key in c:
        return c[key]
    val = _calc_expenses(rt, t)
    c[key] = val
    return val

cdef object _calc_in_moratorium(rt, t):
    """Whether month t falls inside the over-50s moratorium; always False on the UW cell."""
    return t <= fr_moratorium_mths(rt)

cdef object fr_in_moratorium(rt, t):
    c = rt.cache[17]
    key = t
    if key in c:
        return c[key]
    val = _calc_in_moratorium(rt, t)
    c[key] = val
    return val

cdef object _calc_inflation_factor(rt, t):
    """The expense inflation factor in month t: ``(1 + pi)^(y - 1)`` **[std]**.

        Steps on policy anniversaries, not monthly, which is how the notes write it.
        """
    return (1.0 + rt.ctx.inflation_rate) ** (fr_policy_year(rt, t) - 1)

cdef object fr_inflation_factor(rt, t):
    c = rt.cache[18]
    key = t
    if key in c:
        return c[key]
    val = _calc_inflation_factor(rt, t)
    c[key] = val
    return val

cdef object _calc_lapse_rate(rt, t):
    """w(y): the annual lapse rate applying at the end of month t.

        **Zero once premiums have ceased**: there is nothing left to stop paying, and
        applying a lapse decrement there silently destroys liability - the notes list it as
        a pitfall.  Otherwise the table rate, optionally stressed by
        ``1 + beta`` past the crossover, which is off in the base run.
        """
    if fr_cessation_mths(rt) > 0 and t > fr_cessation_mths(rt):
        return 0.0
    w = fr_lapse_rate_base(rt, t)
    if rt.ctx.lapse_crossover_beta > 0.0 and fr_prem_cum_pp(rt, t) > fr_cover_pp(rt, t):
        w = w * (1.0 + rt.ctx.lapse_crossover_beta)
    return min(1.0, w)

cdef object fr_lapse_rate(rt, t):
    c = rt.cache[19]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate(rt, t)
    c[key] = val
    return val

cdef object _calc_lapse_rate_base(rt, t):
    """The table annual lapse rate in month t **[std]**, before the crossover stress.

        Read from the cell's own row of the lapse table; policy years beyond the table take
        its last row.  Both tables are drafting constructions - no public UK whole of life
        lapse study was retrieved - and on a product with no surrender value they are the
        single largest lever on the liability.
        """
    tbl = rt.ctx.data.lapse_table().loc[fr_cell(rt)]
    y = fr_policy_year(rt, t)
    return float(tbl.loc[min(y, int(tbl.index.max())), 'lapse_rate'])

cdef object fr_lapse_rate_base(rt, t):
    c = rt.cache[20]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate_base(rt, t)
    c[key] = val
    return val

cdef object _calc_lapse_rate_mth(rt, t):
    """w_m(y) = 1 - (1 - w)^(1/12): the monthly lapse rate **[std]**."""
    return 1.0 - (1.0 - fr_lapse_rate(rt, t)) ** (1.0 / 12.0)

cdef object fr_lapse_rate_mth(rt, t):
    c = rt.cache[21]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate_mth(rt, t)
    c[key] = val
    return val

cdef object _calc_model_point(rt):
    """The selected model point as a Series."""
    return rt.ctx.data.model_point_table().loc[rt.ctx.point_id]

cdef object fr_model_point(rt):
    c = rt.cache[22]
    key = None
    if key in c:
        return c[key]
    val = _calc_model_point(rt)
    c[key] = val
    return val

cdef object _calc_moratorium_mths(rt):
    """The over-50s moratorium in months, 12; zero on the underwritten cell.

        The underwritten cell has a suicide clause over the same window instead, which is a
        different rule with a different denominator - see :func:`benefit_pp`.
        """
    return int(fr_model_point(rt)['moratorium_months'])

cdef object fr_moratorium_mths(rt):
    c = rt.cache[23]
    key = None
    if key in c:
        return c[key]
    val = _calc_moratorium_mths(rt)
    c[key] = val
    return val

cdef object _calc_mort_basis(rt):
    """The mortality basis the cell takes: ``population`` for O50, ``assured`` for UW.

        Derived from :func:`cell` rather than left as a free parameter, because feeding
        either cell the other's basis produces plausible-looking but wrong margins.  See the
        Space docstring.
        """
    return 'population' if fr_cell(rt) == 'O50' else 'assured'

cdef object fr_mort_basis(rt):
    c = rt.cache[24]
    key = None
    if key in c:
        return c[key]
    val = _calc_mort_basis(rt)
    c[key] = val
    return val

cdef object _calc_mort_improve_factor(rt, t):
    """The mortality improvement factor in month t; 1 in the base run **[std]**.

        ``(1 - improvement)^(y - 1)``.  The market-standard expression is a CMI projections
        model with a chosen long-term rate, but that model is subscriber-restricted, so a
        flat annual improvement is the **[std]** sensitivity proxy.  Improvements lengthen
        exactly the part of the liability that is pure outgo - past the crossover and past
        premium cessation - so this is not a second-order dial on this product.
        """
    return (1.0 - rt.ctx.mort_improvement) ** (fr_policy_year(rt, t) - 1)

cdef object fr_mort_improve_factor(rt, t):
    c = rt.cache[25]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_improve_factor(rt, t)
    c[key] = val
    return val

cdef object _calc_mort_loading(rt):
    """The anti-selection loading on the table rate: 120% for O50, 100% for UW **[std]**.

        Guaranteed acceptance removes underwriting, so the pool cannot be better than the
        population and self-selects worse.  No insurer discloses its guaranteed-acceptance
        pricing basis, so the loading is a placeholder to be calibrated - and a deliberately
        modest one, since population mortality is already heavier than insured experience.
        """
    return rt.ctx.mort_loading_o50 if fr_cell(rt) == 'O50' else rt.ctx.mort_loading_uw

cdef object fr_mort_loading(rt):
    c = rt.cache[26]
    key = None
    if key in c:
        return c[key]
    val = _calc_mort_loading(rt)
    c[key] = val
    return val

cdef object _calc_mort_rate(rt, t):
    """q(y): the annual mortality rate applied in the policy year containing month t.

        The cell's table rate at the attained age, times the anti-selection loading and the
        improvement factor, capped at 1.  Both shipped bases are **[std]** proxies shaped
        like the tables the notes name and are not published tables.
        """
    q = float(rt.ctx.data.mort_table().loc[(fr_mort_basis(rt), fr_sex(rt), fr_smoker(rt), fr_age(rt, t)), 'mort_rate'])
    return min(1.0, q * fr_mort_loading(rt) * fr_mort_improve_factor(rt, t))

cdef object fr_mort_rate(rt, t):
    c = rt.cache[27]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate(rt, t)
    c[key] = val
    return val

cdef object _calc_mort_rate_mth(rt, t):
    """q_m(y) = 1 - (1 - q)^(1/12): the monthly mortality rate **[std]**."""
    return 1.0 - (1.0 - fr_mort_rate(rt, t)) ** (1.0 / 12.0)

cdef object fr_mort_rate_mth(rt, t):
    c = rt.cache[28]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate_mth(rt, t)
    c[key] = val
    return val

cdef object _calc_net_cf(rt, t):
    """CF(t): the net cash flow of month t, **income positive**.

        Premiums less death outgo, expenses and commission.  The notes' own sign and the
        library-wide one, so there is no outgo-positive ``liability_cf`` companion.

        Note that the notes' worked-example table prints premium income and death outgo as
        separate positive columns and omits expenses "for clarity", so ``net_cf`` will not
        equal any column of that table.  Lapse contributes nothing at all: it moves
        :func:`pols_if` and pays no cash.
        """
    return fr_premiums(rt, t) - fr_claims(rt, t) - fr_expenses(rt, t) - fr_commissions(rt, t)

cdef object fr_net_cf(rt, t):
    c = rt.cache[29]
    key = t
    if key in c:
        return c[key]
    val = _calc_net_cf(rt, t)
    c[key] = val
    return val

cdef object _calc_payments_expected(rt):
    """N_expected: the payments expected over the premium-paying period.

        The pro-rata paid-up denominator, so it is the cessation month; zero where premiums
        are payable for life, in which case the variant does not apply.
        """
    return fr_cessation_mths(rt)

cdef object fr_payments_expected(rt):
    c = rt.cache[30]
    key = None
    if key in c:
        return c[key]
    val = _calc_payments_expected(rt)
    c[key] = val
    return val

cdef object _calc_payments_made(rt, t):
    """N_paid(t): the number of monthly payments made by the end of month t."""
    if fr_cessation_mths(rt) <= 0:
        return t
    return min(t, fr_cessation_mths(rt))

cdef object fr_payments_made(rt, t):
    c = rt.cache[31]
    key = t
    if key in c:
        return c[key]
    val = _calc_payments_made(rt, t)
    c[key] = val
    return val

cdef object _calc_policy_year(rt, t):
    """y = floor((t-1)/12) + 1: the policy year containing month t; 1 for t = 1..12."""
    return fr_duration(rt, t) + 1

cdef object fr_policy_year(rt, t):
    c = rt.cache[32]
    key = t
    if key in c:
        return c[key]
    val = _calc_policy_year(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_all(rt, t):
    """All policies in force at the start of month t: full cover plus paid-up.

        The weight on the maintenance expense, and the count the roll-forward closes on.
        """
    return fr_pols_if(rt, t) + fr_pols_pu(rt, t)

cdef object fr_pols_all(rt, t):
    c = rt.cache[33]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_all(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_convert(rt, t):
    """Would-be lapses converted to paid-up at the end of month t.

        All of them once the pro-rata paid-up halfway point is passed **[std]**, none before
        it, and none at all without the variant.  A state change, not a cash flow.
        """
    return fr_pols_exit(rt, t) if fr_pu_eligible(rt, t) else 0.0

cdef object fr_pols_convert(rt, t):
    c = rt.cache[34]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_convert(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_death(rt, t):
    """Deaths on full cover at the end of month t, against the start-of-month in-force."""
    return fr_pols_if(rt, t) * fr_mort_rate_mth(rt, t)

cdef object fr_pols_death(rt, t):
    c = rt.cache[35]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_death(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_exit(rt, t):
    """Would-be lapses at the end of month t, taken from the survivors of mortality.

        What happens to them depends on :func:`pu_eligible`: they either terminate for
        nothing or convert to paid-up.
        """
    return fr_pols_if_at(rt, t, 'BEF_LAPSE') * fr_lapse_rate_mth(rt, t)

cdef object fr_pols_exit(rt, t):
    c = rt.cache[36]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_exit(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_if(rt, t):
    """l(t-1): full-cover policies in force at the **start** of policy month t.

        The notes' in-force probability, and the column their worked-example table prints.
        Paid-up policies are **not** counted here: they are a separate strand,
        :func:`pols_pu`, because their benefit is a reduced amount.  On every model point
        without the pro-rata paid-up variant the two coincide with :func:`pols_all`.
        """
    if t < 1 or t > fr_proj_len(rt):
        return 0.0
    if t == 1:
        return fr_pols_if_init(rt)
    return fr_pols_if(rt, t - 1) * (1.0 - fr_mort_rate_mth(rt, t - 1)) * (1.0 - fr_lapse_rate_mth(rt, t - 1))

cdef object fr_pols_if(rt, t):
    c = rt.cache[37]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_if(rt, t)
    c[key] = val
    return val

cdef object _calc_pols_if_at(rt, t, timing):
    """The number of full-cover policies in force at a point inside month t.

        ``"BEF_DECR"``
            the start of the month, before any decrement; :func:`pols_if`.

        ``"BEF_LAPSE"``
            after deaths, before lapses - the notes' processing order is
            **death before lapse** **[std]**.

        ``"AFT_DECR"``
            the notes' ``l(t)``, the end-of-month count.
        """
    if timing == 'BEF_DECR':
        return fr_pols_if(rt, t)
    if timing == 'BEF_LAPSE':
        return fr_pols_if(rt, t) * (1.0 - fr_mort_rate_mth(rt, t))
    if timing == 'AFT_DECR':
        if t < 1 or t >= fr_proj_len(rt):
            return 0.0
        return fr_pols_if(rt, t + 1)
    raise ValueError('invalid timing')

cdef object fr_pols_if_at(rt, t, timing):
    c = rt.cache[38]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_pols_if_at(rt, t, timing)
    c[key] = val
    return val

cdef object _calc_pols_if_init(rt):
    """Initial number of policies in force; 1.0 on a single-policy model point."""
    return float(fr_model_point(rt)['pols_if_init'])

cdef object fr_pols_if_init(rt):
    c = rt.cache[39]
    key = None
    if key in c:
        return c[key]
    val = _calc_pols_if_init(rt)
    c[key] = val
    return val

cdef object _calc_pols_pu(rt, t):
    """Paid-up policies in force at the start of month t.

        Zero without the pro-rata paid-up variant.  Paid-up policies pay no premium, carry no
        lapse decrement and do not escalate, so they roll forward on mortality alone and take
        conversions in from the full-cover strand.
        """
    if t < 1 or t > fr_proj_len(rt) or (not fr_pu_variant(rt)):
        return 0.0
    if t == 1:
        return 0.0
    return fr_pols_pu(rt, t - 1) * (1.0 - fr_mort_rate_mth(rt, t - 1)) + fr_pols_convert(rt, t - 1)

cdef object fr_pols_pu(rt, t):
    c = rt.cache[40]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_pu(rt, t)
    c[key] = val
    return val

cdef object _calc_prem_cum_pp(rt, t):
    """CumPrem(t): cumulative premiums paid per policy to the end of month t.

        The premium falls at the beginning of the month and death at the end, so a death in
        month t has had the month-t premium paid on it - which is why the moratorium refund
        at ``t = 1`` is one month's premium and not nothing.  This is the **refund base**: a
        year-one non-accidental claim pays cumulative premiums paid, not the cash sum and
        not an annualized premium.
        """
    if t <= 0:
        return 0.0
    return fr_prem_cum_pp(rt, t - 1) + fr_premium_pp(rt, t)

cdef object fr_prem_cum_pp(rt, t):
    c = rt.cache[41]
    key = t
    if key in c:
        return c[key]
    val = _calc_prem_cum_pp(rt, t)
    c[key] = val
    return val

cdef object _calc_premium_mth(rt):
    """P: the monthly premium at outset, guaranteed never to increase.

        A model point input, not a rate-table lookup: no insurer publishes whole of life
        premium rate tables, so any shipped scale would be a **[std]** snapshot calibrated
        to the handful of public quote anchors.
        """
    return float(fr_model_point(rt)['premium_mth'])

cdef object fr_premium_mth(rt):
    c = rt.cache[42]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_mth(rt)
    c[key] = val
    return val

cdef object _calc_premium_pp(rt, t):
    """P(t): the monthly premium due at the beginning of month t.

        Zero once the premium cessation month has passed, and zero on a paid-up policy -
        which is carried as a separate population strand rather than as a premium of zero,
        so it does not appear here.
        """
    if fr_cessation_mths(rt) > 0 and t > fr_cessation_mths(rt):
        return 0.0
    return fr_premium_mth(rt) * (1.0 + fr_esc_prem_step(rt)) ** (fr_policy_year(rt, t) - 1)

cdef object fr_premium_pp(rt, t):
    c = rt.cache[43]
    key = t
    if key in c:
        return c[key]
    val = _calc_premium_pp(rt, t)
    c[key] = val
    return val

cdef object _calc_premiums(rt, t):
    """E[premium](t): premium income at the beginning of month t, an inflow.

        Carried on the full-cover strand only: paid-up policies pay nothing, and neither do
        over-50s policies past cessation, where :func:`premium_pp` is already zero.
        """
    return fr_premium_pp(rt, t) * fr_pols_if(rt, t)

cdef object fr_premiums(rt, t):
    c = rt.cache[44]
    key = t
    if key in c:
        return c[key]
    val = _calc_premiums(rt, t)
    c[key] = val
    return val

cdef object _calc_proj_len(rt):
    """Projection length in months: ``12 x (omega_age - entry_age)``.

        Whole of life has no maturity date, so the horizon is a **limiting age** rather than
        a contractual one.  The shipped mortality tables reach 1 well before ``omega_age``,
        so the population is exhausted inside the projection rather than truncated by it;
        :func:`check_truncation` asserts that, because a limiting age set too low would
        silently drop liability off the end.
        """
    return 12 * (rt.ctx.omega_age - fr_age_at_entry(rt))

cdef object fr_proj_len(rt):
    c = rt.cache[45]
    key = None
    if key in c:
        return c[key]
    val = _calc_proj_len(rt)
    c[key] = val
    return val

cdef object _calc_pu_benefit(rt, t):
    """The aggregate paid-up cover in force at the start of month t.

        Carrying the aggregate benefit alongside the count is what removes the need for a
        per-conversion cohort dimension: the paid-up payout depends on when the policy
        converted, but every paid-up policy thereafter rolls forward on the same survival
        factor, so the sum of their payouts satisfies the same recursion as the count.
        Death outgo on the strand is then ``pu_benefit(t) x q_m(t)``.
        """
    if t < 1 or t > fr_proj_len(rt) or (not fr_pu_variant(rt)):
        return 0.0
    if t == 1:
        return 0.0
    return fr_pu_benefit(rt, t - 1) * (1.0 - fr_mort_rate_mth(rt, t - 1)) + fr_pols_convert(rt, t - 1) * fr_benefit_pp(rt, t - 1, 'PAID_UP')

cdef object fr_pu_benefit(rt, t):
    c = rt.cache[46]
    key = t
    if key in c:
        return c[key]
    val = _calc_pu_benefit(rt, t)
    c[key] = val
    return val

cdef object _calc_pu_eligible(rt, t):
    """Whether a would-be lapse in month t converts to paid-up instead of terminating.

        The pro-rata paid-up rule: at least half the expected payments must have been made
        [S9].  Before that halfway point a lapse is a total loss and the base lapse rate
        applies; after it, forfeiture is strictly dominated, so **all** would-be lapses are
        assumed to convert **[std]**.
        """
    if not fr_pu_variant(rt):
        return False
    return fr_payments_made(rt, t) >= fr_payments_expected(rt) / 2.0

cdef object fr_pu_eligible(rt, t):
    c = rt.cache[47]
    key = t
    if key in c:
        return c[key]
    val = _calc_pu_eligible(rt, t)
    c[key] = val
    return val

cdef object _calc_pu_variant(rt):
    """Whether the pro-rata paid-up variant applies.

        Once half the expected payments have been made, a would-be lapse converts to a
        paid-up policy instead of forfeiting everything.  Requires a premium cessation date,
        since ``N_expected`` is measured to it; the underwritten cell has none, so the
        combination raises rather than dividing by zero.
        """
    v = bool(fr_model_point(rt)['variant_paid_up'])
    if v and fr_cessation_mths(rt) <= 0:
        raise ValueError('the pro-rata paid-up value needs a premium cessation date')
    return v

cdef object fr_pu_variant(rt):
    c = rt.cache[48]
    key = None
    if key in c:
        return c[key]
    val = _calc_pu_variant(rt)
    c[key] = val
    return val

cdef object _calc_sex(rt):
    """The sex (M / F) of the selected model point.

        Carried for the basis lookup.  The over-50s documents state age and smoker status as
        the rate factors and do not rate by sex, so on that cell this drives the shipped
        **[std]** proxy table and nothing contractual.
        """
    return fr_model_point(rt)['sex']

cdef object fr_sex(rt):
    c = rt.cache[49]
    key = None
    if key in c:
        return c[key]
    val = _calc_sex(rt)
    c[key] = val
    return val

cdef object _calc_smoker(rt):
    """The smoker status (NS / S).

        The underwritten specimen distinguishes three smoking states; they are collapsed to
        two here **[std]**.
        """
    return fr_model_point(rt)['smoker']

cdef object fr_smoker(rt):
    c = rt.cache[50]
    key = None
    if key in c:
        return c[key]
    val = _calc_smoker(rt)
    c[key] = val
    return val

cdef object _calc_sum_assured(rt):
    """SA: the sum assured or cash sum at outset.

        :func:`cover_pp` is the amount in force in a given month, which differs from this on
        the escalating variants.
        """
    return float(fr_model_point(rt)['sum_assured'])

cdef object fr_sum_assured(rt):
    c = rt.cache[51]
    key = None
    if key in c:
        return c[key]
    val = _calc_sum_assured(rt)
    c[key] = val
    return val

def evaluate(rt, ctx):
    rt.bind(ctx)
    return fr_bench_net_cf(rt)
