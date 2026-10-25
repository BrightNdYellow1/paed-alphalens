"""Reproducible synthetic look-ahead bias demonstration."""
from dataclasses import dataclass, asdict
import hashlib
import json
import numpy as np
import pandas as pd

@dataclass
class Finding:
    case: str
    validity: str
    original_sharpe: float
    corrected_sharpe: float
    dataset_sha256: str
    explanation: str

def sharpe(r):
    std = r.std(ddof=1)
    return float(np.sqrt(252)*r.mean()/std) if len(r)>2 and std>0 else 0.0

def synthetic_case(contaminated=True, seed=17, n=420):
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.00015, 0.012, n)
    # An illegal position uses the return it is supposed to predict.
    if contaminated:
        positions = np.sign(returns)
    else:
        positions = np.concatenate(([0.], np.sign(returns[:-1])))
    return pd.DataFrame({"period":range(n),"market_return":returns,"position":positions})

def investigate(df, contaminated, cost_bps=1.0):
    required={"period","market_return","position"}
    if not required.issubset(df):
        raise ValueError("Missing required columns")
    if df.isna().any().any() or not df.period.is_monotonic_increasing or df.period.duplicated().any():
        raise ValueError("Invalid data order or missing entries")
    if (df.position.abs()>1).any() or cost_bps<0:
        raise ValueError("Invalid position or cost")
    pos=df.position.astype(float)
    corrected_pos=pos.shift(1).fillna(0) if contaminated else pos
    def returns_for(p):
        turnover=p.diff().abs().fillna(p.abs())
        return p*df.market_return-turnover*cost_bps/10000
    raw=returns_for(pos)
    corrected=returns_for(corrected_pos)
    chart=pd.DataFrame({"original":(1+raw).cumprod(),"corrected":(1+corrected).cumprod()})
    label="FAILED: signal uses same-period future return" if contaminated else "PASSED: known past-only construction"
    explanation=("The synthetic input was constructed with future information; delaying the signal removes that particular timing violation."
                 if contaminated else "The synthetic control was constructed with past information. It is not proof of overall profitability.")
    finding=Finding("future-aware" if contaminated else "clean control",label,
                    sharpe(raw),sharpe(corrected),
                    hashlib.sha256(df.to_csv(index=False).encode()).hexdigest(),explanation)
    return finding,chart

def report_json(finding):
    return json.dumps(asdict(finding),indent=2)
