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


def run(raw, contaminated, write):
    source_hash = sha256(raw).hexdigest()
    case = "future-aware" if contaminated else "clean-control"
    batch = f"v1/{case}/{source_hash}"
    write(f"{batch}/raw.csv", raw)
    outputs, rows = transform(raw, contaminated)
    for name, content in outputs.items():
        write(f"{batch}/{name}", content)
    manifest = {
        "batch": batch,
        "schema_version": 1,
        "source_sha256": source_hash,
        "rows": rows,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "outputs": {name: sha256(content).hexdigest() for name, content in outputs.items()},
    }
    write(f"{batch}/manifest.json", json.dumps(manifest, indent=2).encode())
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
    args = parser.parse_args()
    contaminated = args.case == "future-aware"
    raw = synthetic_case(contaminated).to_csv(index=False).encode() if args.synthetic else args.input.read_bytes()

    if args.azure_account_url:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient

        with DefaultAzureCredential() as credential:
            with BlobServiceClient(args.azure_account_url, credential=credential) as service:
                container = service.get_container_client(args.container)
                manifest = run(raw, contaminated, lambda path, data: container.upload_blob(path, data, overwrite=True))
    else:
        def write(path, data):
            target = args.output / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        manifest = run(raw, contaminated, write)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
