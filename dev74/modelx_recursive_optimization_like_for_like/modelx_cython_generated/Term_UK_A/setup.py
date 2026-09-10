import sys
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="Term_UK_A_mxg_778c82b8ac_nomx_cy",
    ext_modules=cythonize([
        "Term_UK_A_mxg_778c82b8ac_nomx_cy/_mx_sys.py",
        "Term_UK_A_mxg_778c82b8ac_nomx_cy/_mx_classes.py"
        ],
        annotate=True
    )
)
