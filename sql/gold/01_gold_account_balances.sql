/* ============================================================
   gold_account_balances — current balance per GL account
   ------------------------------------------------------------
   Aggregates posted subledger transactions by GL account,
   enriched with account name and class. Full-refresh: rebuilt
   from current Silver data on every run (a balance is a
   snapshot of all data, not an incremental append).
   ============================================================ */

USE fin_model;
GO

IF OBJECT_ID('dbo.gold_account_balances', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.gold_account_balances (
        gold_id          INT IDENTITY(1,1) PRIMARY KEY,
        GL_Account_Code  INT             NOT NULL,
        Account_Name     VARCHAR(255)    NULL,
        Account_Class    VARCHAR(100)    NULL,
        transaction_count INT            NOT NULL,
        total_balance    DECIMAL(18,2)   NOT NULL,
        computed_at      DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO
PRINT 'gold_account_balances table ready.';
GO