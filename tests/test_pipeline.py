import json

import pytest

from alphalens.core import synthetic_case
from alphalens.pipeline import run


def test_pipeline_publishes_evidence_and_manifest_last():
    raw = synthetic_case().to_csv(index=False).encode()
    writes = {}
    manifest = run(raw, True, writes.__setitem__)
    batch = manifest["batch"]

    assert writes[f"{batch}/raw.csv"] == raw
    report = json.loads(writes[f"{batch}/evidence.json"])
    assert report["original_sharpe"] > report["corrected_sharpe"]
    assert list(writes)[-1] == f"{batch}/manifest.json"
    assert manifest["rows"] == 420
    assert run(raw, True, writes.__setitem__)["batch"] == batch
    assert len(writes) == 4


def test_invalid_batch_keeps_raw_without_completion_manifest():
    raw = b"period,market_return,position\n0,0.1,1\n0,0.2,1\n2,0.3,1\n"
    writes = {}
    with pytest.raises(ValueError, match="Invalid data order"):
        run(raw, True, writes.__setitem__)
    assert len(writes) == 1
    assert next(iter(writes)).endswith("/raw.csv")
