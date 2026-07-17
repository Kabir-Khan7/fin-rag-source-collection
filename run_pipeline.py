"""
Command-line entry point to run the data warehouse pipeline.

Usage (from project root, venv active):
    python run_pipeline.py
"""

from app.pipeline.orchestrator import run_pipeline


def main() -> None:
    """Run the pipeline and print a human-readable summary."""
    summary = run_pipeline()

    print("\n" + "=" * 55)
    print("PIPELINE RUN SUMMARY")
    print("=" * 55)

    for r in summary.results:
        print(
            f"  {r.source_table:<24} "
            f"inserted={r.inserted:<5} quarantined={r.quarantined:<5} "
            f"(watermark={r.watermark})"
        )

    print("-" * 55)
    print(f"  TOTAL inserted:     {summary.total_inserted}")
    print(f"  TOTAL quarantined:  {summary.total_quarantined}")

    if summary.succeeded:
        print(f"\n  Status: SUCCESS")
    else:
        print(f"\n  Status: FAILED at {summary.failed_step}")
        print(f"  Error: {summary.error}")
    print("=" * 55)
    
    if summary.gold_results:
        print("\n  GOLD METRICS BUILT:")
        for g in summary.gold_results:
            print(f"    {g.metric_table:<28} rows={g.rows_built}")


if __name__ == "__main__":
    main()