import pytest
from alphalens.core import synthetic_case,investigate,report_json

def test_future_case_corrected():
    finding,_=investigate(synthetic_case(True),True)
    assert finding.validity.startswith("FAILED")
    assert finding.original_sharpe>finding.corrected_sharpe

def test_clean_control():
    finding,_=investigate(synthetic_case(False),False)
    assert finding.validity.startswith("PASSED")
    assert finding.original_sharpe==finding.corrected_sharpe

def test_invalid_cost():
    with pytest.raises(ValueError):
        investigate(synthetic_case(),True,-1)

def test_missing_column():
    with pytest.raises(ValueError):
        investigate(synthetic_case().drop(columns="position"),True)
