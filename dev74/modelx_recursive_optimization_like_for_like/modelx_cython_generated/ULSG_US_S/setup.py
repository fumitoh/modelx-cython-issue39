import sys
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="ULSG_US_S_mxg_82773408d0_nomx_cy",
    ext_modules=cythonize([
        "ULSG_US_S_mxg_82773408d0_nomx_cy/_mx_sys.py",
        "ULSG_US_S_mxg_82773408d0_nomx_cy/_mx_classes.py"
        ],
        annotate=True
    )
)
