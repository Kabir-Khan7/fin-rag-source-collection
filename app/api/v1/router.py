from fastapi import APIRouter

from app.api.v1.endpoints import (
    bank_feed,
    chart_of_accounts,
    master_directory,
    pipeline,
    raw_invoices,
    transactions,
)

api_router = APIRouter()
api_router.include_router(transactions.router)
api_router.include_router(bank_feed.router)
api_router.include_router(chart_of_accounts.router)
api_router.include_router(master_directory.router)
api_router.include_router(raw_invoices.router)
api_router.include_router(pipeline.router)