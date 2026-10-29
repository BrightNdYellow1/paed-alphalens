import pytest
from alphalens.macro import macro_scenarios

def test_base_reproduces_inputs():
    b=macro_scenarios(2,4,1)["scenarios"][0]
    assert (b["inflation_pct"],b["policy_rate_pct"],b["growth_pct"])==(2,4,1)

def test_growth_shock():
    s=macro_scenarios()["scenarios"][-1]
    assert s["growth_pct"]<macro_scenarios()["scenarios"][0]["growth_pct"]

def test_forecast_not_claimed():
    assert "not forecasts" in macro_scenarios()["method"]

def test_bounds():
    with pytest.raises(ValueError):
        macro_scenarios(inflation_pct=999)
