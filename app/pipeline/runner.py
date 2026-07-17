"""
Stored procedure runner for the data warehouse pipeline.

Executes transformation stored procedures against MS SQL Server and returns
the counts they report. Python orchestrates (decides what runs and when);
the stored procedures perform the actual set-based transformation.
"""

from dataclasses import dataclass

from sqlalchemy import text

from app.database.session import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TransformResult:
    """Counts returned by a transformation stored procedure."""

    source_table: str
    processed: int
    inserted: int
    quarantined: int
    watermark: int


def run_transform(procedure_name: str) -> TransformResult:
    """
    Execute a transformation stored procedure and return its result counts.

    The procedure is expected to return a single row with the columns:
    source_table, processed, inserted, quarantined, watermark.

    Args:
        procedure_name: The stored procedure to run, e.g.
            'dbo.usp_transform_subledger'.

    Returns:
        TransformResult: The counts reported by the procedure.

    Raises:
        Exception: Re-raises any database error (the SP rolls back on failure).
    """
    db = SessionLocal()
    try:
        logger.info("Running transformation: %s", procedure_name)

        # EXEC the procedure. It returns a result set with the counts.
        result = db.execute(text(f"EXEC {procedure_name}"))
        row = result.fetchone()
        # Commit so the SP's committed work is finalized on this connection.
        db.commit()

        if row is None:
            raise RuntimeError(
                f"{procedure_name} returned no result row."
            )

        transform_result = TransformResult(
            source_table=row.source_table,
            processed=row.processed,
            inserted=row.inserted,
            quarantined=row.quarantined,
            watermark=row.watermark,
        )

        logger.info(
            "%s complete — processed=%d inserted=%d quarantined=%d watermark=%d",
            procedure_name,
            transform_result.processed,
            transform_result.inserted,
            transform_result.quarantined,
            transform_result.watermark,
        )
        return transform_result

    except Exception as exc:
        db.rollback()
        logger.error("Transformation %s failed: %s", procedure_name, exc, exc_info=True)
        raise
    finally:
        db.close()
        
@dataclass
class GoldBuildResult:
    """Counts returned by a Gold metric-build stored procedure."""

    metric_table: str
    rows_built: int


def run_gold_build(procedure_name: str) -> GoldBuildResult:
    """
    Execute a Gold metric-build stored procedure and return its count.

    Gold procedures full-refresh their target table and return a single
    row: (metric_table, rows_built).

    Args:
        procedure_name: e.g. 'dbo.usp_build_account_balances'.

    Returns:
        GoldBuildResult: The table name and number of rows built.
    """
    db = SessionLocal()
    try:
        logger.info("Running Gold build: %s", procedure_name)
        result = db.execute(text(f"EXEC {procedure_name}"))
        row = result.fetchone()
        db.commit()

        if row is None:
            raise RuntimeError(f"{procedure_name} returned no result row.")

        build_result = GoldBuildResult(
            metric_table=row.metric_table,
            rows_built=row.rows_built,
        )
        logger.info("%s complete — rows_built=%d", procedure_name, build_result.rows_built)
        return build_result

    except Exception as exc:
        db.rollback()
        logger.error("Gold build %s failed: %s", procedure_name, exc, exc_info=True)
        raise
    finally:
        db.close()