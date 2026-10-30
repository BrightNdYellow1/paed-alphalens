import pytest
from alphalens.paper_audit import audit_text

def test_extracts_candidate_claim():
    d=audit_text("Our Sharpe ratio was 3.2. The weather was cold.")
    assert len(d["candidate_claims"])==1
    assert d["candidate_claims"][0]["status"]=="UNVERIFIED"

def test_does_not_invent_validation():
    d=audit_text("Returns increased 12%.")
    assert len(d["candidate_claims"]) == 1
    assert all(r["status"]=="UNVERIFIED" for r in d["candidate_claims"])

def test_reproducible_hash():
    assert audit_text("Predictive alpha of 2%.")["source_sha256"]==audit_text("Predictive alpha of 2%.")["source_sha256"]

def test_invalid_text():
    with pytest.raises(ValueError):
        audit_text("")
