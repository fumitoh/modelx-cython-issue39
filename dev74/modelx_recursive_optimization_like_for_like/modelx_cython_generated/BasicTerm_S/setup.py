import sys
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="BasicTerm_S_mxg_f32da97f78_nomx_cy",
    ext_modules=cythonize([
        "BasicTerm_S_mxg_f32da97f78_nomx_cy/_mx_sys.py",
        "BasicTerm_S_mxg_f32da97f78_nomx_cy/_mx_classes.py"
        ],
        annotate=True
    )
)
