from __future__ import annotations

from pathlib import Path
import importlib.util
import os
import subprocess
import sys
import sysconfig


def _compiler_flags(*, openmp: bool, optimization: str, native_arch: bool):
    """Return conservative platform-specific native build flags.

    Native C -O2 is the default. Prior experiments did not show durable runtime
    gains from higher C optimization levels on these generated kernels, while
    some large sources took materially longer to compile.
    """
    opt = optimization.upper().replace("-", "")
    if opt not in {"O0", "O1", "O2", "O3"}:
        raise ValueError("optimization must be one of O0, O1, O2 or O3")

    if os.name == "nt":
        compile_args = [f"/{opt}"] if opt != "O0" else ["/Od"]
        if openmp:
            compile_args.append("/openmp")
        # MSVC has no direct equivalent of -march=native that is appropriate
        # for portable extension builds.  Deliberately ignore native_arch here.
        link_args: list[str] = []
    else:
        compile_args = [f"-{opt}"]
        if native_arch:
            compile_args.append("-march=native")
        link_args = []
        if openmp:
            compile_args.append("-fopenmp")
            link_args.append("-fopenmp")
    return compile_args, link_args


def build_extension(
    pyx_path,
    module_name,
    build_dir,
    *,
    openmp: bool = True,
    optimization: str = "O2",
    native_arch: bool = True,
    extra_compile=None,
    extra_link=None,
):
    """Build and import a generated Cython extension.

    The helper is intentionally small.  Production packaging should delegate to
    the project's normal build system, but keeping build flags explicit makes
    benchmark/research builds reproducible.
    """
    pyx_path = Path(pyx_path).resolve()
    build_dir = Path(build_dir).resolve()
    build_dir.mkdir(parents=True, exist_ok=True)
    setup = build_dir / "setup_build.py"

    compile_args, link_args = _compiler_flags(
        openmp=openmp, optimization=optimization, native_arch=native_arch
    )
    compile_args += list(extra_compile or [])
    link_args += list(extra_link or [])

    setup.write_text(
        "import sys\n"
        "sys.setrecursionlimit(10000)\n"
        "from setuptools import setup, Extension\n"
        "from Cython.Build import cythonize\n"
        "import numpy as np\n"
        f"ext=Extension({module_name!r}, [{str(pyx_path)!r}], "
        f"include_dirs=[np.get_include()], extra_compile_args={compile_args!r}, "
        f"extra_link_args={link_args!r})\n"
        f"setup(name={module_name!r}, ext_modules=cythonize([ext], "
        "compiler_directives={'language_level': 3}), "
        "script_args=['build_ext','--inplace'], zip_safe=False)\n"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(pyx_path.parent), env.get("PYTHONPATH", "")]
    )
    proc = subprocess.run(
        [sys.executable, str(setup)],
        cwd=build_dir,
        env=env,
        text=True,
        capture_output=True,
    )
    if proc.returncode:
        raise RuntimeError(
            f"extension build failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    suffix = sysconfig.get_config_var("EXT_SUFFIX")
    candidates = list(build_dir.glob(module_name + "*" + suffix))
    if not candidates:
        candidates = list(build_dir.glob(module_name + "*.so"))
    if not candidates:
        raise RuntimeError("built extension not found")

    so_path = candidates[0]
    spec = importlib.util.spec_from_file_location(module_name, so_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, so_path, proc
