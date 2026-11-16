"""Generate SSAS deployment and processing commands for the synthetic lab."""
import argparse
import json
from pathlib import Path


def table(name, columns, measures=()):
    return {
        "name": name,
        "columns": [
            {"name": column, "sourceColumn": column, "dataType": data_type}
            for column, data_type in columns
        ],
        "measures": [
            {"name": measure, "expression": expression}
            for measure, expression in measures
        ],
        "partitions": [{
            "name": name,
            "mode": "import",
            "source": {
                "type": "query",
                "dataSource": "AlphaLensWarehouse",
                "query": f"SELECT {', '.join(column for column, _ in columns)} FROM dbo.[{name}]",
            },
        }],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sql-server", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if any(marker in args.sql_server for marker in ';="\r\n'):
        parser.error("Supply a SQL Server host or instance name.")
    database = "AlphaLensWarehouseTabularLab"
    model = {
        "name": "Model",
        "culture": "en-GB",
        "dataSources": [{
            "type": "provider",
            "name": "AlphaLensWarehouse",
            "connectionString": (
                f"Provider=MSOLEDBSQL;Data Source={args.sql_server};"
                "Initial Catalog=AlphaLensWarehouseLab;Integrated Security=SSPI;"
            ),
            "impersonationMode": "impersonateServiceAccount",
        }],
        "tables": [
            table("Batch", [("batch_id", "string"), ("case_label", "string"), ("row_count", "int64")],
                  [("Published Batches", "DISTINCTCOUNT(Batch[batch_id])")]),
            table("Observation", [("batch_id", "string"), ("period", "int64"), ("market_return", "double")],
                  [("Published Observations", "COUNTROWS(Observation)")]),
            table("LoadStatus", [("attempt_id", "int64"), ("status", "string")],
                  [("Rejected Attempts", 'CALCULATE(COUNTROWS(LoadStatus), LoadStatus[status] = "rejected")')]),
        ],
        "relationships": [{
            "name": "ObservationBatch",
            "fromTable": "Observation",
            "fromColumn": "batch_id",
            "toTable": "Batch",
            "toColumn": "batch_id",
        }],
    }
    commands = {
        "deploy": {"createOrReplace": {
            "object": {"database": database},
            "database": {"name": database, "id": database, "compatibilityLevel": 1200, "model": model},
        }},
        "refresh": {"refresh": {"type": "full", "objects": [{"database": database}]}},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for name, command in commands.items():
        (args.output / f"{name}.json").write_text(json.dumps(command, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
