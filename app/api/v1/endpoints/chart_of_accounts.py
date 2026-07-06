"""
API endpoints for the Chart of Accounts (stg_chart_of_accounts) resource.

Defines full CRUD HTTP routes. Routes validate input against
chart-of-accounts-specific schemas and delegate to the service layer.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.chart_of_accounts import (
    ChartOfAccountsCreate,
    ChartOfAccountsResponse,
    ChartOfAccountsUpdate,
)
from app.services.chart_of_accounts_service import ChartOfAccountsService

router = APIRouter(prefix="/chart-of-accounts", tags=["Chart of Accounts"])


@router.post(
    "",
    response_model=ChartOfAccountsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chart of accounts record",
)
def create_chart_of_accounts(
    payload: ChartOfAccountsCreate,
    db: Session = Depends(get_db),
) -> ChartOfAccountsResponse:
    """Insert a new raw chart of accounts record into the Bronze staging table."""
    service = ChartOfAccountsService(db)
    return service.create_chart_of_accounts(payload)


@router.get(
    "",
    response_model=list[ChartOfAccountsResponse],
    summary="List chart of accounts records",
)
def list_chart_of_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[ChartOfAccountsResponse]:
    """Retrieve a paginated list of chart of accounts records."""
    service = ChartOfAccountsService(db)
    return service.get_chart_of_accounts_list(skip=skip, limit=limit)


@router.get(
    "/{record_id}",
    response_model=ChartOfAccountsResponse,
    summary="Get a chart of accounts record by id",
)
def get_chart_of_accounts(
    record_id: int,
    db: Session = Depends(get_db),
) -> ChartOfAccountsResponse:
    """Retrieve a single chart of accounts record by its surrogate id."""
    service = ChartOfAccountsService(db)
    record = service.get_chart_of_accounts(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart of accounts record with id {record_id} not found",
        )
    return record


@router.put(
    "/{record_id}",
    response_model=ChartOfAccountsResponse,
    summary="Update a chart of accounts record",
)
def update_chart_of_accounts(
    record_id: int,
    payload: ChartOfAccountsUpdate,
    db: Session = Depends(get_db),
) -> ChartOfAccountsResponse:
    """Update an existing chart of accounts record by id."""
    service = ChartOfAccountsService(db)
    record = service.update_chart_of_accounts(record_id, payload)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart of accounts record with id {record_id} not found",
        )
    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chart of accounts record",
)
def delete_chart_of_accounts(
    record_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a chart of accounts record by id."""
    service = ChartOfAccountsService(db)
    if not service.delete_chart_of_accounts(record_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart of accounts record with id {record_id} not found",
        )