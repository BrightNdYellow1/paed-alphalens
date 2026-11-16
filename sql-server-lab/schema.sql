IF DB_ID(N'AlphaLensWarehouseLab') IS NULL
    CREATE DATABASE AlphaLensWarehouseLab;
GO
USE AlphaLensWarehouseLab;
GO

IF OBJECT_ID(N'dbo.Batch', N'U') IS NULL
CREATE TABLE dbo.Batch (
    batch_id char(64) NOT NULL PRIMARY KEY,
    case_label varchar(30) NOT NULL,
    row_count int NOT NULL CHECK (row_count > 0),
    original_sharpe float NOT NULL,
    corrected_sharpe float NOT NULL,
    loaded_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME()
);

IF OBJECT_ID(N'dbo.Observation', N'U') IS NULL
CREATE TABLE dbo.Observation (
    batch_id char(64) NOT NULL REFERENCES dbo.Batch(batch_id),
    period int NOT NULL CHECK (period >= 0),
    market_return float NOT NULL,
    position float NOT NULL CHECK (position BETWEEN -1 AND 1),
    original_equity float NOT NULL,
    corrected_equity float NOT NULL,
    CONSTRAINT PK_Observation PRIMARY KEY (batch_id, period)
);

IF OBJECT_ID(N'dbo.LoadAttempt', N'U') IS NULL
CREATE TABLE dbo.LoadAttempt (
    attempt_id bigint IDENTITY PRIMARY KEY,
    batch_id char(64) NULL,
    started_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME(),
    ended_at datetime2 NULL,
    status varchar(12) NOT NULL CHECK (status IN
        ('running', 'completed', 'replayed', 'rejected', 'failed')),
    input_rows int NULL,
    inserted_rows int NULL,
    error_message nvarchar(2048) NULL,
    payload nvarchar(max) NOT NULL
);
GO

CREATE OR ALTER PROCEDURE dbo.LoadEvidence @payload nvarchar(max)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @batch char(64) = CONVERT(char(64), HASHBYTES('SHA2_256', @payload), 2);
    DECLARE @attempt bigint, @rows int, @expected int;
    DECLARE @case varchar(30), @original float, @corrected float;

    INSERT dbo.LoadAttempt (batch_id, status, payload) VALUES (@batch, 'running', @payload);
    SET @attempt = SCOPE_IDENTITY();

    BEGIN TRY
        IF ISJSON(@payload, OBJECT) <> 1
            THROW 51001, 'Expected a JSON object.', 1;

        SELECT @case = JSON_VALUE(@payload, '$.case_label'),
               @expected = TRY_CONVERT(int, JSON_VALUE(@payload, '$.row_count')),
               @original = TRY_CONVERT(float, JSON_VALUE(@payload, '$.original_sharpe')),
               @corrected = TRY_CONVERT(float, JSON_VALUE(@payload, '$.corrected_sharpe'));

        IF @case IS NULL OR @case NOT IN ('future-aware', 'clean control')
            OR @expected IS NULL OR @expected < 1 OR @original IS NULL OR @corrected IS NULL
            OR ISNULL(ISJSON(JSON_QUERY(@payload, '$.observations'), ARRAY), 0) <> 1
            THROW 51001, 'Invalid batch metadata or observations array.', 1;

        SELECT TRY_CONVERT(int, period) AS period,
               TRY_CONVERT(float, market_return) AS market_return,
               TRY_CONVERT(float, position) AS position,
               TRY_CONVERT(float, original_equity) AS original_equity,
               TRY_CONVERT(float, corrected_equity) AS corrected_equity
        INTO #incoming
        FROM OPENJSON(@payload, '$.observations') WITH (
            period nvarchar(100), market_return nvarchar(100), position nvarchar(100),
            original_equity nvarchar(100), corrected_equity nvarchar(100)
        );

        SET @rows = @@ROWCOUNT;

        IF @rows <> @expected OR EXISTS (
            SELECT 1 FROM #incoming
            WHERE period IS NULL OR period < 0 OR market_return IS NULL OR position IS NULL
                OR position NOT BETWEEN -1 AND 1 OR original_equity IS NULL OR corrected_equity IS NULL
        )
            THROW 51001, 'Row count or observation values failed validation.', 1;

        IF EXISTS (SELECT period FROM #incoming GROUP BY period HAVING COUNT(*) > 1)
            THROW 51001, 'Duplicate period identifiers.', 1;

        BEGIN TRANSACTION;
        IF EXISTS (SELECT 1 FROM dbo.Batch WITH (UPDLOCK, HOLDLOCK) WHERE batch_id = @batch)
        BEGIN
            UPDATE dbo.LoadAttempt SET status = 'replayed', ended_at = SYSUTCDATETIME(),
                input_rows = @rows, inserted_rows = 0 WHERE attempt_id = @attempt;
        END
        ELSE
        BEGIN
            INSERT dbo.Batch (batch_id, case_label, row_count, original_sharpe, corrected_sharpe)
            VALUES (@batch, @case, @rows, @original, @corrected);

            INSERT dbo.Observation (batch_id, period, market_return, position, original_equity, corrected_equity)
            SELECT @batch, period, market_return, position, original_equity, corrected_equity
            FROM #incoming;

            UPDATE dbo.LoadAttempt SET status = 'completed', ended_at = SYSUTCDATETIME(),
                input_rows = @rows, inserted_rows = @rows WHERE attempt_id = @attempt;
        END;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        UPDATE dbo.LoadAttempt
        SET status = CASE WHEN ERROR_NUMBER() = 51001 THEN 'rejected' ELSE 'failed' END,
            ended_at = SYSUTCDATETIME(), input_rows = @rows, inserted_rows = 0,
            error_message = ERROR_MESSAGE()
        WHERE attempt_id = @attempt;
        THROW;
    END CATCH;
END;
GO

CREATE OR ALTER VIEW dbo.LoadStatus
AS SELECT a.attempt_id, a.batch_id, a.started_at, a.ended_at,
          a.status, a.input_rows, a.inserted_rows, a.error_message,
          b.case_label, b.original_sharpe, b.corrected_sharpe
   FROM dbo.LoadAttempt AS a LEFT JOIN dbo.Batch AS b ON b.batch_id = a.batch_id;
GO
