"""Tiny function-oriented runtime used as the readable/reference executor.

The compiler reads the same source file, so actuarial formulas are never
re-authored in Cython. The decorators are intentionally lightweight.
"""
from __future__ import annotations
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps

_inputs = ContextVar("lifelib_fp_inputs", default=None)
_point = ContextVar("lifelib_fp_point", default=0)
_registered = []


def cell(_fn=None, *, dtype="double"):
    def decorate(fn):
        cache = {}
        @wraps(fn)
        def wrapped(*args):
            key = (_point.get(), args)
            if key not in cache:
                cache[key] = fn(*args)
            return cache[key]
        wrapped._lifelib_cell = True
        wrapped._lifelib_dtype = dtype
        wrapped._cache = cache
        _registered.append(wrapped)
        return wrapped
    return decorate if _fn is None else decorate(_fn)


def clear_caches():
    for fn in _registered:
        fn._cache.clear()


@contextmanager
def use_inputs(inputs, point=0, clear=False):
    if clear:
        clear_caches()
    tok_i = _inputs.set(inputs)
    tok_p = _point.set(point)
    try:
        yield
    finally:
        _point.reset(tok_p)
        _inputs.reset(tok_i)


def input_scalar(name):
    data = _inputs.get()
    if data is None:
        raise RuntimeError("No model inputs are bound")
    return data[name][_point.get()]


def curve1d(name, index):
    data = _inputs.get()
    if data is None:
        raise RuntimeError("No model inputs are bound")
    return data[name][index]


def table2d(name, row, col):
    data = _inputs.get()
    if data is None:
        raise RuntimeError("No model inputs are bound")
    return data[name][row, col]
