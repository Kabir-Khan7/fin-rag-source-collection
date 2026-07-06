"""
Aggregates all v1 API endpoint routers into a single router.

Registers the CRUD routers for all five Bronze-layer staging tables.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    bank_feed,
    chart_of_accounts,
    master_directory,
    raw_invoices,
    transactions,
)

api_router = APIRouter()
api_router.include_router(transactions.router)
api_router.include_router(bank_feed.router)
api_router.include_router(chart_of_accounts.router)
api_router.include_router(master_directory.router)
api_router.include_router(raw_invoices.router)