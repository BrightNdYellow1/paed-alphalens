"""Static checks for the judge facing Streamlit application."""
import ast
from pathlib import Path

def test_app_syntax():
    source=Path("app.py").read_text(encoding="utf-8")
    ast.parse(source)

def test_all_five_research_modules_present():
    source=Path("app.py").read_text(encoding="utf-8")
    for name in ("Research Trial","Nemotron Investigator","Bond Risk","Portfolio Stress","Evidence Benchmark"):
        assert name in source

def test_evidence_limitations_explicit():
    source=Path("app.py").read_text(encoding="utf-8")
    assert "not proof of performance on real historical markets" in source
    assert "Live inference is not yet independently verified" in source
