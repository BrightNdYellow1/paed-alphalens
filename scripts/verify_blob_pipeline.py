"""Verify AlphaLens batch outputs in an existing private Blob Storage container."""
import argparse
from hashlib import sha256
import json
from uuid import uuid4

from azure.identity import AzureCliCredential
from azure.storage.blob import BlobServiceClient

from alphalens.core import synthetic_case
from alphalens.pipeline import run


def verify(container):
    prefix = f"verification/{uuid4().hex}"

    def write(path, content):
        container.upload_blob(f"{prefix}/{path}", content, overwrite=True)

    def read(path):
        return container.download_blob(f"{prefix}/{path}").readall()

    def verify_completed(raw, manifest):
        batch = manifest["batch"]
        if read(f"{batch}/raw.csv") != raw:
            raise RuntimeError("Raw input did not round-trip")
        if json.loads(read(f"{batch}/manifest.json")) != manifest:
            raise RuntimeError("Persisted manifest differs from the run result")
        for name, checksum in manifest["outputs"].items():
            if sha256(read(f"{batch}/{name}")).hexdigest() != checksum:
                raise RuntimeError(f"Checksum mismatch: {name}")

    valid = synthetic_case().to_csv(index=False).encode()
    completed = run(valid, True, write)
    verify_completed(valid, completed)

    invalid = b"period,market_return,position\n0,0.1,1\n0,0.2,1\n2,0.3,1\n"
    rejected_batch = f"v1/future-aware/{sha256(invalid).hexdigest()}"
    try:
        run(invalid, True, write)
    except ValueError as error:
        if str(error) != "Invalid data order or missing entries":
            raise
        rejection = str(error)
    else:
        raise RuntimeError("Duplicate periods were accepted")

    rejected_prefix = f"{prefix}/{rejected_batch}/"
    rejected_blobs = sorted(container.list_blob_names(name_starts_with=rejected_prefix))
    if rejected_blobs != [f"{rejected_prefix}raw.csv"] or read(f"{rejected_batch}/raw.csv") != invalid:
        raise RuntimeError("Rejected batch must contain only the unchanged raw input")

    corrected = invalid.replace(b"\n0,0.2,1", b"\n1,0.2,1")
    recovered = run(corrected, True, write)
    verify_completed(corrected, recovered)

    return {
        "prefix": prefix,
        "valid_batch": completed,
        "rejected_batch": rejected_batch,
        "rejection": rejection,
        "rejected_outputs": ["raw.csv"],
        "corrected_batch": recovered,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azure-account-url", required=True)
    parser.add_argument("--container", default="alphalens")
    args = parser.parse_args()
    with AzureCliCredential() as credential:
        with BlobServiceClient(args.azure_account_url, credential=credential) as service:
            result = verify(service.get_container_client(args.container))
    result["environment"] = args.azure_account_url
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
