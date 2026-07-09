"""
API endpoints for triggering and monitoring the data warehouse pipeline.

Exposes the Bronze -> Silver transformation pipeline over HTTP so it can be
triggered from the frontend or other tools, in addition to the CLI.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.pipeline.orchestrator import run_pipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


class StepResult(BaseModel):
    """Per-table transformation result."""

    source_table: str
    inserted: int
    quarantined: int
    watermark: int


class PipelineRunResponse(BaseModel):
    """Response summarizing a pipeline run."""

    succeeded: bool
    total_inserted: int
    total_quarantined: int
    failed_step: str | None = None
    error: str | None = None
    results: list[StepResult]


@router.post(
    "/run",
    response_model=PipelineRunResponse,
    summary="Run the Bronze to Silver transformation pipeline",
)
def trigger_pipeline() -> PipelineRunResponse:
    """
    Run all Bronze -> Silver transformation steps in dependency order.

    Processes only new Bronze rows (incremental, watermark-based). Returns
    a summary of rows inserted and quarantined per table.
    """
    logger.info("Pipeline triggered via API")
    summary = run_pipeline()

    return PipelineRunResponse(
        succeeded=summary.succeeded,
        total_inserted=summary.total_inserted,
        total_quarantined=summary.total_quarantined,
        failed_step=summary.failed_step,
        error=summary.error,
        results=[
            StepResult(
                source_table=r.source_table,
                inserted=r.inserted,
                quarantined=r.quarantined,
                watermark=r.watermark,
            )
            for r in summary.results
        ],
    )