import sqlite3

import pytest

from alphalens.core import synthetic_case
from alphalens.pipeline import InvalidBatch, run_with_catalog


def test_rerun_tracks_both_attempts_without_duplicate_observations(tmp_path):
    path = tmp_path / "catalog.db"
    raw = synthetic_case(n=12).to_csv(index=False).encode()
    blobs = {}
    first = run_with_catalog(raw, True, blobs.__setitem__, path)
    second = run_with_catalog(raw, True, blobs.__setitem__, path)

    assert first["batch"] == second["batch"]
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM batches").fetchone() == (1,)
        assert connection.execute("SELECT COUNT(*) FROM observations").fetchone() == (12,)
        assert connection.execute(
            "SELECT status, COUNT(*) FROM runs WHERE ended_at IS NOT NULL GROUP BY status"
        ).fetchall() == [("completed", 2)]


def test_input_rejection_and_storage_failure_have_distinct_run_states(tmp_path):
    path = tmp_path / "catalog.db"
    invalid = b"period,market_return,position\n0,0.1,1\n0,0.2,1\n2,0.3,1\n"
    blobs = {}
    with pytest.raises(InvalidBatch):
        run_with_catalog(invalid, True, blobs.__setitem__, path)
    assert len(blobs) == 1
    assert next(iter(blobs)).endswith("/raw.csv")

    def denied(path, content):
        raise PermissionError("private request details")

    with pytest.raises(PermissionError):
        run_with_catalog(synthetic_case().to_csv(index=False).encode(), True, denied, path)
    with sqlite3.connect(path) as connection:
        assert connection.execute(
            "SELECT status, error_type, error_message FROM runs ORDER BY run_id"
        ).fetchall() == [
            ("rejected", "InvalidBatch", "Invalid data order or missing entries"),
            ("failed", "PermissionError", None),
        ]
        assert connection.execute("SELECT COUNT(*) FROM batches").fetchone() == (0,)
