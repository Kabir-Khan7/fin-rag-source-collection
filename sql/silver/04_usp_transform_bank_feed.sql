USE fin_model;
GO

CREATE OR ALTER PROCEDURE dbo.usp_transform_bank_feed
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @source_table VARCHAR(100) = 'stg_bank_feed';
    DECLARE @watermark INT, @max_id INT, @inserted INT = 0, @quarantined INT = 0;

    SELECT @watermark = last_processed_id FROM dbo.etl_watermark WHERE source_table = @source_table;
    SELECT @max_id = MAX(id) FROM dbo.stg_bank_feed;

    IF @max_id IS NULL OR @max_id <= @watermark
    BEGIN
        SELECT @source_table AS source_table, 0 AS processed, 0 AS inserted, 0 AS quarantined, @watermark AS watermark;
        RETURN;
    END

    BEGIN TRY
        BEGIN TRANSACTION;

        SELECT
            b.id AS bronze_id,
            b.Bank_Row_ID AS raw_bankrow,
            b.Booking_Date AS raw_booking,
            b.Value_Date AS raw_value,
            b.Transaction_Text_Narrative AS raw_narrative,
            b.Amount AS raw_amount,
            b.Running_Balance AS raw_balance,
            TRY_CONVERT(DATETIME2, b.Booking_Date) AS c_booking,
            TRY_CONVERT(DATETIME2, b.Value_Date) AS c_value,
            TRY_CONVERT(DECIMAL(18,2), REPLACE(b.Amount, ',', '')) AS c_amount,
            TRY_CONVERT(DECIMAL(18,2), REPLACE(b.Running_Balance, ',', '')) AS c_balance,
            CAST(NULL AS VARCHAR(50)) AS fail_reason
        INTO #staging
        FROM dbo.stg_bank_feed b
        WHERE b.id > @watermark AND b.id <= @max_id;

        UPDATE #staging
        SET fail_reason =
            CASE
                WHEN raw_bankrow IS NULL OR LTRIM(RTRIM(raw_bankrow)) = '' THEN 'INVALID_BANK_ROW_ID'
                WHEN raw_amount IS NULL OR c_amount IS NULL THEN 'INVALID_AMOUNT'
                WHEN raw_booking IS NOT NULL AND raw_booking <> '' AND c_booking IS NULL THEN 'INVALID_BOOKING_DATE'
                WHEN raw_value IS NOT NULL AND raw_value <> '' AND c_value IS NULL THEN 'INVALID_VALUE_DATE'
                WHEN raw_balance IS NOT NULL AND raw_balance <> '' AND c_balance IS NULL THEN 'INVALID_RUNNING_BALANCE'
                ELSE NULL
            END;

        ;WITH ranked AS (
            SELECT bronze_id, ROW_NUMBER() OVER (PARTITION BY LTRIM(RTRIM(raw_bankrow)) ORDER BY bronze_id DESC) AS rn
            FROM #staging WHERE fail_reason IS NULL
        )
        UPDATE s SET fail_reason = 'DUPLICATE'
        FROM #staging s JOIN ranked r ON s.bronze_id = r.bronze_id
        WHERE r.rn > 1;

        INSERT INTO dbo.etl_quarantine (source_table, bronze_id, reason_code, reason_detail, row_snapshot)
        SELECT @source_table, bronze_id, fail_reason, CONCAT('Row failed rule: ', fail_reason),
            (SELECT raw_bankrow AS Bank_Row_ID, raw_amount AS Amount, raw_booking AS Booking_Date
             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM #staging WHERE fail_reason IS NOT NULL;
        SET @quarantined = @@ROWCOUNT;

        INSERT INTO dbo.silver_bank_feed
            (Bank_Row_ID, Booking_Date, Value_Date, Transaction_Text_Narrative, Amount, Running_Balance, bronze_id)
        SELECT
            LTRIM(RTRIM(raw_bankrow)), c_booking, c_value, LTRIM(RTRIM(raw_narrative)), c_amount, c_balance, bronze_id
        FROM #staging WHERE fail_reason IS NULL;
        SET @inserted = @@ROWCOUNT;

        UPDATE dbo.etl_watermark
        SET last_processed_id = @max_id, last_run_at = SYSUTCDATETIME(),
            last_run_inserted = @inserted, last_run_quarantined = @quarantined
        WHERE source_table = @source_table;

        DROP TABLE #staging;
        COMMIT TRANSACTION;

        SELECT @source_table AS source_table, (@inserted + @quarantined) AS processed,
            @inserted AS inserted, @quarantined AS quarantined, @max_id AS watermark;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO
PRINT 'usp_transform_bank_feed ready.';
GO