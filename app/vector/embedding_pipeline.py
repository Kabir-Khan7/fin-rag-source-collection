"""
Embedding pipeline: Gold documents -> vectors -> Qdrant.

Orchestrates the local embedding flow:
  1. Load un-embedded documents from Gold.
  2. Embed their text locally.
  3. Upsert vectors + metadata payloads to Qdrant.
  4. Stamp embedded_at (watermark) so they aren't re-embedded.
"""

import json
from dataclasses import dataclass

from qdrant_client.models import PointStruct

from app.vector.qdrant_client import get_qdrant_client, ensure_collection
from app.core.config import settings
from app.vector.loader import load_unembedded_documents, mark_documents_embedded
from app.vector.embedder import embed_texts
from app.utils.logger import get_logger

logger = get_logger(__name__)

BATCH_SIZE = 100


@dataclass
class EmbeddingRunSummary:
    """Summary of an embedding run."""

    total_embedded: int = 0
    failed: bool = False
    error: str | None = None


def run_embedding_pipeline() -> EmbeddingRunSummary:
    """
    Embed all un-embedded Gold documents and store them in Qdrant.

    Processes in batches. Only marks documents embedded after a successful
    upsert, so a failure leaves them to be retried next run.
    """
    logger.info("=== Embedding pipeline started ===")
    summary = EmbeddingRunSummary()

    client = get_qdrant_client()
    ensure_collection(client)

    try:
        while True:
            docs = load_unembedded_documents(limit=BATCH_SIZE)
            if not docs:
                break

            texts = [d.content_text for d in docs]
            vectors = embed_texts(texts)

            points = []
            for doc, vector in zip(docs, vectors):
                payload = json.loads(doc.metadata_json) if doc.metadata_json else {}
                # Keep the source text in the payload too, for retrieval display.
                payload["content_text"] = doc.content_text
                points.append(
                    PointStruct(id=doc.doc_id, vector=vector, payload=payload)
                )

            # Upsert this batch to Qdrant.
            client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)

            # Watermark: mark them embedded only after successful upsert.
            mark_documents_embedded([d.doc_id for d in docs])
            summary.total_embedded += len(docs)
            logger.info("Embedded batch of %d (total %d).", len(docs), summary.total_embedded)

        logger.info("=== Embedding pipeline complete — %d embedded ===", summary.total_embedded)
    except Exception as exc:
        summary.failed = True
        summary.error = str(exc)
        logger.error("Embedding pipeline failed: %s", exc, exc_info=True)

    return summary