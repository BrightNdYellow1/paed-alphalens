from hashlib import sha256
import json
from pathlib import Path

import pytest

from alphalens.sde_demo import SCHEMAS
from alphalens.sde_job import run


def test_failed_feed_preserves_success_and_corrected_version_recovers():
    root = Path(__file__).resolve().parents[1] / "sde-lab" / "fixtures"
    inputs = {
        f"inputs/{version}/{name}": (root / name).read_bytes()
        for version in ("valid", "duplicate", "corrected") for name in SCHEMAS
    }
    inputs["inputs/duplicate/cohort.csv"] += b"S01,Fictional South\n"
    blobs = {}
    logs = []

    first = run("valid", inputs.__getitem__, blobs.__setitem__, logs.append)
    successful_output = dict(blobs)
    with pytest.raises(ValueError, match="one valid row"):
        run("duplicate", inputs.__getitem__, blobs.__setitem__, logs.append)

    rejection = json.loads(logs[-1])
    rejected_prefix = f"runs/{rejection['run_id']}"
    assert rejection["status"] == "rejected"
    assert rejection["stage"] == "validation"
    assert set(blobs) - set(successful_output) == {f"{rejected_prefix}/failure.json"}
    assert {name: blobs[name] for name in successful_output} == successful_output

    corrected = run("corrected", inputs.__getitem__, blobs.__setitem__, logs.append)
    assert corrected["status"] == "completed"
    assert corrected["run_id"] != first["run_id"]
    assert blobs[corrected["report"]] == blobs[first["report"]]
    assert sha256(blobs[corrected["report"]]).hexdigest() == corrected["report_sha256"]


def test_publication_failure_does_not_create_success_manifest():
    root = Path(__file__).resolve().parents[1] / "sde-lab" / "fixtures"
    blobs = {}
    logs = []

    def write(path, data):
        if path.endswith("manifest.json"):
            raise PermissionError("private details")
        blobs[path] = data

    with pytest.raises(PermissionError):
        run("valid", lambda path: (root / path.rsplit("/", 1)[-1]).read_bytes(), write, logs.append)
    failure = json.loads(logs[-1])
    assert failure["status"] == "failed"
    assert failure["stage"] == "publish"
    assert "private details" not in logs[-1]
    assert not any(path.endswith("manifest.json") for path in blobs)
