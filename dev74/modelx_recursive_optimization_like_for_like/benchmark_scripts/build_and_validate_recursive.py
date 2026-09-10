from pathlib import Path
import subprocess, sys, os, json, time, importlib.util
import numpy as np

name=sys.argv[1]
d=Path('/mnt/data/lfl_benchmark/artifacts')/name
src=d/'fast_recursive_full.pyx'
bdir=d/'fast_recursive_build'
bdir.mkdir(exist_ok=True)
(bdir/'fast_recursive_full.pyx').write_text(src.read_text())
setup='''\nfrom setuptools import setup, Extension\nfrom Cython.Build import cythonize\nimport numpy\next=Extension("fast_recursive_full", ["fast_recursive_full.pyx"], include_dirs=[numpy.get_include()], extra_compile_args=["-O2"])\nsetup(ext_modules=cythonize([ext], compiler_directives={"language_level":3}))\n'''
(bdir/'setup.py').write_text(setup)
t0=time.perf_counter()
p=subprocess.run([sys.executable,'setup.py','build_ext','--inplace'],cwd=bdir,capture_output=True,text=True)
build_s=time.perf_counter()-t0
(bdir/'build.stdout').write_text(p.stdout);(bdir/'build.stderr').write_text(p.stderr)
res={'model':name,'build_returncode':p.returncode,'build_s':build_s}
if p.returncode:
 print(json.dumps(res));sys.exit(1)
so=next(bdir.glob('fast_recursive_full*.so'))
spec=importlib.util.spec_from_file_location('fast_recursive_full',so)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
z=np.load(d/'stage_inputs.npz',allow_pickle=False)
m.init_inputs({k:z[k] for k in z.files})
got=np.asarray(m.run_all(),dtype=float);ref=np.load(d/'reference.npy')
res.update({'outputs':got.tolist(),'reference':ref.tolist(),'max_abs':float(np.max(np.abs(got-ref))),'allclose_1e12':bool(np.allclose(got,ref,rtol=1e-12,atol=1e-12)),'checksum':float(got.sum()),'so_bytes':so.stat().st_size})
(d/'fast_recursive_validation.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res))
