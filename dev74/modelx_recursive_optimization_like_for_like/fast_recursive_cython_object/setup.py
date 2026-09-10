from setuptools import setup, Extension
from Cython.Build import cythonize
import sys
name=sys.argv[-1] if sys.argv[-1].startswith('MODEL=') else None
if name:
    model=name.split('=',1)[1];sys.argv.pop()
else:
    raise SystemExit('pass MODEL=<name>')
ext=Extension('frcy_'+model,[model+'.pyx'],extra_compile_args=['-O2'])
setup(name='frcy_'+model,ext_modules=cythonize([ext],compiler_directives={'language_level':3},quiet=True))
