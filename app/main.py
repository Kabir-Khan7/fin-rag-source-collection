"""
Main application entry point for the Local RAG System.

Creates and configures the FastAPI application instance, registers routes,
and defines application-level endpoints.
"""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Phase 1: Source Collection - FastAPI backend connected to MS SQL Server.",
    version=settings.APP_VERSION,
)

# Register all v1 API routes under the /api/v1 prefix.
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Verifies the API server is running and responsive.
    """
    return {"status": "ok", "message": "Local RAG System is running"}