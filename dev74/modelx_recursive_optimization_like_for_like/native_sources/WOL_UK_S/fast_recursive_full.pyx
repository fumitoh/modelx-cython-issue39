# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False
from libc.math cimport pow, fabs, rint, exp, log, sqrt, sin, cos, floor, ceil, isnan, isinf, erf, NAN
from libc.stdlib cimport malloc, calloc, free
cimport numpy as cnp
import numpy as np

cdef Py_ssize_t CACHE_WIDTH = 4096
cdef Py_ssize_t CACHE_OFFSET = 1024
cdef Py_ssize_t CACHE_ROWS = 46
cdef double* _cache = NULL
cdef unsigned int* _valid = NULL
cdef unsigned int _epoch = 1
cdef Py_ssize_t _n = 0

cdef double[::1] p_1
cdef long[::1] p_2
cdef long g_3
cdef long[::1] p_4
cdef double[::1] p_5
cdef long[::1] p_6
cdef double g_7
cdef double g_8
cdef double g_9
cdef double g_10
cdef double g_11
cdef long[::1] p_12
cdef double g_13
cdef double g_14
cdef double g_15
cdef long[::1] p_16
cdef long[::1] p_17
cdef double[:, :, :, ::1] exttn_18
cdef long[::1] p_19
cdef double[::1] p_20
cdef double g_21
cdef double g_22
cdef double g_23
cdef double g_24
cdef long[::1] p_25
cdef double g_26
cdef double g_27
cdef double g_28
cdef double g_29
cdef double g_30
cdef double g_31
cdef long[::1] extmeta_32
cdef double[:, ::1] exttn_33
cdef long[::1] p_34

cpdef init_inputs(dict d):
    global _cache, _valid, _epoch, _n, p_1, p_2, g_3, p_4, p_5, p_6, g_7, g_8, g_9, g_10, g_11, p_12, g_13, g_14, g_15, p_16, p_17, exttn_18, p_19, p_20, g_21, g_22, g_23, g_24, p_25, g_26, g_27, g_28, g_29, g_30, g_31, extmeta_32, exttn_33, p_34
    p_1 = np.ascontiguousarray(d['p_1'], dtype=np.float64)
    p_2 = np.ascontiguousarray(d['p_2'], dtype=np.int64)
    g_3 = int(np.asarray(d['g_3']).reshape(()))
    p_4 = np.ascontiguousarray(d['p_4'], dtype=np.int64)
    p_5 = np.ascontiguousarray(d['p_5'], dtype=np.float64)
    p_6 = np.ascontiguousarray(d['p_6'], dtype=np.int64)
    g_7 = float(np.asarray(d['g_7']).reshape(()))
    g_8 = float(np.asarray(d['g_8']).reshape(()))
    g_9 = float(np.asarray(d['g_9']).reshape(()))
    g_10 = float(np.asarray(d['g_10']).reshape(()))
    g_11 = float(np.asarray(d['g_11']).reshape(()))
    p_12 = np.ascontiguousarray(d['p_12'], dtype=np.int64)
    g_13 = float(np.asarray(d['g_13']).reshape(()))
    g_14 = float(np.asarray(d['g_14']).reshape(()))
    g_15 = float(np.asarray(d['g_15']).reshape(()))
    p_16 = np.ascontiguousarray(d['p_16'], dtype=np.int64)
    p_17 = np.ascontiguousarray(d['p_17'], dtype=np.int64)
    exttn_18 = np.ascontiguousarray(d['exttn_18'], dtype=np.float64)
    p_19 = np.ascontiguousarray(d['p_19'], dtype=np.int64)
    p_20 = np.ascontiguousarray(d['p_20'], dtype=np.float64)
    g_21 = float(np.asarray(d['g_21']).reshape(()))
    g_22 = float(np.asarray(d['g_22']).reshape(()))
    g_23 = float(np.asarray(d['g_23']).reshape(()))
    g_24 = float(np.asarray(d['g_24']).reshape(()))
    p_25 = np.ascontiguousarray(d['p_25'], dtype=np.int64)
    g_26 = float(np.asarray(d['g_26']).reshape(()))
    g_27 = float(np.asarray(d['g_27']).reshape(()))
    g_28 = float(np.asarray(d['g_28']).reshape(()))
    g_29 = float(np.asarray(d['g_29']).reshape(()))
    g_30 = float(np.asarray(d['g_30']).reshape(()))
    g_31 = float(np.asarray(d['g_31']).reshape(()))
    extmeta_32 = np.ascontiguousarray(d['extmeta_32'], dtype=np.int64)
    exttn_33 = np.ascontiguousarray(d['exttn_33'], dtype=np.float64)
    p_34 = np.ascontiguousarray(d['p_34'], dtype=np.int64)
    _n = p_1.shape[0]
    if p_2.shape[0] != _n:
        raise ValueError('point input length mismatch: p_2')
    if p_4.shape[0] != _n:
        raise ValueError('point input length mismatch: p_4')
    if p_5.shape[0] != _n:
        raise ValueError('point input length mismatch: p_5')
    if p_6.shape[0] != _n:
        raise ValueError('point input length mismatch: p_6')
    if p_12.shape[0] != _n:
        raise ValueError('point input length mismatch: p_12')
    if p_16.shape[0] != _n:
        raise ValueError('point input length mismatch: p_16')
    if p_17.shape[0] != _n:
        raise ValueError('point input length mismatch: p_17')
    if p_19.shape[0] != _n:
        raise ValueError('point input length mismatch: p_19')
    if p_20.shape[0] != _n:
        raise ValueError('point input length mismatch: p_20')
    if p_25.shape[0] != _n:
        raise ValueError('point input length mismatch: p_25')
    if p_34.shape[0] != _n:
        raise ValueError('point input length mismatch: p_34')
    if _cache == NULL:
        _cache = <double*>malloc(CACHE_ROWS * CACHE_WIDTH * sizeof(double))
        _valid = <unsigned int*>calloc(CACHE_ROWS * CACHE_WIDTH, sizeof(unsigned int))
        if _cache == NULL or _valid == NULL: raise MemoryError()
    _epoch = 1
    return None

cdef inline long calc_v_0018754bd3ad(Py_ssize_t i) noexcept nogil:
    return <long>((<long>((<long>(p_2[i])))))
    return <long>0

cdef inline double calc_v_002d35e02c59(Py_ssize_t i, long t) noexcept nogil:
    if (((<long>(p_12[i])) == 0) and r_v_71a858b6427b(i, <long>(t))):
        return <double>(r_v_fbe2ee8c3de5(i, <long>(t)))
    return <double>(r_v_f2a7f830f2b5(i, <long>(t)))
    return <double>0

cdef inline long calc_v_087ef9eedc4b(Py_ssize_t i) noexcept nogil:
    return <long>((<long>((<long>(p_4[i])))))
    return <long>0

cdef inline double calc_v_1f417154a7db(Py_ssize_t i, long t) noexcept nogil:
    if ((<long>(p_12[i])) != 0):
        return <double>(r_v_f2a7f830f2b5(i, <long>(t)))
    if r_v_71a858b6427b(i, <long>(t)):
        return <double>(r_v_f2a7f830f2b5(i, <long>(t)))
    return <double>(((r_v_261d66058626(i)) * (r_v_f2a7f830f2b5(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_261d66058626(Py_ssize_t i) noexcept nogil:
    return <double>((2.0 if (<bint>((<long>(p_34[i])))) else 1.0))
    return <double>0

cdef inline double calc_v_29fce575a104(Py_ssize_t i, long t) noexcept nogil:
    return <double>(0.0)
    return <double>0

cdef inline double calc_v_319b8be529df(Py_ssize_t i, long t) noexcept nogil:
    if (r_v_4163499708dc(i, <long>(t)) > 1):
        return <double>(0.0)
    return <double>(((g_31) * (r_v_56a90e1fadcf(i, <long>(t)))))
    return <double>0

cdef inline long calc_v_4163499708dc(Py_ssize_t i, long t) noexcept nogil:
    return <long>(((r_v_881153203729(i, <long>(t))) + (1)))
    return <long>0

cdef inline double calc_v_45e36b4cfa88(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_6d03c211d769(i, <long>(t))) * (r_v_9691d5b1cad4(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_48e82a135007(Py_ssize_t i) noexcept nogil:
    cdef double acc = <double>(0.0)
    cdef long t = <long>(1)
    cdef long stop = <long>(((r_v_d0eaf3265ed2(i)) + (1)))
    cdef long step = <long>(1)
    while (t < stop if step > 0 else t > stop):
        acc = <double>(acc + (r_v_848204f3aaf6(i, <long>(t))))
        t += step
    return acc

cdef inline double calc_v_48e899e59a60(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_1[i])))
    return <double>0

cdef inline double calc_v_5200e3fc2c0d(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_b5101875359b(i, <long>(t))) * (r_v_9691d5b1cad4(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_56a90e1fadcf(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_f1f8c6f9858e(i, <long>(t))) * (r_v_6d03c211d769(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_5ee64001942e(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_6d03c211d769(i, <long>(t))) + (r_v_d66b41911940(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_6a925f67e581(Py_ssize_t i, long t) noexcept nogil:
    cdef double l_q = 0.0
    l_q = (<double>(exttn_18[<Py_ssize_t>((0 if ((<long>(p_12[i])) == 0) else 1)), <Py_ssize_t>((<long>(p_16[i]))), <Py_ssize_t>((<long>(p_17[i]))), <Py_ssize_t>((<long>(((r_v_ca26d4194058(i, <long>(t))) - (18)) / (1))))]))
    return <double>(((1.0) if (1.0) <= (((((l_q) * (r_v_c783ba20651a(i)))) * (r_v_e5124f4a3444(i, <long>(t))))) else (((((l_q) * (r_v_c783ba20651a(i)))) * (r_v_e5124f4a3444(i, <long>(t)))))))
    return <double>0

cdef inline double calc_v_6d03c211d769(Py_ssize_t i, long t) noexcept nogil:
    if ((t < 1) or (t > r_v_d0eaf3265ed2(i))):
        return <double>(0.0)
    if (t == 1):
        return <double>(r_v_48e899e59a60(i))
    return <double>(((((r_v_6d03c211d769(i, <long>(((t) - (1))))) * (((1.0) - (r_v_9691d5b1cad4(i, <long>(((t) - (1))))))))) * (((1.0) - (r_v_dca164a86b17(i, <long>(((t) - (1)))))))))
    return <double>0

cdef inline bint calc_v_71a858b6427b(Py_ssize_t i, long t) noexcept nogil:
    return <bint>((t <= r_v_9436baa68f18(i)))
    return <bint>0

cdef inline double calc_v_7f927c265f15(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_45e36b4cfa88(i, <long>(t))) * (r_v_e5fb0b04845d(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_7fbfc86fd6a7(Py_ssize_t i, long t) noexcept nogil:
    cdef double l___mx_h_result_0 = 0.0
    cdef long l___mx_h_result_1 = 0
    if (not r_v_86774bd9246e(i)):
        return <double>(0.0)
    if (r_v_087ef9eedc4b(i) <= 0):
        l___mx_h_result_0 = t
    else:
        l___mx_h_result_0 = ((t) if (t) <= (r_v_087ef9eedc4b(i)) else (r_v_087ef9eedc4b(i)))
    l___mx_h_result_1 = r_v_087ef9eedc4b(i)
    return <double>(((<double>(((r_v_f2a7f830f2b5(i, <long>(t))) * (l___mx_h_result_0)))) / (l___mx_h_result_1)))
    return <double>0

cdef inline double calc_v_848204f3aaf6(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((((((r_v_56a90e1fadcf(i, <long>(t))) - (r_v_ce648ae213c6(i, <long>(t))))) - (r_v_caa4106c8023(i, <long>(t))))) - (r_v_319b8be529df(i, <long>(t)))))
    return <double>0

cdef inline bint calc_v_86774bd9246e(Py_ssize_t i) noexcept nogil:
    cdef bint l_v = 0
    l_v = (<bint>((<long>(p_25[i]))))
    if (l_v and (r_v_087ef9eedc4b(i) <= 0)):
        return <bint>(0)
    return <bint>(l_v)
    return <bint>0

cdef inline long calc_v_881153203729(Py_ssize_t i, long t) noexcept nogil:
    return <long>(((((t) - (1))) // (12)))
    return <long>0

cdef inline double calc_v_8b7e3dc6890c(Py_ssize_t i) noexcept nogil:
    cdef long l_e = 0
    l_e = (<long>(p_6[i]))
    if (l_e == 0):
        return <double>(0.0)
    if (l_e == 1):
        return <double>(((g_21) * (g_8)))
    return <double>(((((((g_10) if (g_10) >= (0.0) else (0.0))) if (((g_10) if (g_10) >= (0.0) else (0.0))) <= (g_22) else (g_22))) * (g_8)))
    return <double>0

cdef inline double calc_v_8d6e86aba264(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_20[i])))
    return <double>0

cdef inline long calc_v_9436baa68f18(Py_ssize_t i) noexcept nogil:
    return <long>((<long>((<long>(p_19[i])))))
    return <long>0

cdef inline double calc_v_9691d5b1cad4(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((1.0) - (pow((((1.0) - (r_v_6a925f67e581(i, <long>(t))))), (((<double>(1.0)) / (12.0)))))))
    return <double>0

cdef inline double calc_v_9ce2efb30a11(Py_ssize_t i) noexcept nogil:
    return <double>((g_26 if ((<long>(p_12[i])) == 0) else g_27))
    return <double>0

cdef inline double calc_v_b5101875359b(Py_ssize_t i, long t) noexcept nogil:
    cdef double l___mx_h_result_0 = 0.0
    if ((t < 1) or (t > r_v_d0eaf3265ed2(i)) or (not r_v_86774bd9246e(i))):
        return <double>(0.0)
    if (t == 1):
        return <double>(0.0)
    l___mx_h_result_0 = (((((r_v_6d03c211d769(i, <long>(((t) - (1))))) * (((1.0) - (r_v_9691d5b1cad4(i, <long>(((t) - (1))))))))) * (r_v_dca164a86b17(i, <long>(((t) - (1)))))) if (False if (not r_v_86774bd9246e(i)) else ((((t) - (1)) if (r_v_087ef9eedc4b(i) <= 0) else ((((t) - (1))) if (((t) - (1))) <= (r_v_087ef9eedc4b(i)) else (r_v_087ef9eedc4b(i)))) >= ((<double>(r_v_087ef9eedc4b(i))) / (2.0)))) else 0.0)
    return <double>(((((r_v_b5101875359b(i, <long>(((t) - (1))))) * (((1.0) - (r_v_9691d5b1cad4(i, <long>(((t) - (1))))))))) + (((l___mx_h_result_0) * (r_v_7fbfc86fd6a7(i, <long>(((t) - (1)))))))))
    return <double>0

cdef inline double calc_v_b96fffd05d69(Py_ssize_t i, long t) noexcept nogil:
    return <double>(pow((((1.0) + (g_30))), (((r_v_4163499708dc(i, <long>(t))) - (1)))))
    return <double>0

cdef inline double calc_v_c783ba20651a(Py_ssize_t i) noexcept nogil:
    return <double>((g_13 if ((<long>(p_12[i])) == 0) else g_14))
    return <double>0

cdef inline long calc_v_ca26d4194058(Py_ssize_t i, long t) noexcept nogil:
    return <long>(((r_v_0018754bd3ad(i)) + (r_v_881153203729(i, <long>(t)))))
    return <long>0

cdef inline double calc_v_caa4106c8023(Py_ssize_t i, long t) noexcept nogil:
    cdef double l_acq = 0.0
    l_acq = (((r_v_9ce2efb30a11(i)) * (r_v_6d03c211d769(i, <long>(t)))) if (t == 1) else 0.0)
    return <double>(((l_acq) + (((((((<double>(r_v_f9b27f4eb703(i))) / (12.0))) * (r_v_b96fffd05d69(i, <long>(t))))) * (r_v_5ee64001942e(i, <long>(t)))))))
    return <double>0

cdef inline double calc_v_cba9652cd3b4(Py_ssize_t i, long t) noexcept nogil:
    cdef double l_w = 0.0
    if ((r_v_087ef9eedc4b(i) > 0) and (t > r_v_087ef9eedc4b(i))):
        return <double>(0.0)
    l_w = r_v_f70ccd185689(i, <long>(t))
    return <double>(((1.0) if (1.0) <= (l_w) else (l_w)))
    return <double>0

cdef inline double calc_v_ce648ae213c6(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((((((0) + (r_v_7f927c265f15(i, <long>(t))))) + (r_v_5200e3fc2c0d(i, <long>(t))))) + (r_v_29fce575a104(i, <long>(t)))))
    return <double>0

cdef inline long calc_v_d0eaf3265ed2(Py_ssize_t i) noexcept nogil:
    return <long>(((12) * ((((<long>(g_3))) - (r_v_0018754bd3ad(i))))))
    return <long>0

cdef inline double calc_v_d66b41911940(Py_ssize_t i, long t) noexcept nogil:
    cdef double l___mx_h_result_0 = 0.0
    if ((t < 1) or (t > r_v_d0eaf3265ed2(i)) or (not r_v_86774bd9246e(i))):
        return <double>(0.0)
    if (t == 1):
        return <double>(0.0)
    l___mx_h_result_0 = (((((r_v_6d03c211d769(i, <long>(((t) - (1))))) * (((1.0) - (r_v_9691d5b1cad4(i, <long>(((t) - (1))))))))) * (r_v_dca164a86b17(i, <long>(((t) - (1)))))) if (False if (not r_v_86774bd9246e(i)) else ((((t) - (1)) if (r_v_087ef9eedc4b(i) <= 0) else ((((t) - (1))) if (((t) - (1))) <= (r_v_087ef9eedc4b(i)) else (r_v_087ef9eedc4b(i)))) >= ((<double>(r_v_087ef9eedc4b(i))) / (2.0)))) else 0.0)
    return <double>(((((r_v_d66b41911940(i, <long>(((t) - (1))))) * (((1.0) - (r_v_9691d5b1cad4(i, <long>(((t) - (1))))))))) + (l___mx_h_result_0)))
    return <double>0

cdef inline double calc_v_d7573e5c34b9(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_5[i])))
    return <double>0

cdef inline double calc_v_dca164a86b17(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((1.0) - (pow((((1.0) - (r_v_cba9652cd3b4(i, <long>(t))))), (((<double>(1.0)) / (12.0)))))))
    return <double>0

cdef inline double calc_v_e5124f4a3444(Py_ssize_t i, long t) noexcept nogil:
    return <double>(pow((((1.0) - (g_15))), (((r_v_4163499708dc(i, <long>(t))) - (1)))))
    return <double>0

cdef inline double calc_v_e5fb0b04845d(Py_ssize_t i, long t) noexcept nogil:
    if ((<long>(p_12[i])) == 0):
        return <double>(((((((1.0) - (g_23))) * (r_v_002d35e02c59(i, <long>(t))))) + (((g_23) * (r_v_1f417154a7db(i, <long>(t)))))))
    if (t <= 12):
        return <double>(((((((1.0) - (g_24))) * (r_v_f2a7f830f2b5(i, <long>(t))))) + (((g_24) * (r_v_fbe2ee8c3de5(i, <long>(t)))))))
    return <double>(r_v_f2a7f830f2b5(i, <long>(t)))
    return <double>0

cdef inline double calc_v_f1f8c6f9858e(Py_ssize_t i, long t) noexcept nogil:
    if ((r_v_087ef9eedc4b(i) > 0) and (t > r_v_087ef9eedc4b(i))):
        return <double>(0.0)
    return <double>(((r_v_d7573e5c34b9(i)) * (pow((((1.0) + (r_v_fb2fd68f2b83(i)))), (((r_v_4163499708dc(i, <long>(t))) - (1)))))))
    return <double>0

cdef inline double calc_v_f2a7f830f2b5(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_8d6e86aba264(i)) * (pow((((1.0) + (r_v_8b7e3dc6890c(i)))), (((r_v_4163499708dc(i, <long>(t))) - (1)))))))
    return <double>0

cdef inline double calc_v_f70ccd185689(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_y = 0
    l_y = r_v_4163499708dc(i, <long>(t))
    return <double>((<double>(exttn_33[<Py_ssize_t>((<long>(p_12[i]))), <Py_ssize_t>((<long>(((((l_y) if (l_y) <= ((<long>((<long>(extmeta_32[<Py_ssize_t>((<long>(p_12[i])))]))))) else ((<long>((<long>(extmeta_32[<Py_ssize_t>((<long>(p_12[i])))]))))))) - (1)) / (1))))])))
    return <double>0

cdef inline double calc_v_f9b27f4eb703(Py_ssize_t i) noexcept nogil:
    return <double>((g_28 if ((<long>(p_12[i])) == 0) else g_29))
    return <double>0

cdef inline double calc_v_fb2fd68f2b83(Py_ssize_t i) noexcept nogil:
    cdef long l_e = 0
    l_e = (<long>(p_6[i]))
    if (l_e == 0):
        return <double>(0.0)
    if (l_e == 1):
        return <double>(((g_7) * (g_8)))
    return <double>(((((((((g_9) * (g_10))) if (((g_9) * (g_10))) >= (0.0) else (0.0))) if (((((g_9) * (g_10))) if (((g_9) * (g_10))) >= (0.0) else (0.0))) <= (g_11) else (g_11))) * (g_8)))
    return <double>0

cdef inline double calc_v_fbe2ee8c3de5(Py_ssize_t i, long t) noexcept nogil:
    if (t <= 0):
        return <double>(0.0)
    return <double>(((r_v_fbe2ee8c3de5(i, <long>(((t) - (1))))) + (r_v_f1f8c6f9858e(i, <long>(t)))))
    return <double>0

cdef inline long r_v_0018754bd3ad(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 0 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_0018754bd3ad(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_002d35e02c59(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 1 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_002d35e02c59(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_087ef9eedc4b(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 2 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_087ef9eedc4b(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_1f417154a7db(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 3 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_1f417154a7db(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_261d66058626(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 4 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_261d66058626(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_29fce575a104(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 5 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_29fce575a104(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_319b8be529df(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 6 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_319b8be529df(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_4163499708dc(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 7 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_4163499708dc(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_45e36b4cfa88(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 8 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_45e36b4cfa88(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_48e82a135007(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 9 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_48e82a135007(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_48e899e59a60(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 10 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_48e899e59a60(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_5200e3fc2c0d(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 11 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_5200e3fc2c0d(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_56a90e1fadcf(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 12 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_56a90e1fadcf(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_5ee64001942e(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 13 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_5ee64001942e(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_6a925f67e581(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 14 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_6a925f67e581(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_6d03c211d769(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 15 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_6d03c211d769(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline bint r_v_71a858b6427b(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 16 * CACHE_WIDTH + pos
    cdef bint val
    if pos < 0 or pos >= CACHE_WIDTH: return <bint>NAN
    if _valid[idx] == _epoch: return <bint>_cache[idx]
    val = calc_v_71a858b6427b(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7f927c265f15(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 17 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7f927c265f15(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7fbfc86fd6a7(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 18 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7fbfc86fd6a7(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_848204f3aaf6(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 19 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_848204f3aaf6(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline bint r_v_86774bd9246e(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 20 * CACHE_WIDTH + CACHE_OFFSET
    cdef bint val
    if _valid[idx] == _epoch: return <bint>_cache[idx]
    val = calc_v_86774bd9246e(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_881153203729(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 21 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_881153203729(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_8b7e3dc6890c(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 22 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_8b7e3dc6890c(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_8d6e86aba264(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 23 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_8d6e86aba264(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_9436baa68f18(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 24 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_9436baa68f18(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_9691d5b1cad4(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 25 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_9691d5b1cad4(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_9ce2efb30a11(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 26 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_9ce2efb30a11(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_b5101875359b(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 27 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_b5101875359b(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_b96fffd05d69(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 28 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_b96fffd05d69(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_c783ba20651a(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 29 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_c783ba20651a(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_ca26d4194058(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 30 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_ca26d4194058(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_caa4106c8023(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 31 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_caa4106c8023(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_cba9652cd3b4(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 32 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_cba9652cd3b4(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_ce648ae213c6(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 33 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_ce648ae213c6(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_d0eaf3265ed2(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 34 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_d0eaf3265ed2(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_d66b41911940(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 35 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_d66b41911940(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_d7573e5c34b9(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 36 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_d7573e5c34b9(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_dca164a86b17(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 37 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_dca164a86b17(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_e5124f4a3444(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 38 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_e5124f4a3444(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_e5fb0b04845d(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 39 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_e5fb0b04845d(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_f1f8c6f9858e(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 40 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_f1f8c6f9858e(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_f2a7f830f2b5(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 41 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_f2a7f830f2b5(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_f70ccd185689(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 42 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_f70ccd185689(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_f9b27f4eb703(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 43 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_f9b27f4eb703(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_fb2fd68f2b83(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 44 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_fb2fd68f2b83(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_fbe2ee8c3de5(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 45 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_fbe2ee8c3de5(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double _eval_one(Py_ssize_t i) noexcept nogil:
    global _epoch
    _epoch += 1
    return <double>r_v_48e82a135007(i)

cpdef cnp.ndarray run_all():
    cdef cnp.ndarray arr = np.empty(_n, dtype=np.float64)
    cdef double[::1] out = arr
    cdef Py_ssize_t i
    with nogil:
        for i in range(_n): out[i] = _eval_one(i)
    return arr

cpdef double bench(long reps):
    cdef long j
    cdef Py_ssize_t i
    cdef double acc = 0.0
    with nogil:
        for j in range(reps):
            for i in range(_n): acc += _eval_one(i)
    return acc
