USE fin_model;
GO

CREATE OR ALTER PROCEDURE dbo.usp_transform_invoices
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @source_table VARCHAR(100) = 'stg_raw_invoices';
    DECLARE @watermark INT, @max_id INT, @inserted INT = 0, @quarantined INT = 0;

    SELECT @watermark = last_processed_id FROM dbo.etl_watermark WHERE source_table = @source_table;
    SELECT @max_id = MAX(id) FROM dbo.stg_raw_invoices;

    IF @max_id IS NULL OR @max_id <= @watermark
    BEGIN
        SELECT @source_table AS source_table, 0 AS processed, 0 AS inserted, 0 AS quarantined, @watermark AS watermark;
        RETURN;
    END

    BEGIN TRY
        BEGIN TRANSACTION;

        SELECT
            b.id AS bronze_id,
            b.Vendor_ID AS raw_vendorid,
            b.Vendor_Name AS raw_vendorname,
            b.Invoice_Number AS raw_invnum,
            b.Invoice_Date AS raw_invdate,
            b.Line_Item_Description AS raw_desc,
            b.Line_Item_Quantity AS raw_qty,
            b.Line_Item_Unit_Price AS raw_unitprice,
            b.Total_Tax AS raw_tax,
            b.Grand_Total AS raw_grand,
            b.Raw_Text AS raw_text,
            TRY_CONVERT(DATETIME2, b.Invoice_Date) AS c_invdate,
            TRY_CONVERT(DECIMAL(18,2), REPLACE(b.Line_Item_Quantity, ',', '')) AS c_qty,
            TRY_CONVERT(DECIMAL(18,2), REPLACE(b.Line_Item_Unit_Price, ',', '')) AS c_unitprice,
            TRY_CONVERT(DECIMAL(18,2), REPLACE(b.Total_Tax, ',', '')) AS c_tax,
            TRY_CONVERT(DECIMAL(18,2), REPLACE(b.Grand_Total, ',', '')) AS c_grand,
            CAST(NULL AS VARCHAR(50)) AS fail_reason
        INTO #staging
        FROM dbo.stg_raw_invoices b
        WHERE b.id > @watermark AND b.id <= @max_id;

        UPDATE #staging
        SET fail_reason =
            CASE
                WHEN raw_invnum IS NULL OR LTRIM(RTRIM(raw_invnum)) = '' THEN 'MISSING_INVOICE_NUMBER'
                WHEN raw_invdate IS NOT NULL AND raw_invdate <> '' AND c_invdate IS NULL THEN 'INVALID_INVOICE_DATE'
                WHEN raw_grand IS NOT NULL AND raw_grand <> '' AND c_grand IS NULL THEN 'INVALID_GRAND_TOTAL'
                WHEN raw_tax IS NOT NULL AND raw_tax <> '' AND c_tax IS NULL THEN 'INVALID_TOTAL_TAX'
                ELSE NULL
            END;

        -- Dedup by (Invoice_Number + Line_Item_Description) since grain is line item.
        ;WITH ranked AS (
            SELECT bronze_id,
                ROW_NUMBER() OVER (
                    PARTITION BY LTRIM(RTRIM(raw_invnum)), LTRIM(RTRIM(ISNULL(raw_desc, '')))
                    ORDER BY bronze_id DESC
                ) AS rn
            FROM #staging WHERE fail_reason IS NULL
        )
        UPDATE s SET fail_reason = 'DUPLICATE'
        FROM #staging s JOIN ranked r ON s.bronze_id = r.bronze_id
        WHERE r.rn > 1;

        INSERT INTO dbo.etl_quarantine (source_table, bronze_id, reason_code, reason_detail, row_snapshot)
        SELECT @source_table, bronze_id, fail_reason, CONCAT('Row failed rule: ', fail_reason),
            (SELECT raw_invnum AS Invoice_Number, raw_grand AS Grand_Total FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM #staging WHERE fail_reason IS NOT NULL;
        SET @quarantined = @@ROWCOUNT;

        INSERT INTO dbo.silver_invoices
            (Vendor_ID, Vendor_Name, Invoice_Number, Invoice_Date, Line_Item_Description,
             Line_Item_Quantity, Line_Item_Unit_Price, Total_Tax, Grand_Total, Raw_Text, bronze_id)
        SELECT
            LTRIM(RTRIM(raw_vendorid)), LTRIM(RTRIM(raw_vendorname)), LTRIM(RTRIM(raw_invnum)),
            c_invdate, LTRIM(RTRIM(raw_desc)), c_qty, c_unitprice, c_tax, c_grand,
            raw_text, bronze_id
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
PRINT 'usp_transform_invoices ready.';
GO