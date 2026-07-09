"""
Data warehouse pipeline orchestrator.

Runs the Bronze -> Silver transformation stored procedures in dependency
order, aggregates their results, and produces a run summary. This is the
"conductor": it decides what runs and in what order, while the stored
procedures perform the actual transformation.
"""

from dataclasses import dataclass, field

from app.pipeline.runner import run_transform, TransformResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Transformation steps in dependency order.
# Reference tables first, then fact-like tables. As we add more
# procedures (Milestone 5), they get appended here.
TRANSFORM_STEPS: list[str] = [
    "dbo.usp_transform_subledger",
    "dbo.usp_transform_chart_of_accounts",
    "dbo.usp_transform_entities",
    "dbo.usp_transform_bank_feed",
    "dbo.usp_transform_invoices",
]


@dataclass
class PipelineRunSummary:
    """Aggregated summary of a full pipeline run."""

    results: list[TransformResult] = field(default_factory=list)
    failed_step: str | None = None
    error: str | None = None

    @property
    def total_inserted(self) -> int:
        return sum(r.inserted for r in self.results)

    @property
    def total_quarantined(self) -> int:
        return sum(r.quarantined for r in self.results)

    @property
    def succeeded(self) -> bool:
        return self.failed_step is None


def run_pipeline() -> PipelineRunSummary:
    """
    Run all Bronze -> Silver transformation steps in order.

    If a step fails, the pipeline stops (later steps do not run) and the
    summary records which step failed. Each step is independent at the DB
    level (its own transaction), so completed steps stay committed.

    Returns:
        PipelineRunSummary: Aggregated results and any failure information.
    """
    logger.info("=== Pipeline run started ===")
    summary = PipelineRunSummary()

    for step in TRANSFORM_STEPS:
        try:
            result = run_transform(step)
            summary.results.append(result)
        except Exception as exc:
            summary.failed_step = step
            summary.error = str(exc)
            logger.error("Pipeline stopped at %s: %s", step, exc)
            break

    if summary.succeeded:
        logger.info(
            "=== Pipeline run complete — inserted=%d quarantined=%d ===",
            summary.total_inserted,
            summary.total_quarantined,
        )
    else:
        logger.error("=== Pipeline run FAILED at %s ===", summary.failed_step)

    return summary