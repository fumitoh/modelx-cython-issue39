from __future__ import annotations

import argparse
import logging
import pathlib

import modelx as mx

from .api import translate_model, compile_export


def _parse_log_level(value):
    if isinstance(value, int):
        return value
    text = str(value).upper()
    if text.isdigit():
        return int(text)
    level = getattr(logging, text, None)
    if not isinstance(level, int):
        raise argparse.ArgumentTypeError(f"invalid log level: {value}")
    return level


def main(argv=None):
    p = argparse.ArgumentParser(
        description=(
            "Translate a saved modelx model into an exported Python package "
            "with semantic Cython/OpenMP acceleration."
        )
    )
    p.add_argument(
        "model_path",
        help=(
            "Path to a saved modelx model. Unlike mx2cy, which receives an "
            "already exported package, the prototype re-opens the model so "
            "semantic Cell dependencies remain available."
        ),
    )
    p.add_argument("--output", default="", help="Output package path (default: <model>_native)")
    p.add_argument("--space", default="Projection")
    p.add_argument(
        "--sample",
        default="sample.py",
        help="mx2cy-compatible sample workload used to select hot public Cells (default: sample.py)",
    )
    spec = p.add_mutually_exclusive_group()
    spec.add_argument("--spec", default="spec.py", help="mx2cy-compatible spec file (default: spec.py)")
    spec.add_argument("--no-spec", action="store_true", help="Skip the spec file")
    p.add_argument(
        "--setup",
        default="",
        help="Path for the generated setuptools build script (mirrors mx2cy --setup)",
    )
    task = p.add_mutually_exclusive_group()
    task.add_argument("--translate-only", action="store_true")
    task.add_argument("--compile-only", action="store_true")
    p.add_argument("--threads", type=int, default=0, help="Default OpenMP thread count; 0 = automatic")
    p.add_argument("--no-openmp", action="store_true")
    p.add_argument("--no-native-arch", action="store_true")
    p.add_argument("--log-level", default=logging.WARNING, type=_parse_log_level)
    args = p.parse_args(argv)

    logging.basicConfig(level=args.log_level)

    model_path = pathlib.Path(args.model_path).resolve()
    out = pathlib.Path(args.output).resolve() if args.output else model_path.with_name(model_path.name + "_native")
    setup_path = pathlib.Path(args.setup).resolve() if args.setup else None

    if args.compile_only:
        compile_export(out, setup=setup_path)
        return 0

    model = mx.read_model(model_path)
    sample = None if not pathlib.Path(args.sample).exists() else args.sample
    spec_path = None if args.no_spec else args.spec
    if spec_path is not None and not pathlib.Path(spec_path).exists():
        raise FileNotFoundError(f"Spec file {spec_path!r} not found; use --no-spec to skip it")

    result = translate_model(
        model,
        out,
        space=args.space,
        sample=sample,
        spec=spec_path,
        no_spec=args.no_spec,
        native_arch=not args.no_native_arch,
        openmp=not args.no_openmp,
        threads=args.threads,
        setup=setup_path,
    )
    if not args.translate_only:
        result.compilation_seconds = compile_export(out, setup=setup_path)
        result.compiled = True
    print(result.as_dict())
    return 0


def entry_point_main():
    raise SystemExit(main())


if __name__ == "__main__":
    entry_point_main()
