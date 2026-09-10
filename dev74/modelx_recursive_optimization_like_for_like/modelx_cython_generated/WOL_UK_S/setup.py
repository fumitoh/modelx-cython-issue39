import sys
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="WOL_UK_S_mxg_96ebab816f_nomx_cy",
    ext_modules=cythonize([
        "WOL_UK_S_mxg_96ebab816f_nomx_cy/_mx_sys.py",
        "WOL_UK_S_mxg_96ebab816f_nomx_cy/_mx_classes.py"
        ],
        annotate=True
    )
)
