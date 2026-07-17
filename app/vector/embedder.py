"""
Local text embedding using sentence-transformers.

Loads the configured model once (expensive to initialize) and reuses it.
Model is config-driven so it can be swapped (e.g., to bge-base-en-v1.5)
via settings without code changes.
"""

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Load (once) and return the configured embedding model."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded.")
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts into normalized vectors."""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [emb.tolist() for emb in embeddings]