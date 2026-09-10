import os
from pathlib import Path
import numpy as np
import pytest
import modelx as mx
from modelx_native import ModelxModelCompiler

ROOT_ENV="LIFELIB_LIBRARIES_ROOT"
root=os.environ.get(ROOT_ENV)
pytestmark=pytest.mark.skipif(not root, reason=f"set {ROOT_ENV} to lifelib/libraries")

@pytest.mark.parametrize("name", ["BasicTerm_S","BasicTerm_SE","BasicTerm_SC"])
def test_live_model_compiles(name):
    m=mx.read_model(Path(root)/"basiclife"/name,name="Test_"+name)
    c=ModelxModelCompiler(m)
    assert c.manifest()["frontend"] == "live-modelx"
    assert set(c.outputs) == {"pv_premiums","pv_claims","pv_expenses","pv_commissions","pv_net_cf"}
    assert c.model_point_count == 10000
    assert c.pass_manifest()

def test_basicterm_se_literal_state_specialization():
    m=mx.read_model(Path(root)/"basiclife"/"BasicTerm_SE",name="Test_SE_Spec")
    c=ModelxModelCompiler(m)
    specs=c.manifest()["specializations"]
    assert any("BEF_MAT" in x for x in specs.values())
    assert any("BEF_DECR" in x for x in specs.values())

def test_basicterm_sc_cross_space_arrays():
    m=mx.read_model(Path(root)/"basiclife"/"BasicTerm_SC",name="Test_SC_Ext")
    c=ModelxModelCompiler(m)
    arrays=set(c.manifest()["external_arrays"])
    assert "data__mort_table_array" in arrays
    assert "data__disc_rate_ann_array" in arrays

def test_live_reference_rebind():
    m=mx.read_model(Path(root)/"basiclife"/"BasicTerm_S",name="Test_Rebind")
    c=ModelxModelCompiler(m)
    before=c.bind_inputs()["ref__disc_rate_ann"].copy()
    m.Projection.disc_rate_ann = m.Projection.disc_rate_ann + 0.001
    after=c.bind_inputs()["ref__disc_rate_ann"]
    assert np.max(np.abs(after-before)) > 0
