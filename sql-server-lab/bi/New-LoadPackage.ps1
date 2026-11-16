[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ManagedDtsPath,
    [Parameter(Mandatory)][string]$SqlServer,
    [Parameter(Mandatory)][string]$Fixture,
    [Parameter(Mandatory)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
if ($SqlServer -notmatch '^[a-zA-Z0-9_.\\,-]+$') { throw 'Invalid SQL Server name.' }
Add-Type -Path (Resolve-Path -LiteralPath $ManagedDtsPath).Path
$payload = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $Fixture).Path)
$null = ConvertFrom-Json -InputObject $payload -ErrorAction Stop
$package = New-Object Microsoft.SqlServer.Dts.Runtime.Package
$package.Name = 'AlphaLensSyntheticLoad'
$package.ProtectionLevel = 'DontSaveSensitive'
$connection = $package.Connections.Add('OLEDB')
$connection.Name = 'AlphaLensWarehouse'
$connection.ConnectionString = "Provider=MSOLEDBSQL;Data Source=$SqlServer;Initial Catalog=AlphaLensWarehouseLab;Integrated Security=SSPI;"
$hostTask = $package.Executables.Add('STOCK:SQLTask')
$hostTask.Name = 'Load synthetic AlphaLens evidence'
$task = $hostTask.InnerObject
$task.Connection = $connection.ID
$task.SqlStatementSource = "EXEC dbo.LoadEvidence @payload = N'" + $payload.Replace("'", "''") + "';"
$application = New-Object Microsoft.SqlServer.Dts.Runtime.Application
$application.SaveToXml([IO.Path]::GetFullPath($OutputPath), $package, $null)
