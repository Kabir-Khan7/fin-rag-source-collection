USE fin_model;
GO

CREATE OR ALTER PROCEDURE dbo.usp_transform_chart_of_accounts
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @source_table VARCHAR(100) = 'stg_chart_of_accounts';
    DECLARE @watermark INT, @max_id INT, @inserted INT = 0, @quarantined INT = 0;

    SELECT @watermark = last_processed_id FROM dbo.etl_watermark WHERE source_table = @source_table;
    SELECT @max_id = MAX(id) FROM dbo.stg_chart_of_accounts;

    IF @max_id IS NULL OR @max_id <= @watermark
    BEGIN
        SELECT @source_table AS source_table, 0 AS processed, 0 AS inserted, 0 AS quarantined, @watermark AS watermark;
        RETURN;
    END

    BEGIN TRY
        BEGIN TRANSACTION;

        SELECT
            b.id AS bronze_id,
            b.GL_Account_Code AS raw_gl,
            b.Account_Name AS raw_name,
            b.Account_Class AS raw_class,
            b.Financial_Statement_Section AS raw_section,
            TRY_CONVERT(INT, b.GL_Account_Code) AS c_gl,
            CAST(NULL AS VARCHAR(50)) AS fail_reason
        INTO #staging
        FROM dbo.stg_chart_of_accounts b
        WHERE b.id > @watermark AND b.id <= @max_id;

        UPDATE #staging
        SET fail_reason =
            CASE
                WHEN raw_gl IS NULL OR c_gl IS NULL THEN 'INVALID_GL_ACCOUNT_CODE'
                WHEN raw_name IS NULL OR LTRIM(RTRIM(raw_name)) = '' THEN 'MISSING_ACCOUNT_NAME'
                ELSE NULL
            END;

        ;WITH ranked AS (
            SELECT bronze_id, ROW_NUMBER() OVER (PARTITION BY c_gl ORDER BY bronze_id DESC) AS rn
            FROM #staging WHERE fail_reason IS NULL
        )
        UPDATE s SET fail_reason = 'DUPLICATE'
        FROM #staging s JOIN ranked r ON s.bronze_id = r.bronze_id
        WHERE r.rn > 1;

        INSERT INTO dbo.etl_quarantine (source_table, bronze_id, reason_code, reason_detail, row_snapshot)
        SELECT @source_table, bronze_id, fail_reason, CONCAT('Row failed rule: ', fail_reason),
            (SELECT raw_gl AS GL_Account_Code, raw_name AS Account_Name FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM #staging WHERE fail_reason IS NOT NULL;
        SET @quarantined = @@ROWCOUNT;

        INSERT INTO dbo.silver_chart_of_accounts
            (GL_Account_Code, Account_Name, Account_Class, Financial_Statement_Section, bronze_id)
        SELECT c_gl, LTRIM(RTRIM(raw_name)), LTRIM(RTRIM(raw_class)), LTRIM(RTRIM(raw_section)), bronze_id
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
PRINT 'usp_transform_chart_of_accounts ready.';
GO