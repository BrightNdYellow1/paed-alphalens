"""SQLite catalog for AlphaLens datasets, observations and execution attempts."""
from contextlib import closing
from datetime import datetime, timezone
from io import BytesIO
import json
import sqlite3

import pandas as pd


SCHEMA = """
CREATE TABLE IF NOT EXISTS batches (
    batch_id TEXT PRIMARY KEY,
    case_label TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    original_sharpe REAL NOT NULL,
    corrected_sharpe REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS observations (
    batch_id TEXT NOT NULL REFERENCES batches(batch_id),
    period INTEGER NOT NULL,
    market_return REAL NOT NULL,
    position REAL NOT NULL,
    original_equity REAL NOT NULL,
    corrected_equity REAL NOT NULL,
    PRIMARY KEY (batch_id, period)
);
CREATE TABLE IF NOT EXISTS runs (
    run_id INTEGER PRIMARY KEY,
    batch_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'rejected', 'failed')),
    error_type TEXT,
    error_message TEXT
);
"""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def open_catalog(path):
    connection = sqlite3.connect(path, timeout=30)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return closing(connection)


def start_run(connection, batch_id):
    with connection:
        cursor = connection.execute(
            "INSERT INTO runs (batch_id, started_at, status) VALUES (?, ?, 'running')",
            (batch_id, utc_now()),
        )
        return cursor.lastrowid


def finish_run(connection, run_id, status, error_type=None, error_message=None):
    connection.execute(
        "UPDATE runs SET ended_at = ?, status = ?, error_type = ?, error_message = ? WHERE run_id = ?",
        (utc_now(), status, error_type, error_message, run_id),
    )


def load_batch(connection, manifest, outputs):
    evidence = json.loads(outputs["evidence.json"])
    batch = manifest["batch"]
    inserted = connection.execute(
        "INSERT INTO batches VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(batch_id) DO NOTHING",
        (
            batch, evidence["case"], manifest["source_sha256"], manifest["rows"],
            evidence["original_sharpe"], evidence["corrected_sharpe"],
        ),
    )
    if inserted.rowcount == 0:
        return

    curated = pd.read_csv(BytesIO(outputs["curated.csv"]))
    connection.executemany(
        "INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?)",
        ((batch, *row) for row in curated.itertuples(index=False, name=None)),
    )
