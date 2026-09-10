# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False
cimport cython
from libc.math cimport pow, rint
import numpy as np
cimport numpy as cnp

cdef inline void _run_one(
    Py_ssize_t i,
    const long[::1] mp__policy_term,
    const long[::1] mp__sum_assured,
    const long[::1] mp__age_at_entry,
    const double[::1] ref__disc_rate_ann,
    const double[:, ::1] ref__mort_table,
    double[:, ::1] out
) noexcept nogil:
    cdef double s_pv_net_cf = 0
    cdef double a_pv_commissions = 0.0
    cdef double a_pv_expenses = 0.0
    cdef double a_pv_premiums = 0.0
    cdef double a_pv_claims = 0.0
    cdef double c_commissions = 0
    cdef long s_proj_len = 0
    cdef double c_expenses = 0
    cdef double c_premiums = 0
    cdef double c_claims = 0
    cdef long c_duration = 0
    cdef long s_policy_term = 0
    cdef double c_inflation_factor = 0
    cdef double s_expense_acq = 0
    cdef double c_pols_if = 0
    cdef double s_expense_maint = 0
    cdef double s_premium_pp = 0
    cdef double c_claim_pp = 0
    cdef double c_pols_death = 0
    cdef double s_inflation_rate = 0
    cdef double s_pols_if_init = 0
    cdef double c_pols_maturity = 0
    cdef double c_pols_lapse = 0
    cdef double s_net_premium_pp = 0
    cdef double s_loading_prem = 0
    cdef double s_sum_assured = 0
    cdef double c_mort_rate_mth = 0
    cdef double c_lapse_rate = 0
    cdef double a_pv_pols_if = 0.0
    cdef double c_mort_rate = 0
    cdef long c_age = 0
    cdef long s_age_at_entry = 0
    cdef double c_disc_factors__at = 0
    cdef double c_disc_rate_mth__at = 0
    cdef double p_pols_death = 0
    cdef double p_pols_if = 0
    cdef double p_pols_lapse = 0
    cdef double l_expenses_maint = 0.0
    cdef long t

    # ---- recurrence stage 0 ----
    s_age_at_entry = mp__age_at_entry[i]
    s_expense_acq = 300
    s_expense_maint = 60
    s_inflation_rate = 0.01
    s_loading_prem = 0.5
    s_policy_term = mp__policy_term[i]
    s_pols_if_init = 1
    s_proj_len = ((12 * mp__policy_term[i]) + 1)
    s_sum_assured = mp__sum_assured[i]
    a_pv_claims = 0.0
    a_pv_expenses = 0.0
    a_pv_pols_if = 0.0
    p_pols_death = 0
    p_pols_if = 0
    p_pols_lapse = 0
    for t in range(s_proj_len):
        c_claim_pp = mp__sum_assured[i]
        c_disc_rate_mth__at = (pow((1 + ref__disc_rate_ann[<Py_ssize_t>((t // 12))]), ((<double>(1)) / (<double>(12)))) - 1)
        c_duration = (t // 12)
        c_inflation_factor = pow((1 + s_inflation_rate), ((<double>(t)) / (<double>(12))))
        if (t == (mp__policy_term[i] * 12)):
            c_pols_maturity = ((p_pols_if - p_pols_lapse) - p_pols_death)
        else:
            c_pols_maturity = 0
        c_age = (mp__age_at_entry[i] + c_duration)
        c_disc_factors__at = pow((1 + c_disc_rate_mth__at), (-t))
        c_lapse_rate = (((0.1 - (0.02 * c_duration))) if ((0.1 - (0.02 * c_duration))) >= (0.02) else (0.02))
        if (t == 0):
            c_pols_if = s_pols_if_init
        else:
            if (t > (mp__policy_term[i] * 12)):
                c_pols_if = 0
            else:
                c_pols_if = (((p_pols_if - p_pols_lapse) - p_pols_death) - c_pols_maturity)
        l_expenses_maint = (((<double>((c_pols_if * s_expense_maint))) / (<double>(12))) * c_inflation_factor)
        if (t == 0):
            c_expenses = (s_expense_acq + l_expenses_maint)
        else:
            c_expenses = l_expenses_maint
        c_mort_rate = ref__mort_table[<Py_ssize_t>(c_age), <Py_ssize_t>(((((5) if (5) <= (c_duration) else (c_duration))) if (((5) if (5) <= (c_duration) else (c_duration))) >= (0) else (0)))]
        c_mort_rate_mth = (1 - pow((1 - c_mort_rate), ((<double>(1)) / (<double>(12)))))
        c_pols_death = (c_pols_if * c_mort_rate_mth)
        c_claims = (c_claim_pp * c_pols_death)
        c_pols_lapse = ((c_pols_if - c_pols_death) * (1 - pow((1 - c_lapse_rate), ((<double>(1)) / (<double>(12))))))
        a_pv_claims += (c_claims * c_disc_factors__at)
        a_pv_expenses += (c_expenses * c_disc_factors__at)
        a_pv_pols_if += (c_pols_if * c_disc_factors__at)
        p_pols_death = c_pols_death
        p_pols_if = c_pols_if
        p_pols_lapse = c_pols_lapse

    # ---- recurrence stage 1 ----
    s_net_premium_pp = ((<double>(a_pv_claims)) / (<double>(a_pv_pols_if)))
    s_premium_pp = (rint((((1 + s_loading_prem) * s_net_premium_pp)) * 100.0) / 100.0)
    a_pv_commissions = 0.0
    a_pv_premiums = 0.0
    p_pols_death = 0
    p_pols_if = 0
    p_pols_lapse = 0
    for t in range(s_proj_len):
        c_claim_pp = mp__sum_assured[i]
        c_disc_rate_mth__at = (pow((1 + ref__disc_rate_ann[<Py_ssize_t>((t // 12))]), ((<double>(1)) / (<double>(12)))) - 1)
        c_duration = (t // 12)
        c_inflation_factor = pow((1 + s_inflation_rate), ((<double>(t)) / (<double>(12))))
        if (t == (mp__policy_term[i] * 12)):
            c_pols_maturity = ((p_pols_if - p_pols_lapse) - p_pols_death)
        else:
            c_pols_maturity = 0
        c_age = (mp__age_at_entry[i] + c_duration)
        c_disc_factors__at = pow((1 + c_disc_rate_mth__at), (-t))
        c_lapse_rate = (((0.1 - (0.02 * c_duration))) if ((0.1 - (0.02 * c_duration))) >= (0.02) else (0.02))
        if (t == 0):
            c_pols_if = s_pols_if_init
        else:
            if (t > (mp__policy_term[i] * 12)):
                c_pols_if = 0
            else:
                c_pols_if = (((p_pols_if - p_pols_lapse) - p_pols_death) - c_pols_maturity)
        l_expenses_maint = (((<double>((c_pols_if * s_expense_maint))) / (<double>(12))) * c_inflation_factor)
        if (t == 0):
            c_expenses = (s_expense_acq + l_expenses_maint)
        else:
            c_expenses = l_expenses_maint
        c_mort_rate = ref__mort_table[<Py_ssize_t>(c_age), <Py_ssize_t>(((((5) if (5) <= (c_duration) else (c_duration))) if (((5) if (5) <= (c_duration) else (c_duration))) >= (0) else (0)))]
        c_premiums = (s_premium_pp * c_pols_if)
        c_commissions = (c_premiums if (c_duration == 0) else 0)
        c_mort_rate_mth = (1 - pow((1 - c_mort_rate), ((<double>(1)) / (<double>(12)))))
        c_pols_death = (c_pols_if * c_mort_rate_mth)
        c_claims = (c_claim_pp * c_pols_death)
        c_pols_lapse = ((c_pols_if - c_pols_death) * (1 - pow((1 - c_lapse_rate), ((<double>(1)) / (<double>(12))))))
        a_pv_commissions += (c_commissions * c_disc_factors__at)
        a_pv_premiums += (c_premiums * c_disc_factors__at)
        p_pols_death = c_pols_death
        p_pols_if = c_pols_if
        p_pols_lapse = c_pols_lapse

    s_pv_net_cf = (((a_pv_premiums - a_pv_claims) - a_pv_expenses) - a_pv_commissions)
    out[i, 0] = s_pv_net_cf

cpdef cnp.ndarray run(
    cnp.ndarray[cnp.int64_t, ndim=1] mp__policy_term,
    cnp.ndarray[cnp.int64_t, ndim=1] mp__sum_assured,
    cnp.ndarray[cnp.int64_t, ndim=1] mp__age_at_entry,
    cnp.ndarray[cnp.float64_t, ndim=1] ref__disc_rate_ann,
    cnp.ndarray[cnp.float64_t, ndim=2] ref__mort_table,
    int threads=1,
):
    cdef Py_ssize_t n = mp__policy_term.shape[0]
    cdef cnp.ndarray[cnp.float64_t, ndim=2] out_arr = np.empty((n, 1), dtype=np.float64)
    cdef long[::1] m_mp__policy_term = mp__policy_term
    cdef long[::1] m_mp__sum_assured = mp__sum_assured
    cdef long[::1] m_mp__age_at_entry = mp__age_at_entry
    cdef double[::1] m_ref__disc_rate_ann = ref__disc_rate_ann
    cdef double[:,::1] m_ref__mort_table = ref__mort_table
    cdef double[:,::1] out = out_arr
    cdef Py_ssize_t i
    if threads != 1:
        raise ValueError('Part-1 fast foundation is serial-only; threads must be 1')
    with nogil:
        for i in range(n):
            _run_one(i, m_mp__policy_term, m_mp__sum_assured, m_mp__age_at_entry, m_ref__disc_rate_ann, m_ref__mort_table, out)
    return out_arr
