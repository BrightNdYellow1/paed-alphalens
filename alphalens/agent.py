"""Nebius Nemotron guided investigation with allowlisted deterministic research tools."""
import json
import os
import re
import numpy as np
import pandas as pd
from openai import OpenAI
from alphalens.core import sharpe

TOOLS = {
    "timing_audit": "Compare documented signal availability with the return interval.",
    "performance_audit": "Calculate the Sharpe ratio and transaction cost adjusted return.",
    "counterfactual": "Shift execution by one period and compare measured outcomes.",
}
MODEL = os.getenv("NEBIUS_MODEL", "nvidia/nemotron-3-super-120b-a12b")
ENDPOINT = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.us-central1.nebius.com/v1/")

def parse_plan(text):
    """Validate a model proposed investigation plan without executing generated code."""
    found = re.search(r"\{.*\}", text or "", flags=re.S)
    if not found:
        raise ValueError("Model did not return a JSON investigation plan")
    plan = json.loads(found.group())
    selected = plan.get("tests", [])
    if not isinstance(selected, list) or not selected or len(selected) > 3:
        raise ValueError("Invalid tool selection")
    if any(test not in TOOLS for test in selected):
        raise ValueError("Unapproved tool requested")
    return list(dict.fromkeys(selected))

def run_tools(df, selected, cost_bps=1.0):
    """Run bounded deterministic checks. Never execute LLM generated Python."""
    from alphalens.core import investigate
    if cost_bps < 0:
        raise ValueError("Costs must be nonnegative")
    evidence = {}
    p = df["position"].astype(float).to_numpy()
    r = df["market_return"].astype(float).to_numpy()
    if "timing_audit" in selected:
        same = float(np.mean((p == np.sign(r)) & (p != 0)))
        lag = float(np.mean(p[1:] == np.sign(r[:-1]))) if len(p)>1 else 0.0
        evidence["timing_audit"] = {"same_period_alignment":round(same,4),
                                  "past_period_alignment":round(lag,4),
                                  "assessment":"Suspicious same period return alignment" if same>0.95 else "No deterministic same period signature detected",
                                  "caveat":"Statistical alignment alone cannot prove actual publication and execution timestamps."}
    if "performance_audit" in selected:
        returns = p*r - np.abs(np.diff(np.r_[0,p]))*cost_bps/10000
        evidence["performance_audit"] = {"sharpe":round(sharpe(pd.Series(returns)),4),
                                         "total_return_pct":round(float(((1+returns).prod()-1)*100),4)}
    if "counterfactual" in selected:
        delayed = np.r_[0,p[:-1]]
        a = p*r - np.abs(np.diff(np.r_[0,p]))*cost_bps/10000
        b = delayed*r - np.abs(np.diff(np.r_[0,delayed]))*cost_bps/10000
        evidence["counterfactual"] = {"original_sharpe":round(sharpe(pd.Series(a)),4),
                                       "lagged_sharpe":round(sharpe(pd.Series(b)),4),
                                       "note":"Lagged execution is a diagnostic counterfactual, not proof of a feasible trading implementation."}
    return evidence

def client_from_key(key=None):
    token = key or os.getenv("NEBIUS_API_KEY")
    if not token:
        raise RuntimeError("NEBIUS_API_KEY is missing. Configure it as a private secret.")
    return OpenAI(api_key=token, base_url=ENDPOINT, timeout=35.0, max_retries=1)

def investigate_with_agent(df, question, cost_bps=1.0, key=None):
    """Two model calls around deterministic Python tools; no hidden ground truth provided."""
    if not set(["market_return","position"]).issubset(df.columns) or df.isna().any().any():
        raise ValueError("Invalid dataset")
    if not 30 <= len(df) <= 10000 or (df["position"].abs()>1).any():
        raise ValueError("Dataset must have 30 to 10000 observations and bounded positions")
    client = client_from_key(key)
    first = client.chat.completions.create(
        model=MODEL, temperature=0, max_tokens=450,
        messages=[
            {"role":"system","content":"You are a cautious quantitative research auditor. Choose one to three tools from timing_audit, performance_audit, counterfactual. Return ONLY JSON like {\"tests\":[\"timing_audit\",\"counterfactual\"]}. Never claim a strategy is profitable."},
            {"role":"user","content":f"Research question: {question}\nRows: {len(df)}. Fields: {list(df.columns)}. Available tools: {json.dumps(TOOLS)}"}
        ])
    selected = parse_plan(first.choices[0].message.content)
    evidence = run_tools(df,selected,cost_bps)
    second = client.chat.completions.create(
        model=MODEL,temperature=0,max_tokens=700,
        messages=[
            {"role":"system","content":"You are a skeptical quantitative research analyst. Interpret ONLY supplied numeric evidence, identify uncertainty, never invent statistics, and do not equate alignment with definitive time leakage. Explain for both beginner and quant audiences, 250 words maximum."},
            {"role":"user","content":json.dumps({"question":question,"tests":evidence,"limitations":"Synthetic sample. No verified market timestamps or executable prices. No known case labels passed to the model."})}
        ])
    return {"model":MODEL,"selected_tests":selected,"evidence":evidence,"interpretation":second.choices[0].message.content,
            "status":"Live model call completed","note":"Unverified explanations should be cross checked with deterministic evidence."}
