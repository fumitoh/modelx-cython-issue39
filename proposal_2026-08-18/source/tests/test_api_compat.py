import json
import os
from pathlib import Path

import modelx as mx
import pytest

from modelx_native import infer_outputs_from_sample, translate_model


def test_sample_selects_hot_zero_arg_cells(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "m.Projection[1].pv_net_cf()\n"
        "m.Projection[1].age(0)\n"
        "m.Projection[1].pv_net_cf()\n",
        encoding="utf-8",
    )
    got = infer_outputs_from_sample(sample, {"pv_net_cf", "age", "pv_claims"})
    assert got == ["pv_net_cf"]


@pytest.mark.skipif(not os.environ.get("LIFELIB_LIBRARIES_ROOT"), reason="set LIFELIB_LIBRARIES_ROOT")
def test_translate_keeps_modelx_export_shell_and_mx2cy_style_files(tmp_path):
    root = Path(os.environ["LIFELIB_LIBRARIES_ROOT"])
    model = mx.read_model(root / "basiclife" / "BasicTerm_S", name="APICompatBasicTerm")
    sample = tmp_path / "sample.py"
    sample.write_text("m.Projection[1].pv_net_cf()\n", encoding="utf-8")
    setup = tmp_path / "setup_semantic.py"
    out = tmp_path / "APICompatBasicTerm_native"

    result = translate_model(
        model,
        out,
        sample=sample,
        spec={"cells_param_size": {"t": 241}},
        setup=setup,
        backup=False,
    )

    assert result.outputs == ["pv_net_cf"]
    assert (out / "__init__.py").exists()
    assert (out / "_mx_native.py").exists()
    assert (out / "_mx_native_ext.pyx").exists()
    assert setup.exists()

    manifest = json.loads((out / "_mx_native_manifest.json").read_text(encoding="utf-8"))
    assert manifest["api"] == "modelx-export-compatible"
    assert manifest["fallback"] == "modelx-exported-python"
    assert manifest["sample_selected_outputs"] == ["pv_net_cf"]
    assert manifest["spec"]["cells_param_size"]["t"] == 241
    assert manifest["setup_file"] == str(setup.resolve())
    init_text = (out / "__init__.py").read_text(encoding="utf-8")
    assert "modelx-native semantic accelerator" in init_text
