"""Scenario analysis, not a statistical forecast of future macroeconomic outcomes."""
def macro_scenarios(inflation_pct=2.5, policy_rate_pct=4.0, growth_pct=1.5):
    vals=(inflation_pct,policy_rate_pct,growth_pct)
    if any(not isinstance(x,(int,float)) or not -20<=x<=50 for x in vals):
        raise ValueError("Macro inputs must be finite reasonable percentages")
    # Explicit illustrative assumptions, not empirically estimated causal coefficients.
    scenarios=[
        ("Base",0.0,0.0,0.0),
        ("Inflation persistence",1.5,0.75,-0.35),
        ("Disinflation", -1.0,-0.5,0.25),
        ("Growth shock", -0.5,-1.0,-2.0)]
    return {"method":"Transparent deterministic sensitivity scenarios, not forecasts",
       "inputs":{"inflation_pct":inflation_pct,"policy_rate_pct":policy_rate_pct,"growth_pct":growth_pct},
       "scenarios":[{"scenario":name,"inflation_pct":round(inflation_pct+di,2),
                     "policy_rate_pct":round(policy_rate_pct+dr,2),
                     "growth_pct":round(growth_pct+dg,2)}
                    for name,di,dr,dg in scenarios],
       "limitations":"Illustrative directional shocks; assumed changes are not econometrically estimated, probability weighted or investment advice."}
