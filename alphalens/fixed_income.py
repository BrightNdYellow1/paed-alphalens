"""Transparent educational fixed income and macro scenario calculations.

Annual coupon, annual yield compounding, and parallel yield curve shock.
These are illustrative approximations, not a production bond risk engine.
"""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Bond:
    face: float = 1000.0
    coupon_rate: float = 0.04
    years: int = 5
    yield_rate: float = 0.045

def price(bond: Bond, yield_rate: float | None = None) -> float:
    y = bond.yield_rate if yield_rate is None else yield_rate
    if bond.face <= 0 or bond.years < 1 or bond.years > 100:
        raise ValueError("Invalid face value or years")
    if not -0.99 < y <= 2.0 or not 0 <= bond.coupon_rate <= 1:
        raise ValueError("Invalid yield or coupon rate")
    coupon = bond.face * bond.coupon_rate
    return sum((coupon + (bond.face if t == bond.years else 0)) / ((1 + y)**t)
               for t in range(1, bond.years + 1))

def risk_measures(bond: Bond):
    """Macaulay and modified duration plus convexity for annual payments."""
    y = bond.yield_rate
    p = price(bond)
    coupon = bond.face * bond.coupon_rate
    cashflows = [(t, coupon + (bond.face if t == bond.years else 0))
                 for t in range(1, bond.years + 1)]
    macaulay = sum(t * cf / ((1 + y)**t) for t, cf in cashflows) / p
    modified = macaulay / (1 + y)
    convexity = sum(t * (t + 1) * cf / ((1 + y)**(t + 2)) for t, cf in cashflows) / p
    return {"price":p, "macaulay_duration":macaulay,
            "modified_duration":modified, "convexity":convexity}

def rate_shock(bond: Bond, shock_bps: float):
    if not -10000 <= shock_bps <= 10000:
        raise ValueError("Shock outside permitted range")
    dy = shock_bps / 10000
    old = price(bond)
    new = price(bond, bond.yield_rate + dy)
    risk = risk_measures(bond)
    approximation = -risk["modified_duration"] * dy + 0.5 * risk["convexity"] * dy**2
    return {"yield_shock_bps":shock_bps, "price_before":old,
            "price_after":new, "exact_change_pct":100 * (new / old - 1),
            "duration_convexity_approx_pct":100 * approximation,
            "assumptions":"Fixed annual cashflows, parallel yield shock, no default, no trading costs"}
