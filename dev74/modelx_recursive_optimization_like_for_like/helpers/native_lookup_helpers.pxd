# cython: language_level=3
# Tiny C-level primitives intended for generated/native code after provider
# normalization.  Exact dense lookups become direct array indexing and do not
# need a helper.  These functions cover predecessor/step search.

cdef inline Py_ssize_t predecessor_index_double(
        const double* keys, Py_ssize_t n, double x) noexcept nogil:
    cdef Py_ssize_t lo = 0
    cdef Py_ssize_t hi = n
    cdef Py_ssize_t mid
    while lo < hi:
        mid = lo + ((hi - lo) >> 1)
        if keys[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo - 1

cdef inline Py_ssize_t predecessor_index_long(
        const long* keys, Py_ssize_t n, long x) noexcept nogil:
    cdef Py_ssize_t lo = 0
    cdef Py_ssize_t hi = n
    cdef Py_ssize_t mid
    while lo < hi:
        mid = lo + ((hi - lo) >> 1)
        if keys[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo - 1
