import pytest
from alphalens.fixed_income import Bond, price, risk_measures, rate_shock

def test_par_bond():
    bond = Bond(face=1000, coupon_rate=0.05, years=5, yield_rate=0.05)
    assert price(bond) == pytest.approx(1000)

def test_rate_up_price_down():
    bond = Bond()
    assert rate_shock(bond, 100)["price_after"] < price(bond)

def test_rate_down_price_up():
    bond = Bond()
    assert rate_shock(bond, -100)["price_after"] > price(bond)

def test_duration_convexity_positive():
    risk = risk_measures(Bond())
    assert risk["modified_duration"] > 0
    assert risk["convexity"] > 0

def test_zero_shock():
    assert rate_shock(Bond(), 0)["exact_change_pct"] == pytest.approx(0)

def test_invalid_bond():
    with pytest.raises(ValueError):
        price(Bond(face=-10))
