# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False, nonecheck=False
"""Fast recursive BasicTerm prototype.

This module intentionally preserves demand-driven recursive Cells semantics.
There is no recovered dependency graph, recurrence schedule, or recurrence-to-loop
lowering in the hot policy evaluator.  Formula dependencies are requested at
runtime through ``_eval_time`` / ``_eval_scalar`` using integer Cell IDs and are
memoized in a flat per-policy C context.

The batch wrapper only supplies flat numeric inputs and a C-level policy loop.
"""

cimport cython
from libc.math cimport pow, rint, NAN
from libc.string cimport memset
import numpy as np
cimport numpy as cnp

DEF MAX_T = 241
DEF N_TIME = 16
DEF N_SCALAR = 17

# Time-indexed Cell IDs. Their numeric values are intentionally runtime data to
# _eval_time: formulas do not rely on a precomputed execution schedule.
cdef enum TimeCell:
    TC_AGE = 0
    TC_CLAIM_PP = 1
    TC_CLAIMS = 2
    TC_COMMISSIONS = 3
    TC_DURATION = 4
    TC_EXPENSES = 5
    TC_INFLATION_FACTOR = 6
    TC_LAPSE_RATE = 7
    TC_MORT_RATE = 8
    TC_MORT_RATE_MTH = 9
    TC_NET_CF = 10
    TC_POLS_DEATH = 11
    TC_POLS_IF = 12
    TC_POLS_LAPSE = 13
    TC_POLS_MATURITY = 14
    TC_PREMIUMS = 15

cdef enum ScalarCell:
    SC_AGE_AT_ENTRY = 0
    SC_EXPENSE_ACQ = 1
    SC_EXPENSE_MAINT = 2
    SC_INFLATION_RATE = 3
    SC_LOADING_PREM = 4
    SC_NET_PREMIUM_PP = 5
    SC_POLICY_TERM = 6
    SC_POLS_IF_INIT = 7
    SC_PREMIUM_PP = 8
    SC_PROJ_LEN = 9
    SC_PV_CLAIMS = 10
    SC_PV_COMMISSIONS = 11
    SC_PV_EXPENSES = 12
    SC_PV_NET_CF = 13
    SC_PV_POLS_IF = 14
    SC_PV_PREMIUMS = 15
    SC_SUM_ASSURED = 16

ctypedef struct RecContext:
    long policy_term
    long sum_assured
    long age_at_entry
    const double* disc_factor
    const double* mort_table
    double time_v[N_TIME][MAX_T]
    unsigned char time_has[N_TIME][MAX_T]
    double scalar_v[N_SCALAR]
    unsigned char scalar_has[N_SCALAR]


cdef inline void _ctx_init(
    RecContext* ctx,
    long policy_term,
    long sum_assured,
    long age_at_entry,
    const double* disc_factor,
    const double* mort_table,
) noexcept nogil:
    ctx.policy_term = policy_term
    ctx.sum_assured = sum_assured
    ctx.age_at_entry = age_at_entry
    ctx.disc_factor = disc_factor
    ctx.mort_table = mort_table
    memset(&ctx.time_has[0][0], 0, N_TIME * MAX_T * sizeof(unsigned char))
    memset(&ctx.scalar_has[0], 0, N_SCALAR * sizeof(unsigned char))


cdef double _eval(RecContext* ctx, int kind, int cell, int t) noexcept nogil:
    """Dynamic recursive dispatcher.

    kind=0 addresses scalar Cells; kind=1 addresses time-indexed Cells.  Every
    dependency below re-enters this same dispatcher at runtime.  There is no
    precomputed traversal order.
    """
    cdef double v
    cdef double acc
    cdef double maint
    cdef double x
    cdef long duration
    cdef long age
    cdef long dcol
    cdef int q
    cdef int n

    if kind == 1:
        if cell < 0 or cell >= N_TIME or t < 0 or t >= MAX_T:
            return NAN
        if ctx.time_has[cell][t]:
            return ctx.time_v[cell][t]

        if cell == TC_AGE:
            v = _eval(ctx, 0, SC_AGE_AT_ENTRY, 0) + _eval(ctx, 1, TC_DURATION, t)
        elif cell == TC_CLAIM_PP:
            v = _eval(ctx, 0, SC_SUM_ASSURED, 0)
        elif cell == TC_CLAIMS:
            v = _eval(ctx, 1, TC_CLAIM_PP, t) * _eval(ctx, 1, TC_POLS_DEATH, t)
        elif cell == TC_COMMISSIONS:
            if <long>_eval(ctx, 1, TC_DURATION, t) == 0:
                v = _eval(ctx, 1, TC_PREMIUMS, t)
            else:
                v = 0.0
        elif cell == TC_DURATION:
            v = <double>(t // 12)
        elif cell == TC_EXPENSES:
            maint = (
                _eval(ctx, 1, TC_POLS_IF, t)
                * _eval(ctx, 0, SC_EXPENSE_MAINT, 0)
                / 12.0
                * _eval(ctx, 1, TC_INFLATION_FACTOR, t)
            )
            if t == 0:
                v = _eval(ctx, 0, SC_EXPENSE_ACQ, 0) + maint
            else:
                v = maint
        elif cell == TC_INFLATION_FACTOR:
            v = pow(1.0 + _eval(ctx, 0, SC_INFLATION_RATE, 0), (<double>t) / 12.0)
        elif cell == TC_LAPSE_RATE:
            x = 0.1 - 0.02 * _eval(ctx, 1, TC_DURATION, t)
            v = x if x >= 0.02 else 0.02
        elif cell == TC_MORT_RATE:
            duration = <long>_eval(ctx, 1, TC_DURATION, t)
            dcol = duration
            if dcol < 0:
                dcol = 0
            elif dcol > 5:
                dcol = 5
            age = <long>_eval(ctx, 1, TC_AGE, t)
            if age < 0 or age > 120:
                return NAN
            v = ctx.mort_table[age * 6 + dcol]
        elif cell == TC_MORT_RATE_MTH:
            v = 1.0 - pow(1.0 - _eval(ctx, 1, TC_MORT_RATE, t), 1.0 / 12.0)
        elif cell == TC_NET_CF:
            v = (
                _eval(ctx, 1, TC_PREMIUMS, t)
                - _eval(ctx, 1, TC_CLAIMS, t)
                - _eval(ctx, 1, TC_EXPENSES, t)
                - _eval(ctx, 1, TC_COMMISSIONS, t)
            )
        elif cell == TC_POLS_DEATH:
            v = _eval(ctx, 1, TC_POLS_IF, t) * _eval(ctx, 1, TC_MORT_RATE_MTH, t)
        elif cell == TC_POLS_IF:
            if t == 0:
                v = _eval(ctx, 0, SC_POLS_IF_INIT, 0)
            elif t > <long>_eval(ctx, 0, SC_POLICY_TERM, 0) * 12:
                v = 0.0
            else:
                v = (
                    _eval(ctx, 1, TC_POLS_IF, t - 1)
                    - _eval(ctx, 1, TC_POLS_LAPSE, t - 1)
                    - _eval(ctx, 1, TC_POLS_DEATH, t - 1)
                    - _eval(ctx, 1, TC_POLS_MATURITY, t)
                )
        elif cell == TC_POLS_LAPSE:
            v = (
                _eval(ctx, 1, TC_POLS_IF, t) - _eval(ctx, 1, TC_POLS_DEATH, t)
            ) * (1.0 - pow(1.0 - _eval(ctx, 1, TC_LAPSE_RATE, t), 1.0 / 12.0))
        elif cell == TC_POLS_MATURITY:
            if t == <long>_eval(ctx, 0, SC_POLICY_TERM, 0) * 12:
                v = (
                    _eval(ctx, 1, TC_POLS_IF, t - 1)
                    - _eval(ctx, 1, TC_POLS_LAPSE, t - 1)
                    - _eval(ctx, 1, TC_POLS_DEATH, t - 1)
                )
            else:
                v = 0.0
        elif cell == TC_PREMIUMS:
            v = _eval(ctx, 0, SC_PREMIUM_PP, 0) * _eval(ctx, 1, TC_POLS_IF, t)
        else:
            return NAN

        ctx.time_v[cell][t] = v
        ctx.time_has[cell][t] = 1
        return v

    # Scalar Cells.
    if cell < 0 or cell >= N_SCALAR:
        return NAN
    if ctx.scalar_has[cell]:
        return ctx.scalar_v[cell]

    if cell == SC_AGE_AT_ENTRY:
        v = <double>ctx.age_at_entry
    elif cell == SC_EXPENSE_ACQ:
        v = 300.0
    elif cell == SC_EXPENSE_MAINT:
        v = 60.0
    elif cell == SC_INFLATION_RATE:
        v = 0.01
    elif cell == SC_LOADING_PREM:
        v = 0.5
    elif cell == SC_NET_PREMIUM_PP:
        v = _eval(ctx, 0, SC_PV_CLAIMS, 0) / _eval(ctx, 0, SC_PV_POLS_IF, 0)
    elif cell == SC_POLICY_TERM:
        v = <double>ctx.policy_term
    elif cell == SC_POLS_IF_INIT:
        v = 1.0
    elif cell == SC_PREMIUM_PP:
        v = rint((1.0 + _eval(ctx, 0, SC_LOADING_PREM, 0)) * _eval(ctx, 0, SC_NET_PREMIUM_PP, 0) * 100.0) / 100.0
    elif cell == SC_PROJ_LEN:
        v = <double>(12 * ctx.policy_term + 1)
    elif cell == SC_SUM_ASSURED:
        v = <double>ctx.sum_assured
    else:
        n = <int>_eval(ctx, 0, SC_PROJ_LEN, 0)
        if cell == SC_PV_CLAIMS:
            acc = 0.0
            for q in range(n):
                acc += _eval(ctx, 1, TC_CLAIMS, q) * ctx.disc_factor[q]
            v = acc
        elif cell == SC_PV_COMMISSIONS:
            acc = 0.0
            for q in range(n):
                acc += _eval(ctx, 1, TC_COMMISSIONS, q) * ctx.disc_factor[q]
            v = acc
        elif cell == SC_PV_EXPENSES:
            acc = 0.0
            for q in range(n):
                acc += _eval(ctx, 1, TC_EXPENSES, q) * ctx.disc_factor[q]
            v = acc
        elif cell == SC_PV_NET_CF:
            v = (
                _eval(ctx, 0, SC_PV_PREMIUMS, 0)
                - _eval(ctx, 0, SC_PV_CLAIMS, 0)
                - _eval(ctx, 0, SC_PV_EXPENSES, 0)
                - _eval(ctx, 0, SC_PV_COMMISSIONS, 0)
            )
        elif cell == SC_PV_POLS_IF:
            acc = 0.0
            for q in range(n):
                acc += _eval(ctx, 1, TC_POLS_IF, q) * ctx.disc_factor[q]
            v = acc
        elif cell == SC_PV_PREMIUMS:
            acc = 0.0
            for q in range(n):
                acc += _eval(ctx, 1, TC_PREMIUMS, q) * ctx.disc_factor[q]
            v = acc
        else:
            return NAN

    ctx.scalar_v[cell] = v
    ctx.scalar_has[cell] = 1
    return v

cdef inline double _run_one(
    long policy_term,
    long sum_assured,
    long age_at_entry,
    const double* disc_factor,
    const double* mort_table,
) noexcept nogil:
    cdef RecContext ctx
    _ctx_init(&ctx, policy_term, sum_assured, age_at_entry, disc_factor, mort_table)
    # One runtime Cell request. Everything below this point is recursive demand.
    return _eval(&ctx, 0, SC_PV_NET_CF, 0)


cpdef cnp.ndarray run(
    cnp.ndarray[cnp.int64_t, ndim=1, mode='c'] policy_term,
    cnp.ndarray[cnp.int64_t, ndim=1, mode='c'] sum_assured,
    cnp.ndarray[cnp.int64_t, ndim=1, mode='c'] age_at_entry,
    cnp.ndarray[cnp.float64_t, ndim=1, mode='c'] disc_rate_ann,
    cnp.ndarray[cnp.float64_t, ndim=2, mode='c'] mort_table,
):
    """Evaluate PV for a portfolio using dynamic recursive Cell demand."""
    cdef Py_ssize_t n = policy_term.shape[0]
    cdef cnp.ndarray[cnp.float64_t, ndim=1] out_arr = np.empty(n, dtype=np.float64)
    cdef long[::1] pt = policy_term
    cdef long[::1] sa = sum_assured
    cdef long[::1] aa = age_at_entry
    cdef double[::1] dr = disc_rate_ann
    cdef double[:, ::1] mt = mort_table
    cdef double[::1] out = out_arr
    cdef double disc_local[MAX_T]
    cdef double mth
    cdef Py_ssize_t i
    cdef int t
    if sum_assured.shape[0] != n or age_at_entry.shape[0] != n:
        raise ValueError('point input lengths differ')
    if disc_rate_ann.shape[0] < 21:
        raise ValueError('disc_rate_ann must contain at least 21 years')
    if mort_table.shape[0] < 121 or mort_table.shape[1] < 6:
        raise ValueError('mort_table must be at least 121x6')
    with nogil:
        for t in range(MAX_T):
            mth = pow(1.0 + dr[t // 12], 1.0 / 12.0) - 1.0
            disc_local[t] = pow(1.0 + mth, -t)
        for i in range(n):
            out[i] = _run_one(pt[i], sa[i], aa[i], &disc_local[0], &mt[0, 0])
    return out_arr


cpdef double run_one(
    long policy_term,
    long sum_assured,
    long age_at_entry,
    cnp.ndarray[cnp.float64_t, ndim=1, mode='c'] disc_rate_ann,
    cnp.ndarray[cnp.float64_t, ndim=2, mode='c'] mort_table,
):
    cdef double[::1] dr = disc_rate_ann
    cdef double[:, ::1] mt = mort_table
    cdef double disc_local[MAX_T]
    cdef double mth
    cdef int t
    with nogil:
        for t in range(MAX_T):
            mth = pow(1.0 + dr[t // 12], 1.0 / 12.0) - 1.0
            disc_local[t] = pow(1.0 + mth, -t)
        return _run_one(policy_term, sum_assured, age_at_entry, &disc_local[0], &mt[0,0])


def cell_ids():
    """Stable IDs used by the dynamic dispatcher, for inspection/probing."""
    return {
        'time': {
            'age': TC_AGE, 'claim_pp': TC_CLAIM_PP, 'claims': TC_CLAIMS,
            'commissions': TC_COMMISSIONS, 'duration': TC_DURATION,
            'expenses': TC_EXPENSES, 'inflation_factor': TC_INFLATION_FACTOR,
            'lapse_rate': TC_LAPSE_RATE, 'mort_rate': TC_MORT_RATE,
            'mort_rate_mth': TC_MORT_RATE_MTH, 'net_cf': TC_NET_CF,
            'pols_death': TC_POLS_DEATH, 'pols_if': TC_POLS_IF,
            'pols_lapse': TC_POLS_LAPSE, 'pols_maturity': TC_POLS_MATURITY,
            'premiums': TC_PREMIUMS,
        },
        'scalar': {
            'age_at_entry': SC_AGE_AT_ENTRY, 'expense_acq': SC_EXPENSE_ACQ,
            'expense_maint': SC_EXPENSE_MAINT, 'inflation_rate': SC_INFLATION_RATE,
            'loading_prem': SC_LOADING_PREM, 'net_premium_pp': SC_NET_PREMIUM_PP,
            'policy_term': SC_POLICY_TERM, 'pols_if_init': SC_POLS_IF_INIT,
            'premium_pp': SC_PREMIUM_PP, 'proj_len': SC_PROJ_LEN,
            'pv_claims': SC_PV_CLAIMS, 'pv_commissions': SC_PV_COMMISSIONS,
            'pv_expenses': SC_PV_EXPENSES, 'pv_net_cf': SC_PV_NET_CF,
            'pv_pols_if': SC_PV_POLS_IF, 'pv_premiums': SC_PV_PREMIUMS,
            'sum_assured': SC_SUM_ASSURED,
        },
    }


def probe_requests(
    long policy_term,
    long sum_assured,
    long age_at_entry,
    cnp.ndarray[cnp.float64_t, ndim=1, mode='c'] disc_rate_ann,
    cnp.ndarray[cnp.float64_t, ndim=2, mode='c'] mort_table,
    requests,
):
    """Execute arbitrary runtime Cell requests against one shared memo context.

    ``requests`` is an iterable of ``('scalar', id)`` or ``('time', id, t)``.
    This is intentionally a diagnostic API: it proves the evaluator does not need
    a frozen target schedule and can demand compiled Cells in arbitrary order.
    """
    cdef double[::1] dr = disc_rate_ann
    cdef double[:, ::1] mt = mort_table
    cdef double disc_local[MAX_T]
    cdef double mth
    cdef RecContext ctx
    cdef list out = []
    cdef object req
    cdef int cid
    cdef int t
    for t in range(MAX_T):
        mth = pow(1.0 + dr[t // 12], 1.0 / 12.0) - 1.0
        disc_local[t] = pow(1.0 + mth, -t)
    _ctx_init(&ctx, policy_term, sum_assured, age_at_entry, &disc_local[0], &mt[0,0])
    for req in requests:
        if req[0] == 'scalar':
            cid = int(req[1])
            out.append(_eval(&ctx, 0, cid, 0))
        elif req[0] == 'time':
            cid = int(req[1]); t = int(req[2])
            out.append(_eval(&ctx, 1, cid, t))
        else:
            raise ValueError(f'unknown request kind {req[0]!r}')
    return out
