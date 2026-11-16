"""Run the synthetic vaccination data product against immutable Blob inputs."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import re
from time import monotonic
from uuid import uuid4

from alphalens.sde_demo import SCHEMAS, analyse


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def encode(data):
    return (json.dumps(data, indent=2) + "\n").encode("utf-8")


def run(input_version, read, write, log=print):
    """Write evidence per attempt; a success manifest is the publication marker."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", input_version):
        raise ValueError("Invalid input version")
    run_id = uuid4().hex
    prefix = f"runs/{run_id}"
    started = monotonic()
    record = {
        "run_id": run_id,
        "input_version": input_version,
        "started_at": utc_now(),
        "source_bytes": 0,
    }
    stage = "download"
    try:
        sources = {}
        for name in SCHEMAS:
            sources[name] = read(f"inputs/{input_version}/{name}")
            record["source_bytes"] += len(sources[name])
        stage = "validation"
        report = analyse(sources)
        stage = "publish"
        report_bytes = encode(report)
        report_path = f"{prefix}/report.json"
        write(report_path, report_bytes)
        record.update(
            status="completed", report=report_path, report_bytes=len(report_bytes),
            report_sha256=sha256(report_bytes).hexdigest(),
            ended_at=utc_now(), elapsed_ms=round((monotonic() - started) * 1000),
        )
        write(f"{prefix}/manifest.json", encode(record))
    except Exception as error:
        rejected = stage == "validation" and isinstance(error, ValueError)
        failure = {
            "run_id": run_id, "input_version": input_version,
            "started_at": record["started_at"], "source_bytes": record["source_bytes"],
            "status": "rejected" if rejected else "failed", "stage": stage,
            "error_type": type(error).__name__, "ended_at": utc_now(),
            "elapsed_ms": round((monotonic() - started) * 1000),
        }
        if rejected:
            failure["detail"] = str(error)
        try:
            write(f"{prefix}/failure.json", encode(failure))
        except Exception as logging_error:
            failure["failure_record_write_error"] = type(logging_error).__name__
        log(json.dumps(failure))
        raise
    log(json.dumps(record))
    return record


def main():
    from azure.identity import ManagedIdentityCredential
    from azure.storage.blob import BlobServiceClient

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-version", default=os.environ.get("SDE_INPUT_VERSION"))
    parser.add_argument("--account-url", default=os.environ.get("SDE_ACCOUNT_URL"))
    parser.add_argument("--container", default=os.environ.get("SDE_CONTAINER", "alphalens"))
    args = parser.parse_args()
    if not args.account_url or not args.input_version:
        parser.error("Set the account URL and input version using flags or environment variables.")

    try:
        with ManagedIdentityCredential() as credential:
            with BlobServiceClient(args.account_url, credential=credential) as service:
                container = service.get_container_client(args.container)
                run(
                    args.input_version,
                    lambda path: container.download_blob(path).readall(),
                    lambda path, data: container.upload_blob(path, data, overwrite=False),
                )
    except Exception:
        # The structured failure record avoids exposing SDK request details in job logs.
        raise SystemExit("Vaccination pipeline failed. Check the job execution logs.") from None


if __name__ == "__main__":
    main()
