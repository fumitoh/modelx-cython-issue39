from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
ext=Extension('sequential',['sequential.pyx'],include_dirs=[numpy.get_include()],extra_compile_args=['-O2'])
setup(ext_modules=cythonize([ext],compiler_directives={'language_level':3}))
