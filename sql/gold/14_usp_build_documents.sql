/* ============================================================
   usp_build_documents
   ------------------------------------------------------------
   Composes gold_documents from Silver invoices and subledger.
   Incremental: only inserts documents for source rows that
   don't already have one (via NOT EXISTS on source_type+id).
   Does NOT touch already-embedded rows.
   ============================================================ */

USE fin_model;
GO

CREATE OR ALTER PROCEDURE dbo.usp_build_documents
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @inv_rows INT = 0, @sub_rows INT = 0;

    BEGIN TRY
        BEGIN TRANSACTION;

        /* ---- Invoices -> documents ---- */
        INSERT INTO dbo.gold_documents (source_type, source_id, content_text, metadata_json)
        SELECT
            'invoice',
            i.silver_id,
            CONCAT(
                'Invoice ', ISNULL(i.Invoice_Number, 'N/A'),
                ' from ', ISNULL(i.Vendor_Name, 'Unknown vendor'),
                ' (vendor ', ISNULL(i.Vendor_ID, 'N/A'), ')',
                CASE WHEN i.Invoice_Date IS NOT NULL
                     THEN CONCAT(', dated ', CONVERT(VARCHAR(10), i.Invoice_Date, 120))
                     ELSE '' END,
                '. Line item: ', ISNULL(i.Line_Item_Description, 'not specified'),
                '. Grand total ', ISNULL(CAST(i.Grand_Total AS VARCHAR(20)), '0'),
                CASE WHEN i.Total_Tax IS NOT NULL
                     THEN CONCAT(' (tax ', CAST(i.Total_Tax AS VARCHAR(20)), ')')
                     ELSE '' END,
                '.'
            ),
            (SELECT
                'invoice' AS source_type,
                i.silver_id AS source_id,
                i.Vendor_ID AS vendor_id,
                i.Vendor_Name AS vendor_name,
                i.Grand_Total AS amount,
                CONVERT(VARCHAR(10), i.Invoice_Date, 120) AS date
             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM dbo.silver_invoices i
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.gold_documents d
            WHERE d.source_type = 'invoice' AND d.source_id = i.silver_id
        );
        SET @inv_rows = @@ROWCOUNT;

        /* ---- Subledger -> documents ---- */
        INSERT INTO dbo.gold_documents (source_type, source_id, content_text, metadata_json)
        SELECT
            'subledger',
            s.silver_id,
            CONCAT(
                'Transaction ', CAST(s.Transaction_ID AS VARCHAR(50)),
                CASE WHEN s.Document_Date IS NOT NULL
                     THEN CONCAT(' dated ', CONVERT(VARCHAR(10), s.Document_Date, 120))
                     ELSE '' END,
                ' on account ', ISNULL(CAST(s.GL_Account_Code AS VARCHAR(20)), 'N/A'),
                CASE WHEN s.Entity_ID IS NOT NULL
                     THEN CONCAT(' for entity ', s.Entity_ID) ELSE '' END,
                '. Type: ', ISNULL(s.Transaction_Type, 'N/A'),
                ', status ', ISNULL(s.Status, 'N/A'),
                ', amount ', ISNULL(CAST(s.Amount AS VARCHAR(20)), '0'),
                CASE WHEN s.Description IS NOT NULL AND s.Description <> ''
                     THEN CONCAT('. ', s.Description) ELSE '' END,
                '.'
            ),
            (SELECT
                'subledger' AS source_type,
                s.silver_id AS source_id,
                s.GL_Account_Code AS gl_account,
                s.Entity_ID AS entity_id,
                s.Amount AS amount,
                s.Status AS status,
                CONVERT(VARCHAR(10), s.Document_Date, 120) AS date
             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM dbo.silver_subledger s
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.gold_documents d
            WHERE d.source_type = 'subledger' AND d.source_id = s.silver_id
        );
        SET @sub_rows = @@ROWCOUNT;

        COMMIT TRANSACTION;

        SELECT 'gold_documents' AS metric_table,
               (@inv_rows + @sub_rows) AS rows_built,
               @inv_rows AS invoice_docs,
               @sub_rows AS subledger_docs;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO
PRINT 'usp_build_documents ready.';
GO