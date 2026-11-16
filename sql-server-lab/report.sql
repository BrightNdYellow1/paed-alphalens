USE AlphaLensWarehouseLab;
GO
-- Load monitoring detail. Excludes original payloads.
SELECT attempt_id, batch_id, case_label, status, started_at, ended_at,
       DATEDIFF_BIG(millisecond, started_at, ended_at) AS duration_ms,
       input_rows, inserted_rows, error_message
FROM dbo.LoadStatus
ORDER BY attempt_id DESC;

-- Published batch reconciliation. A clean run returns no rows.
SELECT b.batch_id, b.row_count AS declared_rows, COUNT_BIG(o.period) AS stored_rows
FROM dbo.Batch AS b
LEFT JOIN dbo.Observation AS o ON o.batch_id = b.batch_id
GROUP BY b.batch_id, b.row_count
HAVING COUNT_BIG(o.period) <> b.row_count;
