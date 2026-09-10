"""Generated static fast-recursive reference runtime."""

class FastRecursiveRuntime:

    def __init__(self, ctx=None):
        self.ctx = ctx
        self.cache = [dict() for _ in range(169)]

    def bind(self, ctx):
        self.ctx = ctx
        for c in self.cache:
            c.clear()
        return self

def _calc_adj_pp(rt, t):
    """ADJ(t): the GWB Adjustment amount at the end of month t; 0 once it terminates."""
    if t < 0:
        return 0.0
    if t == 0:
        return fr_adj_pp_init(rt) + rt.ctx.gwb_adj_pct * fr_prem_to_av_pp(rt, 0)
    if fr_is_gwb_adj_date(rt, t) or fr_policy_year(rt, t) > fr_gwb_adj_year(rt):
        return 0.0
    return fr_adj_pp_bef_anniv(rt, t)

def fr_adj_pp(rt, t):
    c = rt.cache[0]
    key = t
    if key in c:
        return c[key]
    val = _calc_adj_pp(rt, t)
    c[key] = val
    return val

def _calc_adj_pp_bef_anniv(rt, t):
    """ADJ carried into the anniversary events of month t [S1][S3].

        Initialized at 105% of net premium at endorsement, increased by ``s x P(1-tau)`` for
        premiums before the first anniversary after endorsement and by ``P(1-tau)`` for later
        ones, and **voided without value** by any earlier partial withdrawal.
        """
    if t < 1:
        return fr_adj_pp_init(rt)
    if fr_has_wd_by(rt, t):
        return 0.0
    rate = rt.ctx.gwb_adj_pct if fr_duration_mth(rt, t) <= 12 else 1.0
    return fr_adj_pp(rt, t - 1) + rate * fr_prem_to_av_pp(rt, t)

def fr_adj_pp_bef_anniv(rt, t):
    c = rt.cache[1]
    key = t
    if key in c:
        return c[key]
    val = _calc_adj_pp_bef_anniv(rt, t)
    c[key] = val
    return val

def _calc_adj_pp_init(rt):
    """GWB Adjustment carried into ``t = 0``; 105% of net premium at issue [S3]."""
    return float(fr_model_point(rt)['adj_init'])

def fr_adj_pp_init(rt):
    c = rt.cache[2]
    key = None
    if key in c:
        return c[key]
    val = _calc_adj_pp_init(rt)
    c[key] = val
    return val

def _calc_age(rt, t):
    """a(t) = x + y - 1: the attained age (ANB) during month t."""
    return fr_age_at_entry(rt) + fr_duration(rt, t)

def fr_age(rt, t):
    c = rt.cache[3]
    key = t
    if key in c:
        return c[key]
    val = _calc_age(rt, t)
    c[key] = val
    return val

def _calc_age_at_anniv(rt, t):
    """The attained age just after the Contract Anniversary at the end of month t.

        ``x + y``, one more than :func:`age`, and the age the GMDB growth cutoff and the
        Bonus Period restart cutoff are stated against [S1].
        """
    return fr_age_at_entry(rt) + fr_policy_year(rt, t)

def fr_age_at_anniv(rt, t):
    c = rt.cache[4]
    key = t
    if key in c:
        return c[key]
    val = _calc_age_at_anniv(rt, t)
    c[key] = val
    return val

def _calc_age_at_entry(rt):
    """x: the issue age (ANB) of the selected model point."""
    return int(fr_model_point(rt)['age_at_entry'])

def fr_age_at_entry(rt):
    c = rt.cache[5]
    key = None
    if key in c:
        return c[key]
    val = _calc_age_at_entry(rt)
    c[key] = val
    return val

def _calc_alloc(rt, i):
    """alloc[i]: the share of net premium allocated to subaccount i, no rebalancing."""
    return float(rt.ctx.data.fund_table().loc[(fr_fund_set(rt), i), 'alloc'])

def fr_alloc(rt, i):
    c = rt.cache[6]
    key = i
    if key in c:
        return c[key]
    val = _calc_alloc(rt, i)
    c[key] = val
    return val

def _calc_asset_charge_pp(rt, t):
    """The M&E and administrative asset charge collected inside the unit value.

        ``Σ_i SA_i^{pre-charge}(t) (m + alpha)/12`` where the pre-charge value is net of the
        fund's own expense, which is deducted first inside :func:`unit_growth`. This is
        insurer charge income.
        """
    if t < 1 or fr_depleted_flag(rt, t - 1):
        return 0.0
    rate = (rt.ctx.asset_charge_me + rt.ctx.asset_charge_admin) / 12.0
    return sum((fr_sa_pp_at(rt, t, i, 'BEF_INV') * (1.0 + fr_inv_return_mth(rt, t, i)) * (1.0 - fr_fund_expense_rate(rt, i) / 12.0) * rate for i in fr_sub_ids(rt)))

def fr_asset_charge_pp(rt, t):
    c = rt.cache[7]
    key = t
    if key in c:
        return c[key]
    val = _calc_asset_charge_pp(rt, t)
    c[key] = val
    return val

def _calc_asset_charges(rt, t):
    """Charge income from the M&E and administrative asset charge, in-force weighted."""
    return 0.0 if t < 1 else fr_asset_charge_pp(rt, t) * fr_pols_if(rt, t)

def fr_asset_charges(rt, t):
    c = rt.cache[8]
    key = t
    if key in c:
        return c[key]
    val = _calc_asset_charges(rt, t)
    c[key] = val
    return val

def _calc_av_pp(rt, t):
    """AV(t): the contract value per contract at the end of month t."""
    return fr_av_pp_at(rt, t, 'EOM')

def fr_av_pp(rt, t):
    c = rt.cache[9]
    key = t
    if key in c:
        return c[key]
    val = _calc_av_pp(rt, t)
    c[key] = val
    return val

def _calc_av_pp_at(rt, t, timing):
    """AV at month t read at the point given by ``timing``: the sum over subaccounts."""
    return sum((fr_sa_pp_at(rt, t, i, timing) for i in fr_sub_ids(rt)))

def fr_av_pp_at(rt, t, timing):
    c = rt.cache[10]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_av_pp_at(rt, t, timing)
    c[key] = val
    return val

def _calc_av_pp_init(rt):
    """AV carried into ``t = 0``; 0 at issue, the in-force cell's contract value else.

        An in-force contract value is split across subaccounts by ``alloc[i]`` **[std]**: the
        notes give an ``av_initial`` model point attribute but no subaccount split, and the
        worked example's carried state is exactly at its 60/40 target allocation.
        """
    return float(fr_model_point(rt)['av_init'])

def fr_av_pp_init(rt):
    c = rt.cache[11]
    key = None
    if key in c:
        return c[key]
    val = _calc_av_pp_init(rt)
    c[key] = val
    return val

def _calc_bb_pp(rt, t):
    """BB(t): the Bonus Base at the end of month t [S1].

        A step-up sets it to ``max(GWB_after_step-up, BB_before)``; the bonus itself never
        changes it.
        """
    if t < 0:
        return 0.0
    if t == 0:
        return min(rt.ctx.gwb_cap, fr_bb_pp_init(rt) + fr_prem_to_av_pp(rt, 0))
    if fr_depleted_flag(rt, t - 1):
        return fr_bb_pp(rt, t - 1)
    b = fr_bb_pp_bef_anniv(rt, t)
    if fr_is_stepup(rt, t):
        b = max(fr_gwb_pp_aft_stepup(rt, t), b)
    return min(rt.ctx.gwb_cap, b)

def fr_bb_pp(rt, t):
    c = rt.cache[12]
    key = t
    if key in c:
        return c[key]
    val = _calc_bb_pp(rt, t)
    c[key] = val
    return val

def _calc_bb_pp_bef_anniv(rt, t):
    """The Bonus Base carried into the anniversary events of month t [S1].

        Increased by net premium, set to ``min(GWB_after, BB_before)`` on an excess
        withdrawal, and otherwise unaffected by withdrawals. Applying the bonus does not
        change it.
        """
    if t < 1:
        return fr_bb_pp_init(rt)
    if fr_depleted_flag(rt, t - 1):
        return fr_bb_pp(rt, t - 1)
    b = min(rt.ctx.gwb_cap, fr_bb_pp(rt, t - 1) + fr_prem_to_av_pp(rt, t))
    if fr_wd_pp(rt, t) > 0.0 and fr_sum_wd_pp(rt, t) > fr_wd_limit_pp(rt, t):
        b = min(fr_gwb_pp_at(rt, t, 'BEF_ANNIV'), b)
    return b

def fr_bb_pp_bef_anniv(rt, t):
    c = rt.cache[13]
    key = t
    if key in c:
        return c[key]
    val = _calc_bb_pp_bef_anniv(rt, t)
    c[key] = val
    return val

def _calc_bb_pp_init(rt):
    """Bonus Base carried into ``t = 0``; it initializes at GWB [S1]."""
    return float(fr_model_point(rt)['bb_init'])

def fr_bb_pp_init(rt):
    c = rt.cache[14]
    key = None
    if key in c:
        return c[key]
    val = _calc_bb_pp_init(rt)
    c[key] = val
    return val

def _calc_bench_net_cf(rt):
    return sum((fr_net_cf(rt, t) for t in range(0, fr_proj_len(rt) + 1)))

def fr_bench_net_cf(rt):
    c = rt.cache[15]
    key = None
    if key in c:
        return c[key]
    val = _calc_bench_net_cf(rt)
    c[key] = val
    return val

def _calc_bonus_end(rt, t):
    """The contract year in which the Bonus Period ends [S1].

        Ten Contract Years from the endorsement effective date, **restarting** on each
        Bonus-Base-increasing step-up occurring on or before the anniversary following the
        Designated Life's 80th birthday. A hard-coded 10-year window from issue materially
        understates the guarantee in rising markets.
        """
    if t <= 0:
        return fr_bonus_end_init(rt) if fr_is_inforce(rt) else rt.ctx.bonus_period_years
    prev = fr_bonus_end(rt, t - 1)
    if fr_is_stepup(rt, t) and fr_age_at_anniv(rt, t) <= rt.ctx.bonus_restart_age and (fr_gwb_pp_aft_stepup(rt, t) > fr_bb_pp_bef_anniv(rt, t)):
        return fr_policy_year(rt, t) + rt.ctx.bonus_period_years
    return prev

def fr_bonus_end(rt, t):
    c = rt.cache[16]
    key = t
    if key in c:
        return c[key]
    val = _calc_bonus_end(rt, t)
    c[key] = val
    return val

def _calc_bonus_end_init(rt):
    """The contract year the Bonus Period ends, carried into ``t = 0``.

        Zero on an at-issue cell, where it is set to ``bonus_period_years`` = 10 [S1].
        """
    return int(fr_model_point(rt)['bonus_end_init'])

def fr_bonus_end_init(rt):
    c = rt.cache[17]
    key = None
    if key in c:
        return c[key]
    val = _calc_bonus_end_init(rt)
    c[key] = val
    return val

def _calc_bonus_pp(rt, t):
    """The GLWB bonus credited at the Contract Anniversary ending month t.

        ``b x BB`` if **no withdrawal was taken in the contract year** and the year is within
        the Bonus Period [S1]. *Any* withdrawal kills the whole year's bonus, including an
        automatic withdrawal or an RMD; pro-rating it for a partial year is wrong.
        """
    if not fr_is_anniv(rt, t) or fr_depleted_flag(rt, t - 1):
        return 0.0
    if fr_policy_year(rt, t) > fr_bonus_end(rt, t - 1) or fr_is_wd_year(rt, t):
        return 0.0
    return rt.ctx.bonus_pct * fr_bb_pp_bef_anniv(rt, t)

def fr_bonus_pp(rt, t):
    c = rt.cache[18]
    key = t
    if key in c:
        return c[key]
    val = _calc_bonus_pp(rt, t)
    c[key] = val
    return val

def _calc_cdsc_schedule(rt):
    """The key into *cdsc_table.csv* naming this contract's withdrawal charge scale."""
    return fr_model_point(rt)['cdsc_schedule']

def fr_cdsc_schedule(rt):
    c = rt.cache[19]
    key = None
    if key in c:
        return c[key]
    val = _calc_cdsc_schedule(rt)
    c[key] = val
    return val

def _calc_charge_income(rt, t):
    """Total insurer charge income in month t, excluding the double-counted CDSC."""
    return fr_asset_charges(rt, t) + fr_fees_glwb(rt, t) + fr_fees_gmdb(rt, t) + fr_maint_fees(rt, t)

def fr_charge_income(rt, t):
    c = rt.cache[20]
    key = t
    if key in c:
        return c[key]
    val = _calc_charge_income(rt, t)
    c[key] = val
    return val

def _calc_charge_pp(rt, t):
    """The total unit cancellation at EOM of month t: the two rider fees and f_c."""
    return fr_charge_pp_due(rt, t) * fr_charge_scale(rt, t)

def fr_charge_pp(rt, t):
    c = rt.cache[21]
    key = t
    if key in c:
        return c[key]
    val = _calc_charge_pp(rt, t)
    c[key] = val
    return val

def _calc_charge_pp_due(rt, t):
    """The total unit cancellation due at EOM before capping at the contract value."""
    return fr_fee_glwb_pp_due(rt, t) + fr_fee_gmdb_pp_due(rt, t) + fr_maint_fee_pp_due(rt, t)

def fr_charge_pp_due(rt, t):
    c = rt.cache[22]
    key = t
    if key in c:
        return c[key]
    val = _calc_charge_pp_due(rt, t)
    c[key] = val
    return val

def _calc_charge_scale(rt, t):
    """The fraction of the charges due that the contract value can actually pay **[std]**.

        Charges are collected only up to the available contract value; the shortfall is not
        carried forward. This binds in at most one month per contract, the one in which the
        account is exhausted, and it is what makes :func:`check_av_roll_fwd` close there.
        """
    due = fr_charge_pp_due(rt, t)
    if due <= 0.0:
        return 0.0
    return min(1.0, fr_av_pp_at(rt, t, 'BEF_FEE') / due)

def fr_charge_scale(rt, t):
    c = rt.cache[23]
    key = t
    if key in c:
        return c[key]
    val = _calc_charge_scale(rt, t)
    c[key] = val
    return val

def _calc_claim_pp(rt, t, kind):
    """The benefit paid per contract in month t by ``kind``.

        ``"DEATH"`` is the gross death benefit :func:`db_pp`. ``"LAPSE"`` is the surrender
        proceeds :func:`surr_benefit_pp`. ``"MATURITY"`` is the surrender value of the
        survivors at the projection horizon.
        """
    if kind == 'DEATH':
        return fr_db_pp(rt, t)
    elif kind == 'LAPSE':
        return fr_surr_benefit_pp(rt, t)
    elif kind == 'MATURITY':
        return fr_surr_benefit_pp(rt, t)
    else:
        raise ValueError('invalid kind')

def fr_claim_pp(rt, t, kind):
    c = rt.cache[24]
    key = (t, kind)
    if key in c:
        return c[key]
    val = _calc_claim_pp(rt, t, kind)
    c[key] = val
    return val

def _calc_claims(rt, t, kind=None):
    """Benefit outgo in month t, for one ``kind`` or, with ``kind=None``, all three."""
    if kind is None:
        return fr_claims(rt, t, 'DEATH') + fr_claims(rt, t, 'LAPSE') + fr_claims(rt, t, 'MATURITY')
    return fr_claim_pp(rt, t, kind) * fr_pols_decr(rt, t, kind)

def fr_claims(rt, t, kind=None):
    c = rt.cache[25]
    key = (t, kind)
    if key in c:
        return c[key]
    val = _calc_claims(rt, t, kind)
    c[key] = val
    return val

def _calc_cmt10(rt, t):
    """The 20-day average 10-year Constant Maturity Treasury rate at month t [S7].

        Used only by the ``cmt_linked`` roll-up rule.
        """
    return fr_scenario_rate(rt, t, 'cmt10')

def fr_cmt10(rt, t):
    c = rt.cache[26]
    key = t
    if key in c:
        return c[key]
    val = _calc_cmt10(rt, t)
    c[key] = val
    return val

def _calc_commissions(rt, t):
    """Acquisition commission; **0 in the base run [std]**, the notes not modelling it."""
    return rt.ctx.comm_rate_acq * fr_premiums(rt, t)

def fr_commissions(rt, t):
    c = rt.cache[27]
    key = t
    if key in c:
        return c[key]
    val = _calc_commissions(rt, t)
    c[key] = val
    return val

def _calc_contract_quarter(rt, t):
    """k(t) = ceil(policy month / 3): the contract quarter containing month t."""
    return (fr_duration_mth(rt, t) + 2) // 3

def fr_contract_quarter(rt, t):
    c = rt.cache[28]
    key = t
    if key in c:
        return c[key]
    val = _calc_contract_quarter(rt, t)
    c[key] = val
    return val

def _calc_cv_pre_excess_pp(rt, t):
    """CV_pre: the contract value after the non-excess portion has been deducted [S1].

        The order is decisive: the non-excess portion reduces the base dollar-for-dollar
        **first**, and the proportional factor for the excess is computed against the
        contract value *after* that reduction. Reversing it changes both GWB and GAWA.
        """
    return fr_av_pp_at(rt, t, 'BEF_WD') - fr_wd_nonexcess_pp(rt, t)

def fr_cv_pre_excess_pp(rt, t):
    c = rt.cache[29]
    key = t
    if key in c:
        return c[key]
    val = _calc_cv_pre_excess_pp(rt, t)
    c[key] = val
    return val

def _calc_db_pp(rt, t):
    """DB(t) = max(AV(t), NP(t), RB(t)): the **gross** death benefit outflow [S1].

        Zero once the contract value has reached zero with the GLWB in force: all other
        endorsements terminate without value and **no death benefit is payable on subsequent
        death** [S1].
        """
    if fr_depleted_flag(rt, t):
        return 0.0
    return max(fr_av_pp(rt, t), fr_gmdb_guarantee_pp(rt, t))

def fr_db_pp(rt, t):
    c = rt.cache[30]
    key = t
    if key in c:
        return c[key]
    val = _calc_db_pp(rt, t)
    c[key] = val
    return val

def _calc_depleted_flag(rt, t):
    """True once the contract value has reached zero with the GLWB in force [S1].

        Absorbing: once set it never clears. The threshold is half a cent **[std]** — the
        charge cap in :func:`charge_scale` and the withdrawal cap in :func:`wd_pp` both drive
        the account to exactly zero, so the threshold only guards floating point.
        """
    if t < 0:
        return False
    if t > 0 and fr_depleted_flag(rt, t - 1):
        return True
    return fr_av_pp(rt, t) <= rt.ctx.av_depletion_threshold

def fr_depleted_flag(rt, t):
    c = rt.cache[31]
    key = t
    if key in c:
        return c[key]
    val = _calc_depleted_flag(rt, t)
    c[key] = val
    return val

def _calc_duration(rt, t):
    """Completed contract years at month t, ``policy_year(t) - 1``, floored at 0."""
    return max(0, fr_policy_year(rt, t) - 1)

def fr_duration(rt, t):
    c = rt.cache[32]
    key = t
    if key in c:
        return c[key]
    val = _calc_duration(rt, t)
    c[key] = val
    return val

def _calc_duration_mth(rt, t):
    """The policy month at projection month t: ``duration_mth_init() + t``."""
    return fr_duration_mth_init(rt) + t

def fr_duration_mth(rt, t):
    c = rt.cache[33]
    key = t
    if key in c:
        return c[key]
    val = _calc_duration_mth(rt, t)
    c[key] = val
    return val

def _calc_duration_mth_init(rt):
    """Policy months already elapsed at ``t = 0``; 0 for an at-issue cell.

        An in-force cell enters mid-contract, so ``t = 1`` is policy month
        ``duration_mth_init() + 1``. The worked example's carried state is entered this way
        on model point 2.
        """
    return int(fr_model_point(rt)['duration_mth_init'])

def fr_duration_mth_init(rt):
    c = rt.cache[34]
    key = None
    if key in c:
        return c[key]
    val = _calc_duration_mth_init(rt)
    c[key] = val
    return val

def _calc_excess_factor(rt, t):
    """``1 - E(t)/CV_pre``: the pro-rata factor applied to GWB, GAWA and BB [S1]."""
    base = fr_cv_pre_excess_pp(rt, t)
    if base <= 0.0:
        return 0.0
    return max(0.0, 1.0 - fr_wd_excess_pp(rt, t) / base)

def fr_excess_factor(rt, t):
    c = rt.cache[35]
    key = t
    if key in c:
        return c[key]
    val = _calc_excess_factor(rt, t)
    c[key] = val
    return val

def _calc_expenses(rt, t):
    """VM-21 §6.C.2 prescribed maintenance expense [R1].

        ``[100 x 1.025^(valuation year - 2015)]/12`` per contract per month, inflating 2.5%
        a year, **plus 7 basis points of projected account value** for a company-administered
        block. Acquisition expense is not modelled in the base run **[std]**.
        """
    if t == 0:
        return rt.ctx.expense_acq * fr_pols_if(rt, 0)
    if t < 0 or t > fr_proj_len(rt):
        return 0.0
    per_contract = rt.ctx.expense_maint / 12.0 * fr_inflation_factor(rt, t)
    per_av = rt.ctx.expense_av_rate / 12.0 * fr_av_pp(rt, t)
    return (per_contract + per_av) * fr_pols_if(rt, t)

def fr_expenses(rt, t):
    c = rt.cache[36]
    key = t
    if key in c:
        return c[key]
    val = _calc_expenses(rt, t)
    c[key] = val
    return val

def _calc_fee_glwb_pp(rt, t):
    """The GLWB rider fee actually collected in month t."""
    return fr_fee_glwb_pp_due(rt, t) * fr_charge_scale(rt, t)

def fr_fee_glwb_pp(rt, t):
    c = rt.cache[37]
    key = t
    if key in c:
        return c[key]
    val = _calc_fee_glwb_pp(rt, t)
    c[key] = val
    return val

def _calc_fee_glwb_pp_due(rt, t):
    """Fee_G = (phi_G/4) x GWB at a Contract Quarterly Anniversary [S1][S3].

        The base is the **benefit base, not the account value** — putting the rider fee on
        account value is the most common and most consequential error on this product. The
        fee therefore rises as markets fall, until the account reaches zero, at which point
        it stops [S4].
        """
    if t < 1 or fr_depleted_flag(rt, t - 1) or (not fr_is_quarterly_anniv(rt, t)):
        return 0.0
    return fr_phi_glwb(rt, t) / 4.0 * fr_gwb_pp_at(rt, t, 'BEF_ANNIV')

def fr_fee_glwb_pp_due(rt, t):
    c = rt.cache[38]
    key = t
    if key in c:
        return c[key]
    val = _calc_fee_glwb_pp_due(rt, t)
    c[key] = val
    return val

def _calc_fee_gmdb_pp(rt, t):
    """The GMDB rider fee actually collected in month t."""
    return fr_fee_gmdb_pp_due(rt, t) * fr_charge_scale(rt, t)

def fr_fee_gmdb_pp(rt, t):
    c = rt.cache[39]
    key = t
    if key in c:
        return c[key]
    val = _calc_fee_gmdb_pp(rt, t)
    c[key] = val
    return val

def _calc_fee_gmdb_pp_due(rt, t):
    """Fee_D = (phi_D/4) x RB at a Contract Quarterly Anniversary [S2][S3].

        The charge base is the GMDB Benefit Base; the quarterly frequency aligns it with the
        GLWB fee **[std]**, the research file recording quarterly for the GMWB family only.
        """
    if t < 1 or fr_depleted_flag(rt, t - 1) or (not fr_is_quarterly_anniv(rt, t)):
        return 0.0
    return fr_phi_gmdb(rt, t) / 4.0 * fr_rb_pp_at(rt, t, 'BEF_ANNIV')

def fr_fee_gmdb_pp_due(rt, t):
    c = rt.cache[40]
    key = t
    if key in c:
        return c[key]
    val = _calc_fee_gmdb_pp_due(rt, t)
    c[key] = val
    return val

def _calc_fee_rate_vix_clip(rt, prior, raw):
    """Clip a VIX-formula rate to the movement band and the absolute corridor [S4].

        The band is +/-0.40% annualized against the prior quarter's rate (advisory class) and
        the corridor is [0.60%, 2.50%]. The second disclosed example clips to 1.82% against a
        prior rate of 1.42%.
        """
    lo = max(rt.ctx.vix_corridor_lo, prior - rt.ctx.vix_band)
    hi = min(rt.ctx.vix_corridor_hi, prior + rt.ctx.vix_band)
    return min(hi, max(lo, raw))

def fr_fee_rate_vix_clip(rt, prior, raw):
    c = rt.cache[41]
    key = (prior, raw)
    if key in c:
        return c[key]
    val = _calc_fee_rate_vix_clip(rt, prior, raw)
    c[key] = val
    return val

def _calc_fee_rate_vix_raw(rt, phi_0, vix_sq_avg):
    """The unclipped VIX-squared fee formula [S4][S6].

        ``phi_0 + 0.05% x [ QuarterlyAverage(daily VIX^2) / 33 - 10 ]``. The disclosed
        examples are an initial 1.45% with a quarterly average of 204.42 giving 1.26%, and
        602.30 giving an unclipped 1.86%.
        """
    return phi_0 + rt.ctx.vix_fee_coef * (vix_sq_avg / rt.ctx.vix_divisor - rt.ctx.vix_offset)

def fr_fee_rate_vix_raw(rt, phi_0, vix_sq_avg):
    c = rt.cache[42]
    key = (phi_0, vix_sq_avg)
    if key in c:
        return c[key]
    val = _calc_fee_rate_vix_raw(rt, phi_0, vix_sq_avg)
    c[key] = val
    return val

def _calc_fee_reset_rule(rt):
    """``none``, ``quinquennial`` or ``vix``.

        ``none`` is the base run **[std]**: the insurer does not increase the rider charge
        and the owner does not opt out. ``quinquennial`` applies the maximum single increase
        of +0.25% at each fifth Contract Anniversary up to the guaranteed maximum [S1].
        ``vix`` applies a second carrier's non-discretionary VIX-squared formula [S4][S6].
        """
    return fr_model_point(rt)['fee_reset_rule']

def fr_fee_reset_rule(rt):
    c = rt.cache[43]
    key = None
    if key in c:
        return c[key]
    val = _calc_fee_reset_rule(rt)
    c[key] = val
    return val

def _calc_fees_glwb(rt, t):
    """Charge income from the GLWB rider fee, in-force weighted."""
    return 0.0 if t < 1 else fr_fee_glwb_pp(rt, t) * fr_pols_if(rt, t)

def fr_fees_glwb(rt, t):
    c = rt.cache[44]
    key = t
    if key in c:
        return c[key]
    val = _calc_fees_glwb(rt, t)
    c[key] = val
    return val

def _calc_fees_gmdb(rt, t):
    """Charge income from the GMDB rider fee, in-force weighted."""
    return 0.0 if t < 1 else fr_fee_gmdb_pp(rt, t) * fr_pols_if(rt, t)

def fr_fees_gmdb(rt, t):
    c = rt.cache[45]
    key = t
    if key in c:
        return c[key]
    val = _calc_fees_gmdb(rt, t)
    c[key] = val
    return val

def _calc_forlife_flag(rt):
    """Whether the For Life Guarantee is in effect from issue [S1].

        True when the Designated Life is 59 1/2 or older. On an age-nearest-birthday basis an
        ANB of 60 is exactly an actual age of 59 1/2 or more, so the test is
        ``age_at_entry() >= 60`` with no approximation **[std]**.
        """
    return fr_age_at_entry(rt) >= rt.ctx.forlife_age

def fr_forlife_flag(rt):
    c = rt.cache[46]
    key = None
    if key in c:
        return c[key]
    val = _calc_forlife_flag(rt)
    c[key] = val
    return val

def _calc_free_wd_allow(rt, t):
    """The charge-free amount at month t: earnings first, then 10% of Remaining Premium.

        The notes state it as ``max(0, AV - RP)`` plus ``max(0, 0.10 RP - earnings)``, which
        is ``max(earnings, 0.10 x RP)`` [S1]. Aged-out premium is free too, which the CDSC
        scale delivers by reaching 0.0% at seven completed years [S2].
        """
    rp = fr_rp_pp(rt, t - 1) + fr_premium_pp(rt, t) if t >= 1 else fr_rp_pp_init(rt)
    earnings = max(0.0, fr_av_pp_at(rt, t, 'BEF_WD') - rp)
    return max(earnings, rt.ctx.free_wd_rate * rp)

def fr_free_wd_allow(rt, t):
    c = rt.cache[47]
    key = t
    if key in c:
        return c[key]
    val = _calc_free_wd_allow(rt, t)
    c[key] = val
    return val

def _calc_free_wd_avail(rt, t):
    """The free-withdrawal allowance still unused in the contract year at BOM of month t."""
    if t < 1:
        return 0.0
    used = 0.0 if fr_is_year_start(rt, t) else fr_free_wd_used_cum_pp(rt, t - 1)
    return max(0.0, fr_free_wd_allow(rt, t) - used)

def fr_free_wd_avail(rt, t):
    c = rt.cache[48]
    key = t
    if key in c:
        return c[key]
    val = _calc_free_wd_avail(rt, t)
    c[key] = val
    return val

def _calc_free_wd_used_cum_pp(rt, t):
    """The free allowance consumed so far in the contract year, including month t.

        The year-to-date cumulative of :func:`wd_free_pp`, reset at each contract year
        start; it is what :func:`free_wd_avail` and :func:`surr_free_pp` net off.
        """
    if t < 1:
        return 0.0
    prev = 0.0 if fr_is_year_start(rt, t) else fr_free_wd_used_cum_pp(rt, t - 1)
    return prev + fr_wd_free_pp(rt, t)

def fr_free_wd_used_cum_pp(rt, t):
    c = rt.cache[49]
    key = t
    if key in c:
        return c[key]
    val = _calc_free_wd_used_cum_pp(rt, t)
    c[key] = val
    return val

def _calc_fund_expense_rate(rt, i):
    """e_i: the annual fund expense ratio of subaccount i, paid to the fund [S2]."""
    return float(rt.ctx.data.fund_table().loc[(fr_fund_set(rt), i), 'fund_expense'])

def fr_fund_expense_rate(rt, i):
    c = rt.cache[50]
    key = i
    if key in c:
        return c[key]
    val = _calc_fund_expense_rate(rt, i)
    c[key] = val
    return val

def _calc_fund_set(rt):
    """The key into *fund_table.csv* naming this contract's subaccount allocation."""
    return fr_model_point(rt)['fund_set']

def fr_fund_set(rt):
    c = rt.cache[51]
    key = None
    if key in c:
        return c[key]
    val = _calc_fund_set(rt)
    c[key] = val
    return val

def _calc_gawa_pct_at_age(rt, a):
    """g(a): the GAWA% for attained age a, from *gawa_pct_table.csv* [S3]."""
    grid = rt.ctx.data.gawa_pct_table().loc[fr_glwb_option(rt)]
    bands = [b for b in grid.index if b <= a]
    if not bands:
        return 0.0
    return float(grid.loc[max(bands), 'gawa_pct'])

def fr_gawa_pct_at_age(rt, a):
    c = rt.cache[52]
    key = a
    if key in c:
        return c[key]
    val = _calc_gawa_pct_at_age(rt, a)
    c[key] = val
    return val

def _calc_gawa_pct_fixed(rt, t):
    """The GAWA% locked at the first withdrawal; 0 until then [S1].

        If the contract value reaches zero with the percentage not yet fixed, it is fixed at
        the percentage for the attained age at that moment [S1].
        """
    if t < 0:
        return 0.0
    if t == 0:
        return fr_gawa_pct_init(rt)
    prev = fr_gawa_pct_fixed(rt, t - 1)
    if prev > 0.0:
        return prev
    if fr_is_first_wd(rt, t) or fr_depleted_flag(rt, t):
        return fr_gawa_pct_at_age(rt, fr_age(rt, t))
    return 0.0

def fr_gawa_pct_fixed(rt, t):
    c = rt.cache[53]
    key = t
    if key in c:
        return c[key]
    val = _calc_gawa_pct_fixed(rt, t)
    c[key] = val
    return val

def _calc_gawa_pct_init(rt):
    """The GAWA% already locked at ``t = 0``; 0 when no withdrawal has been taken."""
    return float(fr_model_point(rt)['gawa_pct_init'])

def fr_gawa_pct_init(rt):
    c = rt.cache[54]
    key = None
    if key in c:
        return c[key]
    val = _calc_gawa_pct_init(rt)
    c[key] = val
    return val

def _calc_gawa_pp(rt, t):
    """GAWA(t): the Guaranteed Annual Withdrawal Amount at the end of month t [S1].

        After the first withdrawal, both the bonus and the step-up raise it to
        ``max(g x GWB, GAWA)``. If the For Life Guarantee is not in effect and ``GWB < GAWA``
        at a Contract Year end, GAWA is set equal to GWB.
        """
    if t < 0:
        return 0.0
    if t == 0:
        return fr_gawa_pp_init(rt)
    if fr_depleted_flag(rt, t - 1):
        return fr_gawa_pp(rt, t - 1)
    g = fr_gawa_pp_at(rt, t, 'BEF_ANNIV')
    if fr_is_anniv(rt, t):
        pct = fr_gawa_pct_fixed(rt, t)
        if fr_has_wd_by(rt, t) and pct > 0.0:
            if fr_bonus_pp(rt, t) > 0.0:
                g = max(pct * fr_gwb_pp_aft_bonus(rt, t), g)
            if fr_is_stepup(rt, t):
                g = max(pct * fr_gwb_pp_aft_stepup(rt, t), g)
        if not fr_forlife_flag(rt) and fr_gwb_pp(rt, t) < g:
            g = fr_gwb_pp(rt, t)
    if g <= 0.0 and fr_depleted_flag(rt, t) and (fr_gawa_pct_fixed(rt, t) > 0.0):
        g = fr_gawa_pct_fixed(rt, t) * fr_gwb_pp(rt, t)
    return g

def fr_gawa_pp(rt, t):
    c = rt.cache[55]
    key = t
    if key in c:
        return c[key]
    val = _calc_gawa_pp(rt, t)
    c[key] = val
    return val

def _calc_gawa_pp_at(rt, t, timing):
    """GAWA at month t read at ``BEF_PREM``, ``BEF_WD`` or ``BEF_ANNIV`` [S1]."""
    if t < 1:
        return fr_gawa_pp_init(rt)
    if fr_depleted_flag(rt, t - 1):
        return fr_gawa_pp(rt, t - 1)
    g = fr_gawa_pp(rt, t - 1)
    if timing == 'BEF_PREM':
        return g
    if fr_has_wd_by(rt, t - 1) and fr_prem_to_av_pp(rt, t) > 0.0:
        g = g + fr_gawa_pct_fixed(rt, t - 1) * fr_prem_to_av_pp(rt, t)
    if timing == 'BEF_WD':
        return g
    if fr_is_first_wd(rt, t):
        g = fr_gawa_pct_at_age(rt, fr_age(rt, t)) * fr_gwb_pp_at(rt, t, 'BEF_WD')
    if fr_wd_pp(rt, t) > 0.0 and fr_sum_wd_pp(rt, t) > fr_wd_limit_pp(rt, t):
        g = min(g * fr_excess_factor(rt, t), fr_gwb_pp_at(rt, t, 'BEF_ANNIV'))
    if timing == 'BEF_ANNIV':
        return g
    raise ValueError('invalid timing')

def fr_gawa_pp_at(rt, t, timing):
    c = rt.cache[56]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_gawa_pp_at(rt, t, timing)
    c[key] = val
    return val

def _calc_gawa_pp_init(rt):
    """GAWA carried into ``t = 0``; 0 until the first withdrawal fixes it [S1]."""
    return float(fr_model_point(rt)['gawa_init'])

def fr_gawa_pp_init(rt):
    c = rt.cache[57]
    key = None
    if key in c:
        return c[key]
    val = _calc_gawa_pp_init(rt)
    c[key] = val
    return val

def _calc_glwb_option(rt):
    """The GLWB election, and the key into the GAWA% grid; ``single_core`` [S3]."""
    return fr_model_point(rt)['glwb_option']

def fr_glwb_option(rt):
    c = rt.cache[58]
    key = None
    if key in c:
        return c[key]
    val = _calc_glwb_option(rt)
    c[key] = val
    return val

def _calc_glwb_payment_pp(rt, t):
    """The insurer-funded GLWB payment in month t once the contract is depleted [S1].

        With the For Life Guarantee in effect, GAWA is paid for the life of the Designated
        Life. Without it, payments continue until the earlier of death and GWB depletion, the
        final one truncated to the remaining GWB. The notes place the routine at BOM and the
        payment "at each Contract Anniversary"; the model pays it at the BOM of the first
        month of each contract year **[std]**, the instant just after the anniversary, which
        keeps it on the same clock as the pre-depletion withdrawals.
        """
    if t < 1 or t > fr_proj_len(rt) or (not fr_depleted_flag(rt, t - 1)):
        return 0.0
    if not fr_is_year_start(rt, t):
        return 0.0
    amount = fr_gawa_pp(rt, t - 1)
    return amount if fr_forlife_flag(rt) else min(amount, fr_gwb_pp(rt, t - 1))

def fr_glwb_payment_pp(rt, t):
    c = rt.cache[59]
    key = t
    if key in c:
        return c[key]
    val = _calc_glwb_payment_pp(rt, t)
    c[key] = val
    return val

def _calc_glwb_payments(rt, t):
    """Insurer-funded post-depletion GLWB payments, weighted by ``pols_if(t)``."""
    return 0.0 if t < 1 else fr_glwb_payment_pp(rt, t) * fr_pols_if(rt, t)

def fr_glwb_payments(rt, t):
    c = rt.cache[60]
    key = t
    if key in c:
        return c[key]
    val = _calc_glwb_payments(rt, t)
    c[key] = val
    return val

def _calc_gmdb_allow_pp(rt, t):
    """The contract year's dollar-for-dollar GMDB withdrawal allowance [S1].

        ``rho x RB`` at the previous anniversary. Withdrawals inside it reduce the Benefit
        Base dollar for dollar; anything above it reduces it proportionally.
        """
    return fr_rollup_rate(rt, t) * fr_rb_prior_anniv_pp(rt, t)

def fr_gmdb_allow_pp(rt, t):
    c = rt.cache[61]
    key = t
    if key in c:
        return c[key]
    val = _calc_gmdb_allow_pp(rt, t)
    c[key] = val
    return val

def _calc_gmdb_dfd_acc_pp(rt, t):
    """The dollar-for-dollar reduction accrued so far in the contract year [S1].

        **GMDB withdrawal adjustments are applied at Contract Year end**, not at the
        withdrawal; applying them immediately changes the base the roll-up compounds on.
        """
    if t < 1:
        return 0.0
    prev = 0.0 if fr_is_year_start(rt, t) else fr_gmdb_dfd_acc_pp(rt, t - 1)
    return prev + fr_gmdb_wd_dfd_pp(rt, t)

def fr_gmdb_dfd_acc_pp(rt, t):
    c = rt.cache[62]
    key = t
    if key in c:
        return c[key]
    val = _calc_gmdb_dfd_acc_pp(rt, t)
    c[key] = val
    return val

def _calc_gmdb_factor_acc(rt, t):
    """The proportional factor accrued so far in the contract year **[std]**."""
    if t < 1:
        return 1.0
    prev = 1.0 if fr_is_year_start(rt, t) else fr_gmdb_factor_acc(rt, t - 1)
    return prev * fr_gmdb_wd_factor(rt, t)

def fr_gmdb_factor_acc(rt, t):
    c = rt.cache[63]
    key = t
    if key in c:
        return c[key]
    val = _calc_gmdb_factor_acc(rt, t)
    c[key] = val
    return val

def _calc_gmdb_guarantee_pp(rt, t):
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
    if fr_gmdb_option(rt) == 'basic':
        return fr_rb_pp(rt, t)
    return max(fr_np_pp(rt, t), fr_rb_pp(rt, t))

def fr_gmdb_guarantee_pp(rt, t):
    c = rt.cache[64]
    key = t
    if key in c:
        return c[key]
    val = _calc_gmdb_guarantee_pp(rt, t)
    c[key] = val
    return val

def _calc_gmdb_option(rt):
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
    return fr_model_point(rt)['gmdb_option']

def fr_gmdb_option(rt):
    c = rt.cache[65]
    key = None
    if key in c:
        return c[key]
    val = _calc_gmdb_option(rt)
    c[key] = val
    return val

def _calc_gmdb_wd_dfd_pp(rt, t):
    """The dollar-for-dollar portion of month t's withdrawal against the allowance [S1]."""
    if t < 1 or fr_wd_pp(rt, t) <= 0.0 or fr_gmdb_option(rt) != 'rollup':
        return 0.0
    used = 0.0 if fr_is_year_start(rt, t) else fr_gmdb_dfd_acc_pp(rt, t - 1)
    return min(fr_wd_pp(rt, t), max(0.0, fr_gmdb_allow_pp(rt, t) - used))

def fr_gmdb_wd_dfd_pp(rt, t):
    c = rt.cache[66]
    key = t
    if key in c:
        return c[key]
    val = _calc_gmdb_wd_dfd_pp(rt, t)
    c[key] = val
    return val

def _calc_gmdb_wd_excess_pp(rt, t):
    """The portion of month t's withdrawal above the GMDB d-f-d allowance [S1]."""
    if t < 1 or fr_gmdb_option(rt) != 'rollup':
        return 0.0
    return fr_wd_pp(rt, t) - fr_gmdb_wd_dfd_pp(rt, t)

def fr_gmdb_wd_excess_pp(rt, t):
    c = rt.cache[67]
    key = t
    if key in c:
        return c[key]
    val = _calc_gmdb_wd_excess_pp(rt, t)
    c[key] = val
    return val

def _calc_gmdb_wd_factor(rt, t):
    """The proportional factor month t's excess GMDB withdrawal accrues **[std]**.

        The notes say the adjustment above the allowance is "proportional to the contract
        value reduction from the excess" but leave the base unstated. The model measures it
        the same way the GLWB does: against the contract value after the dollar-for-dollar
        portion has been deducted.
        """
    if fr_gmdb_wd_excess_pp(rt, t) <= 0.0:
        return 1.0
    base = fr_av_pp_at(rt, t, 'BEF_WD') - fr_gmdb_wd_dfd_pp(rt, t)
    if base <= 0.0:
        return 0.0
    return max(0.0, 1.0 - fr_gmdb_wd_excess_pp(rt, t) / base)

def fr_gmdb_wd_factor(rt, t):
    c = rt.cache[68]
    key = t
    if key in c:
        return c[key]
    val = _calc_gmdb_wd_factor(rt, t)
    c[key] = val
    return val

def _calc_gwb_adj_year(rt):
    """The contract year of the GWB Adjustment Date [S1].

        The later of the anniversary on or after the Designated Life's 70th birthday and the
        12th Contract Anniversary.
        """
    return max(rt.ctx.gwb_adj_min_year, rt.ctx.gwb_adj_age - fr_age_at_entry(rt))

def fr_gwb_adj_year(rt):
    c = rt.cache[69]
    key = None
    if key in c:
        return c[key]
    val = _calc_gwb_adj_year(rt)
    c[key] = val
    return val

def _calc_gwb_pp(rt, t):
    """GWB(t): the Guaranteed Withdrawal Balance at the end of month t [S1].

        Anniversary sub-steps 5 to 7 finish here: the GWB Adjustment Date test, which raises
        the GWB to the Adjustment only if no withdrawal has ever been taken, and the
        $10,000,000 cap. In the depleted state the balance is run down by each payment when
        the For Life Guarantee is not in effect, and is left alone when it is.
        """
    if t < 0:
        return 0.0
    if t == 0:
        return min(rt.ctx.gwb_cap, fr_gwb_pp_init(rt) + fr_prem_to_av_pp(rt, 0))
    if fr_depleted_flag(rt, t - 1):
        g = fr_gwb_pp(rt, t - 1)
        return g if fr_forlife_flag(rt) else max(0.0, g - fr_glwb_payment_pp(rt, t))
    g = fr_gwb_pp_aft_stepup(rt, t)
    if fr_is_gwb_adj_date(rt, t) and (not fr_has_wd_by(rt, t)):
        g = max(g, fr_adj_pp_bef_anniv(rt, t))
    return min(rt.ctx.gwb_cap, g)

def fr_gwb_pp(rt, t):
    c = rt.cache[70]
    key = t
    if key in c:
        return c[key]
    val = _calc_gwb_pp(rt, t)
    c[key] = val
    return val

def _calc_gwb_pp_aft_bonus(rt, t):
    """GWB after anniversary sub-step 3, the GLWB bonus."""
    return fr_gwb_pp_at(rt, t, 'BEF_ANNIV') + fr_bonus_pp(rt, t)

def fr_gwb_pp_aft_bonus(rt, t):
    c = rt.cache[71]
    key = t
    if key in c:
        return c[key]
    val = _calc_gwb_pp_aft_bonus(rt, t)
    c[key] = val
    return val

def _calc_gwb_pp_aft_stepup(rt, t):
    """GWB after anniversary sub-step 4, the step-up.

        The **[std]** order — bonus first, then step-up — gives
        ``max(GWB_old + bonus, AV)``; the reverse gives ``max(GWB_old, AV) + bonus``, which
        is strictly more generous. The research file does not settle the interaction, and the
        choice made here follows the one design in the set that states it explicitly [S8].
        Treat the alternative as a first-order sensitivity, not a rounding issue.
        """
    return max(fr_gwb_pp_aft_bonus(rt, t), fr_stepup_base_pp(rt, t)) if fr_is_anniv(rt, t) else fr_gwb_pp_aft_bonus(rt, t)

def fr_gwb_pp_aft_stepup(rt, t):
    c = rt.cache[72]
    key = t
    if key in c:
        return c[key]
    val = _calc_gwb_pp_aft_stepup(rt, t)
    c[key] = val
    return val

def _calc_gwb_pp_at(rt, t, timing):
    """GWB at month t read at ``BEF_PREM``, ``BEF_WD`` or ``BEF_ANNIV`` [S1]."""
    if t < 1:
        return fr_gwb_pp_init(rt)
    if fr_depleted_flag(rt, t - 1):
        return fr_gwb_pp(rt, t - 1)
    g = fr_gwb_pp(rt, t - 1)
    if timing == 'BEF_PREM':
        return g
    g = min(rt.ctx.gwb_cap, g + fr_prem_to_av_pp(rt, t))
    if timing == 'BEF_WD':
        return g
    if fr_wd_pp(rt, t) > 0.0:
        if fr_sum_wd_pp(rt, t) <= fr_wd_limit_pp(rt, t):
            g = max(g - fr_wd_pp(rt, t), 0.0)
        else:
            g = max((g - fr_wd_nonexcess_pp(rt, t)) * fr_excess_factor(rt, t), 0.0)
    if timing == 'BEF_ANNIV':
        return g
    raise ValueError('invalid timing')

def fr_gwb_pp_at(rt, t, timing):
    c = rt.cache[73]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_gwb_pp_at(rt, t, timing)
    c[key] = val
    return val

def _calc_gwb_pp_init(rt):
    """GWB carried into ``t = 0``; 0 at issue, where the premium creates it [S1]."""
    return float(fr_model_point(rt)['gwb_init'])

def fr_gwb_pp_init(rt):
    c = rt.cache[74]
    key = None
    if key in c:
        return c[key]
    val = _calc_gwb_pp_init(rt)
    c[key] = val
    return val

def _calc_has_wd_by(rt, t):
    """True when a withdrawal has been taken at or before month t."""
    if t < 1:
        return fr_has_wd_init(rt)
    return fr_has_wd_by(rt, t - 1) or fr_is_wd_taken(rt, t)

def fr_has_wd_by(rt, t):
    c = rt.cache[75]
    key = t
    if key in c:
        return c[key]
    val = _calc_has_wd_by(rt, t)
    c[key] = val
    return val

def _calc_has_wd_init(rt):
    """Whether a withdrawal had already been taken before ``t = 0``.

        Inferred from ``gawa_pct_init``, which is non-zero exactly when the GAWA% has been
        locked, so an in-force cell needs no separate flag column.
        """
    return fr_gawa_pct_init(rt) > 0.0

def fr_has_wd_init(rt):
    c = rt.cache[76]
    key = None
    if key in c:
        return c[key]
    val = _calc_has_wd_init(rt)
    c[key] = val
    return val

def _calc_inflation_factor(rt, t):
    """The VM-21 §6.C.2 expense inflation factor for the contract year containing t.

        ``1.025^(valuation year - 2015 + completed contract years)`` [R1].
        """
    return (1.0 + rt.ctx.inflation_rate) ** (rt.ctx.valuation_year - rt.ctx.expense_base_year + fr_duration(rt, t))

def fr_inflation_factor(rt, t):
    c = rt.cache[77]
    key = t
    if key in c:
        return c[key]
    val = _calc_inflation_factor(rt, t)
    c[key] = val
    return val

def _calc_inv_return_mth(rt, t, i):
    """r_i(t): the gross monthly fund return of subaccount i, a scenario input.

        Read from *return_scenario.csv* as a step function of the **policy** month, so a flat
        path is one row per subaccount. VM-21 requires each variable subaccount to be mapped
        to a crafted proxy fund, normally a linear combination of recognized market indices
        [R1]; the model takes the return series as an input rather than hard-coding one.
        """
    sub = rt.ctx.data.return_scenario().loc[fr_scenario_id(rt), i]
    months = [m for m in sub.index if m <= max(fr_duration_mth(rt, t), 0)]
    return float(sub.loc[max(months), 'gross_return'])

def fr_inv_return_mth(rt, t, i):
    c = rt.cache[78]
    key = (t, i)
    if key in c:
        return c[key]
    val = _calc_inv_return_mth(rt, t, i)
    c[key] = val
    return val

def _calc_is_anniv(rt, t):
    """True at the end of a Contract Anniversary month, ``policy month = 0 (mod 12)``."""
    return t >= 1 and t <= fr_proj_len(rt) and (fr_duration_mth(rt, t) % 12 == 0)

def fr_is_anniv(rt, t):
    c = rt.cache[79]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_anniv(rt, t)
    c[key] = val
    return val

def _calc_is_first_wd(rt, t):
    """True in the month of the contract's first withdrawal.

        The notes are explicit that this test must run **before** the annual limit ``L`` is
        formed: a first withdrawal tested against ``GAWA = 0`` would score entirely as excess
        and wreck both benefit bases [S1].
        """
    return fr_is_wd_taken(rt, t) and (not fr_has_wd_by(rt, t - 1))

def fr_is_first_wd(rt, t):
    c = rt.cache[80]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_first_wd(rt, t)
    c[key] = val
    return val

def _calc_is_gwb_adj_date(rt, t):
    """True at the Contract Anniversary that is the GWB Adjustment Date."""
    return fr_is_anniv(rt, t) and fr_policy_year(rt, t) == fr_gwb_adj_year(rt)

def fr_is_gwb_adj_date(rt, t):
    c = rt.cache[81]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_gwb_adj_date(rt, t)
    c[key] = val
    return val

def _calc_is_inforce(rt):
    """True when the model point enters mid-contract rather than at issue."""
    return fr_duration_mth_init(rt) > 0

def fr_is_inforce(rt):
    c = rt.cache[82]
    key = None
    if key in c:
        return c[key]
    val = _calc_is_inforce(rt)
    c[key] = val
    return val

def _calc_is_quarterly_anniv(rt, t):
    """True at a Contract Quarterly Anniversary, ``policy month = 0 (mod 3)`` **[std]**."""
    return t >= 1 and t <= fr_proj_len(rt) and (fr_duration_mth(rt, t) % 3 == 0)

def fr_is_quarterly_anniv(rt, t):
    c = rt.cache[83]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_quarterly_anniv(rt, t)
    c[key] = val
    return val

def _calc_is_stepup(rt, t):
    """True when the anniversary step-up fires: the contract value exceeds the GWB [S1]."""
    return fr_is_anniv(rt, t) and fr_stepup_base_pp(rt, t) > fr_gwb_pp_aft_bonus(rt, t)

def fr_is_stepup(rt, t):
    c = rt.cache[84]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_stepup(rt, t)
    c[key] = val
    return val

def _calc_is_wd_month(rt, t):
    """True when the GLWB utilization withdrawal falls in month t.

        Base run **[std]**: the contract activates in the first month of the contract year in
        which the attained age reaches :func:`wd_start_age`, and withdraws in the first month
        of every contract year thereafter. ``wd_start_age = 0`` never withdraws.
        """
    if t < 1 or t > fr_proj_len(rt) or fr_wd_start_age(rt) <= 0:
        return False
    if fr_depleted_flag(rt, t - 1) or not fr_is_year_start(rt, t):
        return False
    return fr_age(rt, t) >= fr_wd_start_age(rt)

def fr_is_wd_month(rt, t):
    c = rt.cache[85]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_wd_month(rt, t)
    c[key] = val
    return val

def _calc_is_wd_taken(rt, t):
    """True when any withdrawal is taken in month t, before its amount is known.

        Stated as a predicate rather than ``wd_pp(t) > 0`` so that the first-withdrawal test
        can run *before* the GAWA% is fixed, which is what the amount itself depends on.
        """
    if t < 1 or t > fr_proj_len(rt) or fr_depleted_flag(rt, t - 1):
        return False
    return fr_wd_scheduled_pp(rt, t) > 0.0 or fr_is_wd_month(rt, t)

def fr_is_wd_taken(rt, t):
    c = rt.cache[86]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_wd_taken(rt, t)
    c[key] = val
    return val

def _calc_is_wd_year(rt, t):
    """True when any withdrawal falls in the contract year containing month t.

        Drives the VM-21 withdrawal-year surrender factor ``kappa`` [R1] and the rule that
        *any* withdrawal in a Contract Year kills that year's bonus [S1].
        """
    first = fr_t_of_month(rt, 12 * (fr_policy_year(rt, t) - 1) + 1)
    return any((fr_is_wd_taken(rt, u) for u in range(max(1, first), min(first + 12, fr_proj_len(rt) + 1))))

def fr_is_wd_year(rt, t):
    c = rt.cache[87]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_wd_year(rt, t)
    c[key] = val
    return val

def _calc_is_year_start(rt, t):
    """True in the first month of a contract year, where SumW_y resets [S1]."""
    return t >= 1 and (fr_duration_mth(rt, t) - 1) % 12 == 0

def fr_is_year_start(rt, t):
    c = rt.cache[88]
    key = t
    if key in c:
        return c[key]
    val = _calc_is_year_start(rt, t)
    c[key] = val
    return val

def _calc_lapse_dyn_mult(rt, t):
    """lambda*(t) = min(lambda(M_G), lambda(M_D)) [R1].

        The contract carries both a VAGLB and a GMDB, and VM-21 §6.C.6 directs that such
        contracts use the **lower** of the two ITM-based rates.
        """
    return min(fr_lapse_itm_mult(rt, fr_moneyness_glwb(rt, t)), fr_lapse_itm_mult(rt, fr_moneyness_gmdb(rt, t)))

def fr_lapse_dyn_mult(rt, t):
    c = rt.cache[89]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_dyn_mult(rt, t)
    c[key] = val
    return val

def _calc_lapse_itm_mult(rt, m):
    """lambda(M): the VM-21 §7.B.1 Alternative Methodology multiplier [R1].

        ``min[U, max(L, 1 - Mult (M - D))]`` with U = 1.00, L = 0.50, Mult = 1.25, D = 1.10 —
        the only closed-form dynamic lapse formula the Valuation Manual publishes for VAs.
        Note that it floors suppression at 50% while Table 6.3's own ITM grading implies an
        84% suppression; compose one or the other, never both.
        """
    raw = 1.0 - rt.ctx.lapse_itm_mult_coef * (m - rt.ctx.lapse_itm_threshold)
    return min(rt.ctx.lapse_itm_upper, max(rt.ctx.lapse_itm_lower, raw))

def fr_lapse_itm_mult(rt, m):
    c = rt.cache[90]
    key = m
    if key in c:
        return c[key]
    val = _calc_lapse_itm_mult(rt, m)
    c[key] = val
    return val

def _calc_lapse_rate(rt, t):
    """q^w_annual(t) = min[1, base x lambda* x kappa] **[std] composition** [R1].

        The **annual** total surrender rate; :func:`lapse_rate_mth` is the monthly one, the
        pair matching :func:`mort_rate` / :func:`mort_rate_mth`. Zero whenever the contract
        value is zero: the prescribed surrender assumption for a GMWB contract at ``AV = 0``
        is 0% [R1]. This is the single most important behavioural assumption on the product,
        because it determines how many deeply in-the-money contracts persist to become
        claims.
        """
    if fr_av_pp(rt, t) <= 0.0:
        return 0.0
    return min(1.0, fr_lapse_rate_base(rt, t) * fr_lapse_dyn_mult(rt, t) * fr_lapse_wd_factor(rt, t))

def fr_lapse_rate(rt, t):
    c = rt.cache[91]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate_base(rt, t):
    """q^w_base(y): VM-21 Table 6.3's "under 50% ITM" column **[std]** [R1].

        4.0% p.a. during the surrender-charge period (contract years 1 to 7 here [S2]),
        25.0% in the first year after it, 15.0% thereafter.
        """
    year = fr_policy_year(rt, t)
    if year <= rt.ctx.surr_charge_years:
        return rt.ctx.lapse_rate_sc
    elif year == rt.ctx.surr_charge_years + 1:
        return rt.ctx.lapse_rate_shock
    return rt.ctx.lapse_rate_ult

def fr_lapse_rate_base(rt, t):
    c = rt.cache[92]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate_base(rt, t)
    c[key] = val
    return val

def _calc_lapse_rate_mth(rt, t):
    """q^w(t): the monthly surrender rate, ``1 - (1 - q^w_annual)^(1/12)`` **[std]**."""
    return 1.0 - (1.0 - fr_lapse_rate(rt, t)) ** (1.0 / 12.0)

def fr_lapse_rate_mth(rt, t):
    c = rt.cache[93]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_rate_mth(rt, t)
    c[key] = val
    return val

def _calc_lapse_wd_factor(rt, t):
    """kappa(t): 0.60 in any contract year with a projected withdrawal, else 1.00 [R1]."""
    return rt.ctx.lapse_wd_year_factor if fr_is_wd_year(rt, t) else 1.0

def fr_lapse_wd_factor(rt, t):
    c = rt.cache[94]
    key = t
    if key in c:
        return c[key]
    val = _calc_lapse_wd_factor(rt, t)
    c[key] = val
    return val

def _calc_maint_fee_pp(rt, t):
    """The annual contract fee actually collected in month t."""
    return fr_maint_fee_pp_due(rt, t) * fr_charge_scale(rt, t)

def fr_maint_fee_pp(rt, t):
    c = rt.cache[95]
    key = t
    if key in c:
        return c[key]
    val = _calc_maint_fee_pp(rt, t)
    c[key] = val
    return val

def _calc_maint_fee_pp_due(rt, t):
    """f_c: the $35 annual contract fee, waived at a contract value of $50,000 or more.

        Assessed at the Contract Anniversary and deducted proportionally across investment
        divisions [S2]. The waiver is tested on the contract value after the rider fees
        **[std]**, the notes placing the contract fee after them in the processing order.
        """
    if t < 1 or fr_depleted_flag(rt, t - 1) or (not fr_is_anniv(rt, t)):
        return 0.0
    after_riders = fr_av_pp_at(rt, t, 'BEF_FEE') - fr_fee_glwb_pp_due(rt, t) - fr_fee_gmdb_pp_due(rt, t)
    return 0.0 if after_riders >= rt.ctx.maint_fee_waiver_av else rt.ctx.maint_fee

def fr_maint_fee_pp_due(rt, t):
    c = rt.cache[96]
    key = t
    if key in c:
        return c[key]
    val = _calc_maint_fee_pp_due(rt, t)
    c[key] = val
    return val

def _calc_maint_fees(rt, t):
    """Charge income from the annual contract fee, in-force weighted."""
    return 0.0 if t < 1 else fr_maint_fee_pp(rt, t) * fr_pols_if(rt, t)

def fr_maint_fees(rt, t):
    c = rt.cache[97]
    key = t
    if key in c:
        return c[key]
    val = _calc_maint_fees(rt, t)
    c[key] = val
    return val

def _calc_model_point(rt):
    """The selected model point as a Series."""
    return rt.ctx.data.model_point_table().loc[rt.ctx.point_id]

def fr_model_point(rt):
    c = rt.cache[98]
    key = None
    if key in c:
        return c[key]
    val = _calc_model_point(rt)
    c[key] = val
    return val

def _calc_moneyness_glwb(rt, t):
    """M_G(t) = GWB(t) / AV(t): the living-benefit in-the-moneyness ratio [R1]."""
    return fr_gwb_pp(rt, t) / fr_av_pp(rt, t) if fr_av_pp(rt, t) > 0.0 else 0.0

def fr_moneyness_glwb(rt, t):
    c = rt.cache[99]
    key = t
    if key in c:
        return c[key]
    val = _calc_moneyness_glwb(rt, t)
    c[key] = val
    return val

def _calc_moneyness_gmdb(rt, t):
    """M_D(t) = max(NP(t), RB(t)) / AV(t): the death-benefit moneyness ratio [R1].

        Measured on the guarantee actually floored under ``DB``, not on ``RB`` alone.
        """
    return fr_gmdb_guarantee_pp(rt, t) / fr_av_pp(rt, t) if fr_av_pp(rt, t) > 0.0 else 0.0

def fr_moneyness_gmdb(rt, t):
    c = rt.cache[100]
    key = t
    if key in c:
        return c[key]
    val = _calc_moneyness_gmdb(rt, t)
    c[key] = val
    return val

def _calc_mort_rate(rt, t):
    """The annual mortality rate at the attained age and sex, from *mort_table.csv*.

        The shipped table is an illustrative annuitant curve **[std]**, *not* a published
        basis. The prescribed basis is the 2012 IAM **Basic** Table improved to December 31,
        2017 on Projection Scale G2, generational, with no further improvement in the
        projection [R1][REG-R59]; it may not be redistributed here, so swap it in by
        repointing ``Data.mort_table_file``. **Do not use CSO or VBT life tables** —
        annuitant mortality is a different and generally lighter basis [REG-R59].
        """
    table = rt.ctx.data.mort_table()
    top = max((a for a, s in table.index))
    return float(table.loc[(min(fr_age(rt, t), top), fr_sex(rt)), 'mort_rate'])

def fr_mort_rate(rt, t):
    c = rt.cache[101]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate(rt, t)
    c[key] = val
    return val

def _calc_mort_rate_mth(rt, t):
    """q^d(t): the monthly mortality rate, ``1 - (1 - q_x)^(1/12)`` **[std]**."""
    return 1.0 - (1.0 - fr_mort_rate(rt, t)) ** (1.0 / 12.0)

def fr_mort_rate_mth(rt, t):
    c = rt.cache[102]
    key = t
    if key in c:
        return c[key]
    val = _calc_mort_rate_mth(rt, t)
    c[key] = val
    return val

def _calc_net_cf(rt, t):
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
    return fr_premiums(rt, t) + fr_charge_income(rt, t) - fr_withdrawals(rt, t) - fr_glwb_payments(rt, t) - fr_claims(rt, t) - fr_expenses(rt, t) - fr_commissions(rt, t) - fr_premium_taxes(rt, t)

def fr_net_cf(rt, t):
    c = rt.cache[103]
    key = t
    if key in c:
        return c[key]
    val = _calc_net_cf(rt, t)
    c[key] = val
    return val

def _calc_np_pp(rt, t):
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
        return fr_np_pp_init(rt) + fr_prem_to_av_pp(rt, 0)
    if fr_depleted_flag(rt, t - 1):
        return fr_np_pp(rt, t - 1)
    return fr_np_pp(rt, t - 1) + fr_prem_to_av_pp(rt, t)

def fr_np_pp(rt, t):
    c = rt.cache[104]
    key = t
    if key in c:
        return c[key]
    val = _calc_np_pp(rt, t)
    c[key] = val
    return val

def _calc_np_pp_init(rt):
    """Cumulative Net Premiums carried into ``t = 0``."""
    return float(fr_model_point(rt)['np_init'])

def fr_np_pp_init(rt):
    c = rt.cache[105]
    key = None
    if key in c:
        return c[key]
    val = _calc_np_pp_init(rt)
    c[key] = val
    return val

def _calc_phi_glwb(rt, t):
    """phi_G: the annual GLWB rider charge rate in force in month t.

        1.25% of the GWB currently [S3], guaranteed maximum 3.00% **[std]** within an
        observed 1.20%-3.00% band by option and vintage [S1]. ``fee_reset_rule`` selects the
        reset mechanism; the base run does not increase the charge and the owner does not opt
        out **[std]**, because opting out forfeits bonus, step-up and GWB Adjustment and
        blocks future premium [S1], so a rational opt-out is a joint decision rather than an
        independent lapse-style rate.
        """
    rule = fr_fee_reset_rule(rt)
    if rule == 'none':
        return rt.ctx.phi_glwb_curr
    elif rule == 'quinquennial':
        steps = fr_duration(rt, t) // rt.ctx.fee_reset_years
        return min(rt.ctx.phi_glwb_max, rt.ctx.phi_glwb_curr + rt.ctx.fee_increase_max * steps)
    elif rule == 'vix':
        return fr_phi_glwb_vix(rt, fr_contract_quarter(rt, t))
    else:
        raise ValueError('invalid fee_reset_rule')

def fr_phi_glwb(rt, t):
    c = rt.cache[106]
    key = t
    if key in c:
        return c[key]
    val = _calc_phi_glwb(rt, t)
    c[key] = val
    return val

def _calc_phi_glwb_vix(rt, k):
    """The VIX-formula GLWB charge rate in contract quarter k [S4][S6]."""
    if k <= 1:
        return rt.ctx.phi_glwb_curr
    prior = fr_phi_glwb_vix(rt, k - 1)
    return fr_fee_rate_vix_clip(rt, prior, fr_fee_rate_vix_raw(rt, rt.ctx.phi_glwb_curr, fr_vix_sq(rt, k)))

def fr_phi_glwb_vix(rt, k):
    c = rt.cache[107]
    key = k
    if key in c:
        return c[key]
    val = _calc_phi_glwb_vix(rt, k)
    c[key] = val
    return val

def _calc_phi_gmdb(rt, t):
    """phi_D: the annual GMDB rider charge rate in force in month t.

        0.90% of the GMDB Benefit Base currently, guaranteed maximum 1.80% [S2][S3]. The
        ``basic`` death benefit is included at no charge [S1][S2], so the rate is zero there.
        """
    return 0.0 if fr_gmdb_option(rt) == 'basic' else rt.ctx.phi_gmdb_curr

def fr_phi_gmdb(rt, t):
    c = rt.cache[108]
    key = t
    if key in c:
        return c[key]
    val = _calc_phi_gmdb(rt, t)
    c[key] = val
    return val

def _calc_policy_term(rt):
    """Contract term in years: entry age to ``omega_age`` **[std]**."""
    return rt.ctx.omega_age - fr_age_at_entry(rt)

def fr_policy_term(rt):
    c = rt.cache[109]
    key = None
    if key in c:
        return c[key]
    val = _calc_policy_term(rt)
    c[key] = val
    return val

def _calc_policy_year(rt, t):
    """y(t) = ceil(policy month / 12): the contract year; 0 at issue."""
    return (fr_duration_mth(rt, t) + 11) // 12

def fr_policy_year(rt, t):
    c = rt.cache[110]
    key = t
    if key in c:
        return c[key]
    val = _calc_policy_year(rt, t)
    c[key] = val
    return val

def _calc_pols_death(rt, t):
    """Deaths in month t, on the contracts in force at the start of it."""
    return 0.0 if t < 1 else fr_pols_if(rt, t) * fr_mort_rate_mth(rt, t)

def fr_pols_death(rt, t):
    c = rt.cache[111]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_death(rt, t)
    c[key] = val
    return val

def _calc_pols_decr(rt, t, kind):
    """The number of contracts leaving in month t by benefit ``kind``."""
    if kind == 'DEATH':
        return fr_pols_death(rt, t)
    elif kind == 'LAPSE':
        return fr_pols_lapse(rt, t)
    elif kind == 'MATURITY':
        return fr_pols_maturity(rt, t)
    else:
        raise ValueError('invalid kind')

def fr_pols_decr(rt, t, kind):
    c = rt.cache[112]
    key = (t, kind)
    if key in c:
        return c[key]
    val = _calc_pols_decr(rt, t, kind)
    c[key] = val
    return val

def _calc_pols_if(rt, t):
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
        return fr_pols_if_init(rt)
    if t > fr_proj_len(rt):
        return 0.0
    return fr_pols_if_at(rt, t - 1, 'AFT_DECR')

def fr_pols_if(rt, t):
    c = rt.cache[113]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_if(rt, t)
    c[key] = val
    return val

def _calc_pols_if_at(rt, t, timing):
    """In-force at month t read at ``BEF_DECR``, ``BEF_LAPSE`` or ``AFT_DECR``.

        The order is the notes' ``l(t) = l(t-1)(1 - q^d(t))(1 - q^w(t))`` — **death first,
        then surrender** **[std]**. ``"BEF_DECR"`` is :func:`pols_if` ``(t)`` and
        ``"AFT_DECR"`` is the notes' ``l(t)``, the end-of-month count.
        """
    if t < 1:
        return fr_pols_if_init(rt)
    pols = fr_pols_if(rt, t)
    if timing == 'BEF_DECR':
        return pols
    pols = pols * (1.0 - fr_mort_rate_mth(rt, t))
    if timing == 'BEF_LAPSE':
        return pols
    pols = pols * (1.0 - fr_lapse_rate_mth(rt, t))
    if timing == 'AFT_DECR':
        return pols
    raise ValueError('invalid timing')

def fr_pols_if_at(rt, t, timing):
    c = rt.cache[114]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_pols_if_at(rt, t, timing)
    c[key] = val
    return val

def _calc_pols_if_init(rt):
    """l(0): in-force probability at entry, 1 for a single-contract model point."""
    return float(fr_model_point(rt)['pols_if_init'])

def fr_pols_if_init(rt):
    c = rt.cache[115]
    key = None
    if key in c:
        return c[key]
    val = _calc_pols_if_init(rt)
    c[key] = val
    return val

def _calc_pols_lapse(rt, t):
    """Full surrenders in month t, on the survivors of mortality."""
    return 0.0 if t < 1 else fr_pols_if_at(rt, t, 'BEF_LAPSE') * fr_lapse_rate_mth(rt, t)

def fr_pols_lapse(rt, t):
    c = rt.cache[116]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_lapse(rt, t)
    c[key] = val
    return val

def _calc_pols_maturity(rt, t):
    """Survivors carried out at the projection horizon; zero in every other month.

        Not a decrement — the projection runs out — but needed for the in-force roll-forward
        to close; see the Space docstring.
        """
    return fr_pols_if_at(rt, t, 'AFT_DECR') if t == fr_proj_len(rt) else 0.0

def fr_pols_maturity(rt, t):
    c = rt.cache[117]
    key = t
    if key in c:
        return c[key]
    val = _calc_pols_maturity(rt, t)
    c[key] = val
    return val

def _calc_prem_scheduled_pp(rt, t):
    """The gross premium scheduled for month t in *transaction_table.csv*, else zero."""
    if t < 1:
        return 0.0
    table = rt.ctx.data.transaction_table()
    key = (fr_txn_id(rt), fr_duration_mth(rt, t))
    return float(table.loc[key, 'prem_amount']) if key in table.index else 0.0

def fr_prem_scheduled_pp(rt, t):
    c = rt.cache[118]
    key = t
    if key in c:
        return c[key]
    val = _calc_prem_scheduled_pp(rt, t)
    c[key] = val
    return val

def _calc_prem_to_av_pp(rt, t):
    """P(t)(1 - tau): the net premium that buys units and raises the guarantee bases.

        The per-contract counterpart of :func:`prem_to_av`, and the name every
        account-value model in this library uses for the premium credited to the account
        value. Not to be confused with ``WholeLife_US_A.premium_net_pp``, which is a *gross*
        premium net of the dividend offset — a different concept entirely.
        """
    return fr_premium_pp(rt, t) * (1.0 - fr_premium_tax_rate(rt))

def fr_prem_to_av_pp(rt, t):
    c = rt.cache[119]
    key = t
    if key in c:
        return c[key]
    val = _calc_prem_to_av_pp(rt, t)
    c[key] = val
    return val

def _calc_premium_pp(rt, t):
    """P(t): the gross premium paid at BOM of month t.

        The model point's single purchase payment at ``t = 0``, plus anything scheduled in
        *transaction_table.csv*. The chassis is flexible-premium [S1][S2] and premium receipt
        is retained as an active term in every guarantee-base recursion, so a subsequent
        payment is a data change rather than a formula change.
        """
    if t == 0:
        return fr_premium_single(rt) + fr_prem_scheduled_pp(rt, t)
    if t < 0 or t > fr_proj_len(rt) or fr_depleted_flag(rt, t - 1):
        return 0.0
    return fr_prem_scheduled_pp(rt, t)

def fr_premium_pp(rt, t):
    c = rt.cache[120]
    key = t
    if key in c:
        return c[key]
    val = _calc_premium_pp(rt, t)
    c[key] = val
    return val

def _calc_premium_single(rt):
    """The single purchase payment stated on the model point, paid at ``t = 0``."""
    return float(fr_model_point(rt)['premium'])

def fr_premium_single(rt):
    c = rt.cache[121]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_single(rt)
    c[key] = val
    return val

def _calc_premium_tax_rate(rt):
    """tau: premium tax deducted from the purchase payment, 0% **[std]**, 0-3.5% [S2].

        Set to zero so that GWB at issue equals gross premium and the worked example is
        checkable; premium tax is contractually deducted from the amounts that initialize the
        guarantee bases [S1].
        """
    return float(fr_model_point(rt)['premium_tax_rate'])

def fr_premium_tax_rate(rt):
    c = rt.cache[122]
    key = None
    if key in c:
        return c[key]
    val = _calc_premium_tax_rate(rt)
    c[key] = val
    return val

def _calc_premium_taxes(rt, t):
    """Premium tax deducted from the purchase payment, 0% **[std]** [S2]."""
    return fr_premium_tax_rate(rt) * fr_premiums(rt, t)

def fr_premium_taxes(rt, t):
    c = rt.cache[123]
    key = t
    if key in c:
        return c[key]
    val = _calc_premium_taxes(rt, t)
    c[key] = val
    return val

def _calc_premiums(rt, t):
    """Premium income in month t, weighted by the contracts in force at the start of it.

        ``pols_if(0)`` is ``pols_if_init()``, so the entry instant needs no special case.
        """
    return 0.0 if t < 0 else fr_premium_pp(rt, t) * fr_pols_if(rt, t)

def fr_premiums(rt, t):
    c = rt.cache[124]
    key = t
    if key in c:
        return c[key]
    val = _calc_premiums(rt, t)
    c[key] = val
    return val

def _calc_proj_len(rt):
    """Projection length in months from ``t = 0``, net of months already elapsed."""
    return 12 * fr_policy_term(rt) - fr_duration_mth_init(rt)

def fr_proj_len(rt):
    c = rt.cache[125]
    key = None
    if key in c:
        return c[key]
    val = _calc_proj_len(rt)
    c[key] = val
    return val

def _calc_rb_pp(rt, t):
    """RB(t): the GMDB Benefit Base at the end of month t.

        Growth cutoffs are **age-based, not duration-based**: roll-up and ratchet growth stop
        at the Contract Anniversary preceding the oldest Covered Life's 81st birthday [S1],
        so an issue-age-60 cell gets 20 roll-up credits and an issue-age-75 cell gets 5.
        """
    if t < 0:
        return 0.0
    if t == 0:
        return fr_rb_pp_init(rt) + fr_prem_to_av_pp(rt, 0)
    if fr_depleted_flag(rt, t - 1):
        return fr_rb_pp(rt, t - 1)
    r = fr_rb_pp_at(rt, t, 'BEF_ANNIV')
    if not fr_is_anniv(rt, t):
        return r
    option = fr_gmdb_option(rt)
    if option == 'rollup':
        r = max(0.0, (r - fr_gmdb_dfd_acc_pp(rt, t)) * fr_gmdb_factor_acc(rt, t))
        if fr_age_at_anniv(rt, t) <= rt.ctx.gmdb_growth_cutoff_age:
            r = r * (1.0 + fr_rollup_rate(rt, t))
    elif option == 'HQAV':
        if fr_age_at_anniv(rt, t) <= rt.ctx.gmdb_growth_cutoff_age:
            r = max(r, fr_av_pp(rt, t))
    elif option == 'basic':
        pass
    else:
        raise ValueError('invalid gmdb_option')
    return r

def fr_rb_pp(rt, t):
    c = rt.cache[126]
    key = t
    if key in c:
        return c[key]
    val = _calc_rb_pp(rt, t)
    c[key] = val
    return val

def _calc_rb_pp_at(rt, t, timing):
    """RB at month t read at ``BEF_PREM``, ``BEF_WD`` or ``BEF_ANNIV``.

        The ``rollup`` form accrues its withdrawal adjustment and applies it at the Contract
        Year end; the ``HQAV`` and ``basic`` forms reduce the base proportionally at the
        withdrawal itself [S1].
        """
    if t < 1:
        return fr_rb_pp_init(rt)
    if fr_depleted_flag(rt, t - 1):
        return fr_rb_pp(rt, t - 1)
    r = fr_rb_pp(rt, t - 1)
    if timing == 'BEF_PREM':
        return r
    r = r + fr_prem_to_av_pp(rt, t)
    if timing == 'BEF_WD':
        return r
    if fr_wd_pp(rt, t) > 0.0 and fr_gmdb_option(rt) != 'rollup':
        base = fr_av_pp_at(rt, t, 'BEF_WD')
        r = r * max(0.0, 1.0 - fr_wd_pp(rt, t) / base) if base > 0.0 else 0.0
    if timing == 'BEF_ANNIV':
        return r
    raise ValueError('invalid timing')

def fr_rb_pp_at(rt, t, timing):
    c = rt.cache[127]
    key = (t, timing)
    if key in c:
        return c[key]
    val = _calc_rb_pp_at(rt, t, timing)
    c[key] = val
    return val

def _calc_rb_pp_init(rt):
    """GMDB Benefit Base carried into ``t = 0``."""
    return float(fr_model_point(rt)['rb_init'])

def fr_rb_pp_init(rt):
    c = rt.cache[128]
    key = None
    if key in c:
        return c[key]
    val = _calc_rb_pp_init(rt)
    c[key] = val
    return val

def _calc_rb_prior_anniv_pp(rt, t):
    """RB at the Contract Anniversary preceding month t, the d-f-d allowance base [S1]."""
    u = fr_t_of_month(rt, 12 * (fr_policy_year(rt, t) - 1))
    return fr_rb_pp(rt, max(0, u))

def fr_rb_prior_anniv_pp(rt, t):
    c = rt.cache[129]
    key = t
    if key in c:
        return c[key]
    val = _calc_rb_prior_anniv_pp(rt, t)
    c[key] = val
    return val

def _calc_rollup_pct(rt):
    """rho at election: 6.00% at age 69 or younger, 5.00% from 70 [S3]."""
    if fr_age_at_entry(rt) >= rt.ctx.rollup_age_split:
        return rt.ctx.rollup_pct_old
    return rt.ctx.rollup_pct_young

def fr_rollup_pct(rt):
    c = rt.cache[130]
    key = None
    if key in c:
        return c[key]
    val = _calc_rollup_pct(rt)
    c[key] = val
    return val

def _calc_rollup_rate(rt, t):
    """rho(t): the GMDB roll-up percentage credited at the anniversary ending month t.

        ``fixed`` is the base run [S3]. ``cmt_linked`` is a third carrier's formula rate:
        the 10-year CMT plus 1.00%, or 1.50% before the first withdrawal, rounded to 0.10%,
        floored at 4% and capped at 8% [S7].
        """
    if fr_rollup_rule(rt) == 'fixed':
        return fr_rollup_pct(rt)
    elif fr_rollup_rule(rt) == 'cmt_linked':
        spread = rt.ctx.cmt_spread if fr_has_wd_by(rt, t) else rt.ctx.cmt_spread_predraw
        raw = fr_cmt10(rt, t) + spread
        step = rt.ctx.cmt_round_step
        rounded = rt.ctx.math.floor(raw / step + 0.5) * step
        return max(rt.ctx.cmt_floor, min(rt.ctx.cmt_cap, rounded))
    else:
        raise ValueError('invalid rollup_rule')

def fr_rollup_rate(rt, t):
    c = rt.cache[131]
    key = t
    if key in c:
        return c[key]
    val = _calc_rollup_rate(rt, t)
    c[key] = val
    return val

def _calc_rollup_rule(rt):
    """``fixed`` or ``cmt_linked``.

        ``fixed`` is the base run **[std]**: 6.00% at election ages up to 69 and 5.00% from
        70 [S3]. ``cmt_linked`` is a third carrier's formula rate, a 20-day average 10-year
        CMT plus 1.00% (1.50% before the first withdrawal), rounded to 0.10%, floored at 4%
        and capped at 8% [S7].
        """
    return fr_model_point(rt)['rollup_rule']

def fr_rollup_rule(rt):
    c = rt.cache[132]
    key = None
    if key in c:
        return c[key]
    val = _calc_rollup_rule(rt)
    c[key] = val
    return val

def _calc_rp_pp(rt, t):
    """RP(t): Remaining Premium, the basis the CDSC is charged on [S2]."""
    if t < 0:
        return 0.0
    if t == 0:
        return fr_rp_pp_init(rt) + fr_premium_pp(rt, 0)
    if fr_depleted_flag(rt, t - 1):
        return fr_rp_pp(rt, t - 1)
    return max(0.0, fr_rp_pp(rt, t - 1) + fr_premium_pp(rt, t) - fr_rp_reduction_pp(rt, t))

def fr_rp_pp(rt, t):
    c = rt.cache[133]
    key = t
    if key in c:
        return c[key]
    val = _calc_rp_pp(rt, t)
    c[key] = val
    return val

def _calc_rp_pp_init(rt):
    """Remaining Premium carried into ``t = 0``; the CDSC basis [S2]."""
    return float(fr_model_point(rt)['rp_init'])

def fr_rp_pp_init(rt):
    c = rt.cache[134]
    key = None
    if key in c:
        return c[key]
    val = _calc_rp_pp_init(rt)
    c[key] = val
    return val

def _calc_rp_reduction_pp(rt, t):
    """The premium portion of month t's withdrawal, earnings coming out first **[std]**.

        The sources state that Remaining Premium falls by "withdrawals of premium including
        withdrawal charges" [S2] and that earnings come out free first [S1], but give no
        algebra; this is the reading that makes the two consistent.
        """
    if t < 1 or fr_wd_pp(rt, t) <= 0.0:
        return 0.0
    rp = fr_rp_pp(rt, t - 1) + fr_premium_pp(rt, t)
    earnings = max(0.0, fr_av_pp_at(rt, t, 'BEF_WD') - rp)
    return min(rp, max(0.0, fr_wd_pp(rt, t) - earnings))

def fr_rp_reduction_pp(rt, t):
    c = rt.cache[135]
    key = t
    if key in c:
        return c[key]
    val = _calc_rp_reduction_pp(rt, t)
    c[key] = val
    return val

def _calc_sa_pp(rt, t, i):
    """SA_i(t): the value of subaccount i per contract at the end of month t."""
    return fr_sa_pp_at(rt, t, i, 'EOM')

def fr_sa_pp(rt, t, i):
    c = rt.cache[136]
    key = (t, i)
    if key in c:
        return c[key]
    val = _calc_sa_pp(rt, t, i)
    c[key] = val
    return val

def _calc_sa_pp_at(rt, t, i, timing):
    """SA_i at month t read at the point given by ``timing``; see the Space docstring.

        A withdrawal and a unit cancellation both scale the subaccount by
        ``(1 - amount / AV)`` — pro-rata deduction — so neither moves the value weights.
        """
    if t < 0:
        return 0.0
    if t == 0:
        return fr_alloc(rt, i) * (fr_av_pp_init(rt) + fr_prem_to_av_pp(rt, 0))
    if fr_depleted_flag(rt, t - 1) or t > fr_proj_len(rt):
        return 0.0
    sa = fr_sa_pp(rt, t - 1, i)
    if timing == 'BEF_PREM':
        return sa
    sa = sa + fr_alloc(rt, i) * fr_prem_to_av_pp(rt, t)
    if timing == 'BEF_WD':
        return sa
    base = fr_av_pp_at(rt, t, 'BEF_WD')
    sa = sa * (1.0 - fr_wd_pp(rt, t) / base) if base > 0.0 else 0.0
    if timing == 'BEF_INV':
        return sa
    sa = sa * fr_unit_growth(rt, t, i)
    if timing == 'BEF_FEE':
        return sa
    base = fr_av_pp_at(rt, t, 'BEF_FEE')
    sa = sa * (1.0 - fr_charge_pp(rt, t) / base) if base > 0.0 else 0.0
    if timing == 'EOM':
        return sa
    raise ValueError('invalid timing')

def fr_sa_pp_at(rt, t, i, timing):
    c = rt.cache[137]
    key = (t, i, timing)
    if key in c:
        return c[key]
    val = _calc_sa_pp_at(rt, t, i, timing)
    c[key] = val
    return val

def _calc_scenario_id(rt):
    """The scenario the model point runs on, a key into the two scenario tables."""
    return fr_model_point(rt)['scenario_id']

def fr_scenario_id(rt):
    c = rt.cache[138]
    key = None
    if key in c:
        return c[key]
    val = _calc_scenario_id(rt)
    c[key] = val
    return val

def _calc_scenario_rate(rt, t, name):
    """Step-function lookup of column ``name`` in the model point's rate scenario.

        Each row of *rate_scenario.csv* states the level that holds from its own policy month
        until the next row of the same scenario, so a flat path is one row.
        """
    sub = rt.ctx.data.rate_scenario().loc[fr_scenario_id(rt)]
    months = [m for m in sub.index if m <= max(fr_duration_mth(rt, t), 0)]
    return float(sub.loc[max(months), name])

def fr_scenario_rate(rt, t, name):
    c = rt.cache[139]
    key = (t, name)
    if key in c:
        return c[key]
    val = _calc_scenario_rate(rt, t, name)
    c[key] = val
    return val

def _calc_sex(rt):
    """The sex of the Designated Life, M or F."""
    return fr_model_point(rt)['sex']

def fr_sex(rt):
    c = rt.cache[140]
    key = None
    if key in c:
        return c[key]
    val = _calc_sex(rt)
    c[key] = val
    return val

def _calc_stepup_base_pp(rt, t):
    """The contract value the step-up test is made against [S1][S3].

        ``annual_CV``: the Contract Value at the anniversary. ``highest_quarterly_CV``: the
        highest contract value over the four most recent Contract Quarterly Anniversaries.
        """
    basis = fr_stepup_basis(rt)
    if basis == 'annual_CV':
        return fr_av_pp(rt, t)
    elif basis == 'highest_quarterly_CV':
        return max((fr_av_pp(rt, t - 3 * j) for j in range(0, 4) if t - 3 * j >= 0))
    else:
        raise ValueError('invalid stepup_basis')

def fr_stepup_base_pp(rt, t):
    c = rt.cache[141]
    key = t
    if key in c:
        return c[key]
    val = _calc_stepup_base_pp(rt, t)
    c[key] = val
    return val

def _calc_stepup_basis(rt):
    """``annual_CV`` or ``highest_quarterly_CV`` [S1][S3].

        ``annual_CV`` is the representative election: the step-up test uses the Contract
        Value at the anniversary. ``highest_quarterly_CV`` uses the highest contract value
        over the four most recent Contract Quarterly Anniversaries; the source also adjusts
        each of those for subsequent premiums and withdrawals under the same
        dollar-for-dollar / proportional rule, which is **not implemented** — see the model
        docstring.
        """
    return fr_model_point(rt)['glwb_stepup_basis']

def fr_stepup_basis(rt):
    c = rt.cache[142]
    key = None
    if key in c:
        return c[key]
    val = _calc_stepup_basis(rt)
    c[key] = val
    return val

def _calc_sub_ids(rt):
    """The subaccount indices of the model point's allocation set, in file order.

        Two subaccounts **[std]** — the minimum that exercises pro-rata charge allocation and
        unit accounting. Real contracts offer far more; one carrier's build-your-own menu
        lists 76 options across 12 asset classes [S4].
        """
    return list(rt.ctx.data.fund_table().loc[fr_fund_set(rt)].index)

def fr_sub_ids(rt):
    c = rt.cache[143]
    key = None
    if key in c:
        return c[key]
    val = _calc_sub_ids(rt)
    c[key] = val
    return val

def _calc_sum_wd_pp(rt, t):
    """SumW_y: cumulative withdrawals in the current contract year, including W(t) [S1]."""
    if t < 1:
        return 0.0
    prev = 0.0 if fr_is_year_start(rt, t) else fr_sum_wd_pp(rt, t - 1)
    return prev + fr_wd_pp(rt, t)

def fr_sum_wd_pp(rt, t):
    c = rt.cache[144]
    key = t
    if key in c:
        return c[key]
    val = _calc_sum_wd_pp(rt, t)
    c[key] = val
    return val

def _calc_surr_benefit_pp(rt, t):
    """Surrender proceeds: ``AV(t)`` less the CDSC.

        There is **no nonforfeiture floor** under this value. NAIC Model #805 expressly
        excludes variable annuities and reaches a VA only through its fixed account under
        Model #250 §7.B [REG-R42][REG-R43], and electing the Roll-up GMDB removes the Fixed
        Account Options [S1]. Contrast :mod:`.MYGA_US_S`, where
        ``max(SV, MGSV)`` is the whole point.
        """
    return fr_av_pp(rt, t) - fr_surr_charge_pp(rt, t)

def fr_surr_benefit_pp(rt, t):
    c = rt.cache[145]
    key = t
    if key in c:
        return c[key]
    val = _calc_surr_benefit_pp(rt, t)
    c[key] = val
    return val

def _calc_surr_charge_pp(rt, t):
    """The CDSC on a full surrender at the end of month t."""
    return fr_surr_charge_rate(rt, t) * fr_surr_chargeable_pp(rt, t)

def fr_surr_charge_pp(rt, t):
    c = rt.cache[146]
    key = t
    if key in c:
        return c[key]
    val = _calc_surr_charge_pp(rt, t)
    c[key] = val
    return val

def _calc_surr_charge_rate(rt, t):
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
    grid = rt.ctx.data.cdsc_table().loc[fr_cdsc_schedule(rt)]
    years = min(fr_duration(rt, t), int(grid.index.max()))
    return float(grid.loc[years, 'surr_charge_rate'])

def fr_surr_charge_rate(rt, t):
    c = rt.cache[147]
    key = t
    if key in c:
        return c[key]
    val = _calc_surr_charge_rate(rt, t)
    c[key] = val
    return val

def _calc_surr_chargeable_pp(rt, t):
    """The Remaining Premium withdrawn on a full surrender, net of the free amount [S2]."""
    return min(fr_rp_pp(rt, t), max(0.0, fr_av_pp(rt, t) - fr_surr_free_pp(rt, t)))

def fr_surr_chargeable_pp(rt, t):
    c = rt.cache[148]
    key = t
    if key in c:
        return c[key]
    val = _calc_surr_chargeable_pp(rt, t)
    c[key] = val
    return val

def _calc_surr_free_pp(rt, t):
    """The charge-free amount left for a full surrender at the end of month t."""
    rp = fr_rp_pp(rt, t)
    earnings = max(0.0, fr_av_pp(rt, t) - rp)
    allow = max(earnings, rt.ctx.free_wd_rate * rp)
    return max(0.0, allow - fr_free_wd_used_cum_pp(rt, t))

def fr_surr_free_pp(rt, t):
    c = rt.cache[149]
    key = t
    if key in c:
        return c[key]
    val = _calc_surr_free_pp(rt, t)
    c[key] = val
    return val

def _calc_t_of_month(rt, m):
    """The projection index t of policy month m; negative before the entry instant."""
    return m - fr_duration_mth_init(rt)

def fr_t_of_month(rt, m):
    c = rt.cache[150]
    key = m
    if key in c:
        return c[key]
    val = _calc_t_of_month(rt, m)
    c[key] = val
    return val

def _calc_txn_id(rt):
    """The scheduled transaction programme, a key into *transaction_table.csv*."""
    return fr_model_point(rt)['txn_id']

def fr_txn_id(rt):
    c = rt.cache[151]
    key = None
    if key in c:
        return c[key]
    val = _calc_txn_id(rt)
    c[key] = val
    return val

def _calc_unit_growth(rt, t, i):
    """The monthly unit value factor of subaccount i.

        ``(1 + r_i(t)) x (1 - e_i/12) x (1 - (m + alpha)/12)`` — a monthly discretization of
        a daily accrual **[std]** [S2]. The fund's own expense and the base contract asset
        charge live **inside** the unit value; charges assessed per contract or on a benefit
        base do not, and are collected by cancelling units instead. Do not additionally
        compound daily: pick one discretization and document it, because reconciling to an
        admin system requires knowing which was used.
        """
    return (1.0 + fr_inv_return_mth(rt, t, i)) * (1.0 - fr_fund_expense_rate(rt, i) / 12.0) * (1.0 - (rt.ctx.asset_charge_me + rt.ctx.asset_charge_admin) / 12.0)

def fr_unit_growth(rt, t, i):
    c = rt.cache[152]
    key = (t, i)
    if key in c:
        return c[key]
    val = _calc_unit_growth(rt, t, i)
    c[key] = val
    return val

def _calc_vix_sq(rt, k):
    """The quarterly average of daily VIX-squared for contract quarter k [S4][S6].

        Read at the last month of the quarter. Used only by the ``vix`` fee reset rule.
        """
    return fr_scenario_rate(rt, fr_t_of_month(rt, 3 * k), 'vix_sq')

def fr_vix_sq(rt, k):
    c = rt.cache[153]
    key = k
    if key in c:
        return c[key]
    val = _calc_vix_sq(rt, k)
    c[key] = val
    return val

def _calc_wd_charge_pp(rt, t):
    """c(t): the withdrawal charge on month t's withdrawal [S2]."""
    return fr_surr_charge_rate(rt, t) * fr_wd_chargeable_pp(rt, t)

def fr_wd_charge_pp(rt, t):
    c = rt.cache[154]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_charge_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_chargeable_pp(rt, t):
    """The portion of W(t) exposed to the CDSC: ``max(0, E(t) - free allowance)``."""
    return fr_wd_pp(rt, t) - fr_wd_exempt_pp(rt, t)

def fr_wd_chargeable_pp(rt, t):
    c = rt.cache[155]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_chargeable_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_excess_pp(rt, t):
    """E(t) = min(W, SumW_y - L) if SumW_y > L else 0: the excess withdrawal [S1].

        This is the **guarantee** excess, not the charge base — see the Space docstring's
        note on the divergence from :mod:`.MYGA_US_S`.
        """
    if fr_wd_pp(rt, t) <= 0.0:
        return 0.0
    over = fr_sum_wd_pp(rt, t) - fr_wd_limit_pp(rt, t)
    return min(fr_wd_pp(rt, t), over) if over > 0.0 else 0.0

def fr_wd_excess_pp(rt, t):
    c = rt.cache[156]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_excess_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_exempt_pp(rt, t):
    """The portion of W(t) bearing no withdrawal charge at all.

        Two exemptions stack: **no CDSC applies to cumulative withdrawals within L** [S1],
        which covers the non-excess portion outright, and the free-withdrawal allowance
        covers part of what is left. So this is identically
        ``wd_nonexcess_pp(t) + wd_free_pp(t)``, and it — not :func:`wd_free_pp` — is what
        complements :func:`wd_chargeable_pp`.
        """
    return min(fr_wd_pp(rt, t), fr_wd_nonexcess_pp(rt, t) + fr_free_wd_avail(rt, t))

def fr_wd_exempt_pp(rt, t):
    c = rt.cache[157]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_exempt_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_free_pp(rt, t):
    """The free-allowance portion of month t's withdrawal: ``min(FW, E(t))``.

        The chassis name for the same thing — :mod:`.MYGA_US_S` has
        ``min(W, FW)`` — differing only in that here the allowance is applied to the
        *guarantee excess* rather than to the whole withdrawal, because the non-excess
        portion is already exempt from the CDSC under the within-``L`` rule [S1]. The
        portion of ``W(t)`` bearing no charge *at all* is therefore the wider
        :func:`wd_exempt_pp`, not this cells.
        """
    return min(fr_free_wd_avail(rt, t), fr_wd_excess_pp(rt, t))

def fr_wd_free_pp(rt, t):
    c = rt.cache[158]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_free_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_glwb_pp(rt, t):
    """The GLWB utilization withdrawal: ``wd_intensity x L(t)`` once activated **[std]**."""
    return fr_wd_intensity(rt) * fr_wd_limit_pp(rt, t) if fr_is_wd_month(rt, t) else 0.0

def fr_wd_glwb_pp(rt, t):
    c = rt.cache[159]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_glwb_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_intensity(rt):
    """The fraction of the annual limit withdrawn once activated; 100% **[std]**.

        100% matches VM-21 §6.C.3's Guarantee Actuarial Present Value construction [R1]. The
        prescribed partial-withdrawal assumption is 90% for lifetime GMWBs and 70% for
        non-lifetime ones [R1].
        """
    return float(fr_model_point(rt)['wd_intensity'])

def fr_wd_intensity(rt):
    c = rt.cache[160]
    key = None
    if key in c:
        return c[key]
    val = _calc_wd_intensity(rt)
    c[key] = val
    return val

def _calc_wd_limit_pp(rt, t):
    """L(t) = max(GAWA, RMD): the annual withdrawal limit governing month t [S1].

        At the first withdrawal the GAWA is fixed on the **pre-withdrawal** GWB, so the limit
        is formed from that. The RMD term is disclosed but inactive: the base run is
        non-qualified and no RMD module is implemented.
        """
    if fr_is_first_wd(rt, t):
        return fr_gawa_pct_at_age(rt, fr_age(rt, t)) * fr_gwb_pp_at(rt, t, 'BEF_WD')
    return fr_gawa_pp_at(rt, t, 'BEF_WD')

def fr_wd_limit_pp(rt, t):
    c = rt.cache[161]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_limit_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_nonexcess_pp(rt, t):
    """N(t) = W(t) - E(t): the guaranteed portion of the withdrawal [S1]."""
    return fr_wd_pp(rt, t) - fr_wd_excess_pp(rt, t)

def fr_wd_nonexcess_pp(rt, t):
    c = rt.cache[162]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_nonexcess_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_payment_pp(rt, t):
    """The cash paid on month t's withdrawal, ``W(t) - c(t)``."""
    return fr_wd_pp(rt, t) - fr_wd_charge_pp(rt, t)

def fr_wd_payment_pp(rt, t):
    c = rt.cache[163]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_payment_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_pp(rt, t):
    """W(t): the gross amount removed from the contract value at BOM of month t.

        Measured **inclusive of withdrawal charges, MVAs, advisory fees and every other
        charge** for all guarantee calculations [S1]; using net proceeds would understate the
        benefit-base reduction. Capped at the available contract value **[std]**.
        """
    return min(fr_wd_pp_due(rt, t), fr_av_pp_at(rt, t, 'BEF_WD'))

def fr_wd_pp(rt, t):
    c = rt.cache[164]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_pp_due(rt, t):
    """The gross withdrawal requested at BOM of month t, before capping at AV.

        Scheduled withdrawals **add to** the utilization withdrawal, which is how a model
        point exercises the excess algebra without disturbing the base run.
        """
    if t < 1 or t > fr_proj_len(rt) or fr_depleted_flag(rt, t - 1):
        return 0.0
    return fr_wd_scheduled_pp(rt, t) + fr_wd_glwb_pp(rt, t)

def fr_wd_pp_due(rt, t):
    c = rt.cache[165]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_pp_due(rt, t)
    c[key] = val
    return val

def _calc_wd_scheduled_pp(rt, t):
    """The gross withdrawal scheduled for month t in *transaction_table.csv*, else zero."""
    if t < 1:
        return 0.0
    table = rt.ctx.data.transaction_table()
    key = (fr_txn_id(rt), fr_duration_mth(rt, t))
    return float(table.loc[key, 'wd_amount']) if key in table.index else 0.0

def fr_wd_scheduled_pp(rt, t):
    c = rt.cache[166]
    key = t
    if key in c:
        return c[key]
    val = _calc_wd_scheduled_pp(rt, t)
    c[key] = val
    return val

def _calc_wd_start_age(rt):
    """The attained age at which GLWB withdrawals begin; 70 in the base run **[std]**.

        Zero means the contract never withdraws. The base-run value rests on the finding that
        activation clusters at the RMD age [REG-R64 **[unverified]**][REG-R57][REG-R58]. The
        prescribed alternative is VM-21's Withdrawal Delay Cohort Method, which is **not
        implemented**.
        """
    return int(fr_model_point(rt)['wd_start_age'])

def fr_wd_start_age(rt):
    c = rt.cache[167]
    key = None
    if key in c:
        return c[key]
    val = _calc_wd_start_age(rt)
    c[key] = val
    return val

def _calc_withdrawals(rt, t):
    """Withdrawal proceeds ``W(t) - c(t)``, weighted by :func:`pols_if` ``(t)``."""
    return 0.0 if t < 1 else fr_wd_payment_pp(rt, t) * fr_pols_if(rt, t)

def fr_withdrawals(rt, t):
    c = rt.cache[168]
    key = t
    if key in c:
        return c[key]
    val = _calc_withdrawals(rt, t)
    c[key] = val
    return val

def evaluate(rt, ctx):
    rt.bind(ctx)
    return fr_bench_net_cf(rt)
