"""Quick check that Qdrant is reachable and the collection can be created."""

from app.vector.qdrant_client import get_qdrant_client, ensure_collection
from app.core.config import settings


def main() -> None:
    client = get_qdrant_client()
    ensure_collection(client)

    info = client.get_collection(settings.QDRANT_COLLECTION)
    print(f"\n✓ Connected to Qdrant.")
    print(f"  Collection: {settings.QDRANT_COLLECTION}")
    print(f"  Vectors: {info.points_count}")
    print(f"  Status: {info.status}")


if __name__ == "__main__":
    main()