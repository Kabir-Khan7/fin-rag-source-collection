"""
Qdrant vector database client and collection management.

Provides a configured Qdrant client and ensures the financial documents
collection exists with the correct vector dimensions (from settings).
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_qdrant_client() -> QdrantClient:
    """Return a configured Qdrant client."""
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


def ensure_collection(client: QdrantClient) -> None:
    """
    Create the financial documents collection if it doesn't exist.

    Configured with the embedding dimension from settings and cosine
    distance (standard for semantic similarity).
    """
    existing = [c.name for c in client.get_collections().collections]

    if settings.QDRANT_COLLECTION in existing:
        logger.info("Collection '%s' already exists.", settings.QDRANT_COLLECTION)
        return

    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(size=settings.EMBEDDING_DIM, distance=Distance.COSINE),
    )
    logger.info(
        "Created collection '%s' (dim=%d, cosine).",
        settings.QDRANT_COLLECTION, settings.EMBEDDING_DIM,
    )