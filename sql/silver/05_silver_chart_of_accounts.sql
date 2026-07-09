USE fin_model;
GO

IF OBJECT_ID('dbo.silver_chart_of_accounts', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.silver_chart_of_accounts (
        silver_id         INT IDENTITY(1,1) PRIMARY KEY,
        GL_Account_Code   INT             NOT NULL,
        Account_Name      VARCHAR(255)    NOT NULL,
        Account_Class     VARCHAR(100)    NULL,
        Financial_Statement_Section VARCHAR(255) NULL,
        bronze_id         INT             NOT NULL,
        processed_at      DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE UNIQUE INDEX UX_silver_coa_bronze_id ON dbo.silver_chart_of_accounts (bronze_id);
END
GO
PRINT 'silver_chart_of_accounts table ready.';
GO