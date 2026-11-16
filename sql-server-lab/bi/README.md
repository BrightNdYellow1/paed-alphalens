# AlphaLens Windows BI lab

Use a disposable Windows lab with the SQL Server warehouse schema already
installed. Install the SQL Server 2022 Integration Services, Reporting
Services and Analysis Services Tabular components for the exercises you run.
Use Windows authentication and grant the relevant lab identity only the
database permissions it needs.

## SSIS load

Generate the JSON fixtures with prepare_drill.py as described in the parent
README. From the repository root in Windows PowerShell, supply your installed
ManagedDTS.dll path and disposable SQL instance name:

```powershell
.\sql-server-lab\bi\New-LoadPackage.ps1 -ManagedDtsPath '<ManagedDTS.dll path>' -SqlServer 'localhost' -Fixture '.\fixtures\valid.json' -OutputPath '.\valid.dtsx'
dtexec /FILE .\valid.dtsx /REPORTING E
```

Run the valid package twice. Generate packages from invalid.json and
corrected.json using the same command and run each. The invalid package should
fail with a duplicate-period error. Check dbo.LoadStatus for completed,
replayed, rejected and completed attempts on a fresh warehouse. The input
is embedded in the generated package, so use the supplied synthetic fixtures.

## SSRS paginated report

Open LoadAttempts.rdl in a Reporting Services project or Report Builder.
Point the Warehouse data source at the lab instance and select an approved
Windows credential configuration. Preview the report, deploy it to the test
report server, then export the rendered results. Check the rejected row and its
diagnostic against dbo.LoadStatus.

## SSAS Tabular model

Generate the commands using the relational SQL Server name:

```powershell
python .\sql-server-lab\bi\New-TabularModel.py --sql-server localhost --output .\tabular-output
```

In SSMS, connect to the lab Analysis Services Tabular instance and run
deploy.json in a new XMLA query, followed by refresh.json. The command replaces
the model named AlphaLensWarehouseTabularLab, so use a disposable instance.
Give the SSAS service account read access to the three source objects. In a DAX
query, run:

```dax
EVALUATE ROW(
    "Published batches", [Published Batches],
    "Published observations", [Published Observations],
    "Rejected attempts", [Rejected Attempts]
)
```

A fresh warehouse after the SSIS drill should show 2 batches, 423 observations,
and 1 rejection. Keep the SQL Server CI run, SSIS execution log, SSRS export and
SSAS query output as distinct evidence. The BI files and generator output can
be checked without Windows. Deployment requires the corresponding services.
