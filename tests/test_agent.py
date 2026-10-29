"""Agent planning and deterministic tool tests without a paid API call."""
import pytest
from alphalens.agent import parse_plan, run_tools
from alphalens.core import synthetic_case

def test_valid_tool_plan():
    assert parse_plan('{"tests":["timing_audit","counterfactual"]}') == ["timing_audit","counterfactual"]

def test_unknown_tool_rejected():
    with pytest.raises(ValueError):
        parse_plan('{"tests":["run_arbitrary_code"]}')

def test_no_tool_rejected():
    with pytest.raises(ValueError):
        parse_plan('{"tests":[]}')

def test_timing_signature_withheld_labels():
    flawed=run_tools(synthetic_case(True), ["timing_audit"])
    clean=run_tools(synthetic_case(False), ["timing_audit"])
    assert flawed["timing_audit"]["same_period_alignment"] > 0.95
    assert clean["timing_audit"]["same_period_alignment"] < 0.75

def test_counterfactual_contains_calculated_sharpe():
    result=run_tools(synthetic_case(True), ["counterfactual"])
    assert result["counterfactual"]["original_sharpe"] > result["counterfactual"]["lagged_sharpe"]
