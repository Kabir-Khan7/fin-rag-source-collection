"""
Command-line entry point for the embedding pipeline.

Usage (venv active, Qdrant running):
    python run_embeddings.py
"""

from app.vector.embedding_pipeline import run_embedding_pipeline


def main() -> None:
    summary = run_embedding_pipeline()
    print("\n" + "=" * 50)
    print("EMBEDDING RUN SUMMARY")
    print("=" * 50)
    print(f"  Documents embedded: {summary.total_embedded}")
    if summary.failed:
        print(f"  Status: FAILED")
        print(f"  Error: {summary.error}")
    else:
        print(f"  Status: SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    main()