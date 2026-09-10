"""Generated static fast-recursive reference runtime."""

class FastRecursiveRuntime:

    def __init__(self, ctx=None):
        self.ctx = ctx
        self.cache = [dict() for _ in range(102)]

    def bind(self, ctx):
        self.ctx = ctx
        for c in self.cache:
            c.clear()
        return self

def _calc_age(rt, t):
    """The attained age (ANB) in policy month t: ``age_at_entry() + duration(t)``.

        Age advances on the policy anniversary, not on the birthday, which is the ANB
        convention the whole model is built on **[std]**.  Mixing an ALB basis into the
        COI or mortality lookups shifts both by up to half a year of mortality, which the
        notes list among the pitfalls.
        """
    return fr_age_at_entry(rt) + fr_duration(rt, t)

def fr_age(rt, t):
    c = rt.cache[0]
    key = t
    if key in c:
        return c[key]
    val = _calc_age(rt, t)
    c[key] = val
    return val

def _calc_age_at_entry(rt):
    """The issue age (ANB) of the selected model point."""
    return int(fr_model_point(rt)['age_at_entry'])

def fr_age_at_entry(rt):
    c = rt.cache[1]
    key = None
    if key in c:
        return c[key]
    val = _calc_age_at_entry(rt)
    c[key] = val
    return val

def _calc_av_pp(rt, t):
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
        return fr_av_pp_init(rt)
    return fr_av_pp_at(rt, t, 'BEF_INV') + fr_inv_income_pp(rt, t)

def fr_av_pp(rt, t):
    c = rt.cache[2]
    key = t
    if key in c:
        return c[key]
    val = _calc_av_pp(rt, t)
    c[key] = val
    return val

def _calc_av_pp_at(rt, t, timing):
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
    if timing == 'BEF_PREM':
        return fr_av_pp(rt, t - 1)
    elif timing == 'BEF_WD':
        return fr_av_pp_at(rt, t, 'BEF_PREM') + fr_prem_to_av_pp(rt, t)
    elif timing == 'BEF_FEE':
        return fr_av_pp_at(rt, t, 'BEF_WD') - fr_wd_pp(rt, t) - fr_wd_fee_pp(rt, t)
    elif timing == 'BEF_COI':
        return fr_av_pp_at(rt, t, 'BEF_FEE') - fr_maint_fee_pp(rt, t)
    elif timing == 'BEF_INV':
        return max(0.0, fr_av_pp_at(rt, t, 'BEF_COI') - fr_coi_pp(rt, t))
    else:
        raise ValueError('invalid timing')

def fr_av_pp_at(rt, t, timing):
    c = rt.cache[3]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_av_pp_at(rt, t, timing)
    c[key] = val
    return val

def _calc_av_pp_init(rt):
    """AV_0: the base account value per policy at the outset, 0 at issue."""
    return float(fr_model_point(rt)['av_pp_init'])

def fr_av_pp_init(rt):
    c = rt.cache[4]
    key = None
    if key in c:
        return c[key]
    val = _calc_av_pp_init(rt)
    c[key] = val
    return val

def _calc_bench_net_cf(rt):
    return sum((fr_net_cf(rt, t) for t in range(1, fr_proj_len(rt) + 1)))

def fr_bench_net_cf(rt):
    c = rt.cache[5]
    key = None
    if key in c:
        return c[key]
    val = _calc_bench_net_cf(rt)
    c[key] = val
    return val

def _calc_claim_pp(rt, t, kind):
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
    if kind == 'DEATH':
        return fr_db_pp(rt, t) - fr_loan_bal_pp(rt, t)
    elif kind == 'LAPSE':
        return fr_ncsv_pp(rt, t)
    elif kind == 'REFUND':
        return max(0.0, min(fr_rop_ratio(rt, t) * fr_cum_prem_pp(rt, t), rt.ctx.rop_cap_rate * fr_sum_assured_at(rt, t)) - fr_loan_bal_pp(rt, t))
    elif kind == 'WITHDRAWAL':
        return fr_wd_pp(rt, t)
    elif kind == 'GRACE':
        return 0.0
    else:
        raise ValueError('invalid kind')

def fr_claim_pp(rt, t, kind):
    c = rt.cache[6]
    key = (t, kind)
    if key in c:
        return c[key]
    val = _calc_claim_pp(rt, t, kind)
    c[key] = val
    return val

def _calc_claims(rt, t, kind=None):
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
    if kind == 'DEATH':
        return fr_claim_pp(rt, t, 'DEATH') * fr_pols_death(rt, t)
    elif kind == 'LAPSE':
        return fr_claim_pp(rt, t, 'LAPSE') * fr_pols_lapse(rt, t)
    elif kind == 'REFUND':
        return fr_claim_pp(rt, t, 'REFUND') * fr_pols_rop(rt, t)
    elif kind == 'GRACE':
        return 0.0
    elif kind is None:
        return sum((fr_claims(rt, t, k) for k in ('DEATH', 'LAPSE', 'REFUND', 'GRACE')))
    else:
        raise ValueError('invalid kind')

def fr_claims(rt, t, kind=None):
    c = rt.cache[7]
    key = (t, kind)
    if key in c:
        return c[key]
    val = _calc_claims(rt, t, kind)
    c[key] = val
    return val

def _calc_class_factor(rt):
    """The underwriting-class multiplier on the best-estimate mortality table **[std]**."""
    return float(rt.ctx.data.class_factor_table().loc[fr_rate_class(rt), 'factor'])

def fr_class_factor(rt):
    c = rt.cache[8]
    key = None
    if key in c:
        return c[key]
    val = _calc_class_factor(rt)
    c[key] = val
    return val

def _calc_coi_pp(rt, t):
    """COI_t: the base cost of insurance charge, ``m_t NAAR_t / 1000``.

        Zero from attained age 121, when all charges cease [S3][S7].
        """
    if fr_age(rt, t) >= rt.ctx.charges_cease_age:
        return 0.0
    return fr_coi_rate(rt, t) / 1000 * fr_net_amt_at_risk(rt, t)

def fr_coi_pp(rt, t):
    c = rt.cache[9]
    key = t
    if key in c:
        return c[key]
    val = _calc_coi_pp(rt, t)
    c[key] = val
    return val

def _calc_coi_rate(rt, t):
    """m_t: the current monthly COI rate, 65% of the guaranteed maximum **[std]**.

        Current COI scales are not published by any carrier, so the factor is a pure
        modelling assumption and one of the first things to sensitivity-test.  The scale
        is held to :func:`coi_rate_dp` decimals per $1,000, which reconciles the notes'
        worked example with the notes' own factor rule -- see :func:`coi_rate_dp`.
        """
    r = rt.ctx.coi_curr_factor * fr_coi_rate_guar(rt, t)
    dp = fr_coi_rate_dp(rt)
    return r if dp < 0 else round(r, dp)

def fr_coi_rate(rt, t):
    c = rt.cache[10]
    key = t
    if key in c:
        return c[key]
    val = _calc_coi_rate(rt, t)
    c[key] = val
    return val

def _calc_coi_rate_dp(rt):
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
    o = fr_model_point(rt)['coi_rate_dp']
    return -1 if rt.ctx.pd.isna(o) else int(o)

def fr_coi_rate_dp(rt):
    c = rt.cache[11]
    key = None
    if key in c:
        return c[key]
    val = _calc_coi_rate_dp(rt)
    c[key] = val
    return val

def _calc_coi_rate_guar(rt, t):
    """m_t^max: the guaranteed maximum **monthly** COI rate per $1,000 of NAAR.

        The annual rate from *coi_rates.csv* divided by twelve -- the notes' simple-twelfth
        conversion, fixed **[std]**.  It differs materially from
        ``1 - (1 - q)^(1/12)`` at ages 85 and over, where q exceeds 0.10, and the notes are
        explicit that the two must not be mixed.  Model 585 requires the guaranteed maxima
        to be stated in the policy [R3]; carriers do not publish them, so the shipped
        scale is illustrative **[std]**, not the 2017 CSO table [REG-R17].
        """
    scale = fr_coi_rate_scale(rt)
    a = min(fr_age(rt, t), int(scale.index.max()))
    return float(scale[a]) / 12

def fr_coi_rate_guar(rt, t):
    c = rt.cache[12]
    key = t
    if key in c:
        return c[key]
    val = _calc_coi_rate_guar(rt, t)
    c[key] = val
    return val

def _calc_coi_rate_scale(rt):
    """The guaranteed maximum annual COI scale for this model point's cell.

        A Series indexed by **attained** age, per $1,000 of net amount at risk, sliced
        once from *coi_rates.csv* for this ``sex`` and ``rate_class``.  The shipped table
        covers the anchor cell M / StdNT over attained ages 45-121 only; a model point on
        any other cell, or a younger attained age, needs the table extended first.
        """
    return rt.ctx.data.coi_rates().loc[fr_sex(rt), fr_rate_class(rt)]['coi_rate_guar_ann']

def fr_coi_rate_scale(rt):
    c = rt.cache[13]
    key = None
    if key in c:
        return c[key]
    val = _calc_coi_rate_scale(rt)
    c[key] = val
    return val

def _calc_corridor_factor(rt, t):
    """kappa(x_t): the GPT corridor factor at the attained age [R4][REG-R13].

        The IRC 7702(d)(2) applicable percentages, every row of them: 250% to attained age
        40, then decreasing by a ratable portion for each full year through the statute's
        breakpoints -- 215% at 45, 185% at 50, 150% at 55, 130% at 60, 120% at 65, 115% at
        70, 105% from 75 to 90 -- and 100% from attained age 95 on, which is the statute's
        last row.  Ages beyond the table take its last row.  Because guaranteed UL account
        values are deliberately thin the corridor never binds in any shipped model point --
        but it is the reason the death benefit is a ``max`` rather than the face amount.
        """
    tbl = rt.ctx.data.corridor_factors()
    a = min(max(fr_age(rt, t), int(tbl.index.min())), int(tbl.index.max()))
    return float(tbl.loc[a, 'corridor_factor'])

def fr_corridor_factor(rt, t):
    c = rt.cache[14]
    key = t
    if key in c:
        return c[key]
    val = _calc_corridor_factor(rt, t)
    c[key] = val
    return val

def _calc_crediting_rate_ann(rt, t):
    """i^c: the current declared annual effective credited rate, 3.50% **[std]**.

        A non-guaranteed element declared at insurer discretion within the guaranteed
        bounds and governed by ASOP 2 [REG-R26].  The base run holds the snapshot scale
        level, as the notes prescribe; re-rating is out of scope.
        """
    return rt.ctx.crediting_rate_curr

def fr_crediting_rate_ann(rt, t):
    c = rt.cache[15]
    key = t
    if key in c:
        return c[key]
    val = _calc_crediting_rate_ann(rt, t)
    c[key] = val
    return val

def _calc_csv_pp(rt, t):
    """The cash surrender value per policy, ``AV_t - SC_t``, floored at zero.

        The floor is **[std]**: a negative cash surrender value would be a payment *from*
        the policyholder.  On this product it binds for years -- guaranteed UL account
        values are deliberately thin and the 15-year surrender charge starts at $9,000 on
        a $500,000 face.
        """
    return max(0.0, fr_av_pp(rt, t) - fr_surr_charge_pp(rt, t))

def fr_csv_pp(rt, t):
    c = rt.cache[16]
    key = t
    if key in c:
        return c[key]
    val = _calc_csv_pp(rt, t)
    c[key] = val
    return val

def _calc_cum_prem_init(rt):
    """CumPrem_0: cumulative premiums already paid at the outset.

        The notes make this a model point attribute because it drives the return-of-premium
        refund [S1] and the 7-pay test [R5].  For the anchor cell it is the 25 annual
        premiums of $10,800 implied by the in-force snapshot **[std]**.
        """
    return float(fr_model_point(rt)['cum_prem_init'])

def fr_cum_prem_init(rt):
    c = rt.cache[17]
    key = None
    if key in c:
        return c[key]
    val = _calc_cum_prem_init(rt)
    c[key] = val
    return val

def _calc_cum_prem_pp(rt, t):
    """CumPrem_t: cumulative premiums paid per policy.

        ``CumPrem_0 = cum_prem_init()``; thereafter ``CumPrem_{t-1} + P_t``, exactly as the
        notes write it.  Withdrawals do **not** reduce it here -- that is the
        cumulative-premium-test variation's ``CumPrem^net``, not this one -- and it drives
        the return-of-premium refund [S1].
        """
    if t == 0:
        return fr_cum_prem_init(rt)
    return fr_cum_prem_pp(rt, t - 1) + fr_premium_pp(rt, t)

def fr_cum_prem_pp(rt, t):
    c = rt.cache[18]
    key = t
    if key in c:
        return c[key]
    val = _calc_cum_prem_pp(rt, t)
    c[key] = val
    return val

def _calc_db_pp(rt, t):
    """DB_t: the death benefit per policy, ``max(F, kappa(x_t) max(AV'_t, 0))`` [S2][S4].

        Level death benefit option only, the guarantee-focused segment's design [S2][S4].
        ``AV'_t`` is the account value after the premium, the withdrawal and the expense
        charges and **before** the cost of insurance, and it is floored at zero so an
        exhausted account cannot pull the death benefit below the face amount.
        """
    return max(fr_sum_assured_at(rt, t), fr_corridor_factor(rt, t) * max(fr_av_pp_at(rt, t, 'BEF_COI'), 0.0))

def fr_db_pp(rt, t):
    c = rt.cache[19]
    key = t
    if key in c:
        return c[key]
    val = _calc_db_pp(rt, t)
    c[key] = val
    return val

def _calc_duration(rt, t):
    """Completed policy years at the beginning of policy month t."""
    return fr_duration_mth(rt, t) // 12

def fr_duration(rt, t):
    c = rt.cache[20]
    key = t
    if key in c:
        return c[key]
    val = _calc_duration(rt, t)
    c[key] = val
    return val

def _calc_duration_mth(rt, t):
    """Completed policy months at the beginning of policy month t.

        ``duration_mth_init() + t - 1``, so it is 0 in the issue month of a new-business
        model point and 300 in the first month of the notes' worked example.  Note the
        contrast with the notes' own month index, which counts the current month as well;
        see :func:`surr_charge_rate`.
        """
    return fr_duration_mth_init(rt) + t - 1

def fr_duration_mth(rt, t):
    c = rt.cache[21]
    key = t
    if key in c:
        return c[key]
    val = _calc_duration_mth(rt, t)
    c[key] = val
    return val

def _calc_duration_mth_init(rt):
    """Completed policy months already elapsed when the projection starts.

        0 for a new-business model point, so that ``t = 1`` is the issue month; 300 for
        the notes' worked-example cell, whose months 301-305 are ``t = 1`` to ``t = 5``.
        This is the notes' ``duration_months``.
        """
    return int(fr_model_point(rt)['duration_mth'])

def fr_duration_mth_init(rt):
    c = rt.cache[22]
    key = None
    if key in c:
        return c[key]
    val = _calc_duration_mth_init(rt)
    c[key] = val
    return val

def _calc_expenses(rt, t):
    """The insurer's own expenses in policy month t **[std]**.

        Acquisition in policy year 1 -- $300 a policy in the issue month plus 90% of every
        first-year premium, which is the notes' combined commission and issue allowance --
        maintenance of $75 a policy a year inflating at 2.5%, spread evenly over the
        months, and $300 of claim expense per death.

        Not to be confused with :func:`maint_fee`, which is the *charge against the
        account value*.
        """
    acq = rt.ctx.expense_acq if fr_duration_mth(rt, t) == 0 else 0.0
    if fr_policy_year(rt, t) == 1:
        acq = acq + rt.ctx.expense_acq_prem_rate * fr_premium_pp(rt, t)
    return (acq + rt.ctx.expense_maint / 12 * fr_inflation_factor(rt, t)) * fr_pols_if(rt, t) + rt.ctx.expense_claim * fr_pols_death(rt, t)

def fr_expenses(rt, t):
    c = rt.cache[23]
    key = t
    if key in c:
        return c[key]
    val = _calc_expenses(rt, t)
    c[key] = val
    return val

def _calc_grace_mth(rt, t):
    """g_t: months elapsed in the grace period, 0 when not in grace [S7].

        The counter advances only when the deduction attempt failed **and** the guarantee
        is not supporting the policy; a failed deduction under an active guarantee is
        forgone and never opens a grace.  ``g_0 = 0``.
        """
    if t < 1:
        return 0
    if fr_is_lapsed(rt, t):
        return 0
    if not fr_is_shortfall(rt, t) or fr_is_guar_supported(rt, t):
        return 0
    return fr_grace_mth(rt, t - 1) + 1

def fr_grace_mth(rt, t):
    c = rt.cache[24]
    key = t
    if key in c:
        return c[key]
    val = _calc_grace_mth(rt, t)
    c[key] = val
    return val

def _calc_guar_rate_mth(rt):
    """j_g: the monthly guaranteed rate, ``(1 + i_guar)^(1/12) - 1`` = 0.0016516."""
    return (1 + rt.ctx.guar_rate_ann) ** (1 / 12) - 1

def fr_guar_rate_mth(rt):
    c = rt.cache[25]
    key = None
    if key in c:
        return c[key]
    val = _calc_guar_rate_mth(rt)
    c[key] = val
    return val

def _calc_guarantee_age(rt):
    """The elected secondary-guarantee age, any attained age from 90 to 121 [S1][S2][S9].

        121 is the lifetime election, which is what the anchor cell carries and what
        switches :func:`lapse_rate_guar_mult` to the 0.55 multiplier [R7].
        """
    return int(fr_model_point(rt)['guarantee_age'])

def fr_guarantee_age(rt):
    c = rt.cache[26]
    key = None
    if key in c:
        return c[key]
    val = _calc_guarantee_age(rt)
    c[key] = val
    return val

def _calc_has_surr_charge(rt):
    """Whether a surrender charge schedule applies to this model point."""
    return bool(fr_model_point(rt)['has_surr_charge'])

def fr_has_surr_charge(rt):
    c = rt.cache[27]
    key = None
    if key in c:
        return c[key]
    val = _calc_has_surr_charge(rt)
    c[key] = val
    return val

def _calc_inflation_factor(rt, t):
    """The expense inflation factor, ``(1 + inflation_rate)^(y - 1)`` **[std]**.

        Expenses inflate by policy year, not by month, which is how the notes write the
        $75 per policy per year maintenance expense.
        """
    return (1 + rt.ctx.inflation_rate) ** (fr_policy_year(rt, t) - 1)

def fr_inflation_factor(rt, t):
    c = rt.cache[28]
    key = t
    if key in c:
        return c[key]
    val = _calc_inflation_factor(rt, t)
    c[key] = val
    return val

def _calc_inv_income_pp(rt, t):
    """Interest credited to the base account value at EOM of policy month t.

        The unloaned part of the post-deduction balance earns the current monthly rate and
        the loaned part the guaranteed loaned rate of 3.0% [S4]::

            (AV''_t - L_{t-1}) x j_c + L_{t-1} x loan_cr_rate_mth()

        With the account value exhausted the credit is zero, which is why the worked
        example shows no interest from month 304.
        """
    loaned = fr_loan_bal_pp(rt, t - 1)
    unloaned = fr_av_pp_at(rt, t, 'BEF_INV') - loaned
    return unloaned * fr_inv_return_mth(rt, t) + loaned * fr_loan_cr_rate_mth(rt)

def fr_inv_income_pp(rt, t):
    c = rt.cache[29]
    key = t
    if key in c:
        return c[key]
    val = _calc_inv_income_pp(rt, t)
    c[key] = val
    return val

def _calc_inv_return_mth(rt, t):
    """j_c: the monthly credited rate, ``(1 + i^c)^(1/12) - 1``, floored at j_g.

        0.0028709 at the **[std]** 3.50% current rate, matching the notes.  The floor is
        the contractual 2.0% guaranteed minimum [S3][S5][S7]; it does not bind at the
        snapshot scale.
        """
    return max((1 + fr_crediting_rate_ann(rt, t)) ** (1 / 12) - 1, fr_guar_rate_mth(rt))

def fr_inv_return_mth(rt, t):
    c = rt.cache[30]
    key = t
    if key in c:
        return c[key]
    val = _calc_inv_return_mth(rt, t)
    c[key] = val
    return val

def _calc_is_guar_active(rt, t):
    """The step-9 in-force test: ``SG_t - L_t > 0`` [S4][S2][S9].

        Measured at EOM, after the shadow interest credit and the loan accrual.  While it
        holds the policy cannot lapse however exhausted the real account value is; when it
        fails, an exhausted account opens the grace period.  Strictly greater than zero, as
        the notes require: a ``>= 0`` target on a monthly grid can leave the guarantee
        failing on the final monthiversary.
        """
    return fr_sg_net_pp(rt, t) > 0

def fr_is_guar_active(rt, t):
    c = rt.cache[31]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_guar_active(rt, t)
    c[key] = val
    return val

def _calc_is_guar_supported(rt, t):
    """The step-6 test: ``SG''_t - L_{t-1} > 0``, measured before the interest credits.

        This is the one that decides what happens to a failed deduction -- forgone by the
        insurer, or grace.  It is deliberately a different measurement point from
        :func:`is_guar_active`, and it is evaluated **after** the full monthly deduction
        attempt: testing before the deduction lets a policy lapse a month early or late and
        shifts claim timing at exactly the durations where the net amount at risk is the
        whole death benefit.
        """
    return fr_sg_pp_at(rt, t, 'BEF_INV') - fr_loan_bal_pp(rt, t - 1) > 0

def fr_is_guar_supported(rt, t):
    c = rt.cache[32]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_guar_supported(rt, t)
    c[key] = val
    return val

def _calc_is_lapsed(rt, t):
    """Whether the policy has terminated for insufficiency at or before BOM of month t.

        The 61-day grace period [S7] is taken as ``grace_months`` = 2 policy months
        **[std]**; when it expires without the required payment the policy lapses at BOM
        with no value -- the cash surrender value is zero in grace by construction.  Lapse
        for insufficiency requires all three of the notes' conditions: the deduction
        attempt failed, ``SG - L <= 0``, and the grace expired uncured.
        """
    if t <= 1:
        return False
    return fr_is_lapsed(rt, t - 1) or fr_grace_mth(rt, t - 1) >= rt.ctx.grace_months

def fr_is_lapsed(rt, t):
    c = rt.cache[33]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_lapsed(rt, t)
    c[key] = val
    return val

def _calc_is_premium_mth(rt, t):
    """Whether a scheduled premium falls due at BOM of policy month t.

        ``LEVEL``    every ``12 / premium_freq()`` months from issue.
        ``SINGLE``   the issue month only.
        ``TEN_PAY``  as ``LEVEL``, for the first ``ten_pay_years`` policy years **[std]**.
        """
    pt = fr_premium_type(rt)
    if pt == 'SINGLE':
        return fr_duration_mth(rt, t) == 0
    elif pt == 'TEN_PAY':
        if fr_duration(rt, t) >= rt.ctx.ten_pay_years:
            return False
    elif pt != 'LEVEL':
        raise ValueError('invalid premium type')
    return fr_duration_mth(rt, t) % (12 // fr_premium_freq(rt)) == 0

def fr_is_premium_mth(rt, t):
    c = rt.cache[34]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_premium_mth(rt, t)
    c[key] = val
    return val

def _calc_is_shortfall(rt, t):
    """Whether the monthly deduction attempt failed: ``AV'_t - COI_t < 0``.

        The notes' step 6 condition, evaluated **after** the full deduction attempt.  On
        its own it says nothing about lapse: while :func:`is_guar_supported` holds the
        shortfall is forgone by the insurer and coverage continues; only when the guarantee
        has failed as well does it open the grace period.
        """
    return fr_av_pp_at(rt, t, 'BEF_COI') - fr_coi_pp(rt, t) < 0

def fr_is_shortfall(rt, t):
    c = rt.cache[35]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_shortfall(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate(rt, t):
    """The total annual lapse rate, ``min(0.5, max(0.003, b(d) G Phi Psi_t))`` **[std]**.

        The 0.3% annual floor is applied after the dynamic factor, as the notes write it,
        and the 50% cap wraps the result; the two cannot conflict.
        """
    rate = fr_lapse_rate_base(rt, t) * fr_lapse_rate_guar_mult(rt) * fr_lapse_rate_pattern_mult(rt) * fr_lapse_rate_dyn_mult(rt, t)
    return min(rt.ctx.lapse_rate_cap, max(rt.ctx.lapse_rate_floor, rate))

def fr_lapse_rate(rt, t):
    c = rt.cache[36]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate_base(rt, t):
    """b(d): the base annual lapse rate by policy year **[std]**.

        4.0%, 3.0%, 2.5%, then 2.0% in years 4-5, 1.5% in 6-10, 1.0% in 11-20 and 0.75%
        thereafter, read from *lapse_table.csv*; policy years beyond the table take its
        last row.  The shape is anchored to the public highlights of the SOA/LIMRA UL
        persistency and lapse studies [R7][REG-R20][REG-R21], whose detailed tables sit in
        a paid data package, so the levels are a standardization.
        """
    tbl = rt.ctx.data.lapse_table()
    y = min(fr_policy_year(rt, t), int(tbl.index.max()))
    return float(tbl.loc[y, 'lapse_rate_ann'])

def fr_lapse_rate_base(rt, t):
    c = rt.cache[37]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate_base(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate_dyn_mult(rt, t):
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
    if not fr_is_guar_active(rt, t):
        return rt.ctx.lapse_dyn_mult_guar_failed
    if fr_av_pp(rt, t) > 0:
        return 1.0
    return rt.ctx.lapse_dyn_mult_guar_only

def fr_lapse_rate_dyn_mult(rt, t):
    c = rt.cache[38]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate_dyn_mult(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate_guar_mult(rt):
    """G: the guarantee-duration lapse multiplier, 0.55 for a lifetime election.

        Lifetime secondary-guarantee lapse rates run 45% below non-lifetime rates on both
        count and amount bases in the 2015-2021 industry experience [R7]; the level is
        derived from that finding and the flat duration shape is **[std]**.  This is the
        first-order assumption for a lapse-supported product: every lapse of a funded
        guarantee releases the insurer from a deeply in-the-money claim.
        """
    if fr_guarantee_age(rt) >= rt.ctx.lifetime_guarantee_age:
        return rt.ctx.lapse_guar_mult
    return 1.0

def fr_lapse_rate_guar_mult(rt):
    c = rt.cache[39]
    key = None
    if key in c:
        return c[key]
    val = _calc_lapse_rate_guar_mult(rt)
    c[key] = val
    return val

def _calc_lapse_rate_mth(rt, t):
    """w_t: the monthly lapse rate, ``1 - (1 - w_annual)^(1/12)``."""
    return 1 - (1 - fr_lapse_rate(rt, t)) ** (1 / 12)

def fr_lapse_rate_mth(rt, t):
    c = rt.cache[40]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate_mth(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate_pattern_mult(rt):
    """Phi: the premium-pattern lapse multiplier **[std]**.

        Single-pay 0.6, ten-pay 0.8, level 1.0, in the direction [R8] reports -- higher
        lapses for level-pay, lower for single-pay.
        """
    pt = fr_premium_type(rt)
    if pt == 'SINGLE':
        return rt.ctx.lapse_pattern_mult_single
    elif pt == 'TEN_PAY':
        return rt.ctx.lapse_pattern_mult_ten_pay
    elif pt == 'LEVEL':
        return 1.0
    else:
        raise ValueError('invalid premium type')

def fr_lapse_rate_pattern_mult(rt):
    c = rt.cache[41]
    key = None
    if key in c:
        return c[key]
    val = _calc_lapse_rate_pattern_mult(rt)
    c[key] = val
    return val

def _calc_load_prem_rate(rt):
    """pi: the base premium expense charge, 25% of every premium, all years [S3][S7].

        Contractual here, unlike the universal life chassis where the load is a
        non-guaranteed element; it sits in the model point table for the same reason it
        does there, so that the table alone describes the policy.
        """
    return float(fr_model_point(rt)['load_prem_rate'])

def fr_load_prem_rate(rt):
    c = rt.cache[42]
    key = None
    if key in c:
        return c[key]
    val = _calc_load_prem_rate(rt)
    c[key] = val
    return val

def _calc_loan_bal_init(rt):
    """L_0: the policy loan balance per policy at the outset, 0 in every shipped point."""
    return float(fr_model_point(rt)['loan_bal_init'])

def fr_loan_bal_init(rt):
    c = rt.cache[43]
    key = None
    if key in c:
        return c[key]
    val = _calc_loan_bal_init(rt)
    c[key] = val
    return val

def _calc_loan_bal_pp(rt, t):
    """L_t: the policy loan balance per policy at the end of policy month t.

        ``L_0 = loan_bal_init()``; thereafter ``L_{t-1} x (1 + r_L)^(1/12)`` at the
        guaranteed 5.0% charged in arrears [S4], accrued monthly **[std]**.  New loans and
        repayments are not modelled -- the notes give no utilisation pattern -- so this
        only rolls the model point's opening balance forward.  Indebtedness is deducted
        from the guarantee in-force test (:func:`sg_net_pp`), from death proceeds and from
        the surrender value; the shadow account itself is not reduced by it [S4][S2].
        """
    if t == 0:
        return fr_loan_bal_init(rt)
    return fr_loan_bal_pp(rt, t - 1) * (1 + fr_loan_rate_mth(rt))

def fr_loan_bal_pp(rt, t):
    c = rt.cache[44]
    key = t
    if key in c:
        return c[key]
    val = _calc_loan_bal_pp(rt, t)
    c[key] = val
    return val

def _calc_loan_cr_rate_mth(rt):
    """The monthly rate credited on the loaned account value, 3.0% annual [S4].

        Guaranteed, and 200 basis points below the charged rate -- the contractual loan
        spread.
        """
    return (1 + rt.ctx.loan_cr_rate_ann) ** (1 / 12) - 1

def fr_loan_cr_rate_mth(rt):
    c = rt.cache[45]
    key = None
    if key in c:
        return c[key]
    val = _calc_loan_cr_rate_mth(rt)
    c[key] = val
    return val

def _calc_loan_rate_mth(rt):
    """The monthly charged loan rate, ``(1 + r_L)^(1/12) - 1`` at r_L = 5.0% [S4].

        Charged in arrears and guaranteed; monthly accrual is the model's discretization
        **[std]**.
        """
    return (1 + rt.ctx.loan_rate_ann) ** (1 / 12) - 1

def fr_loan_rate_mth(rt):
    c = rt.cache[46]
    key = None
    if key in c:
        return c[key]
    val = _calc_loan_rate_mth(rt)
    c[key] = val
    return val

def _calc_maint_fee_pp(rt, t):
    """The non-COI part of the base monthly deduction, ``e_pol + e_u U + rc`` [S3][S7].

        The $5.50 per-policy administrative charge [S3][S7], the $0.20 per $1,000 of initial
        face per month coverage charge **[std]** and rider charges.  Zero from attained age
        121, when charges cease [S3][S7].

        The name follows ``CashValue_SE.maint_fee``: this is a *charge* against the account
        value and therefore insurer income.  It is not :func:`expenses`, which is the
        insurer's own outgo.
        """
    if fr_age(rt, t) >= rt.ctx.charges_cease_age:
        return 0.0
    return rt.ctx.expense_pol_mth + rt.ctx.expense_unit_mth * fr_units(rt, t) + fr_rider_charge_pp(rt, t)

def fr_maint_fee_pp(rt, t):
    c = rt.cache[47]
    key = t
    if key in c:
        return c[key]
    val = _calc_maint_fee_pp(rt, t)
    c[key] = val
    return val

def _calc_model_point(rt):
    """The selected model point as a Series."""
    return rt.ctx.data.model_point_table().loc[rt.ctx.point_id]

def fr_model_point(rt):
    c = rt.cache[48]
    key = None
    if key in c:
        return c[key]
    val = _calc_model_point(rt)
    c[key] = val
    return val

def _calc_mort_improve_factor(rt, t):
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
    if k > rt.ctx.mort_improve_max_years:
        return fr_mort_improve_factor(rt, 12 * rt.ctx.mort_improve_max_years + 1)
    return fr_mort_improve_factor(rt, t - 12) * (1 - fr_mort_improve_rate(rt, t - 12))

def fr_mort_improve_factor(rt, t):
    c = rt.cache[49]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_improve_factor(rt, t)
    c[key] = val
    return val

def _calc_mort_improve_rate(rt, t):
    """The annual mortality improvement rate at the attained age in month t **[std]**.

        1.0% a year to attained age 85, grading linearly to 0% at attained age 95 and zero
        thereafter.  Improvement compounds, so at the late attained ages where the net
        amount at risk is the whole death benefit it is one of the two assumptions that
        move the claims most.
        """
    a = fr_age(rt, t)
    if a <= rt.ctx.mort_improve_full_age:
        return rt.ctx.mort_improve_rate_init
    if a >= rt.ctx.mort_improve_end_age:
        return 0.0
    return rt.ctx.mort_improve_rate_init * ((rt.ctx.mort_improve_end_age - a) / (rt.ctx.mort_improve_end_age - rt.ctx.mort_improve_full_age))

def fr_mort_improve_rate(rt, t):
    c = rt.cache[50]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_improve_rate(rt, t)
    c[key] = val
    return val

def _calc_mort_rate(rt, t):
    """The annual best-estimate mortality rate in policy month t.

        Base table x :func:`class_factor` x the A/E factor, which is 100% in the base run
        **[std]**, x :func:`mort_improve_factor`, capped at 1.0.  The shipped table is a
        small illustrative one **[std]**, *not* the 2015 VBT the notes recommend -- that
        family is licensed and may not be reproduced here.  Ages beyond the table take its
        last row, where the rate is 1.0; the cap is what keeps a class factor above 1 from
        pushing the terminal rate past certainty.
        """
    tbl = rt.ctx.data.mort_table()
    a = min(max(fr_age(rt, t), int(tbl.index.min())), int(tbl.index.max()))
    return min(1.0, float(tbl.loc[a, 'mort_rate']) * fr_class_factor(rt) * rt.ctx.mort_ae_factor * fr_mort_improve_factor(rt, t))

def fr_mort_rate(rt, t):
    c = rt.cache[51]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate(rt, t)
    c[key] = val
    return val

def _calc_mort_rate_mth(rt, t):
    """q_t^d: the monthly best-estimate mortality rate, ``1 - (1 - q)^(1/12)``.

        Note that the **experience** decrement uses the compound conversion while the
        contractual COI rate uses the simple twelfth (:func:`coi_rate_guar`).  The notes
        prescribe exactly that split; the two must not be interchanged.
        """
    return 1 - (1 - fr_mort_rate(rt, t)) ** (1 / 12)

def fr_mort_rate_mth(rt, t):
    c = rt.cache[52]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate_mth(rt, t)
    c[key] = val
    return val

def _calc_naar_factor(rt):
    """The base NAAR factor, ``1 + j_g`` = 1.0016516.

        The death benefit is discounted one month at the **guaranteed** rate, never the
        credited rate.  Using the undiscounted death benefit instead changes the cost of
        insurance by about 0.17% a month at the 2% guarantee, which the notes list first
        among the pitfalls; the same convention must hold on both accounts.
        """
    return 1 + fr_guar_rate_mth(rt)

def fr_naar_factor(rt):
    c = rt.cache[53]
    key = None
    if key in c:
        return c[key]
    val = _calc_naar_factor(rt)
    c[key] = val
    return val

def _calc_ncsv_pp(rt, t):
    """CSV_t in the notes: the net cash surrender value, ``max(AV_t - SC_t - L_t, 0)``.

        What a surrendering policyholder is paid, and the notes' surrender outgo.  The
        notes' symbol ``CSV_t`` already nets indebtedness, so it is this cells and not
        :func:`csv_pp`; the chassis keeps the two apart so the surrender-charge and the
        debt offsets can be read separately.
        """
    return max(0.0, fr_csv_pp(rt, t) - fr_loan_bal_pp(rt, t))

def fr_ncsv_pp(rt, t):
    c = rt.cache[54]
    key = t
    if key in c:
        return c[key]
    val = _calc_ncsv_pp(rt, t)
    c[key] = val
    return val

def _calc_net_amt_at_risk(rt, t):
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
    return max(0.0, fr_db_pp(rt, t) / fr_naar_factor(rt) - max(fr_av_pp_at(rt, t, 'BEF_COI'), 0.0))

def fr_net_amt_at_risk(rt, t):
    c = rt.cache[55]
    key = t
    if key in c:
        return c[key]
    val = _calc_net_amt_at_risk(rt, t)
    c[key] = val
    return val

def _calc_net_cf(rt, t):
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
    return fr_premiums(rt, t) - fr_claims(rt, t) - fr_withdrawals(rt, t) - fr_expenses(rt, t) - fr_premium_taxes(rt, t)

def fr_net_cf(rt, t):
    c = rt.cache[56]
    key = t
    if key in c:
        return c[key]
    val = _calc_net_cf(rt, t)
    c[key] = val
    return val

def _calc_policy_year(rt, t):
    """y: the policy year containing policy month t, 1-based."""
    return fr_duration(rt, t) + 1

def fr_policy_year(rt, t):
    c = rt.cache[57]
    key = t
    if key in c:
        return c[key]
    val = _calc_policy_year(rt, t)
    c[key] = val
    return val

def _calc_pols_death(rt, t):
    """Number of deaths at the end of policy month t, ``l_t x q_t^d``."""
    return fr_pols_if(rt, t) * fr_mort_rate_mth(rt, t)

def fr_pols_death(rt, t):
    c = rt.cache[58]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_death(rt, t)
    c[key] = val
    return val

def _calc_pols_if(rt, t):
    """l_t: the number of policies in force at the beginning of policy month t.

        Decrements are end-of-month events, so the number in force is constant through the
        month and every BOM cash flow is weighted by it.  ``pols_if(1) = l_0 =
        pols_if_init()``.  A policy whose grace has expired is out at BOM with no value,
        which is why :func:`is_lapsed` is tested first.
        """
    if t == 1:
        return fr_pols_if_init(rt)
    if fr_is_lapsed(rt, t):
        return 0.0
    return fr_pols_if(rt, t - 1) - fr_pols_death(rt, t - 1) - fr_pols_lapse(rt, t - 1) - fr_pols_rop(rt, t - 1) - fr_pols_lapse_grace(rt, t - 1)

def fr_pols_if(rt, t):
    c = rt.cache[59]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_if(rt, t)
    c[key] = val
    return val

def _calc_pols_if_init(rt):
    """l_0: the in-force probability at the outset, 1 for a single-policy point."""
    return float(fr_model_point(rt)['pols_if_init'])

def fr_pols_if_init(rt):
    c = rt.cache[60]
    key = None
    if key in c:
        return c[key]
    val = _calc_pols_if_init(rt)
    c[key] = val
    return val

def _calc_pols_lapse(rt, t):
    """Number of surrenders at the end of policy month t.

        ``l_t (1 - q_t^d) w_t``: death is applied before lapse, which is the notes'
        ordering.
        """
    return fr_pols_if(rt, t) * (1 - fr_mort_rate_mth(rt, t)) * fr_lapse_rate_mth(rt, t)

def fr_pols_lapse(rt, t):
    c = rt.cache[61]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_lapse(rt, t)
    c[key] = val
    return val

def _calc_pols_lapse_grace(rt, t):
    """Number of policies terminating for insufficiency at the end of policy month t.

        Non-zero only in the month before the grace period expires, when every remaining
        policy is out.  This is not a rate-based decrement: it is the contractual
        termination of a policy whose account value failed and whose guarantee had already
        gone, and it is needed for the in-force roll-forward to close.  The policies leave
        with no value, so it generates no claim -- the cash surrender value is zero in
        grace by construction.
        """
    if fr_is_lapsed(rt, t) or not fr_is_lapsed(rt, t + 1):
        return 0.0
    return fr_pols_if(rt, t) - fr_pols_death(rt, t) - fr_pols_lapse(rt, t) - fr_pols_rop(rt, t)

def fr_pols_lapse_grace(rt, t):
    c = rt.cache[62]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_lapse_grace(rt, t)
    c[key] = val
    return val

def _calc_pols_rop(rt, t):
    """Number of return-of-premium exercises at the end of policy month t.

        ``l_t (1 - q_t^d)(1 - w_t) w_t^ROP``, matching the notes'
        ``l_{t+1} = l_t (1 - q^d)(1 - w)(1 - w^ROP)``.  Exercise is a full surrender
        [S1][S3], so an exercising policy leaves with the refund and nothing else.
        """
    return fr_pols_if(rt, t) * (1 - fr_mort_rate_mth(rt, t)) * (1 - fr_lapse_rate_mth(rt, t)) * fr_rop_rate(rt, t)

def fr_pols_rop(rt, t):
    c = rt.cache[63]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_rop(rt, t)
    c[key] = val
    return val

def _calc_prem_persistency(rt, t):
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
    o = fr_model_point(rt)['prem_persistency_override']
    if not rt.ctx.pd.isna(o):
        return float(o)
    return rt.ctx.prem_persistency_ann if fr_premium_type(rt) == 'LEVEL' else 1.0

def fr_prem_persistency(rt, t):
    c = rt.cache[64]
    key = t
    if key in c:
        return c[key]
    val = _calc_prem_persistency(rt, t)
    c[key] = val
    return val

def _calc_prem_to_av_pp(rt, t):
    """The net premium credited to the base account value, ``(1 - pi) P_t`` [S3][S7]."""
    return fr_premium_pp(rt, t) * (1 - fr_load_prem_rate(rt))

def fr_prem_to_av_pp(rt, t):
    c = rt.cache[65]
    key = t
    if key in c:
        return c[key]
    val = _calc_prem_to_av_pp(rt, t)
    c[key] = val
    return val

def _calc_prem_to_sg_pp(rt, t):
    """The net premium credited to the shadow account, ``(1 - pi^g) P_t`` **[std]**.

        The shadow load of 8% sits near the 7% market-wide load allowance AG 38 8B uses
        [R1] and far below the 25% base load, which is the whole point: the shadow account
        must credit premiums more generously than the real one for the guarantee to
        outlast the cash value.
        """
    return fr_premium_pp(rt, t) * (1 - rt.ctx.load_prem_rate_sg)

def fr_prem_to_sg_pp(rt, t):
    c = rt.cache[66]
    key = t
    if key in c:
        return c[key]
    val = _calc_prem_to_sg_pp(rt, t)
    c[key] = val
    return val

def _calc_premium_freq(rt):
    """Scheduled premium payments per policy year, from :func:`premium_mode` [S2].

        Annual 1, semi-annual 2, quarterly 4, monthly (EFT only) 12.  Non-annual modes
        carry modal factors in the source design; no carrier publishes them, so the
        scheduled annual premium is divided evenly **[std]** and every shipped model point
        is annual.
        """
    m = fr_premium_mode(rt)
    if m == 'A':
        return 1
    elif m == 'S':
        return 2
    elif m == 'Q':
        return 4
    elif m == 'M':
        return 12
    else:
        raise ValueError('invalid premium mode')

def fr_premium_freq(rt):
    c = rt.cache[67]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_freq(rt)
    c[key] = val
    return val

def _calc_premium_mode(rt):
    """The premium mode: ``"A"``, ``"S"``, ``"Q"`` or ``"M"`` (EFT only) [S2]."""
    return fr_model_point(rt)['premium_mode']

def fr_premium_mode(rt):
    c = rt.cache[68]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_mode(rt)
    c[key] = val
    return val

def _calc_premium_pp(rt, t):
    """P_t: the premium received per policy at BOM of policy month t.

        The scheduled premium in a premium month times :func:`prem_persistency`, zero
        otherwise, and zero from attained age 121 when premiums are no longer accepted
        [S7].  Premiums are flexible in amount and timing after the first [S2][S4]; the
        model projects the scheduled pattern, which is what the guarantee was solved on.
        """
    if fr_age(rt, t) >= rt.ctx.charges_cease_age:
        return 0.0
    if not fr_is_premium_mth(rt, t):
        return 0.0
    if fr_premium_type(rt) == 'SINGLE':
        return fr_premium_pp_ann(rt) * fr_prem_persistency(rt, t)
    return fr_premium_pp_ann(rt) / fr_premium_freq(rt) * fr_prem_persistency(rt, t)

def fr_premium_pp(rt, t):
    c = rt.cache[69]
    key = t
    if key in c:
        return c[key]
    val = _calc_premium_pp(rt, t)
    c[key] = val
    return val

def _calc_premium_pp_ann(rt):
    """The scheduled annual premium per policy, or the single premium for ``"SINGLE"``.

        For the anchor cell this is the notes' solved level no-lapse premium
        ``P* = 10,800`` **[std]**; :func:`no_lapse_premium` re-derives it from the shadow
        recursion rather than reading it from here.
        """
    return float(fr_model_point(rt)['premium_pp_ann'])

def fr_premium_pp_ann(rt):
    c = rt.cache[70]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_pp_ann(rt)
    c[key] = val
    return val

def _calc_premium_taxes(rt, t):
    """Percent-of-premium expense, **zero** on this product.

        The universal life chassis carries a 2.5% premium tax; the guaranteed-UL notes'
        expense list has no percent-of-premium item at all -- the commission sits inside
        the acquisition expense instead -- so the rate is zero and the cells is kept only
        so ``result_cf()`` has the chassis' shape.  Adding a tax here would be an
        unsourced assumption.
        """
    return rt.ctx.premium_tax_rate * fr_premiums(rt, t)

def fr_premium_taxes(rt, t):
    c = rt.cache[71]
    key = t
    if key in c:
        return c[key]
    val = _calc_premium_taxes(rt, t)
    c[key] = val
    return val

def _calc_premium_type(rt):
    """The premium pattern: ``"LEVEL"``, ``"SINGLE"`` or ``"TEN_PAY"`` **[std]**.

        A first-class model point attribute because funding pattern drives both the
        guarantee trajectory and observed lapse behaviour [R8].
        """
    return fr_model_point(rt)['premium_type']

def fr_premium_type(rt):
    c = rt.cache[72]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_type(rt)
    c[key] = val
    return val

def _calc_premiums(rt, t):
    """Premium income at BOM of policy month t, weighted by the in force at BOM."""
    return fr_premium_pp(rt, t) * fr_pols_if(rt, t)

def fr_premiums(rt, t):
    c = rt.cache[73]
    key = t
    if key in c:
        return c[key]
    val = _calc_premiums(rt, t)
    c[key] = val
    return val

def _calc_proj_len(rt):
    """Projection length in policy months.

        ``12 * (charges_cease_age - age_at_entry()) - duration_mth_init()``, the notes'
        maximum projection length: the projection runs to attained age 121, where premiums
        and all charges cease.  Coverage continues past that point under the contract
        [S7], but the illustrative mortality table reaches 1.0 at attained age 120, so
        nothing survives the horizon.
        """
    return 12 * (rt.ctx.charges_cease_age - fr_age_at_entry(rt)) - fr_duration_mth_init(rt)

def fr_proj_len(rt):
    c = rt.cache[74]
    key = None
    if key in c:
        return c[key]
    val = _calc_proj_len(rt)
    c[key] = val
    return val

def _calc_rate_class(rt):
    """The underwriting class of the selected model point (four NT, two tobacco) [S4]."""
    return fr_model_point(rt)['rate_class']

def fr_rate_class(rt):
    c = rt.cache[75]
    key = None
    if key in c:
        return c[key]
    val = _calc_rate_class(rt)
    c[key] = val
    return val

def _calc_rider_charge_pp(rt, t):
    """Rider charges deducted monthly, 0 in the base model **[std]**.

        Rider charges are one of the sourced monthly charge categories [S2][S3][S4][S7][S9],
        but neither rider in scope carries one: the terminal illness accelerated benefit
        takes no premium [S2][S9], and the return-of-premium endorsement is built into the
        representative contract rather than charged for [S1].  The term is carried, as it is
        on the universal life chassis, so that a rider module can be added without changing
        the recursion.
        """
    return 0.0

def fr_rider_charge_pp(rt, t):
    c = rt.cache[76]
    key = t
    if key in c:
        return c[key]
    val = _calc_rider_charge_pp(rt, t)
    c[key] = val
    return val

def _calc_rop_anniversary(rt, t):
    """The return-of-premium anniversary whose window contains month t, or 0 [S1].

        The endorsement is exercisable during the 60 days following policy anniversaries
        20 and 25 [S1][S3][S4].  On a monthly grid the window is taken as the anniversary
        month itself **[std]**, so the exercise rate is applied once rather than spread
        over two monthiversaries.
        """
    if not fr_rop_elected(rt):
        return 0
    if fr_duration_mth(rt, t) % 12 != 0:
        return 0
    y = fr_duration(rt, t)
    return y if y in rt.ctx.data.rop_table().index else 0

def fr_rop_anniversary(rt, t):
    c = rt.cache[77]
    key = t
    if key in c:
        return c[key]
    val = _calc_rop_anniversary(rt, t)
    c[key] = val
    return val

def _calc_rop_elected(rt):
    """Whether the return-of-premium endorsement applies [S1].

        Built into the representative contract, so it is on for every point but the one
        that switches it off to isolate the guarantee mechanics.
        """
    return bool(fr_model_point(rt)['rop_elected'])

def fr_rop_elected(rt):
    c = rt.cache[78]
    key = None
    if key in c:
        return c[key]
    val = _calc_rop_elected(rt)
    c[key] = val
    return val

def _calc_rop_rate(rt, t):
    """w^ROP: the fraction of eligible in-force exercising in the window **[std]**.

        5% at the year-20 window and 10% at the year-25 window.  No public exercise study
        exists; the rationale for keeping them modest is that the 100% refund dominates
        the cash surrender value on a thin-account product, but exercising forfeits a
        now-cheap guarantee.  Mis-setting them distorts years 20-26 of the cash flows.
        """
    a = fr_rop_anniversary(rt, t)
    if a == 0:
        return 0.0
    return float(rt.ctx.data.rop_table().loc[a, 'exercise_rate'])

def fr_rop_rate(rt, t):
    c = rt.cache[79]
    key = t
    if key in c:
        return c[key]
    val = _calc_rop_rate(rt, t)
    c[key] = val
    return val

def _calc_rop_ratio(rt, t):
    """rho: the fraction of cumulative premiums refunded in the window, 50% or 100% [S1]."""
    a = fr_rop_anniversary(rt, t)
    if a == 0:
        return 0.0
    return float(rt.ctx.data.rop_table().loc[a, 'refund_ratio'])

def fr_rop_ratio(rt, t):
    c = rt.cache[80]
    key = t
    if key in c:
        return c[key]
    val = _calc_rop_ratio(rt, t)
    c[key] = val
    return val

def _calc_sex(rt):
    """The sex of the selected model point."""
    return fr_model_point(rt)['sex']

def fr_sex(rt):
    c = rt.cache[81]
    key = None
    if key in c:
        return c[key]
    val = _calc_sex(rt)
    c[key] = val
    return val

def _calc_sg_coi_pp(rt, t):
    """COI_t^g: the shadow cost of insurance charge, ``m_t^g NAAR_t^g / 1000`` **[std]**.

        Notional: it never leaves the insurer and is not a cash flow.  Zero from attained
        age 121, when the shadow charges cease with the base ones **[std]**.
        """
    if fr_age(rt, t) >= rt.ctx.charges_cease_age:
        return 0.0
    return fr_sg_coi_rate(rt, t) / 1000 * fr_sg_net_amt_at_risk(rt, t)

def fr_sg_coi_pp(rt, t):
    c = rt.cache[82]
    key = t
    if key in c:
        return c[key]
    val = _calc_sg_coi_pp(rt, t)
    c[key] = val
    return val

def _calc_sg_coi_rate(rt, t):
    """m_t^g: the shadow monthly COI rate, 55% of the guaranteed maximum **[std]**.

        Kept below the current base rate of 65% so the shadow account depletes more slowly
        than the real one, which is the defining behaviour of the product [S2][S7].
        Rounded like :func:`coi_rate`.
        """
    r = rt.ctx.coi_sg_factor * fr_coi_rate_guar(rt, t)
    dp = fr_coi_rate_dp(rt)
    return r if dp < 0 else round(r, dp)

def fr_sg_coi_rate(rt, t):
    c = rt.cache[83]
    key = t
    if key in c:
        return c[key]
    val = _calc_sg_coi_rate(rt, t)
    c[key] = val
    return val

def _calc_sg_inv_income_pp(rt, t):
    """Interest credited to the shadow account at EOM, ``SG''_t x j^g`` **[std]**.

        Credited on the post-deduction shadow balance with no floor and no loaned/unloaned
        split: the shadow account is notional and carries no loan of its own.
        """
    return fr_sg_pp_at(rt, t, 'BEF_INV') * fr_sg_rate_mth(rt)

def fr_sg_inv_income_pp(rt, t):
    c = rt.cache[84]
    key = t
    if key in c:
        return c[key]
    val = _calc_sg_inv_income_pp(rt, t)
    c[key] = val
    return val

def _calc_sg_maint_fee_pp(rt, t):
    """The non-COI part of the shadow monthly deduction, ``e_u^g U`` **[std]**.

        $0.05 per $1,000 of initial face per month and **no per-policy charge** -- the
        simplest representative choice, since no carrier publishes shadow parameters and
        AG 38 8E only describes shadow accounts as carrying expense charges [R1].
        """
    if fr_age(rt, t) >= rt.ctx.charges_cease_age:
        return 0.0
    return rt.ctx.expense_unit_mth_sg * fr_units(rt, t)

def fr_sg_maint_fee_pp(rt, t):
    c = rt.cache[85]
    key = t
    if key in c:
        return c[key]
    val = _calc_sg_maint_fee_pp(rt, t)
    c[key] = val
    return val

def _calc_sg_naar_factor(rt):
    """The shadow NAAR factor, ``1 + j^g`` = 1.0044717 **[std]**.

        The shadow account discounts the death benefit at *its own* credited rate, which
        is what the notes' step 4 writes, so the two accounts see different net amounts at
        risk even before their balances diverge.
        """
    return 1 + fr_sg_rate_mth(rt)

def fr_sg_naar_factor(rt):
    c = rt.cache[86]
    key = None
    if key in c:
        return c[key]
    val = _calc_sg_naar_factor(rt)
    c[key] = val
    return val

def _calc_sg_net_amt_at_risk(rt, t):
    """NAAR_t^g: the shadow net amount at risk, ``max(DB_t / (1 + j^g) - max(SG'_t, 0), 0)``.

        The same construction as :func:`net_amt_at_risk` on the shadow parameter set
        **[std]**, discounting at the shadow credited rate and flooring the shadow balance
        at zero so that catch-up territory -- a negative shadow account -- does not inflate
        the shadow cost of insurance.
        """
    return max(0.0, fr_db_pp(rt, t) / fr_sg_naar_factor(rt) - max(fr_sg_pp_at(rt, t, 'BEF_COI'), 0.0))

def fr_sg_net_amt_at_risk(rt, t):
    c = rt.cache[87]
    key = t
    if key in c:
        return c[key]
    val = _calc_sg_net_amt_at_risk(rt, t)
    c[key] = val
    return val

def _calc_sg_net_pp(rt, t):
    """SG_t - L_t: the shadow account net of indebtedness, the in-force test quantity.

        Indebtedness is deducted from the guarantee measure rather than from the shadow
        account itself [S4][S2].  The mainstream design; the harshest observed alternative
        voids the guarantee outright on any loan [S5].
        """
    return fr_sg_pp(rt, t) - fr_loan_bal_pp(rt, t)

def fr_sg_net_pp(rt, t):
    c = rt.cache[88]
    key = t
    if key in c:
        return c[key]
    val = _calc_sg_net_pp(rt, t)
    c[key] = val
    return val

def _calc_sg_pp(rt, t):
    """SG_t: the shadow account value per policy at the end of policy month t.

        ``SG_0 = sg_pp_init()``; thereafter ``SG''_t x (1 + j^g)``.  Notional throughout:
        it exists only to run the in-force test and is never payable [S2][S3].
        """
    if t == 0:
        return fr_sg_pp_init(rt)
    return fr_sg_pp_at(rt, t, 'BEF_INV') + fr_sg_inv_income_pp(rt, t)

def fr_sg_pp(rt, t):
    c = rt.cache[89]
    key = t
    if key in c:
        return c[key]
    val = _calc_sg_pp(rt, t)
    c[key] = val
    return val

def _calc_sg_pp_at(rt, t, timing):
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
    if timing == 'BEF_PREM':
        return fr_sg_pp(rt, t - 1)
    elif timing == 'BEF_WD':
        return fr_sg_pp_at(rt, t, 'BEF_PREM') + fr_prem_to_sg_pp(rt, t)
    elif timing == 'BEF_FEE':
        return fr_sg_pp_at(rt, t, 'BEF_WD') - fr_wd_pp(rt, t)
    elif timing == 'BEF_COI':
        return fr_sg_pp_at(rt, t, 'BEF_FEE') - fr_sg_maint_fee_pp(rt, t)
    elif timing == 'BEF_INV':
        return fr_sg_pp_at(rt, t, 'BEF_COI') - fr_sg_coi_pp(rt, t)
    else:
        raise ValueError('invalid timing')

def fr_sg_pp_at(rt, t, timing):
    c = rt.cache[90]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_sg_pp_at(rt, t, timing)
    c[key] = val
    return val

def _calc_sg_pp_init(rt):
    """SG_0: the shadow account value per policy at the outset, 0 at issue.

        Not floored anywhere in the projection: a negative shadow balance measures the
        catch-up shortfall, and flooring it destroys :func:`catch_up_prem_pp`.
        """
    return float(fr_model_point(rt)['sg_pp_init'])

def fr_sg_pp_init(rt):
    c = rt.cache[91]
    key = None
    if key in c:
        return c[key]
    val = _calc_sg_pp_init(rt)
    c[key] = val
    return val

def _calc_sg_rate_mth(rt):
    """j^g: the monthly shadow credited rate, ``(1 + i^g)^(1/12) - 1`` = 0.0044717.

        5.5% annual effective **[std]**, comfortably below the AG 38 8E cap of a
        Moody's-composite-yield index plus 3% that classifies a Design #1 shadow account
        [R1], and well above the 2.0% base guarantee -- which is what makes the guarantee
        outlive the cash value.
        """
    return (1 + rt.ctx.sg_rate_ann) ** (1 / 12) - 1

def fr_sg_rate_mth(rt):
    c = rt.cache[92]
    key = None
    if key in c:
        return c[key]
    val = _calc_sg_rate_mth(rt)
    c[key] = val
    return val

def _calc_sum_assured(rt):
    """F: the initial face amount of the selected model point [S4][S6]."""
    return float(fr_model_point(rt)['sum_assured'])

def fr_sum_assured(rt):
    c = rt.cache[93]
    key = None
    if key in c:
        return c[key]
    val = _calc_sum_assured(rt)
    c[key] = val
    return val

def _calc_sum_assured_at(rt, t):
    """F(t): the face amount in policy month t.

        Level: face increases are not permitted [S2] and elective decreases, option
        changes and the face reduction some designs attach to a withdrawal are not
        modelled -- the notes' withdrawal reduces the account and shadow balances only.
        The cells is kept so the chassis' shape is unchanged and a design with face
        movement can specialise it.
        """
    return fr_sum_assured(rt)

def fr_sum_assured_at(rt, t):
    c = rt.cache[94]
    key = t
    if key in c:
        return c[key]
    val = _calc_sum_assured_at(rt, t)
    c[key] = val
    return val

def _calc_surr_charge_id(rt):
    """The surrender charge schedule ID, a row label of *surr_charge_table.csv*."""
    return fr_model_point(rt)['surr_charge_id']

def fr_surr_charge_id(rt):
    c = rt.cache[95]
    key = None
    if key in c:
        return c[key]
    val = _calc_surr_charge_id(rt)
    c[key] = val
    return val

def _calc_surr_charge_pp(rt, t):
    """SC_t: the surrender charge scheduled per policy in policy month t.

        Quoted on the **initial** face amount.  This is the schedule, not the amount
        collected: see :func:`surr_charge`.
        """
    return fr_surr_charge_rate(rt, t) * fr_sum_assured(rt) / 1000

def fr_surr_charge_pp(rt, t):
    c = rt.cache[96]
    key = t
    if key in c:
        return c[key]
    val = _calc_surr_charge_pp(rt, t)
    c[key] = val
    return val

def _calc_surr_charge_rate(rt, t):
    """SC per $1,000 of initial face in policy month t **[std]**.

        ``max(0, sc_init - (sc_init / runoff_years) x m / 12)`` where ``m`` is the notes'
        own month index ``duration_mth(t) + 1`` -- the current month counts.  With the
        shipped 15-year schedule at $18 per $1,000 this is the spec's
        ``18 x max(0, (180 - m) / 180)``: $17.90 in the issue month, zero from the last
        month of policy year 15.  Reading the notes' month index as ``duration_mth(t)``
        would shift the entire run-off by a month.
        """
    if not fr_has_surr_charge(rt):
        return 0.0
    row = rt.ctx.data.surr_charge_table().loc[fr_surr_charge_id(rt)]
    init = float(row['sc_per_1000_init'])
    yrs = float(row['runoff_years'])
    m = fr_duration_mth(rt, t) + 1
    return max(0.0, init - init / yrs * (m / 12))

def fr_surr_charge_rate(rt, t):
    c = rt.cache[97]
    key = t
    if key in c:
        return c[key]
    val = _calc_surr_charge_rate(rt, t)
    c[key] = val
    return val

def _calc_units(rt, t):
    """U: the face amount in $1,000 units, ``sum_assured_at(t) / 1000``.

        Both per-unit charges are quoted per $1,000 of **initial** face per month, and the
        surrender charge per $1,000 of initial face; with a level face they coincide.
        """
    return fr_sum_assured_at(rt, t) / 1000

def fr_units(rt, t):
    c = rt.cache[98]
    key = t
    if key in c:
        return c[key]
    val = _calc_units(rt, t)
    c[key] = val
    return val

def _calc_wd_fee_pp(rt, t):
    """The $25 withdrawal fee, charged only in a month with a withdrawal [S2][S3][S4][S7].

        Retained by the insurer, so it is account-value outgo but not a liability cash
        flow; it appears in :func:`margin_expense`, not in :func:`claims`.  It is charged
        against the base account only, never the shadow account.
        """
    return rt.ctx.wd_fee if fr_wd_pp(rt, t) > 0 else 0.0

def fr_wd_fee_pp(rt, t):
    c = rt.cache[99]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_fee_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_pp(rt, t):
    """W_t: the partial withdrawal per policy at BOM of policy month t.

        Available after policy year 1 and not after attained age 121 [S2][S3][S4][S7].  The
        amount is the constant monthly figure in the model point's ``wd_pp`` column,
        **0 in every shipped model point**: the notes set utilisation to zero in the base
        model and give no pattern, so the mechanics are implemented and the behaviour is
        left to the data **[std]**.  A withdrawal reduces the account value by the amount
        plus the fee and the shadow account dollar-for-dollar, with no fee [S4].
        """
    if fr_duration_mth(rt, t) < 12 * rt.ctx.wd_first_year:
        return 0.0
    if fr_age(rt, t) >= rt.ctx.charges_cease_age:
        return 0.0
    return float(fr_model_point(rt)['wd_pp'])

def fr_wd_pp(rt, t):
    c = rt.cache[100]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_pp(rt, t)
    c[key] = val
    return val

def _calc_withdrawals(rt, t):
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
    return fr_claim_pp(rt, t, 'WITHDRAWAL') * fr_pols_if(rt, t)

def fr_withdrawals(rt, t):
    c = rt.cache[101]
    key = t
    if key in c:
        return c[key]
    val = _calc_withdrawals(rt, t)
    c[key] = val
    return val

def evaluate(rt, ctx):
    rt.bind(ctx)
    return fr_bench_net_cf(rt)
