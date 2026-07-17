"""
Loads embedding-ready documents from the Gold layer.

Reads gold_documents rows that haven't been embedded yet (embedded_at IS
NULL), returning them as lightweight objects for the embedding pipeline.
This is a thin custom loader over SQLAlchemy — no heavyweight framework
needed to read our own tables.
"""

from dataclasses import dataclass

from sqlalchemy import text

from app.database.session import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GoldDocument:
    """One embedding-ready document from the Gold layer."""

    doc_id: int
    source_type: str
    source_id: int
    content_text: str
    metadata_json: str | None


def load_unembedded_documents(limit: int | None = None) -> list[GoldDocument]:
    """
    Load Gold documents that haven't been embedded yet.

    Args:
        limit: Optional cap on how many to load (useful for batching).

    Returns:
        A list of GoldDocument objects with embedded_at IS NULL.
    """
    db = SessionLocal()
    try:
        sql = """
            SELECT doc_id, source_type, source_id, content_text, metadata_json
            FROM dbo.gold_documents
            WHERE embedded_at IS NULL
            ORDER BY doc_id
        """
        if limit:
            sql = sql.replace("SELECT", f"SELECT TOP {int(limit)}")

        rows = db.execute(text(sql)).fetchall()
        docs = [
            GoldDocument(
                doc_id=r.doc_id,
                source_type=r.source_type,
                source_id=r.source_id,
                content_text=r.content_text,
                metadata_json=r.metadata_json,
            )
            for r in rows
        ]
        logger.info("Loaded %d un-embedded documents.", len(docs))
        return docs
    finally:
        db.close()


def mark_documents_embedded(doc_ids: list[int]) -> None:
    """
    Stamp embedded_at = now for the given document ids (the watermark).

    Called after successful upsert to Qdrant so these documents aren't
    re-embedded on the next run.
    """
    if not doc_ids:
        return

    db = SessionLocal()
    try:
        # Parameterized IN clause.
        placeholders = ", ".join(f":id{i}" for i in range(len(doc_ids)))
        params = {f"id{i}": doc_id for i, doc_id in enumerate(doc_ids)}
        db.execute(
            text(f"""
                UPDATE dbo.gold_documents
                SET embedded_at = SYSUTCDATETIME()
                WHERE doc_id IN ({placeholders})
            """),
            params,
        )
        db.commit()
        logger.info("Marked %d documents as embedded.", len(doc_ids))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()