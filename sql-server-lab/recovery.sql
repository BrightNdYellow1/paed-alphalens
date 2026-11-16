USE master;
GO
IF DB_ID(N'AlphaLensWarehouseLabRestored') IS NOT NULL
    THROW 51003, 'Restore target already exists. Use a clean lab instance.', 1;

BACKUP DATABASE AlphaLensWarehouseLab
    TO DISK = '/var/opt/mssql/data/AlphaLensWarehouseLab.bak'
    WITH COPY_ONLY, INIT, CHECKSUM;
RESTORE VERIFYONLY FROM DISK = '/var/opt/mssql/data/AlphaLensWarehouseLab.bak' WITH CHECKSUM;
RESTORE DATABASE AlphaLensWarehouseLabRestored
    FROM DISK = '/var/opt/mssql/data/AlphaLensWarehouseLab.bak'
    WITH CHECKSUM,
    MOVE 'AlphaLensWarehouseLab' TO '/var/opt/mssql/data/AlphaLensWarehouseLabRestored.mdf',
    MOVE 'AlphaLensWarehouseLab_log' TO '/var/opt/mssql/data/AlphaLensWarehouseLabRestored_log.ldf';
GO
IF (SELECT COUNT_BIG(*) FROM AlphaLensWarehouseLab.dbo.Observation) <>
   (SELECT COUNT_BIG(*) FROM AlphaLensWarehouseLabRestored.dbo.Observation)
   OR (SELECT COUNT_BIG(*) FROM AlphaLensWarehouseLab.dbo.Batch) <>
      (SELECT COUNT_BIG(*) FROM AlphaLensWarehouseLabRestored.dbo.Batch)
   OR (SELECT COUNT_BIG(*) FROM AlphaLensWarehouseLab.dbo.LoadAttempt) <>
      (SELECT COUNT_BIG(*) FROM AlphaLensWarehouseLabRestored.dbo.LoadAttempt)
    THROW 51003, 'Restored warehouse counts did not reconcile.', 1;

SELECT COUNT_BIG(*) AS restored_observations
FROM AlphaLensWarehouseLabRestored.dbo.Observation;
