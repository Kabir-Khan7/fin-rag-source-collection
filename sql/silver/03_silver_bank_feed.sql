USE fin_model;
GO

IF OBJECT_ID('dbo.silver_bank_feed', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.silver_bank_feed (
        silver_id         INT IDENTITY(1,1) PRIMARY KEY,
        Bank_Row_ID       VARCHAR(50)     NOT NULL,
        Booking_Date      DATETIME2       NULL,
        Value_Date        DATETIME2       NULL,
        Transaction_Text_Narrative NVARCHAR(MAX) NULL,
        Amount            DECIMAL(18,2)   NOT NULL,
        Running_Balance   DECIMAL(18,2)   NULL,
        bronze_id         INT             NOT NULL,
        processed_at      DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE UNIQUE INDEX UX_silver_bank_feed_bronze_id ON dbo.silver_bank_feed (bronze_id);
END
GO
PRINT 'silver_bank_feed table ready.';
GO