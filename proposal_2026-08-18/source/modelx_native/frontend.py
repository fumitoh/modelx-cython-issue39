from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
from dataclasses import dataclass
from types import ModuleType
from typing import Iterable, Any

import numpy as np
import pandas as pd

from .compiler import ModelCompiler, CompileError


class ModelxCompileError(CompileError):
    pass


def _call_name(node: ast.AST) -> str | None:
    return node.func.id if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) else None


def _unwrap_list_generator(node: ast.AST) -> ast.GeneratorExp | None:
    if isinstance(node, ast.GeneratorExp):
        return node
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "list" and len(node.args) == 1 and isinstance(node.args[0], ast.GeneratorExp):
        return node.args[0]
    return None


def _time_vector_spec(fn: ast.FunctionDef) -> tuple[str, ast.AST] | None:
    rets = [n for n in fn.body if isinstance(n, ast.Return)]
    if len(rets) != 1:
        return None
    val = rets[0].value
    if not (
        isinstance(val, ast.Call)
        and isinstance(val.func, ast.Attribute)
        and isinstance(val.func.value, ast.Name)
        and val.func.value.id == "np"
        and val.func.attr == "array"
        and len(val.args) == 1
    ):
        return None
    gen = _unwrap_list_generator(val.args[0])
    if gen is None or len(gen.generators) != 1 or not isinstance(gen.generators[0].target, ast.Name):
        return None
    return gen.generators[0].target.id, gen.elt


def _literal(node: ast.AST):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def _safe_suffix(value: Any) -> str:
    if value is None:
        return "NONE"
    txt = str(value)
    return "".join(ch if ch.isalnum() else "_" for ch in txt).strip("_") or "X"


class _SubstituteNames(ast.NodeTransformer):
    def __init__(self, mapping: dict[str, Any]):
        self.mapping = mapping

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load) and node.id in self.mapping:
            return ast.copy_location(ast.Constant(self.mapping[node.id]), node)
        return node


class _ConstantFolder(ast.NodeTransformer):
    """Small, intentionally conservative constant folder for specialized branches."""

    def visit_If(self, node: ast.If):
        node = self.generic_visit(node)
        try:
            test = ast.literal_eval(node.test)
        except Exception:
            return node
        chosen = node.body if bool(test) else node.orelse
        return chosen

    def visit_Compare(self, node: ast.Compare):
        node = self.generic_visit(node)
        try:
            expr = ast.Expression(body=node)
            val = eval(compile(ast.fix_missing_locations(expr), "<const>", "eval"), {"__builtins__": {}}, {})
            return ast.copy_location(ast.Constant(bool(val)), node)
        except Exception:
            return node


class _LiteralSpecializer:
    """Monomorphize non-time Cell parameters when calls supply literals.

    Example: pols_if_at(t, "BEF_MAT") becomes pols_if_at__BEF_MAT(t).
    The actuarial source remains untouched; specialization exists only in IR.
    """

    def __init__(self, funcs: dict[str, ast.FunctionDef]):
        self.funcs = funcs
        self.variants: dict[tuple[str, tuple[Any, ...]], str] = {}
        self.generated: dict[str, ast.FunctionDef] = {}
        self.queue: list[tuple[str, tuple[Any, ...]]] = []

    def _time_param(self, fn: ast.FunctionDef) -> str | None:
        if fn.args.args and fn.args.args[0].arg in ("t", "i"):
            return fn.args.args[0].arg
        return None

    def variant_name(self, name: str, literals: tuple[Any, ...]) -> str:
        if not literals:
            return name
        return name + "__" + "__".join(_safe_suffix(x) for x in literals)

    def request(self, name: str, literals: tuple[Any, ...]):
        key = (name, literals)
        if key not in self.variants:
            self.variants[key] = self.variant_name(name, literals)
            self.queue.append(key)
        return self.variants[key]

    def _defaults(self, fn: ast.FunctionDef) -> dict[str, Any]:
        args = [a.arg for a in fn.args.args]
        defaults = fn.args.defaults
        out = {}
        if defaults:
            for name, val in zip(args[-len(defaults):], defaults):
                lit = _literal(val)
                if lit is not None or isinstance(val, ast.Constant):
                    out[name] = lit
        return out

    def _rewrite_calls(self, node: ast.AST):
        outer = self
        class Rewriter(ast.NodeTransformer):
            def visit_Call(self, n: ast.Call):
                n = self.generic_visit(n)
                if not isinstance(n.func, ast.Name) or n.func.id not in outer.funcs:
                    return n
                fn = outer.funcs[n.func.id]
                params = [a.arg for a in fn.args.args]
                time_param = outer._time_param(fn)
                start = 1 if time_param else 0
                defaults = outer._defaults(fn)
                aux_values = []
                for pos, pname in enumerate(params[start:], start=start):
                    if pos < len(n.args):
                        lit = _literal(n.args[pos])
                        if lit is None and not isinstance(n.args[pos], ast.Constant):
                            # Dynamic auxiliary parameter is outside current native subset.
                            raise ModelxCompileError(
                                f"{n.func.id}: non-time parameter {pname!r} must be literal for native specialization; got {ast.unparse(n.args[pos])}"
                            )
                        aux_values.append(lit)
                    elif pname in defaults:
                        aux_values.append(defaults[pname])
                    else:
                        raise ModelxCompileError(f"{n.func.id}: missing non-time argument {pname!r}")
                if aux_values:
                    vname = outer.request(n.func.id, tuple(aux_values))
                    new_args = n.args[:start]
                    return ast.copy_location(ast.Call(func=ast.Name(vname, ast.Load()), args=new_args, keywords=[]), n)
                return n
        return Rewriter().visit(node)

    def build(self, roots: Iterable[str]) -> dict[str, ast.FunctionDef]:
        # Seed ordinary zero-param / time-only roots.
        for root in roots:
            if root not in self.funcs:
                raise ModelxCompileError(f"Unknown output Cell {root!r}")
            fn = self.funcs[root]
            params = [a.arg for a in fn.args.args]
            time_param = self._time_param(fn)
            aux = params[1:] if time_param else params
            if aux:
                defaults = self._defaults(fn)
                if all(p in defaults for p in aux):
                    self.request(root, tuple(defaults[p] for p in aux))
                else:
                    raise ModelxCompileError(f"Output {root!r} has required non-time parameters; specify a specialized output")
            else:
                self.request(root, ())

        while self.queue:
            name, literals = self.queue.pop(0)
            fn = copy.deepcopy(self.funcs[name])
            params = [a.arg for a in fn.args.args]
            time_param = self._time_param(fn)
            start = 1 if time_param else 0
            aux_params = params[start:]
            mapping = dict(zip(aux_params, literals))
            if mapping:
                fn = _SubstituteNames(mapping).visit(fn)
                fn = _ConstantFolder().visit(fn)
            fn.name = self.variants[(name, literals)]
            fn.args.args = fn.args.args[:start]
            fn.args.defaults = []
            fn = self._rewrite_calls(fn)
            ast.fix_missing_locations(fn)
            self.generated[fn.name] = fn

        # Closure: request ordinary called functions discovered from generated bodies.
        # _rewrite_calls leaves zero/time-only calls untouched, so collect recursively.
        changed = True
        while changed:
            changed = False
            for fn in list(self.generated.values()):
                for n in ast.walk(fn):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in self.funcs:
                        base = n.func.id
                        bfn = self.funcs[base]
                        params = [a.arg for a in bfn.args.args]
                        time_param = self._time_param(bfn)
                        aux = params[1:] if time_param else params
                        if not aux and base not in self.generated:
                            self.request(base, ())
                            changed = True
            while self.queue:
                name, literals = self.queue.pop(0)
                fn = copy.deepcopy(self.funcs[name])
                params = [a.arg for a in fn.args.args]
                time_param = self._time_param(fn)
                start = 1 if time_param else 0
                aux_params = params[start:]
                mapping = dict(zip(aux_params, literals))
                if mapping:
                    fn = _SubstituteNames(mapping).visit(fn)
                    fn = _ConstantFolder().visit(fn)
                fn.name = self.variants[(name, literals)]
                fn.args.args = fn.args.args[:start]
                fn.args.defaults = []
                fn = self._rewrite_calls(fn)
                ast.fix_missing_locations(fn)
                self.generated[fn.name] = fn
        return self.generated


@dataclass
class ExternalArraySpec:
    key: str
    value_getter: Any
    dtype: str
    ndim: int


class _ModelxExprLowerer(ast.NodeTransformer):
    def __init__(self, frontend: "ModelxModelCompiler", vector_helpers: set[str]):
        self.frontend = frontend
        self.vector_helpers = vector_helpers

    def visit_Name(self, node: ast.Name):
        # Numeric model/space references become literals. Space parameter itself is
        # only legal as an index and is handled by visit_Subscript.
        if isinstance(node.ctx, ast.Load) and node.id in self.frontend.refs:
            v = self.frontend.refs[node.id]
            if isinstance(v, (int, float, np.integer, np.floating, bool)) and node.id != self.frontend.space_param:
                return ast.copy_location(ast.Constant(v.item() if hasattr(v, "item") else v), node)
        return node

    def _external_call_key(self, call: ast.Call) -> str | None:
        if not (isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and not call.args):
            return None
        refname = call.func.value.id
        if refname not in self.frontend.refs:
            return None
        obj = self.frontend.refs[refname]
        # Duck-type modelx Space interface.
        if not hasattr(obj, "cells") or call.func.attr not in obj.cells:
            return None
        key = f"{refname}__{call.func.attr}"
        self.frontend.register_external_cell_array(key, obj.cells[call.func.attr])
        return key

    def visit_Subscript(self, node: ast.Subscript):
        # model_point()["column"] -> one vector input by model point.
        if (
            self.frontend.model_point_cell
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == self.frontend.model_point_cell
            and not node.value.args
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            field = node.slice.value
            key = self.frontend.register_model_point_field(field)
            return ast.copy_location(ast.Call(ast.Name("input_scalar", ast.Load()), [ast.Constant(key)], []), node)

        # External Space cell returning ndarray, e.g. data.age_at_entry()[idx]
        if isinstance(node.value, ast.Call):
            key = self._external_call_key(node.value)
            if key:
                sl = node.slice
                if isinstance(sl, ast.Name) and sl.id == self.frontend.space_param:
                    return ast.copy_location(ast.Call(ast.Name("input_scalar", ast.Load()), [ast.Constant(key)], []), node)
                if isinstance(sl, ast.Tuple) and len(sl.elts) == 2:
                    return ast.copy_location(ast.Call(ast.Name("table2d", ast.Load()), [ast.Constant(key), self.visit(sl.elts[0]), self.visit(sl.elts[1])], []), node)
                return ast.copy_location(ast.Call(ast.Name("curve1d", ast.Load()), [ast.Constant(key), self.visit(sl)], []), node)

        # vector_cell()[t] helper
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            name = node.value.func.id
            if name in self.vector_helpers and not node.value.args and not isinstance(node.slice, ast.Slice):
                return ast.copy_location(ast.Call(ast.Name(name + "__at", ast.Load()), [self.visit(node.slice)], []), node)

        # Direct pandas Series/DataFrame refs.
        if isinstance(node.value, ast.Name) and node.value.id in self.frontend.refs:
            refname = node.value.id
            ref = self.frontend.refs[refname]
            if isinstance(node.slice, ast.Tuple) and len(node.slice.elts) == 2:
                key = self.frontend.register_ref_array(refname, ref)
                return ast.copy_location(ast.Call(ast.Name("table2d", ast.Load()), [ast.Constant(key), self.visit(node.slice.elts[0]), self.visit(node.slice.elts[1])], []), node)
            if isinstance(ref, pd.Series):
                key = self.frontend.register_ref_array(refname, ref)
                return ast.copy_location(ast.Call(ast.Name("curve1d", ast.Load()), [ast.Constant(key), self.visit(node.slice)], []), node)

        # DataFrame column then row: table[col][row] -> dense table[row,col].
        if isinstance(node.value, ast.Subscript) and isinstance(node.value.value, ast.Name):
            refname = node.value.value.id
            if refname in self.frontend.refs and isinstance(self.frontend.refs[refname], pd.DataFrame):
                col = node.value.slice
                if isinstance(col, ast.Call) and isinstance(col.func, ast.Name) and col.func.id == "str" and len(col.args) == 1:
                    col = col.args[0]
                key = self.frontend.register_ref_array(refname, self.frontend.refs[refname])
                return ast.copy_location(ast.Call(ast.Name("table2d", ast.Load()), [ast.Constant(key), self.visit(node.slice), self.visit(col)], []), node)

        return self.generic_visit(node)


class ModelxModelCompiler:
    """Compile a live modelx.Model into a Cython/OpenMP execution backend.

    The compiler consumes the live Model/Space/Cells/Refs objects directly.
    Formula strings are obtained from Cells.formula; numeric data are bound from
    live References. No lifelib folder, exported model or adapted actuarial source
    is required.
    """

    def __init__(self, model, space: str | Any = "Projection", outputs: Iterable[str] | None = None):
        self.model = model
        self.space = self._resolve_space(space)
        self.space_name = getattr(self.space, "fullname", None) or getattr(self.space, "name", str(space))
        self.space_params = tuple(self.space.parameters or ())
        if len(self.space_params) > 1:
            raise ModelxCompileError(
                f"Native model-point vectorization currently supports at most one Space parameter; {self.space_name} has {self.space_params}"
            )
        self.space_param = self.space_params[0] if self.space_params else None
        self.refs = dict(self.space.refs)
        self.raw_sources = {name: str(cell.formula) for name, cell in self.space.cells.items()}
        self.raw_funcs = {name: ast.parse(src).body[0] for name, src in self.raw_sources.items()}
        self.model_point_cell, self.model_point_ref = self._detect_model_point_row_cell()
        self.outputs = list(outputs) if outputs is not None else self._infer_outputs()
        if not self.outputs:
            raise ModelxCompileError("Could not infer numeric output Cells; pass outputs=[...]")

        self.external_specs: dict[str, ExternalArraySpec] = {}
        self.model_point_fields: dict[str, str] = {}
        self.ref_array_keys: set[str] = set()

        specializer = _LiteralSpecializer(self.raw_funcs)
        self.specialized_funcs = specializer.build(self.outputs)
        self.specialization_map = dict(specializer.variants)

        self.vector_specs = {
            name: spec for name, fn in self.specialized_funcs.items() if (spec := _time_vector_spec(fn)) is not None
        }
        self.internal_text = self._build_internal_source()
        self.core = ModelCompiler(text=self.internal_text, source_label=f"modelx:{getattr(model,'name','Model')}:{self.space_name}")
        self.inputs = self.core.inputs

    def _resolve_space(self, space):
        if not isinstance(space, str):
            return space
        obj = self.model
        for part in space.split("."):
            if hasattr(obj, "spaces") and part in obj.spaces:
                obj = obj.spaces[part]
            else:
                obj = getattr(obj, part)
        return obj

    def _detect_model_point_row_cell(self):
        if not self.space_param:
            return None, None
        for name, fn in self.raw_funcs.items():
            if fn.args.args:
                continue
            rets = [n for n in fn.body if isinstance(n, ast.Return)]
            if len(rets) != 1:
                continue
            r = rets[0].value
            if (
                isinstance(r, ast.Subscript)
                and isinstance(r.value, ast.Attribute)
                and r.value.attr == "loc"
                and isinstance(r.value.value, ast.Name)
                and isinstance(r.slice, ast.Name)
                and r.slice.id == self.space_param
                and r.value.value.id in self.refs
                and isinstance(self.refs[r.value.value.id], pd.DataFrame)
            ):
                return name, r.value.value.id
        return None, None

    def _infer_outputs(self):
        preferred = ["pv_premiums", "pv_claims", "pv_expenses", "pv_commissions", "pv_net_cf"]
        out = [n for n in preferred if n in self.raw_funcs and len(self.raw_funcs[n].args.args) == 0]
        if out:
            return out
        return sorted(n for n, fn in self.raw_funcs.items() if n.startswith("pv_") and not fn.args.args)

    def register_model_point_field(self, field: str) -> str:
        if not self.model_point_ref:
            raise ModelxCompileError(f"model_point field {field!r} used but no model-point row Cell was detected")
        df = self.refs[self.model_point_ref]
        if field not in df.columns:
            raise ModelxCompileError(f"{self.model_point_ref} has no field {field!r}")
        key = f"mp__{field}"
        self.model_point_fields[field] = key
        return key

    def register_ref_array(self, refname: str, value) -> str:
        key = f"ref__{refname}"
        self.ref_array_keys.add(refname)
        return key

    def register_external_cell_array(self, key: str, cell):
        if key in self.external_specs:
            return
        def getter(c=cell):
            return c()
        value = np.asarray(getter())
        if value.dtype.kind not in "iufb" or value.ndim not in (1, 2):
            raise ModelxCompileError(f"External Cell {cell} must return numeric 1-D/2-D array, got {value.dtype} shape={value.shape}")
        dtype = "int64" if value.dtype.kind in "iub" else "float64"
        self.external_specs[key] = ExternalArraySpec(key, getter, dtype, value.ndim)

    def _dtype_for_vector(self, values) -> str:
        arr = np.asarray(values)
        if arr.dtype.kind in "iub":
            return "int64"
        if arr.dtype.kind in "fc":
            return "float64"
        raise ModelxCompileError(f"Non-numeric model-point input dtype {arr.dtype}")

    def _dense_series(self, series: pd.Series):
        if isinstance(series.index, pd.MultiIndex):
            if series.index.nlevels != 2:
                raise ModelxCompileError("Only 2-level numeric MultiIndex Series are supported")
            coords = [(int(a), int(b)) for a, b in series.index]
            arr = np.zeros((max(a for a,_ in coords)+1, max(b for _,b in coords)+1), dtype=np.float64)
            for (a,b), v in series.items():
                arr[int(a), int(b)] = float(v)
            return np.ascontiguousarray(arr)
        idx = [int(x) for x in series.index]
        arr = np.zeros(max(idx)+1, dtype=np.float64)
        for x, v in series.items():
            arr[int(x)] = float(v)
        return np.ascontiguousarray(arr)

    def _dense_dataframe(self, df: pd.DataFrame):
        rows = [int(x) for x in df.index]
        cols = [int(x) for x in df.columns]
        arr = np.zeros((max(rows)+1, max(cols)+1), dtype=np.float64)
        for csrc, c in zip(df.columns, cols):
            for r, v in df[csrc].items():
                arr[int(r), int(c)] = float(v)
        return np.ascontiguousarray(arr)

    def _build_internal_source(self):
        lowerer = _ModelxExprLowerer(self, set(self.vector_specs))
        body: list[ast.stmt] = [
            ast.ImportFrom(module="modelx_native.dsl", names=[ast.alias("cell"), ast.alias("input_scalar"), ast.alias("curve1d"), ast.alias("table2d")], level=0)
        ]

        # First transform all formulas so input registrations occur.
        transformed = []
        vector_needed = set()
        for name, fn0 in self.specialized_funcs.items():
            if self.model_point_cell and name == self.model_point_cell:
                continue
            if name in self.vector_specs:
                vector_needed.add(name)
                continue
            fn = copy.deepcopy(fn0)
            fn = self._inline_fixed_time_calls(fn)
            fn = self._normalize_vector_reduction(fn)
            fn.body = [lowerer.visit(copy.deepcopy(st)) for st in fn.body]
            fn = self._strip_docstring(fn)
            fn.decorator_list = [self._cell_decorator(name)]
            # Normalize explicit accumulator loops used by BasicTerm_SC.
            fn = self._normalize_explicit_reduction(fn)
            transformed.append(ast.fix_missing_locations(fn))

        # Vector helpers are lowered into scalar __at(t) Cells.
        vector_fns = []
        for name in vector_needed:
            tname, elt = self.vector_specs[name]
            elt = lowerer.visit(copy.deepcopy(elt))
            class Rename(ast.NodeTransformer):
                def visit_Name(self, n):
                    if n.id == tname:
                        return ast.copy_location(ast.Name("t", n.ctx), n)
                    return n
            elt = Rename().visit(elt)
            vf = ast.FunctionDef(
                name=name+"__at",
                args=ast.arguments(posonlyargs=[], args=[ast.arg("t")], kwonlyargs=[], kw_defaults=[], defaults=[]),
                body=[ast.Return(elt)], decorator_list=[self._cell_decorator(name)]
            )
            ast.fix_missing_locations(vf)
            vector_fns.append(vf)

        # Rewrite calls/slices to vector helper names after variants exist.
        class VecCallRewrite(ast.NodeTransformer):
            def visit_Call(self, n):
                n = self.generic_visit(n)
                if isinstance(n.func, ast.Name) and n.func.id in vector_needed and len(n.args)==1:
                    n.func.id = n.func.id + "__at"
                return n
        transformed = [ast.fix_missing_locations(VecCallRewrite().visit(f)) for f in transformed]

        inputs: dict[str, dict[str, object]] = {}
        if self.model_point_fields:
            df = self.space.refs[self.model_point_ref]
            for field, key in self.model_point_fields.items():
                inputs[key] = {"dtype": self._dtype_for_vector(df[field].to_numpy()), "ndim": 1}
        for refname in sorted(self.ref_array_keys):
            value = self.space.refs[refname]
            key = f"ref__{refname}"
            if isinstance(value, pd.Series):
                nd = 2 if isinstance(value.index, pd.MultiIndex) else 1
            elif isinstance(value, pd.DataFrame):
                nd = 2
            else:
                arr = np.asarray(value); nd = arr.ndim
            inputs[key] = {"dtype": "float64", "ndim": nd}
        for key, spec in self.external_specs.items():
            inputs[key] = {"dtype": spec.dtype, "ndim": spec.ndim}

        # Outputs may have been specialized only if defaults existed. Current test
        # models have ordinary zero-param outputs, so map them directly.
        out_names = []
        for out in self.outputs:
            key = (out, ())
            out_names.append(self.specialization_map.get(key, out))

        body += [
            ast.Assign([ast.Name("INPUTS", ast.Store())], ast.parse(repr(inputs), mode="eval").body),
            ast.Assign([ast.Name("OUTPUTS", ast.Store())], ast.parse(repr(out_names), mode="eval").body),
        ]
        body.extend(transformed)
        body.extend(vector_fns)
        mod = ast.Module(body=body, type_ignores=[])
        ast.fix_missing_locations(mod)
        return ast.unparse(mod) + "\n"



    def _inline_fixed_time_calls(self, fn: ast.FunctionDef):
        frontend = self
        class Inliner(ast.NodeTransformer):
            depth = 0
            def visit_Call(self, n: ast.Call):
                n = self.generic_visit(n)
                if self.depth > 8:
                    return n
                if not (isinstance(n.func, ast.Name) and n.func.id in frontend.specialized_funcs and len(n.args)==1 and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, int)):
                    return n
                target = copy.deepcopy(frontend.specialized_funcs[n.func.id])
                if not target.args.args or target.args.args[0].arg not in ("t", "i"):
                    return n
                tname = target.args.args[0].arg
                target = _SubstituteNames({tname: int(n.args[0].value)}).visit(target)
                target = _ConstantFolder().visit(target)
                if isinstance(target, list):
                    return n
                target = frontend._strip_docstring(target)
                meaningful = target.body
                if len(meaningful)==1 and isinstance(meaningful[0], ast.Return):
                    self.depth += 1
                    value = self.visit(copy.deepcopy(meaningful[0].value))
                    self.depth -= 1
                    return ast.copy_location(value, n)
                return n
        return ast.fix_missing_locations(Inliner().visit(fn))

    def _strip_docstring(self, fn: ast.FunctionDef):
        if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant) and isinstance(fn.body[0].value.value, str):
            fn.body = fn.body[1:]
        return fn

    def _cell_decorator(self, name: str):
        base = name.split("__", 1)[0]
        int_names = {
            "age", "age_at_entry", "duration", "duration_mth", "duration_yr",
            "policy_term", "proj_len", "max_proj_len", "issue_age", "entry_age"
        }
        if base in int_names:
            return ast.Call(ast.Name("cell", ast.Load()), [], [ast.keyword("dtype", ast.Constant("long"))])
        return ast.Name("cell", ast.Load())

    def _normalize_vector_reduction(self, fn: ast.FunctionDef):
        # lifelib BasicTerm form:
        # return sum(list(claims(t) for t in range(proj_len())) * disc_factors()[:proj_len()])
        body = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))]
        if len(body) != 1 or not isinstance(body[0], ast.Return):
            return fn
        ret = body[0].value
        if not (isinstance(ret, ast.Call) and isinstance(ret.func, ast.Name) and ret.func.id == "sum" and len(ret.args)==1):
            return fn
        arg = ret.args[0]
        if not (isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mult)):
            return fn
        for gen_side, vec_side in ((arg.left,arg.right),(arg.right,arg.left)):
            gen = _unwrap_list_generator(gen_side)
            if gen is None or len(gen.generators)!=1 or not isinstance(gen.generators[0].target, ast.Name):
                continue
            if isinstance(vec_side, ast.Subscript) and isinstance(vec_side.value, ast.Call) and isinstance(vec_side.value.func, ast.Name):
                helper = vec_side.value.func.id
                if helper in self.vector_specs:
                    tname = gen.generators[0].target.id
                    new_elt = ast.BinOp(
                        left=gen.elt, op=ast.Mult(),
                        right=ast.Call(ast.Name(helper+"__at", ast.Load()), [ast.Name(tname, ast.Load())], [])
                    )
                    fn.body = [ast.Return(ast.Call(ast.Name("sum", ast.Load()), [ast.GeneratorExp(new_elt, copy.deepcopy(gen.generators))], []))]
                    return ast.fix_missing_locations(fn)
        return fn

    def _normalize_explicit_reduction(self, fn: ast.FunctionDef):
        # Canonicalize: x=0; for t in range(...): x += EXPR; return x
        meaningful = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))]
        if len(meaningful) == 3 and isinstance(meaningful[0], ast.Assign) and isinstance(meaningful[1], ast.For) and isinstance(meaningful[2], ast.Return):
            a, loop, ret = meaningful
            if len(a.targets)==1 and isinstance(a.targets[0], ast.Name) and isinstance(ret.value, ast.Name) and ret.value.id == a.targets[0].id:
                acc = a.targets[0].id
                if len(loop.body)==1 and isinstance(loop.body[0], ast.AugAssign) and isinstance(loop.body[0].target, ast.Name) and loop.body[0].target.id==acc and isinstance(loop.body[0].op, ast.Add):
                    gen = ast.GeneratorExp(elt=loop.body[0].value, generators=[ast.comprehension(target=loop.target, iter=loop.iter, ifs=[], is_async=0)])
                    fn.body = [ast.Return(ast.Call(ast.Name("sum", ast.Load()), [gen], []))]
        return fn

    @property
    def model_point_count(self) -> int:
        if self.model_point_ref:
            return len(self.space.refs[self.model_point_ref])
        sizes = []
        for spec in self.external_specs.values():
            arr = np.asarray(spec.value_getter())
            if arr.ndim == 1:
                sizes.append(arr.shape[0])
        if not sizes:
            raise ModelxCompileError("Could not infer model-point count from live model")
        return max(sizes)

    def bind_inputs(self, limit: int | None = None) -> dict[str, np.ndarray]:
        out: dict[str, np.ndarray] = {}
        if self.model_point_fields:
            df = self.space.refs[self.model_point_ref]
            for field, key in self.model_point_fields.items():
                dt = np.int64 if self.core.inputs[key]["dtype"] == "int64" else np.float64
                out[key] = np.ascontiguousarray(df[field].to_numpy(dtype=dt))
        for refname in self.ref_array_keys:
            value = self.space.refs[refname]
            key = f"ref__{refname}"
            if isinstance(value, pd.Series):
                out[key] = self._dense_series(value)
            elif isinstance(value, pd.DataFrame):
                out[key] = self._dense_dataframe(value)
            else:
                out[key] = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
        for key, spec in self.external_specs.items():
            arr = np.asarray(spec.value_getter())
            dt = np.int64 if spec.dtype == "int64" else np.float64
            out[key] = np.ascontiguousarray(arr, dtype=dt)
        if limit is not None:
            n = self.model_point_count
            limit = min(int(limit), n)
            for key, arr in list(out.items()):
                if arr.ndim == 1 and arr.shape[0] == n:
                    out[key] = np.ascontiguousarray(arr[:limit])
        return out

    def pass_manifest(self):
        return self.core.pass_manifest()

    def manifest(self):
        m = self.core.manifest()
        m.update({
            "frontend": "live-modelx",
            "model_name": getattr(self.model, "name", None),
            "space": self.space_name,
            "space_parameters": list(self.space_params),
            "source_kind": "Cells.formula",
            "formula_sha256": {
                n: hashlib.sha256(src.encode()).hexdigest() for n, src in self.raw_sources.items() if n in self.raw_sources
            },
            "model_point_cell": self.model_point_cell,
            "model_point_reference": self.model_point_ref,
            "specializations": {f"{n}{args}": v for (n,args),v in self.specialization_map.items() if args},
            "external_arrays": sorted(self.external_specs),
        })
        return m

    def explain(self, name: str):
        # Original modelx source remains the explanation surface.
        base = name.split("__", 1)[0]
        lowered = name
        if name in self.vector_specs:
            lowered = name + "__at"
        if lowered in self.core.formulas:
            info = self.core.explain(lowered)
        elif name in self.core.formulas:
            info = self.core.explain(name)
        else:
            # find specialization
            candidates = [v for (n,_),v in self.specialization_map.items() if n==name]
            if len(candidates)==1 and candidates[0] in self.core.formulas:
                info = self.core.explain(candidates[0])
            else:
                raise KeyError(name)
        if base in self.raw_sources:
            info["source"] = self.raw_sources[base]
            info["source_origin"] = f"{self.space_name}.{base}.formula"
        return info

    def generate_cython(self, path, module_name="modelx_compiled"):
        return self.core.generate_cython(path, module_name=module_name)

    def write_manifest(self, path):
        with open(path, "w") as f:
            json.dump(self.manifest(), f, indent=2)

    def make_reference_module(self, name="_modelx_lowered_reference") -> ModuleType:
        mod = ModuleType(name)
        exec(compile(self.internal_text, f"modelx:{self.space_name}", "exec"), mod.__dict__)
        return mod
