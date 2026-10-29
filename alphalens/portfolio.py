"""Deterministic portfolio valuation under an illustrative parallel rate shock."""
from dataclasses import dataclass
from alphalens.fixed_income import Bond, price, risk_measures

@dataclass(frozen=True)
class Holding:
    bond: Bond
    units: float

def portfolio_scenario(holdings: list[Holding], shock_bps: float):
    if not holdings or len(holdings)>100 or any(h.units<=0 for h in holdings):
        raise ValueError("Supply 1 to 100 positive holdings")
    if abs(shock_bps)>500:
        raise ValueError("Shock limited to 500 basis points")
    dy=shock_bps/10000
    rows=[]
    for index,h in enumerate(holdings,1):
        current=price(h.bond)*h.units
        shocked=price(h.bond,h.bond.yield_rate+dy)*h.units
        rows.append({"holding":index,"value_before":current,"value_after":shocked,
                     "pnl":shocked-current,"duration":risk_measures(h.bond)["modified_duration"]})
    total=sum(row["value_before"] for row in rows)
    after=sum(row["value_after"] for row in rows)
    return {"positions":rows,"value_before":total,"value_after":after,
            "pnl":after-total,"change_pct":100*(after/total-1),
            "weighted_modified_duration":sum(r["value_before"]*r["duration"] for r in rows)/total,
            "assumptions":"Parallel deterministic yield shock, no credit, liquidity, default or trading costs"}
