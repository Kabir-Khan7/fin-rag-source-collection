/* ============================================================
   gold_documents — embedding-ready text documents
   ------------------------------------------------------------
   Composes human-readable text from Silver rows, paired with
   JSON metadata for filtered vector search. One row = one
   document. The embedding pipeline reads rows WHERE
   embedded_at IS NULL (incremental), embeds content_text,
   upserts to Qdrant, then stamps embedded_at.
   ============================================================ */

USE fin_model;
GO

IF OBJECT_ID('dbo.gold_documents', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.gold_documents (
        doc_id           INT IDENTITY(1,1) PRIMARY KEY,
        source_type      VARCHAR(50)     NOT NULL,  -- 'invoice' | 'subledger'
        source_id        INT             NOT NULL,  -- the silver row's id
        content_text     NVARCHAR(MAX)   NOT NULL,  -- the text to embed
        metadata_json    NVARCHAR(MAX)   NULL,      -- filterable payload
        created_at       DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),
        embedded_at      DATETIME2       NULL       -- NULL = not yet embedded
    );

    -- Prevent duplicate documents for the same source row.
    CREATE UNIQUE INDEX UX_gold_documents_source
        ON dbo.gold_documents (source_type, source_id);
END
GO
PRINT 'gold_documents table ready.';
GO