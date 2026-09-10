# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False
from libc.math cimport pow, fabs, rint, exp, log, sqrt, sin, cos, floor, ceil, isnan, isinf, erf, NAN
from libc.stdlib cimport malloc, calloc, free
cimport numpy as cnp
import numpy as np

cdef inline double _round_ndigits(double x, long n) noexcept nogil:
    cdef double scale
    if n >= 0:
        scale = pow(10.0, <double>n)
        return rint(x * scale) / scale
    scale = pow(10.0, <double>(-n))
    return rint(x / scale) * scale

cdef Py_ssize_t CACHE_WIDTH = 4096
cdef Py_ssize_t CACHE_OFFSET = 1024
cdef Py_ssize_t CACHE_ROWS = 210
cdef double* _cache = NULL
cdef unsigned int* _valid = NULL
cdef unsigned int _epoch = 1
cdef Py_ssize_t _n = 0

cdef long[::1] p_1
cdef long[::1] p_2
cdef double[::1] p_3
cdef long[::1] p_4
cdef double[::1] p_5
cdef double[::1] p_6
cdef double[::1] p_7
cdef double[::1] p_8
cdef long[::1] p_9
cdef long[::1] p_10
cdef long g_11
cdef long[::1] p_12
cdef double[::1] p_13
cdef double[::1] p_14
cdef double g_15
cdef double[::1] extt1_16
cdef double[::1] p_17
cdef double g_18
cdef double g_19
cdef double g_20
cdef double extt0_21
cdef double[::1] extt1_22
cdef double g_23
cdef double[::1] extt1_24
cdef double[::1] p_25
cdef double g_26
cdef double g_27
cdef double g_28
cdef double g_29
cdef double extt0_30
cdef long extt0_31
cdef double[::1] extt1_32
cdef long[::1] p_33
cdef double g_34
cdef double g_35
cdef double g_36
cdef double[::1] p_37
cdef double g_38
cdef double g_39
cdef double g_40
cdef double g_41
cdef double g_42
cdef double g_43
cdef double g_44
cdef double g_45
cdef long[::1] p_46
cdef double[::1] extt1_47
cdef double[::1] p_48
cdef double g_49
cdef double[::1] extt1_50
cdef double g_51
cdef double g_52
cdef double g_53
cdef double g_54
cdef double g_55
cdef double g_56
cdef long g_57
cdef double g_58
cdef long g_59
cdef long g_60

cpdef init_inputs(dict d):
    global _cache, _valid, _epoch, _n, p_1, p_2, p_3, p_4, p_5, p_6, p_7, p_8, p_9, p_10, g_11, p_12, p_13, p_14, g_15, extt1_16, p_17, g_18, g_19, g_20, extt0_21, extt1_22, g_23, extt1_24, p_25, g_26, g_27, g_28, g_29, extt0_30, extt0_31, extt1_32, p_33, g_34, g_35, g_36, p_37, g_38, g_39, g_40, g_41, g_42, g_43, g_44, g_45, p_46, extt1_47, p_48, g_49, extt1_50, g_51, g_52, g_53, g_54, g_55, g_56, g_57, g_58, g_59, g_60
    p_1 = np.ascontiguousarray(d['p_1'], dtype=np.int64)
    p_2 = np.ascontiguousarray(d['p_2'], dtype=np.int64)
    p_3 = np.ascontiguousarray(d['p_3'], dtype=np.float64)
    p_4 = np.ascontiguousarray(d['p_4'], dtype=np.int64)
    p_5 = np.ascontiguousarray(d['p_5'], dtype=np.float64)
    p_6 = np.ascontiguousarray(d['p_6'], dtype=np.float64)
    p_7 = np.ascontiguousarray(d['p_7'], dtype=np.float64)
    p_8 = np.ascontiguousarray(d['p_8'], dtype=np.float64)
    p_9 = np.ascontiguousarray(d['p_9'], dtype=np.int64)
    p_10 = np.ascontiguousarray(d['p_10'], dtype=np.int64)
    g_11 = int(np.asarray(d['g_11']).reshape(()))
    p_12 = np.ascontiguousarray(d['p_12'], dtype=np.int64)
    p_13 = np.ascontiguousarray(d['p_13'], dtype=np.float64)
    p_14 = np.ascontiguousarray(d['p_14'], dtype=np.float64)
    g_15 = float(np.asarray(d['g_15']).reshape(()))
    extt1_16 = np.ascontiguousarray(d['extt1_16'], dtype=np.float64)
    p_17 = np.ascontiguousarray(d['p_17'], dtype=np.float64)
    g_18 = float(np.asarray(d['g_18']).reshape(()))
    g_19 = float(np.asarray(d['g_19']).reshape(()))
    g_20 = float(np.asarray(d['g_20']).reshape(()))
    extt0_21 = float(np.asarray(d['extt0_21']).reshape(()))
    extt1_22 = np.ascontiguousarray(d['extt1_22'], dtype=np.float64)
    g_23 = float(np.asarray(d['g_23']).reshape(()))
    extt1_24 = np.ascontiguousarray(d['extt1_24'], dtype=np.float64)
    p_25 = np.ascontiguousarray(d['p_25'], dtype=np.float64)
    g_26 = float(np.asarray(d['g_26']).reshape(()))
    g_27 = float(np.asarray(d['g_27']).reshape(()))
    g_28 = float(np.asarray(d['g_28']).reshape(()))
    g_29 = float(np.asarray(d['g_29']).reshape(()))
    extt0_30 = float(np.asarray(d['extt0_30']).reshape(()))
    extt0_31 = int(np.asarray(d['extt0_31']).reshape(()))
    extt1_32 = np.ascontiguousarray(d['extt1_32'], dtype=np.float64)
    p_33 = np.ascontiguousarray(d['p_33'], dtype=np.int64)
    g_34 = float(np.asarray(d['g_34']).reshape(()))
    g_35 = float(np.asarray(d['g_35']).reshape(()))
    g_36 = float(np.asarray(d['g_36']).reshape(()))
    p_37 = np.ascontiguousarray(d['p_37'], dtype=np.float64)
    g_38 = float(np.asarray(d['g_38']).reshape(()))
    g_39 = float(np.asarray(d['g_39']).reshape(()))
    g_40 = float(np.asarray(d['g_40']).reshape(()))
    g_41 = float(np.asarray(d['g_41']).reshape(()))
    g_42 = float(np.asarray(d['g_42']).reshape(()))
    g_43 = float(np.asarray(d['g_43']).reshape(()))
    g_44 = float(np.asarray(d['g_44']).reshape(()))
    g_45 = float(np.asarray(d['g_45']).reshape(()))
    p_46 = np.ascontiguousarray(d['p_46'], dtype=np.int64)
    extt1_47 = np.ascontiguousarray(d['extt1_47'], dtype=np.float64)
    p_48 = np.ascontiguousarray(d['p_48'], dtype=np.float64)
    g_49 = float(np.asarray(d['g_49']).reshape(()))
    extt1_50 = np.ascontiguousarray(d['extt1_50'], dtype=np.float64)
    g_51 = float(np.asarray(d['g_51']).reshape(()))
    g_52 = float(np.asarray(d['g_52']).reshape(()))
    g_53 = float(np.asarray(d['g_53']).reshape(()))
    g_54 = float(np.asarray(d['g_54']).reshape(()))
    g_55 = float(np.asarray(d['g_55']).reshape(()))
    g_56 = float(np.asarray(d['g_56']).reshape(()))
    g_57 = int(np.asarray(d['g_57']).reshape(()))
    g_58 = float(np.asarray(d['g_58']).reshape(()))
    g_59 = int(np.asarray(d['g_59']).reshape(()))
    g_60 = int(np.asarray(d['g_60']).reshape(()))
    _n = p_1.shape[0]
    if p_2.shape[0] != _n:
        raise ValueError('point input length mismatch: p_2')
    if p_3.shape[0] != _n:
        raise ValueError('point input length mismatch: p_3')
    if p_4.shape[0] != _n:
        raise ValueError('point input length mismatch: p_4')
    if p_5.shape[0] != _n:
        raise ValueError('point input length mismatch: p_5')
    if p_6.shape[0] != _n:
        raise ValueError('point input length mismatch: p_6')
    if p_7.shape[0] != _n:
        raise ValueError('point input length mismatch: p_7')
    if p_8.shape[0] != _n:
        raise ValueError('point input length mismatch: p_8')
    if p_9.shape[0] != _n:
        raise ValueError('point input length mismatch: p_9')
    if p_10.shape[0] != _n:
        raise ValueError('point input length mismatch: p_10')
    if p_12.shape[0] != _n:
        raise ValueError('point input length mismatch: p_12')
    if p_13.shape[0] != _n:
        raise ValueError('point input length mismatch: p_13')
    if p_14.shape[0] != _n:
        raise ValueError('point input length mismatch: p_14')
    if p_17.shape[0] != _n:
        raise ValueError('point input length mismatch: p_17')
    if p_25.shape[0] != _n:
        raise ValueError('point input length mismatch: p_25')
    if p_33.shape[0] != _n:
        raise ValueError('point input length mismatch: p_33')
    if p_37.shape[0] != _n:
        raise ValueError('point input length mismatch: p_37')
    if p_46.shape[0] != _n:
        raise ValueError('point input length mismatch: p_46')
    if p_48.shape[0] != _n:
        raise ValueError('point input length mismatch: p_48')
    if _cache == NULL:
        _cache = <double*>malloc(CACHE_ROWS * CACHE_WIDTH * sizeof(double))
        _valid = <unsigned int*>calloc(CACHE_ROWS * CACHE_WIDTH, sizeof(unsigned int))
        if _cache == NULL or _valid == NULL: raise MemoryError()
    _epoch = 1
    return None

cdef inline long calc_v_00cac884b755(Py_ssize_t i, long t) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (t))) - (1)))
    return <long>0

cdef inline double calc_v_060e64fce405(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((1.0) if (1.0) <= ((((((((<double>(extt1_22[<Py_ssize_t>(((((((r_v_724bf4d7126c(i, <long>(t))) if (r_v_724bf4d7126c(i, <long>(t))) >= ((<long>(45))) else ((<long>(45))))) if (((r_v_724bf4d7126c(i, <long>(t))) if (r_v_724bf4d7126c(i, <long>(t))) >= ((<long>(45))) else ((<long>(45))))) <= ((<long>(120))) else ((<long>(120))))) - (45)))]))) * (r_v_58cd68bd0f8a(i)))) * (g_23))) * (r_v_9edbb44d4c06(i, <long>(t))))) else ((((((((<double>(extt1_22[<Py_ssize_t>(((((((r_v_724bf4d7126c(i, <long>(t))) if (r_v_724bf4d7126c(i, <long>(t))) >= ((<long>(45))) else ((<long>(45))))) if (((r_v_724bf4d7126c(i, <long>(t))) if (r_v_724bf4d7126c(i, <long>(t))) >= ((<long>(45))) else ((<long>(45))))) <= ((<long>(120))) else ((<long>(120))))) - (45)))]))) * (r_v_58cd68bd0f8a(i)))) * (g_23))) * (r_v_9edbb44d4c06(i, <long>(t)))))))
    return <double>0

cdef inline double calc_v_085e0f33632c(Py_ssize_t i, long t) noexcept nogil:
    if (t == 1):
        return <double>(r_v_15e799ddf9f3(i))
    if r_v_2b89cb6420d2(i, <long>(t)):
        return <double>(0.0)
    return <double>(((((((((r_v_085e0f33632c(i, <long>(((t) - (1))))) - (r_v_08985c5ea0ac(i, <long>(((t) - (1))))))) - (r_v_e75213b4b943(i, <long>(((t) - (1))))))) - (r_v_bd1626ec57b1(i, <long>(((t) - (1))))))) - (r_v_b365e04f5e68(i, <long>(((t) - (1)))))))
    return <double>0

cdef inline double calc_v_08985c5ea0ac(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_085e0f33632c(i, <long>(t))) * (r_v_fea9b16c8ae2(i, <long>(t)))))
    return <double>0

cdef inline long calc_v_09790277bb3a(Py_ssize_t i, long t) noexcept nogil:
    if (t < 1):
        return <long>(0)
    if r_v_2b89cb6420d2(i, <long>(t)):
        return <long>(0)
    if ((not r_v_dd7273420244(i, <long>(t))) or r_v_0a9ae2866144(i, <long>(t))):
        return <long>(0)
    return <long>(((r_v_09790277bb3a(i, <long>(((t) - (1))))) + (1)))
    return <long>0

cdef inline bint calc_v_0a9ae2866144(Py_ssize_t i, long t) noexcept nogil:
    return <bint>((((r_v_0c8b1dc7fa99(i, <long>(t))) - (r_v_d412ff51f832(i, <long>(((t) - (1)))))) > 0))
    return <bint>0

cdef inline double calc_v_0b4b0c03129b(Py_ssize_t i, long t) noexcept nogil:
    return <double>(r_v_63b0c8fbde95(i, <long>(((t) - (1)))))
    return <double>0

cdef inline double calc_v_0c8b1dc7fa99(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_9821f58b3858(i, <long>(t))) - (r_v_ce40e4c023f2(i, <long>(t)))))
    return <double>0

cdef inline long calc_v_10910b14fe37(Py_ssize_t i) noexcept nogil:
    return <long>((<long>((<long>(p_10[i])))))
    return <long>0

cdef inline double calc_v_15e799ddf9f3(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_8[i])))
    return <double>0

cdef inline double calc_v_171a7d6038fe(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((0.0) if (0.0) >= (((((<double>(r_v_b6723d12867c(i, <long>(t)))) / (r_v_527a4c5d5fed(i)))) - (((r_v_9821f58b3858(i, <long>(t))) if (r_v_9821f58b3858(i, <long>(t))) >= (0.0) else (0.0))))) else (((((<double>(r_v_b6723d12867c(i, <long>(t)))) / (r_v_527a4c5d5fed(i)))) - (((r_v_9821f58b3858(i, <long>(t))) if (r_v_9821f58b3858(i, <long>(t))) >= (0.0) else (0.0)))))))
    return <double>0

cdef inline double calc_v_17309634da2d(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_216f150ab78f(i, <long>(t))) * (r_v_e75213b4b943(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_180fdd694e62(Py_ssize_t i, long t) noexcept nogil:
    if (r_v_724bf4d7126c(i, <long>(t)) >= 121):
        return <double>(0.0)
    return <double>(((g_39) * (r_v_c98ef0a4f9f7(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_191b62404134(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((<double>((<double>(extt1_24[<Py_ssize_t>(((((r_v_724bf4d7126c(i, <long>(t))) if (r_v_724bf4d7126c(i, <long>(t))) <= ((<long>(121))) else ((<long>(121))))) - (45)))])))) / (12)))
    return <double>0

cdef inline double calc_v_1ab04f45b315(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((0.0) if (0.0) >= (((((<double>(r_v_b6723d12867c(i, <long>(t)))) / (r_v_7922171d762c(i)))) - (((r_v_1d4416fd8dee(i, <long>(t))) if (r_v_1d4416fd8dee(i, <long>(t))) >= (0.0) else (0.0))))) else (((((<double>(r_v_b6723d12867c(i, <long>(t)))) / (r_v_7922171d762c(i)))) - (((r_v_1d4416fd8dee(i, <long>(t))) if (r_v_1d4416fd8dee(i, <long>(t))) >= (0.0) else (0.0)))))))
    return <double>0

cdef inline double calc_v_1cb225ed960e(Py_ssize_t i) noexcept nogil:
    if (r_v_91991af267ed(i) >= 121):
        return <double>(g_34)
    return <double>(1.0)
    return <double>0

cdef inline double calc_v_1d4416fd8dee(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_c2957380cf52(i, <long>(t))) - (r_v_7f778c30a0bc(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_1e03e469e091(Py_ssize_t i, long t) noexcept nogil:
    if (t == 0):
        return <double>(r_v_dce87cc64b35(i))
    return <double>(((r_v_1e03e469e091(i, <long>(((t) - (1))))) + (r_v_38879954341b(i, <long>(t)))))
    return <double>0

cdef inline long calc_v_1e3dacbf5af4(Py_ssize_t i) noexcept nogil:
    cdef double l_o = 0.0
    l_o = p_25[i]
    return <long>(((-1) if isnan(<double>(l_o)) else (<long>(l_o))))
    return <long>0

cdef inline bint calc_v_1fd042196776(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_pt = 0
    l_pt = (<long>(p_12[i]))
    if (l_pt == 1):
        return <bint>((r_v_00cac884b755(i, <long>(t)) == 0))
    else:
        if False:
            if (r_v_6aa454da9c91(i, <long>(t)) >= 10):
                return <bint>(False)
        else:
            if (l_pt != 0):
                return <bint>(0)
    return <bint>((((r_v_00cac884b755(i, <long>(t))) % (((12) // (r_v_83672a59fc09(i))))) == 0))
    return <bint>0

cdef inline double calc_v_216f150ab78f(Py_ssize_t i, long t) noexcept nogil:
    return <double>(r_v_652a64655085(i, <long>(t)))
    return <double>0

cdef inline double calc_v_299fafca332f(Py_ssize_t i, long t) noexcept nogil:
    cdef double l_loaned = 0.0
    cdef double l_unloaned = 0.0
    l_loaned = r_v_d412ff51f832(i, <long>(((t) - (1))))
    l_unloaned = ((r_v_600d48f86152(i, <long>(t))) - (l_loaned))
    return <double>(((((l_unloaned) * (r_v_9bc52957e758(i, <long>(t))))) + (((l_loaned) * (r_v_72ddbcded512(i))))))
    return <double>0

cdef inline double calc_v_2abc297880e0(Py_ssize_t i, long t) noexcept nogil:
    return <double>(pow((((1) + (g_51))), (((r_v_2df6bf4c2dbf(i, <long>(t))) - (1)))))
    return <double>0

cdef inline bint calc_v_2b89cb6420d2(Py_ssize_t i, long t) noexcept nogil:
    if (t <= 1):
        return <bint>(False)
    return <bint>((r_v_2b89cb6420d2(i, <long>(((t) - (1)))) or (r_v_09790277bb3a(i, <long>(((t) - (1)))) >= (<long>(g_57)))))
    return <bint>0

cdef inline long calc_v_2be2509482b8(Py_ssize_t i) noexcept nogil:
    return <long>(((((12) * ((((<long>(g_11))) - (r_v_f2c754e54e7f(i)))))) - (r_v_10910b14fe37(i))))
    return <long>0

cdef inline double calc_v_2d1a9910c695(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_5[i])))
    return <double>0

cdef inline long calc_v_2df6bf4c2dbf(Py_ssize_t i, long t) noexcept nogil:
    return <long>(((r_v_6aa454da9c91(i, <long>(t))) + (1)))
    return <long>0

cdef inline bint calc_v_359543fd71b6(Py_ssize_t i) noexcept nogil:
    return <bint>((<bint>((<long>(p_46[i])))))
    return <bint>0

cdef inline double calc_v_38879954341b(Py_ssize_t i, long t) noexcept nogil:
    if (r_v_724bf4d7126c(i, <long>(t)) >= 121):
        return <double>(0.0)
    if (not r_v_1fd042196776(i, <long>(t))):
        return <double>(0.0)
    if ((<long>(p_12[i])) == 1):
        return <double>(((r_v_c156869f907a(i)) * (r_v_761b9f8afdde(i, <long>(t)))))
    return <double>(((((<double>(r_v_c156869f907a(i))) / (r_v_83672a59fc09(i)))) * (r_v_761b9f8afdde(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_4117b6d32875(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_0b4b0c03129b(i, <long>(t))) + (r_v_67433777b17b(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_49d1c13d2698(Py_ssize_t i, long t) noexcept nogil:
    cdef double l_rate = 0.0
    l_rate = ((((((r_v_c3970ad2ed18(i, <long>(t))) * (r_v_1cb225ed960e(i)))) * (r_v_678a332a77ce(i)))) * (r_v_86f21db6ffbc(i, <long>(t))))
    return <double>(((g_44) if (g_44) <= (((g_45) if (g_45) >= (l_rate) else (l_rate))) else (((g_45) if (g_45) >= (l_rate) else (l_rate)))))
    return <double>0

cdef inline double calc_v_527a4c5d5fed(Py_ssize_t i) noexcept nogil:
    return <double>(((1) + (r_v_c13b3576a8a5(i))))
    return <double>0

cdef inline bint calc_v_557c64b0b275(Py_ssize_t i, long t) noexcept nogil:
    return <bint>((r_v_912715b3e4c1(i, <long>(t)) > 0))
    return <bint>0

cdef inline double calc_v_56238bb95db5(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_fa5111502a7e(i, <long>(t))) * (r_v_085e0f33632c(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_58cd68bd0f8a(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(extt0_21)))
    return <double>0

cdef inline double calc_v_5c2948769e25(Py_ssize_t i, long t) noexcept nogil:
    return <double>(0.0)
    return <double>0

cdef inline double calc_v_5d2c15336093(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_a = 0
    l_a = r_v_fe375b3640a2(i, <long>(t))
    if (l_a == 0):
        return <double>(0.0)
    return <double>((<double>(extt1_47[<Py_ssize_t>(((((r_v_fe375b3640a2(i, <long>(t))) - (20))) // (5)))])))
    return <double>0

cdef inline double calc_v_600d48f86152(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((0.0) if (0.0) >= (((r_v_1d4416fd8dee(i, <long>(t))) - (r_v_fb63239bcaf4(i, <long>(t))))) else (((r_v_1d4416fd8dee(i, <long>(t))) - (r_v_fb63239bcaf4(i, <long>(t)))))))
    return <double>0

cdef inline double calc_v_602b31c3292a(Py_ssize_t i, long t) noexcept nogil:
    if (t == 0):
        return <double>(r_v_a03e65d9a726(i))
    return <double>(((r_v_0c8b1dc7fa99(i, <long>(t))) + (r_v_a99017c46bdd(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_6099c329751b(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_38879954341b(i, <long>(t))) * (r_v_085e0f33632c(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_63b0c8fbde95(Py_ssize_t i, long t) noexcept nogil:
    if (t == 0):
        return <double>(r_v_79055b2863ce(i))
    return <double>(((r_v_600d48f86152(i, <long>(t))) + (r_v_299fafca332f(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_652a64655085(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((0.0) if (0.0) >= (((r_v_7766c1f5ba43(i, <long>(t))) - (r_v_d412ff51f832(i, <long>(t))))) else (((r_v_7766c1f5ba43(i, <long>(t))) - (r_v_d412ff51f832(i, <long>(t)))))))
    return <double>0

cdef inline double calc_v_67433777b17b(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_38879954341b(i, <long>(t))) * (((1) - (r_v_fd31871d8b0f(i))))))
    return <double>0

cdef inline double calc_v_678a332a77ce(Py_ssize_t i) noexcept nogil:
    cdef long l_pt = 0
    l_pt = (<long>(p_12[i]))
    if (l_pt == 1):
        return <double>(g_35)
    else:
        if False:
            return <double>(g_36)
        else:
            if (l_pt == 0):
                return <double>(1.0)
            else:
                return <double>(NAN)
    return <double>0

cdef inline long calc_v_6aa454da9c91(Py_ssize_t i, long t) noexcept nogil:
    return <long>(((r_v_00cac884b755(i, <long>(t))) // (12)))
    return <long>0

cdef inline double calc_v_70732c567ed9(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_7a217024e68c(i, <long>(t))) * (r_v_08985c5ea0ac(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_70cc01298727(Py_ssize_t i, long t) noexcept nogil:
    if (r_v_00cac884b755(i, <long>(t)) < ((12) * (1))):
        return <double>(0.0)
    if (r_v_724bf4d7126c(i, <long>(t)) >= 121):
        return <double>(0.0)
    return <double>((<double>(p_6[i])))
    return <double>0

cdef inline long calc_v_724bf4d7126c(Py_ssize_t i, long t) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_v_6aa454da9c91(i, <long>(t)))))
    return <long>0

cdef inline double calc_v_72ddbcded512(Py_ssize_t i) noexcept nogil:
    return <double>(((pow((((1) + (g_29))), (((<double>(1)) / (12))))) - (1)))
    return <double>0

cdef inline double calc_v_72f40ac54d00(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_a = 0
    l_a = r_v_724bf4d7126c(i, <long>(t))
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_v_761b9f8afdde(Py_ssize_t i, long t) noexcept nogil:
    cdef double l_o = 0.0
    l_o = p_14[i]
    if (not isnan(<double>(l_o))):
        return <double>((<double>(l_o)))
    return <double>((g_15 if ((<long>(p_12[i])) == 0) else 1.0))
    return <double>0

cdef inline double calc_v_771ce5c5860b(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((<double>(((r_v_d18fe1c6c0b2(i, <long>(t))) * (r_v_2d1a9910c695(i))))) / (1000)))
    return <double>0

cdef inline double calc_v_7766c1f5ba43(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((0.0) if (0.0) >= (((r_v_63b0c8fbde95(i, <long>(t))) - (r_v_771ce5c5860b(i, <long>(t))))) else (((r_v_63b0c8fbde95(i, <long>(t))) - (r_v_771ce5c5860b(i, <long>(t)))))))
    return <double>0

cdef inline double calc_v_79055b2863ce(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_17[i])))
    return <double>0

cdef inline double calc_v_7922171d762c(Py_ssize_t i) noexcept nogil:
    return <double>(((1) + (r_v_828276648c84(i))))
    return <double>0

cdef inline double calc_v_7a217024e68c(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_b6723d12867c(i, <long>(t))) - (r_v_d412ff51f832(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_7bf778bc7964(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_826fb7bd4dc7(i, <long>(t))) + (r_v_a6ce98136045(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_7c052059790f(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((((((((r_v_6099c329751b(i, <long>(t))) - (r_v_b895ae67dd0e(i, <long>(t))))) - (r_v_56238bb95db5(i, <long>(t))))) - (r_v_b52b6f2be8cb(i, <long>(t))))) - (r_v_b795ac4497e6(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_7ec902c106f7(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_7bf778bc7964(i, <long>(t))) - (r_v_70cc01298727(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_7f778c30a0bc(Py_ssize_t i, long t) noexcept nogil:
    if (r_v_724bf4d7126c(i, <long>(t)) >= 121):
        return <double>(0.0)
    return <double>(((((g_18) + (((g_19) * (r_v_c98ef0a4f9f7(i, <long>(t))))))) + (r_v_5c2948769e25(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_826fb7bd4dc7(Py_ssize_t i, long t) noexcept nogil:
    return <double>(r_v_602b31c3292a(i, <long>(((t) - (1)))))
    return <double>0

cdef inline double calc_v_828276648c84(Py_ssize_t i) noexcept nogil:
    return <double>(((pow((((1) + (g_27))), (((<double>(1)) / (12))))) - (1)))
    return <double>0

cdef inline long calc_v_83672a59fc09(Py_ssize_t i) noexcept nogil:
    return <long>(1)
    return <long>0

cdef inline double calc_v_86f21db6ffbc(Py_ssize_t i, long t) noexcept nogil:
    if (not r_v_557c64b0b275(i, <long>(t))):
        return <double>(g_42)
    if (r_v_63b0c8fbde95(i, <long>(t)) > 0):
        return <double>(1.0)
    return <double>(g_43)
    return <double>0

cdef inline double calc_v_912715b3e4c1(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_602b31c3292a(i, <long>(t))) - (r_v_d412ff51f832(i, <long>(t)))))
    return <double>0

cdef inline long calc_v_91991af267ed(Py_ssize_t i) noexcept nogil:
    return <long>((<long>((<long>(p_33[i])))))
    return <long>0

cdef inline double calc_v_93ed088a39d6(Py_ssize_t i) noexcept nogil:
    cdef double acc = <double>(0.0)
    cdef long t = <long>(1)
    cdef long stop = <long>(((r_v_2be2509482b8(i)) + (1)))
    cdef long step = <long>(1)
    while (t < stop if step > 0 else t > stop):
        acc = <double>(acc + (r_v_7c052059790f(i, <long>(t))))
        t += step
    return acc

cdef inline double calc_v_95d087b307fd(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((0.0) if (0.0) >= (((((((r_v_5d2c15336093(i, <long>(t))) * (r_v_1e03e469e091(i, <long>(t))))) if (((r_v_5d2c15336093(i, <long>(t))) * (r_v_1e03e469e091(i, <long>(t))))) <= (((g_49) * (r_v_effa5208db32(i, <long>(t))))) else (((g_49) * (r_v_effa5208db32(i, <long>(t))))))) - (r_v_d412ff51f832(i, <long>(t))))) else (((((((r_v_5d2c15336093(i, <long>(t))) * (r_v_1e03e469e091(i, <long>(t))))) if (((r_v_5d2c15336093(i, <long>(t))) * (r_v_1e03e469e091(i, <long>(t))))) <= (((g_49) * (r_v_effa5208db32(i, <long>(t))))) else (((g_49) * (r_v_effa5208db32(i, <long>(t))))))) - (r_v_d412ff51f832(i, <long>(t)))))))
    return <double>0

cdef inline double calc_v_96abb0a799c7(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_3[i])))
    return <double>0

cdef inline double calc_v_9821f58b3858(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_7ec902c106f7(i, <long>(t))) - (r_v_180fdd694e62(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_9bc52957e758(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((((pow((((1) + (r_v_fa50c495e040(i, <long>(t))))), (((<double>(1)) / (12))))) - (1))) if (((pow((((1) + (r_v_fa50c495e040(i, <long>(t))))), (((<double>(1)) / (12))))) - (1))) >= (r_v_828276648c84(i)) else (r_v_828276648c84(i))))
    return <double>0

cdef inline double calc_v_9edbb44d4c06(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_k = 0
    l_k = ((((t) - (1))) // (12))
    if (l_k <= 0):
        return <double>(1.0)
    if (l_k > 20):
        return <double>(r_vfix_48e4dc6cc1dd(i))
    return <double>(((r_v_9edbb44d4c06(i, <long>(((t) - (12))))) * (((1) - (r_v_72f40ac54d00(i, <long>(((t) - (12)))))))))
    return <double>0

cdef inline double calc_v_a03e65d9a726(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_37[i])))
    return <double>0

cdef inline double calc_v_a4ab4b63bd70(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((1) - (pow((((1) - (r_v_49d1c13d2698(i, <long>(t))))), (((<double>(1)) / (12)))))))
    return <double>0

cdef inline double calc_v_a6ce98136045(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_38879954341b(i, <long>(t))) * (((1) - (g_38)))))
    return <double>0

cdef inline double calc_v_a86b1946564f(Py_ssize_t i, long t) noexcept nogil:
    return <double>((<double>(extt1_16[<Py_ssize_t>(((((((r_v_724bf4d7126c(i, <long>(t))) if (r_v_724bf4d7126c(i, <long>(t))) >= ((<long>(18))) else ((<long>(18))))) if (((r_v_724bf4d7126c(i, <long>(t))) if (r_v_724bf4d7126c(i, <long>(t))) >= ((<long>(18))) else ((<long>(18))))) <= ((<long>(121))) else ((<long>(121))))) - (18)))])))
    return <double>0

cdef inline double calc_v_a96c8c1bf1b6(Py_ssize_t i, long t) noexcept nogil:
    return <double>(0.0)
    return <double>0

cdef inline double calc_v_a99017c46bdd(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_0c8b1dc7fa99(i, <long>(t))) * (r_v_c13b3576a8a5(i))))
    return <double>0

cdef inline double calc_v_aadb4f6835cd(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_95d087b307fd(i, <long>(t))) * (r_v_bd1626ec57b1(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_b365e04f5e68(Py_ssize_t i, long t) noexcept nogil:
    return <double>(0.0)
    return <double>0

cdef inline double calc_v_b52b6f2be8cb(Py_ssize_t i, long t) noexcept nogil:
    cdef double l_acq = 0.0
    l_acq = (g_52 if (r_v_00cac884b755(i, <long>(t)) == 0) else 0.0)
    if (r_v_2df6bf4c2dbf(i, <long>(t)) == 1):
        l_acq = ((l_acq) + (((g_53) * (r_v_38879954341b(i, <long>(t))))))
    return <double>(((((((l_acq) + (((((<double>(g_54)) / (12))) * (r_v_2abc297880e0(i, <long>(t))))))) * (r_v_085e0f33632c(i, <long>(t))))) + (((g_55) * (r_v_08985c5ea0ac(i, <long>(t)))))))
    return <double>0

cdef inline double calc_v_b6723d12867c(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((r_v_effa5208db32(i, <long>(t))) if (r_v_effa5208db32(i, <long>(t))) >= (((r_v_a86b1946564f(i, <long>(t))) * (((r_v_1d4416fd8dee(i, <long>(t))) if (r_v_1d4416fd8dee(i, <long>(t))) >= (0.0) else (0.0))))) else (((r_v_a86b1946564f(i, <long>(t))) * (((r_v_1d4416fd8dee(i, <long>(t))) if (r_v_1d4416fd8dee(i, <long>(t))) >= (0.0) else (0.0)))))))
    return <double>0

cdef inline double calc_v_b795ac4497e6(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((g_56) * (r_v_6099c329751b(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_b895ae67dd0e(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((((((((0) + (r_v_70732c567ed9(i, <long>(t))))) + (r_v_17309634da2d(i, <long>(t))))) + (r_v_aadb4f6835cd(i, <long>(t))))) + (r_v_d2ae133ffe50(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_bd1626ec57b1(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((((((r_v_085e0f33632c(i, <long>(t))) * (((1) - (r_v_fea9b16c8ae2(i, <long>(t))))))) * (((1) - (r_v_a4ab4b63bd70(i, <long>(t))))))) * (r_v_fcb72235115c(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_c13b3576a8a5(Py_ssize_t i) noexcept nogil:
    return <double>(((pow((((1) + (g_41))), (((<double>(1)) / (12))))) - (1)))
    return <double>0

cdef inline double calc_v_c156869f907a(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_13[i])))
    return <double>0

cdef inline double calc_v_c2957380cf52(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((((r_v_4117b6d32875(i, <long>(t))) - (r_v_70cc01298727(i, <long>(t))))) - (r_v_a96c8c1bf1b6(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_c3970ad2ed18(Py_ssize_t i, long t) noexcept nogil:
    return <double>((<double>(extt1_32[<Py_ssize_t>(((((r_v_2df6bf4c2dbf(i, <long>(t))) if (r_v_2df6bf4c2dbf(i, <long>(t))) <= ((<long>(21))) else ((<long>(21))))) - (1)))])))
    return <double>0

cdef inline double calc_v_c98ef0a4f9f7(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((<double>(r_v_effa5208db32(i, <long>(t)))) / (1000)))
    return <double>0

cdef inline double calc_v_ce40e4c023f2(Py_ssize_t i, long t) noexcept nogil:
    if (r_v_724bf4d7126c(i, <long>(t)) >= 121):
        return <double>(0.0)
    return <double>(((((<double>(r_v_db4c924081fa(i, <long>(t)))) / (1000))) * (r_v_171a7d6038fe(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_d18fe1c6c0b2(Py_ssize_t i, long t) noexcept nogil:
    cdef double l_init = 0.0
    cdef long l_m = 0
    cdef double l_yrs = 0.0
    l_init = (<double>(extt0_30))
    l_yrs = (<double>((<long>(extt0_31))))
    l_m = ((r_v_00cac884b755(i, <long>(t))) + (1))
    return <double>(((0.0) if (0.0) >= (((l_init) - (((((<double>(l_init)) / (l_yrs))) * (((<double>(l_m)) / (12))))))) else (((l_init) - (((((<double>(l_init)) / (l_yrs))) * (((<double>(l_m)) / (12)))))))))
    return <double>0

cdef inline double calc_v_d2ae133ffe50(Py_ssize_t i, long t) noexcept nogil:
    return <double>(0.0)
    return <double>0

cdef inline double calc_v_d412ff51f832(Py_ssize_t i, long t) noexcept nogil:
    if (t == 0):
        return <double>(r_v_96abb0a799c7(i))
    return <double>(((r_v_d412ff51f832(i, <long>(((t) - (1))))) * (((1) + (r_v_f5a256c753a0(i))))))
    return <double>0

cdef inline double calc_v_db4c924081fa(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_dp = 0
    cdef double l_r = 0.0
    l_r = ((g_40) * (r_v_191b62404134(i, <long>(t))))
    l_dp = r_v_1e3dacbf5af4(i)
    return <double>((l_r if (l_dp < 0) else _round_ndigits(<double>(l_r), <long>(l_dp))))
    return <double>0

cdef inline double calc_v_dce87cc64b35(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_48[i])))
    return <double>0

cdef inline bint calc_v_dd7273420244(Py_ssize_t i, long t) noexcept nogil:
    return <bint>((((r_v_1d4416fd8dee(i, <long>(t))) - (r_v_fb63239bcaf4(i, <long>(t)))) < 0))
    return <bint>0

cdef inline double calc_v_e48299ccff7e(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_dp = 0
    cdef double l_r = 0.0
    l_r = ((g_26) * (r_v_191b62404134(i, <long>(t))))
    l_dp = r_v_1e3dacbf5af4(i)
    return <double>((l_r if (l_dp < 0) else _round_ndigits(<double>(l_r), <long>(l_dp))))
    return <double>0

cdef inline double calc_v_e75213b4b943(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((((r_v_085e0f33632c(i, <long>(t))) * (((1) - (r_v_fea9b16c8ae2(i, <long>(t))))))) * (r_v_a4ab4b63bd70(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_effa5208db32(Py_ssize_t i, long t) noexcept nogil:
    return <double>(r_v_2d1a9910c695(i))
    return <double>0

cdef inline long calc_v_f2c754e54e7f(Py_ssize_t i) noexcept nogil:
    return <long>((<long>((<long>(p_1[i])))))
    return <long>0

cdef inline double calc_v_f5a256c753a0(Py_ssize_t i) noexcept nogil:
    return <double>(((pow((((1) + (g_20))), (((<double>(1)) / (12))))) - (1)))
    return <double>0

cdef inline double calc_v_fa50c495e040(Py_ssize_t i, long t) noexcept nogil:
    return <double>(g_28)
    return <double>0

cdef inline double calc_v_fa5111502a7e(Py_ssize_t i, long t) noexcept nogil:
    return <double>(r_v_70cc01298727(i, <long>(t)))
    return <double>0

cdef inline double calc_v_fb63239bcaf4(Py_ssize_t i, long t) noexcept nogil:
    if (r_v_724bf4d7126c(i, <long>(t)) >= 121):
        return <double>(0.0)
    return <double>(((((<double>(r_v_e48299ccff7e(i, <long>(t)))) / (1000))) * (r_v_1ab04f45b315(i, <long>(t)))))
    return <double>0

cdef inline double calc_v_fcb72235115c(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_a = 0
    l_a = r_v_fe375b3640a2(i, <long>(t))
    if (l_a == 0):
        return <double>(0.0)
    return <double>((<double>(extt1_50[<Py_ssize_t>(((((r_v_fe375b3640a2(i, <long>(t))) - (20))) // (5)))])))
    return <double>0

cdef inline double calc_v_fd31871d8b0f(Py_ssize_t i) noexcept nogil:
    return <double>((<double>(p_7[i])))
    return <double>0

cdef inline long calc_v_fe375b3640a2(Py_ssize_t i, long t) noexcept nogil:
    cdef long l_y = 0
    if (not r_v_359543fd71b6(i)):
        return <long>(0)
    if (((r_v_00cac884b755(i, <long>(t))) % (12)) != 0):
        return <long>(0)
    l_y = r_v_6aa454da9c91(i, <long>(t))
    return <long>((l_y if ((r_v_6aa454da9c91(i, <long>(t)) >= 20) and (r_v_6aa454da9c91(i, <long>(t)) <= 25) and (((((r_v_6aa454da9c91(i, <long>(t))) - (20))) % (5)) == 0)) else 0))
    return <long>0

cdef inline double calc_v_fea9b16c8ae2(Py_ssize_t i, long t) noexcept nogil:
    return <double>(((1) - (pow((((1) - (r_v_060e64fce405(i, <long>(t))))), (((<double>(1)) / (12)))))))
    return <double>0

cdef inline double calc_vfix_000934e1c2a7(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_73f6e99b5497(i)) * (((1) - (r_vfix_ba745e290dfe(i))))))
    return <double>0

cdef inline long calc_vfix_02ad5c2dff7c(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_bf659a368d77(i))))
    return <long>0

cdef inline double calc_vfix_036a8d118989(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_acf76d38124c(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_08141bc19b07(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_a18edd0f3620(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_09e365a15f98(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_cf2399a0a151(i)) * (((1) - (r_vfix_8614b9aacc0d(i))))))
    return <double>0

cdef inline double calc_vfix_0bf9ee71b29c(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_6a7af2c18bff(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_0e1d900c527c(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_9841308c8563(i))))
    return <long>0

cdef inline double calc_vfix_0e819a45b6eb(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_f504da450c1d(i)) * (((1) - (r_vfix_cb9b5e20a220(i))))))
    return <double>0

cdef inline long calc_vfix_1238afd514f3(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (217))) - (1)))
    return <long>0

cdef inline double calc_vfix_12a2d3bfcad4(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_5c652e5ab7a4(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_1375ca2ff24a(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_61fb72975655(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_1402f2ba4163(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_a297335abc1c(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_155d3fd2e8ce(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_2cc54a8d599c(i)) * (((1) - (r_vfix_2849619d802e(i))))))
    return <double>0

cdef inline long calc_vfix_1b9f10e43955(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_93667357c3bc(i))))
    return <long>0

cdef inline long calc_vfix_1ced80658ccc(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_2fa2e76b8978(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_207fdffdd3fe(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_9a54f4181258(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_26108814ea96(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (25))) - (1)))
    return <long>0

cdef inline double calc_vfix_280a3f070d21(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_d97e58c6d0f8(i)) * (((1) - (r_vfix_8236fa399c18(i))))))
    return <double>0

cdef inline double calc_vfix_2849619d802e(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_c14aeeb85bdb(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_2bcf3ac2764e(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_1ced80658ccc(i))))
    return <long>0

cdef inline double calc_vfix_2cc54a8d599c(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_000934e1c2a7(i)) * (((1) - (r_vfix_c03239b2eba1(i))))))
    return <double>0

cdef inline long calc_vfix_2f49635ce0b1(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (133))) - (1)))
    return <long>0

cdef inline long calc_vfix_2fa2e76b8978(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (61))) - (1)))
    return <long>0

cdef inline long calc_vfix_3003ca7f580b(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_207fdffdd3fe(i))))
    return <long>0

cdef inline long calc_vfix_307413ed2f05(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (97))) - (1)))
    return <long>0

cdef inline double calc_vfix_4055b5f2f843(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_0e1d900c527c(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_4276e79fee81(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_a27f7cb71328(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_48e4dc6cc1dd(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_81851eaa2459(i)) * (((1) - (r_vfix_f5077eba5f59(i))))))
    return <double>0

cdef inline long calc_vfix_49a4f1e418ec(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_8f90c7a0a87d(i))))
    return <long>0

cdef inline double calc_vfix_4a14a4e02c7e(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_7943f8fdcffd(i)) * (((1) - (r_vfix_5a3e6c518299(i))))))
    return <double>0

cdef inline long calc_vfix_4cba624e9901(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_8e3cb701de4f(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_50f119da80cc(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_c225be4256e2(i)) * (((1) - (r_vfix_f4389f754cf7(i))))))
    return <double>0

cdef inline long calc_vfix_579bea428630(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (13))) - (1)))
    return <long>0

cdef inline long calc_vfix_5a060f81aaec(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_f0f43d2c6e52(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_5a3e6c518299(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_c6e832dece21(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_5c652e5ab7a4(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_d92186d30afa(i))))
    return <long>0

cdef inline long calc_vfix_5c7d1d4a0310(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_a285fad7dca4(i))))
    return <long>0

cdef inline long calc_vfix_6079a228736f(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_80caf7fa2eaf(i))))
    return <long>0

cdef inline long calc_vfix_61fb72975655(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (49))) - (1)))
    return <long>0

cdef inline long calc_vfix_65f7965d708a(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_5a060f81aaec(i))))
    return <long>0

cdef inline long calc_vfix_6a7af2c18bff(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_e745ba4b7bb5(i))))
    return <long>0

cdef inline double calc_vfix_6bec57fc5ce2(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_155d3fd2e8ce(i)) * (((1) - (r_vfix_f338154bfe1b(i))))))
    return <double>0

cdef inline double calc_vfix_725a505857df(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_847f25bca2dd(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_73f6e99b5497(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_85a9416a70b2(i)) * (((1) - (r_vfix_036a8d118989(i))))))
    return <double>0

cdef inline long calc_vfix_75e49f5e80fe(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (205))) - (1)))
    return <long>0

cdef inline double calc_vfix_7943f8fdcffd(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_0e819a45b6eb(i)) * (((1) - (r_vfix_12a2d3bfcad4(i))))))
    return <double>0

cdef inline long calc_vfix_798df74d7f65(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (73))) - (1)))
    return <long>0

cdef inline long calc_vfix_80caf7fa2eaf(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_f087a39edd01(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_81851eaa2459(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_09e365a15f98(i)) * (((1) - (r_vfix_82ebd6be132b(i))))))
    return <double>0

cdef inline double calc_vfix_8236fa399c18(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_84dcf7b82b29(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_82815416a846(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_65f7965d708a(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_82ebd6be132b(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_e7a4d3dea04f(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_836399e3a518(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (109))) - (1)))
    return <long>0

cdef inline long calc_vfix_847f25bca2dd(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_1402f2ba4163(i))))
    return <long>0

cdef inline long calc_vfix_84dcf7b82b29(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_ebe27c05a4a6(i))))
    return <long>0

cdef inline double calc_vfix_85a9416a70b2(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_280a3f070d21(i)) * (((1) - (r_vfix_f79efabae258(i))))))
    return <double>0

cdef inline double calc_vfix_8614b9aacc0d(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_5c7d1d4a0310(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_8c0b3700c3ae(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_1375ca2ff24a(i))))
    return <long>0

cdef inline long calc_vfix_8e3cb701de4f(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (1))) - (1)))
    return <long>0

cdef inline long calc_vfix_8f90c7a0a87d(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_d275406a834b(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_93667357c3bc(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_26108814ea96(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_9841308c8563(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_307413ed2f05(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_9a54f4181258(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (85))) - (1)))
    return <long>0

cdef inline long calc_vfix_a18edd0f3620(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (37))) - (1)))
    return <long>0

cdef inline long calc_vfix_a27f7cb71328(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_4cba624e9901(i))))
    return <long>0

cdef inline long calc_vfix_a285fad7dca4(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_75e49f5e80fe(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_a297335abc1c(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (193))) - (1)))
    return <long>0

cdef inline long calc_vfix_ab2e577e3461(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_836399e3a518(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_acf76d38124c(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_08141bc19b07(i))))
    return <long>0

cdef inline long calc_vfix_ad6e657fe3ab(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (121))) - (1)))
    return <long>0

cdef inline long calc_vfix_aea5ee2f9420(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (145))) - (1)))
    return <long>0

cdef inline long calc_vfix_b27ab65ab233(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_2f49635ce0b1(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_b3b848e2f3c3(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_4a14a4e02c7e(i)) * (((1) - (r_vfix_0bf9ee71b29c(i))))))
    return <double>0

cdef inline long calc_vfix_b72694a8651b(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_ab2e577e3461(i))))
    return <long>0

cdef inline double calc_vfix_ba745e290dfe(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_8c0b3700c3ae(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_bf659a368d77(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_fd84a7f03bb0(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_c03239b2eba1(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_2bcf3ac2764e(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_c14aeeb85bdb(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_f00dbf4525de(i))))
    return <long>0

cdef inline double calc_vfix_c180e3a19160(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_6079a228736f(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_c225be4256e2(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_b3b848e2f3c3(i)) * (((1) - (r_vfix_82815416a846(i))))))
    return <double>0

cdef inline long calc_vfix_c6e832dece21(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_b27ab65ab233(i))))
    return <long>0

cdef inline double calc_vfix_cb9b5e20a220(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_b72694a8651b(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_cf2399a0a151(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_e851948661b4(i)) * (((1) - (r_vfix_725a505857df(i))))))
    return <double>0

cdef inline long calc_vfix_d275406a834b(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (169))) - (1)))
    return <long>0

cdef inline long calc_vfix_d92186d30afa(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_ad6e657fe3ab(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_d97e58c6d0f8(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_e795d3277647(i)) * (((1) - (r_vfix_4276e79fee81(i))))))
    return <double>0

cdef inline long calc_vfix_e6a853e78c8e(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_1238afd514f3(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_e745ba4b7bb5(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_aea5ee2f9420(i)) // (12)))
    return <long>0

cdef inline double calc_vfix_e795d3277647(Py_ssize_t i) noexcept nogil:
    return <double>(1.0)
    return <double>0

cdef inline long calc_vfix_e7a4d3dea04f(Py_ssize_t i) noexcept nogil:
    return <long>(((r_v_f2c754e54e7f(i)) + (r_vfix_e6a853e78c8e(i))))
    return <long>0

cdef inline double calc_vfix_e851948661b4(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_50f119da80cc(i)) * (((1) - (r_vfix_c180e3a19160(i))))))
    return <double>0

cdef inline long calc_vfix_ebe27c05a4a6(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_579bea428630(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_f00dbf4525de(Py_ssize_t i) noexcept nogil:
    return <long>(((r_vfix_798df74d7f65(i)) // (12)))
    return <long>0

cdef inline long calc_vfix_f087a39edd01(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (181))) - (1)))
    return <long>0

cdef inline long calc_vfix_f0f43d2c6e52(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (157))) - (1)))
    return <long>0

cdef inline double calc_vfix_f338154bfe1b(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_3003ca7f580b(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_f4389f754cf7(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_49a4f1e418ec(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_f504da450c1d(Py_ssize_t i) noexcept nogil:
    return <double>(((r_vfix_6bec57fc5ce2(i)) * (((1) - (r_vfix_4055b5f2f843(i))))))
    return <double>0

cdef inline double calc_vfix_f5077eba5f59(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_02ad5c2dff7c(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline double calc_vfix_f79efabae258(Py_ssize_t i) noexcept nogil:
    cdef long l_a = 0
    l_a = r_vfix_1b9f10e43955(i)
    if (l_a <= 85):
        return <double>(g_58)
    if (l_a >= 95):
        return <double>(0.0)
    return <double>(((g_58) * (((<double>((((<long>(g_59))) - (l_a)))) / ((((<long>(g_59))) - ((<long>(g_60)))))))))
    return <double>0

cdef inline long calc_vfix_fd84a7f03bb0(Py_ssize_t i) noexcept nogil:
    return <long>(((((r_v_10910b14fe37(i)) + (229))) - (1)))
    return <long>0

cdef inline long r_v_00cac884b755(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 0 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_00cac884b755(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_060e64fce405(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 1 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_060e64fce405(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_085e0f33632c(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 2 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_085e0f33632c(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_08985c5ea0ac(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 3 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_08985c5ea0ac(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_09790277bb3a(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 4 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_09790277bb3a(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline bint r_v_0a9ae2866144(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 5 * CACHE_WIDTH + pos
    cdef bint val
    if pos < 0 or pos >= CACHE_WIDTH: return <bint>NAN
    if _valid[idx] == _epoch: return <bint>_cache[idx]
    val = calc_v_0a9ae2866144(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_0b4b0c03129b(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 6 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_0b4b0c03129b(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_0c8b1dc7fa99(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 7 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_0c8b1dc7fa99(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_10910b14fe37(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 8 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_10910b14fe37(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_15e799ddf9f3(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 9 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_15e799ddf9f3(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_171a7d6038fe(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 10 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_171a7d6038fe(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_17309634da2d(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 11 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_17309634da2d(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_180fdd694e62(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 12 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_180fdd694e62(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_191b62404134(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 13 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_191b62404134(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_1ab04f45b315(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 14 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_1ab04f45b315(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_1cb225ed960e(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 15 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_1cb225ed960e(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_1d4416fd8dee(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 16 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_1d4416fd8dee(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_1e03e469e091(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 17 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_1e03e469e091(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_1e3dacbf5af4(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 18 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_1e3dacbf5af4(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline bint r_v_1fd042196776(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 19 * CACHE_WIDTH + pos
    cdef bint val
    if pos < 0 or pos >= CACHE_WIDTH: return <bint>NAN
    if _valid[idx] == _epoch: return <bint>_cache[idx]
    val = calc_v_1fd042196776(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_216f150ab78f(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 20 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_216f150ab78f(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_299fafca332f(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 21 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_299fafca332f(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_2abc297880e0(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 22 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_2abc297880e0(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline bint r_v_2b89cb6420d2(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 23 * CACHE_WIDTH + pos
    cdef bint val
    if pos < 0 or pos >= CACHE_WIDTH: return <bint>NAN
    if _valid[idx] == _epoch: return <bint>_cache[idx]
    val = calc_v_2b89cb6420d2(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_2be2509482b8(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 24 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_2be2509482b8(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_2d1a9910c695(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 25 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_2d1a9910c695(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_2df6bf4c2dbf(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 26 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_2df6bf4c2dbf(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline bint r_v_359543fd71b6(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 27 * CACHE_WIDTH + CACHE_OFFSET
    cdef bint val
    if _valid[idx] == _epoch: return <bint>_cache[idx]
    val = calc_v_359543fd71b6(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_38879954341b(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 28 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_38879954341b(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_4117b6d32875(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 29 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_4117b6d32875(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_49d1c13d2698(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 30 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_49d1c13d2698(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_527a4c5d5fed(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 31 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_527a4c5d5fed(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline bint r_v_557c64b0b275(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 32 * CACHE_WIDTH + pos
    cdef bint val
    if pos < 0 or pos >= CACHE_WIDTH: return <bint>NAN
    if _valid[idx] == _epoch: return <bint>_cache[idx]
    val = calc_v_557c64b0b275(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_56238bb95db5(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 33 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_56238bb95db5(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_58cd68bd0f8a(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 34 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_58cd68bd0f8a(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_5c2948769e25(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 35 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_5c2948769e25(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_5d2c15336093(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 36 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_5d2c15336093(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_600d48f86152(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 37 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_600d48f86152(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_602b31c3292a(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 38 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_602b31c3292a(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_6099c329751b(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 39 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_6099c329751b(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_63b0c8fbde95(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 40 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_63b0c8fbde95(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_652a64655085(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 41 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_652a64655085(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_67433777b17b(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 42 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_67433777b17b(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_678a332a77ce(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 43 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_678a332a77ce(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_6aa454da9c91(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 44 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_6aa454da9c91(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_70732c567ed9(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 45 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_70732c567ed9(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_70cc01298727(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 46 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_70cc01298727(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_724bf4d7126c(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 47 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_724bf4d7126c(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_72ddbcded512(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 48 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_72ddbcded512(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_72f40ac54d00(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 49 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_72f40ac54d00(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_761b9f8afdde(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 50 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_761b9f8afdde(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_771ce5c5860b(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 51 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_771ce5c5860b(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7766c1f5ba43(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 52 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7766c1f5ba43(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_79055b2863ce(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 53 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_79055b2863ce(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7922171d762c(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 54 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7922171d762c(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7a217024e68c(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 55 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7a217024e68c(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7bf778bc7964(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 56 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7bf778bc7964(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7c052059790f(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 57 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7c052059790f(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7ec902c106f7(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 58 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7ec902c106f7(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_7f778c30a0bc(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 59 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_7f778c30a0bc(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_826fb7bd4dc7(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 60 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_826fb7bd4dc7(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_828276648c84(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 61 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_828276648c84(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_83672a59fc09(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 62 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_83672a59fc09(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_86f21db6ffbc(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 63 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_86f21db6ffbc(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_912715b3e4c1(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 64 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_912715b3e4c1(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_91991af267ed(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 65 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_91991af267ed(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_93ed088a39d6(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 66 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_93ed088a39d6(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_95d087b307fd(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 67 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_95d087b307fd(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_96abb0a799c7(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 68 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_96abb0a799c7(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_9821f58b3858(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 69 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_9821f58b3858(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_9bc52957e758(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 70 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_9bc52957e758(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_9edbb44d4c06(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 71 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_9edbb44d4c06(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_a03e65d9a726(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 72 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_a03e65d9a726(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_a4ab4b63bd70(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 73 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_a4ab4b63bd70(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_a6ce98136045(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 74 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_a6ce98136045(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_a86b1946564f(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 75 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_a86b1946564f(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_a96c8c1bf1b6(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 76 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_a96c8c1bf1b6(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_a99017c46bdd(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 77 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_a99017c46bdd(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_aadb4f6835cd(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 78 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_aadb4f6835cd(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_b365e04f5e68(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 79 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_b365e04f5e68(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_b52b6f2be8cb(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 80 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_b52b6f2be8cb(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_b6723d12867c(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 81 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_b6723d12867c(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_b795ac4497e6(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 82 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_b795ac4497e6(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_b895ae67dd0e(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 83 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_b895ae67dd0e(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_bd1626ec57b1(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 84 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_bd1626ec57b1(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_c13b3576a8a5(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 85 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_c13b3576a8a5(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_c156869f907a(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 86 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_c156869f907a(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_c2957380cf52(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 87 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_c2957380cf52(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_c3970ad2ed18(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 88 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_c3970ad2ed18(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_c98ef0a4f9f7(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 89 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_c98ef0a4f9f7(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_ce40e4c023f2(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 90 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_ce40e4c023f2(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_d18fe1c6c0b2(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 91 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_d18fe1c6c0b2(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_d2ae133ffe50(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 92 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_d2ae133ffe50(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_d412ff51f832(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 93 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_d412ff51f832(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_db4c924081fa(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 94 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_db4c924081fa(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_dce87cc64b35(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 95 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_dce87cc64b35(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline bint r_v_dd7273420244(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 96 * CACHE_WIDTH + pos
    cdef bint val
    if pos < 0 or pos >= CACHE_WIDTH: return <bint>NAN
    if _valid[idx] == _epoch: return <bint>_cache[idx]
    val = calc_v_dd7273420244(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_e48299ccff7e(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 97 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_e48299ccff7e(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_e75213b4b943(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 98 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_e75213b4b943(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_effa5208db32(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 99 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_effa5208db32(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_f2c754e54e7f(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 100 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_f2c754e54e7f(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_f5a256c753a0(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 101 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_f5a256c753a0(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_fa50c495e040(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 102 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_fa50c495e040(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_fa5111502a7e(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 103 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_fa5111502a7e(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_fb63239bcaf4(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 104 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_fb63239bcaf4(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_fcb72235115c(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 105 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_fcb72235115c(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_fd31871d8b0f(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 106 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_fd31871d8b0f(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_v_fe375b3640a2(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 107 * CACHE_WIDTH + pos
    cdef long val
    if pos < 0 or pos >= CACHE_WIDTH: return <long>NAN
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_v_fe375b3640a2(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_v_fea9b16c8ae2(Py_ssize_t i, long t) noexcept nogil:
    cdef Py_ssize_t pos = <Py_ssize_t>t + CACHE_OFFSET
    cdef Py_ssize_t idx = 108 * CACHE_WIDTH + pos
    cdef double val
    if pos < 0 or pos >= CACHE_WIDTH: return <double>NAN
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_v_fea9b16c8ae2(i, t)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_000934e1c2a7(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 109 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_000934e1c2a7(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_02ad5c2dff7c(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 110 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_02ad5c2dff7c(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_036a8d118989(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 111 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_036a8d118989(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_08141bc19b07(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 112 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_08141bc19b07(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_09e365a15f98(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 113 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_09e365a15f98(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_0bf9ee71b29c(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 114 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_0bf9ee71b29c(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_0e1d900c527c(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 115 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_0e1d900c527c(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_0e819a45b6eb(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 116 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_0e819a45b6eb(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_1238afd514f3(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 117 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_1238afd514f3(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_12a2d3bfcad4(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 118 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_12a2d3bfcad4(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_1375ca2ff24a(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 119 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_1375ca2ff24a(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_1402f2ba4163(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 120 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_1402f2ba4163(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_155d3fd2e8ce(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 121 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_155d3fd2e8ce(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_1b9f10e43955(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 122 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_1b9f10e43955(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_1ced80658ccc(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 123 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_1ced80658ccc(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_207fdffdd3fe(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 124 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_207fdffdd3fe(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_26108814ea96(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 125 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_26108814ea96(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_280a3f070d21(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 126 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_280a3f070d21(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_2849619d802e(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 127 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_2849619d802e(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_2bcf3ac2764e(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 128 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_2bcf3ac2764e(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_2cc54a8d599c(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 129 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_2cc54a8d599c(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_2f49635ce0b1(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 130 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_2f49635ce0b1(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_2fa2e76b8978(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 131 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_2fa2e76b8978(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_3003ca7f580b(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 132 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_3003ca7f580b(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_307413ed2f05(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 133 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_307413ed2f05(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_4055b5f2f843(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 134 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_4055b5f2f843(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_4276e79fee81(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 135 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_4276e79fee81(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_48e4dc6cc1dd(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 136 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_48e4dc6cc1dd(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_49a4f1e418ec(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 137 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_49a4f1e418ec(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_4a14a4e02c7e(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 138 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_4a14a4e02c7e(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_4cba624e9901(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 139 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_4cba624e9901(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_50f119da80cc(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 140 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_50f119da80cc(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_579bea428630(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 141 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_579bea428630(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_5a060f81aaec(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 142 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_5a060f81aaec(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_5a3e6c518299(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 143 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_5a3e6c518299(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_5c652e5ab7a4(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 144 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_5c652e5ab7a4(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_5c7d1d4a0310(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 145 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_5c7d1d4a0310(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_6079a228736f(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 146 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_6079a228736f(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_61fb72975655(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 147 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_61fb72975655(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_65f7965d708a(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 148 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_65f7965d708a(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_6a7af2c18bff(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 149 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_6a7af2c18bff(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_6bec57fc5ce2(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 150 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_6bec57fc5ce2(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_725a505857df(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 151 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_725a505857df(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_73f6e99b5497(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 152 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_73f6e99b5497(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_75e49f5e80fe(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 153 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_75e49f5e80fe(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_7943f8fdcffd(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 154 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_7943f8fdcffd(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_798df74d7f65(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 155 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_798df74d7f65(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_80caf7fa2eaf(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 156 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_80caf7fa2eaf(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_81851eaa2459(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 157 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_81851eaa2459(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_8236fa399c18(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 158 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_8236fa399c18(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_82815416a846(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 159 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_82815416a846(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_82ebd6be132b(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 160 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_82ebd6be132b(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_836399e3a518(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 161 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_836399e3a518(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_847f25bca2dd(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 162 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_847f25bca2dd(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_84dcf7b82b29(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 163 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_84dcf7b82b29(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_85a9416a70b2(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 164 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_85a9416a70b2(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_8614b9aacc0d(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 165 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_8614b9aacc0d(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_8c0b3700c3ae(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 166 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_8c0b3700c3ae(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_8e3cb701de4f(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 167 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_8e3cb701de4f(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_8f90c7a0a87d(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 168 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_8f90c7a0a87d(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_93667357c3bc(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 169 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_93667357c3bc(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_9841308c8563(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 170 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_9841308c8563(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_9a54f4181258(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 171 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_9a54f4181258(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_a18edd0f3620(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 172 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_a18edd0f3620(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_a27f7cb71328(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 173 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_a27f7cb71328(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_a285fad7dca4(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 174 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_a285fad7dca4(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_a297335abc1c(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 175 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_a297335abc1c(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_ab2e577e3461(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 176 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_ab2e577e3461(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_acf76d38124c(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 177 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_acf76d38124c(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_ad6e657fe3ab(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 178 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_ad6e657fe3ab(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_aea5ee2f9420(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 179 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_aea5ee2f9420(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_b27ab65ab233(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 180 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_b27ab65ab233(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_b3b848e2f3c3(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 181 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_b3b848e2f3c3(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_b72694a8651b(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 182 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_b72694a8651b(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_ba745e290dfe(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 183 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_ba745e290dfe(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_bf659a368d77(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 184 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_bf659a368d77(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_c03239b2eba1(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 185 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_c03239b2eba1(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_c14aeeb85bdb(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 186 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_c14aeeb85bdb(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_c180e3a19160(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 187 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_c180e3a19160(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_c225be4256e2(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 188 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_c225be4256e2(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_c6e832dece21(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 189 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_c6e832dece21(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_cb9b5e20a220(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 190 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_cb9b5e20a220(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_cf2399a0a151(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 191 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_cf2399a0a151(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_d275406a834b(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 192 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_d275406a834b(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_d92186d30afa(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 193 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_d92186d30afa(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_d97e58c6d0f8(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 194 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_d97e58c6d0f8(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_e6a853e78c8e(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 195 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_e6a853e78c8e(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_e745ba4b7bb5(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 196 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_e745ba4b7bb5(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_e795d3277647(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 197 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_e795d3277647(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_e7a4d3dea04f(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 198 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_e7a4d3dea04f(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_e851948661b4(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 199 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_e851948661b4(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_ebe27c05a4a6(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 200 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_ebe27c05a4a6(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_f00dbf4525de(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 201 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_f00dbf4525de(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_f087a39edd01(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 202 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_f087a39edd01(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_f0f43d2c6e52(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 203 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_f0f43d2c6e52(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_f338154bfe1b(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 204 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_f338154bfe1b(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_f4389f754cf7(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 205 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_f4389f754cf7(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_f504da450c1d(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 206 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_f504da450c1d(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_f5077eba5f59(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 207 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_f5077eba5f59(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double r_vfix_f79efabae258(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 208 * CACHE_WIDTH + CACHE_OFFSET
    cdef double val
    if _valid[idx] == _epoch: return <double>_cache[idx]
    val = calc_vfix_f79efabae258(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline long r_vfix_fd84a7f03bb0(Py_ssize_t i) noexcept nogil:
    cdef Py_ssize_t idx = 209 * CACHE_WIDTH + CACHE_OFFSET
    cdef long val
    if _valid[idx] == _epoch: return <long>_cache[idx]
    val = calc_vfix_fd84a7f03bb0(i)
    _cache[idx] = <double>val
    _valid[idx] = _epoch
    return val

cdef inline double _eval_one(Py_ssize_t i) noexcept nogil:
    global _epoch
    _epoch += 1
    return <double>r_v_93ed088a39d6(i)

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
