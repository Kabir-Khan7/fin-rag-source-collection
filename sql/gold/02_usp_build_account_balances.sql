/* ============================================================
   usp_build_account_balances
   ------------------------------------------------------------
   Full-refresh rebuild of gold_account_balances from Silver.
   Sums POSTED subledger amounts per GL account, enriched with
   account metadata from silver_chart_of_accounts.
   ============================================================ */

USE fin_model;
GO

CREATE OR ALTER PROCEDURE dbo.usp_build_account_balances
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @rows INT = 0;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Full refresh: clear then rebuild.
        TRUNCATE TABLE dbo.gold_account_balances;

        INSERT INTO dbo.gold_account_balances
            (GL_Account_Code, Account_Name, Account_Class, transaction_count, total_balance)
        SELECT
            s.GL_Account_Code,
            MAX(coa.Account_Name)   AS Account_Name,   -- MAX = pick the (single) matching name
            MAX(coa.Account_Class)  AS Account_Class,
            COUNT(*)                AS transaction_count,
            SUM(s.Amount)           AS total_balance
        FROM dbo.silver_subledger s
        LEFT JOIN dbo.silver_chart_of_accounts coa
            ON s.GL_Account_Code = coa.GL_Account_Code
        WHERE s.Status = 'Posted'          -- only finalized transactions
          AND s.GL_Account_Code IS NOT NULL
        GROUP BY s.GL_Account_Code;

        SET @rows = @@ROWCOUNT;

        COMMIT TRANSACTION;

        -- Return a count for the orchestrator.
        SELECT 'gold_account_balances' AS metric_table, @rows AS rows_built;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO
PRINT 'usp_build_account_balances ready.';
GO