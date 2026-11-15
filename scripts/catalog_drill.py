"""Run a synthetic research catalog drill and assert the expected outcomes."""
import json
from pathlib import Path
import tempfile

from alphalens.catalog import open_catalog
from alphalens.core import synthetic_case
from alphalens.pipeline import InvalidBatch, run_with_catalog


def main():
    output = Path(tempfile.mkdtemp(prefix="run-", dir=Path("catalog-evidence")))
    catalog = output / "catalog.db"

    def write(name, content):
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    for contaminated in (True, True, False):
        raw = synthetic_case(contaminated).to_csv(index=False).encode()
        run_with_catalog(raw, contaminated, write, catalog)

    invalid = b"period,market_return,position\n0,0.1,1\n0,0.2,1\n2,0.3,1\n"
    try:
        run_with_catalog(invalid, True, write, catalog)
    except InvalidBatch as error:
        print(f"Expected rejection: {error}")
    else:
        raise RuntimeError("The invalid batch was accepted")

    with open_catalog(catalog) as connection:
        statuses = dict(connection.execute("SELECT status, COUNT(*) FROM runs GROUP BY status"))
        observations = connection.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        batches = connection.execute("SELECT COUNT(*) FROM batches").fetchone()[0]

    summary = {"runs": statuses, "unique_batches": batches, "observations": observations}
    if summary != {"runs": {"completed": 3, "rejected": 1}, "unique_batches": 2, "observations": 840}:
        raise RuntimeError(f"Unexpected catalog state: {summary}")
    report = json.dumps(summary, indent=2)
    (output / "summary.json").write_text(report + "\n")
    print(report)


if __name__ == "__main__":
    Path("catalog-evidence").mkdir(exist_ok=True)
    main()
