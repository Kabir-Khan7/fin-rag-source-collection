USE fin_model;
GO

IF OBJECT_ID('dbo.silver_invoices', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.silver_invoices (
        silver_id         INT IDENTITY(1,1) PRIMARY KEY,
        Vendor_ID         VARCHAR(50)     NULL,
        Vendor_Name       VARCHAR(255)    NULL,
        Invoice_Number    VARCHAR(100)    NOT NULL,
        Invoice_Date      DATETIME2       NULL,
        Line_Item_Description NVARCHAR(MAX) NULL,
        Line_Item_Quantity DECIMAL(18,2)  NULL,
        Line_Item_Unit_Price DECIMAL(18,2) NULL,
        Total_Tax         DECIMAL(18,2)   NULL,
        Grand_Total       DECIMAL(18,2)   NULL,
        Raw_Text          NVARCHAR(MAX)   NULL,
        bronze_id         INT             NOT NULL,
        processed_at      DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE UNIQUE INDEX UX_silver_invoices_bronze_id ON dbo.silver_invoices (bronze_id);
END
GO
PRINT 'silver_invoices table ready.';
GO