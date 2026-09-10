import sys
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="VA_US_S_mxg_e6aefd4967_nomx_cy",
    ext_modules=cythonize([
        "VA_US_S_mxg_e6aefd4967_nomx_cy/_mx_sys.py",
        "VA_US_S_mxg_e6aefd4967_nomx_cy/_mx_classes.py"
        ],
        annotate=True
    )
)
