USE fin_model;
GO

IF OBJECT_ID('dbo.silver_entities', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.silver_entities (
        silver_id         INT IDENTITY(1,1) PRIMARY KEY,
        Entity_ID         VARCHAR(50)     NOT NULL,
        Legal_Name        VARCHAR(255)    NOT NULL,
        Trade_Name        VARCHAR(255)    NULL,
        Tax_Registration_Number VARCHAR(100) NULL,
        Country_Code      CHAR(2)         NULL,
        Account_Creation_Date DATETIME2   NULL,
        Is_Active         BIT             NULL,
        bronze_id         INT             NOT NULL,
        processed_at      DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE UNIQUE INDEX UX_silver_entities_bronze_id ON dbo.silver_entities (bronze_id);
END
GO
PRINT 'silver_entities table ready.';
GO