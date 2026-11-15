"""Batch ETL for AlphaLens research evidence."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

import numpy as np
import pandas as pd

from alphalens.core import investigate, synthetic_case


class InvalidBatch(ValueError):
    """Input failed schema or data-quality validation."""


def transform(raw, contaminated):
    frame = pd.read_csv(BytesIO(raw))
    columns = ["period", "market_return", "position"]
    if list(frame.columns) != columns or len(frame) < 3:
        raise ValueError("Expected period, market_return, position and at least three rows")
    frame = frame.apply(pd.to_numeric, errors="raise")
    if not np.isfinite(frame.to_numpy()).all():
        raise ValueError("All values must be finite")
    if not np.equal(frame.period, np.floor(frame.period)).all() or (frame.period < 0).any():
        raise ValueError("Periods must be non-negative integers")
    frame = frame.astype({"period": "int64", "market_return": "float64", "position": "float64"})
    finding, equity = investigate(frame, contaminated)
    curated = frame.join(equity)
    return {
        "curated.csv": curated.to_csv(index=False).encode(),
        "evidence.json": json.dumps(asdict(finding), indent=2, allow_nan=False).encode(),
    }, len(frame)


def batch_id(raw, contaminated):
    case = "future-aware" if contaminated else "clean-control"
    return f"v1/{case}/{sha256(raw).hexdigest()}"


def run(raw, contaminated, write):
    batch = batch_id(raw, contaminated)
    write(f"{batch}/raw.csv", raw)
    try:
        outputs, rows = transform(raw, contaminated)
    except ValueError as error:
        raise InvalidBatch(str(error)) from error
    for name, content in outputs.items():
        write(f"{batch}/{name}", content)
    manifest = {
        "batch": batch,
        "schema_version": 1,
        "source_sha256": sha256(raw).hexdigest(),
        "rows": rows,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "outputs": {name: sha256(content).hexdigest() for name, content in outputs.items()},
    }
    write(f"{batch}/manifest.json", json.dumps(manifest, indent=2).encode())
    return manifest



def run_with_catalog(raw, contaminated, write, catalog_path):
    from alphalens.catalog import finish_run, load_batch, open_catalog, start_run

    outputs = {}

    def publish(path, content):
        write(path, content)
        name = path.rsplit("/", 1)[-1]
        if name in {"curated.csv", "evidence.json"}:
            outputs[name] = content

    with open_catalog(catalog_path) as connection:
        run_id = start_run(connection, batch_id(raw, contaminated))
        try:
            manifest = run(raw, contaminated, publish)
            with connection:
                load_batch(connection, manifest, outputs)
                finish_run(connection, run_id, "completed")
        except InvalidBatch as error:
            with connection:
                finish_run(connection, run_id, "rejected", type(error).__name__, str(error))
            raise
        except Exception as error:
            # Remote error strings may contain request details. Store only the type and status.
            status = getattr(error, "status_code", None)
            detail = f"HTTP {status}" if isinstance(status, int) else None
            with connection:
                finish_run(connection, run_id, "failed", type(error).__name__, detail)
            raise

        return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="CSV containing research trial inputs")
    source.add_argument("--synthetic", action="store_true", help="Generate the demo input")
    parser.add_argument("--case", choices=["future-aware", "clean-control"], required=True)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--azure-account-url")
    parser.add_argument("--container", default="alphalens")
    parser.add_argument("--catalog", type=Path, help="Record attempts and curated rows in SQLite")
    args = parser.parse_args()
    contaminated = args.case == "future-aware"
    raw = synthetic_case(contaminated).to_csv(index=False).encode() if args.synthetic else args.input.read_bytes()

    def execute(write):
        if args.catalog:
            return run_with_catalog(raw, contaminated, write, args.catalog)
        return run(raw, contaminated, write)

    if args.azure_account_url:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient

        with DefaultAzureCredential() as credential:
            with BlobServiceClient(args.azure_account_url, credential=credential) as service:
                container = service.get_container_client(args.container)
                manifest = execute(lambda path, data: container.upload_blob(path, data, overwrite=True))
    else:
        def write(path, data):
            target = args.output / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        manifest = execute(write)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
