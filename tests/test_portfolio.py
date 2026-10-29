import pytest
from alphalens.fixed_income import Bond
from alphalens.portfolio import Holding, portfolio_scenario

def test_zero_shock():
    p=portfolio_scenario([Holding(Bond(),2)],0)
    assert p["pnl"]==pytest.approx(0)

def test_rising_yields_reduce_value():
    p=portfolio_scenario([Holding(Bond(),2),Holding(Bond(years=10),1)],100)
    assert p["pnl"]<0
    assert p["weighted_modified_duration"]>0

def test_more_units_scale_value():
    a=portfolio_scenario([Holding(Bond(),1)],100)
    b=portfolio_scenario([Holding(Bond(),3)],100)
    assert b["pnl"]==pytest.approx(3*a["pnl"])

def test_invalid_holdings():
    with pytest.raises(ValueError):
        portfolio_scenario([],100)
    with pytest.raises(ValueError):
        portfolio_scenario([Holding(Bond(),0)],100)
