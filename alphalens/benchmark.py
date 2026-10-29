"""Deterministic benchmark of the timing signature heuristic.

This benchmark tests the heuristic on labelled synthetic constructions.
It does not measure real-world accuracy or an LLM's explanation quality.
"""
import numpy as np
from alphalens.core import synthetic_case
from alphalens.agent import run_tools

def evaluate_timing_benchmark(seeds=range(20), threshold=0.95):
    results=[]
    for seed in seeds:
        for flawed in (True,False):
            df=synthetic_case(contaminated=flawed,seed=int(seed))
            finding=run_tools(df,["timing_audit"])["timing_audit"]
            score=finding["same_period_alignment"]
            predicted=score>threshold
            results.append({"seed":int(seed),"known_flaw":flawed,
                            "flagged":bool(predicted),"alignment":score})
    if not results:
        raise ValueError("At least one seed required")
    tp=sum(r["known_flaw"] and r["flagged"] for r in results)
    tn=sum(not r["known_flaw"] and not r["flagged"] for r in results)
    fp=sum(not r["known_flaw"] and r["flagged"] for r in results)
    fn=sum(r["known_flaw"] and not r["flagged"] for r in results)
    return {"cases":len(results),"true_positive":tp,"true_negative":tn,
            "false_positive":fp,"false_negative":fn,
            "accuracy":(tp+tn)/len(results),
            "precision":tp/(tp+fp) if tp+fp else None,
            "recall":tp/(tp+fn) if tp+fn else None,
            "false_positive_rate":fp/(fp+tn) if fp+tn else None,
            "rows":results,
            "limitation":"Labelled synthetic constructions only; no claims of real-market accuracy."}
