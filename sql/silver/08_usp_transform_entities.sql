USE fin_model;
GO

CREATE OR ALTER PROCEDURE dbo.usp_transform_entities
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @source_table VARCHAR(100) = 'stg_master_directory';
    DECLARE @watermark INT, @max_id INT, @inserted INT = 0, @quarantined INT = 0;

    SELECT @watermark = last_processed_id FROM dbo.etl_watermark WHERE source_table = @source_table;
    SELECT @max_id = MAX(id) FROM dbo.stg_master_directory;

    IF @max_id IS NULL OR @max_id <= @watermark
    BEGIN
        SELECT @source_table AS source_table, 0 AS processed, 0 AS inserted, 0 AS quarantined, @watermark AS watermark;
        RETURN;
    END

    BEGIN TRY
        BEGIN TRANSACTION;

        SELECT
            b.id AS bronze_id,
            b.Entity_ID AS raw_entity,
            b.Legal_Name AS raw_legal,
            b.Trade_Name AS raw_trade,
            b.Tax_Registration_Number AS raw_tax,
            b.Country_Code AS raw_country,
            b.Account_Creation_Date AS raw_created,
            b.Is_Active AS raw_active,
            TRY_CONVERT(DATETIME2, b.Account_Creation_Date) AS c_created,
            -- Normalize Is_Active to BIT: true/1/yes/y -> 1, false/0/no/n -> 0, else NULL(=invalid)
            CASE
                WHEN LOWER(LTRIM(RTRIM(b.Is_Active))) IN ('true','1','yes','y') THEN 1
                WHEN LOWER(LTRIM(RTRIM(b.Is_Active))) IN ('false','0','no','n') THEN 0
                ELSE NULL
            END AS c_active,
            CAST(NULL AS VARCHAR(50)) AS fail_reason
        INTO #staging
        FROM dbo.stg_master_directory b
        WHERE b.id > @watermark AND b.id <= @max_id;

        UPDATE #staging
        SET fail_reason =
            CASE
                WHEN raw_entity IS NULL OR LTRIM(RTRIM(raw_entity)) = '' THEN 'MISSING_ENTITY_ID'
                WHEN raw_legal IS NULL OR LTRIM(RTRIM(raw_legal)) = '' THEN 'MISSING_LEGAL_NAME'
                WHEN raw_active IS NOT NULL AND raw_active <> '' AND c_active IS NULL THEN 'INVALID_IS_ACTIVE'
                WHEN raw_created IS NOT NULL AND raw_created <> '' AND c_created IS NULL THEN 'INVALID_CREATION_DATE'
                ELSE NULL
            END;

        ;WITH ranked AS (
            SELECT bronze_id, ROW_NUMBER() OVER (PARTITION BY UPPER(LTRIM(RTRIM(raw_entity))) ORDER BY bronze_id DESC) AS rn
            FROM #staging WHERE fail_reason IS NULL
        )
        UPDATE s SET fail_reason = 'DUPLICATE'
        FROM #staging s JOIN ranked r ON s.bronze_id = r.bronze_id
        WHERE r.rn > 1;

        INSERT INTO dbo.etl_quarantine (source_table, bronze_id, reason_code, reason_detail, row_snapshot)
        SELECT @source_table, bronze_id, fail_reason, CONCAT('Row failed rule: ', fail_reason),
            (SELECT raw_entity AS Entity_ID, raw_legal AS Legal_Name, raw_active AS Is_Active
             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM #staging WHERE fail_reason IS NOT NULL;
        SET @quarantined = @@ROWCOUNT;

        INSERT INTO dbo.silver_entities
            (Entity_ID, Legal_Name, Trade_Name, Tax_Registration_Number, Country_Code, Account_Creation_Date, Is_Active, bronze_id)
        SELECT
            UPPER(LTRIM(RTRIM(raw_entity))),
            LTRIM(RTRIM(raw_legal)),
            LTRIM(RTRIM(raw_trade)),
            LTRIM(RTRIM(raw_tax)),
            UPPER(LTRIM(RTRIM(raw_country))),
            c_created,
            c_active,
            bronze_id
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
PRINT 'usp_transform_entities ready.';
GO