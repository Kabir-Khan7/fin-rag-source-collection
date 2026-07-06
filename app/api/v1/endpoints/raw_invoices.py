"""
API endpoints for the Raw Invoices (stg_raw_invoices) resource.

Defines full CRUD HTTP routes. Routes validate input against
raw-invoice-specific schemas and delegate to the service layer.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.raw_invoices import (
    RawInvoiceCreate,
    RawInvoiceResponse,
    RawInvoiceUpdate,
)
from app.services.raw_invoices_service import RawInvoiceService

router = APIRouter(prefix="/raw-invoices", tags=["Raw Invoices"])


@router.post(
    "",
    response_model=RawInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new raw invoice record",
)
def create_raw_invoice(
    payload: RawInvoiceCreate,
    db: Session = Depends(get_db),
) -> RawInvoiceResponse:
    """Insert a new raw invoice record into the Bronze staging table."""
    service = RawInvoiceService(db)
    return service.create_raw_invoice(payload)


@router.get(
    "",
    response_model=list[RawInvoiceResponse],
    summary="List raw invoice records",
)
def list_raw_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[RawInvoiceResponse]:
    """Retrieve a paginated list of raw invoice records."""
    service = RawInvoiceService(db)
    return service.get_raw_invoices(skip=skip, limit=limit)


@router.get(
    "/{record_id}",
    response_model=RawInvoiceResponse,
    summary="Get a raw invoice record by id",
)
def get_raw_invoice(
    record_id: int,
    db: Session = Depends(get_db),
) -> RawInvoiceResponse:
    """Retrieve a single raw invoice record by its surrogate id."""
    service = RawInvoiceService(db)
    record = service.get_raw_invoice(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Raw invoice record with id {record_id} not found",
        )
    return record


@router.put(
    "/{record_id}",
    response_model=RawInvoiceResponse,
    summary="Update a raw invoice record",
)
def update_raw_invoice(
    record_id: int,
    payload: RawInvoiceUpdate,
    db: Session = Depends(get_db),
) -> RawInvoiceResponse:
    """Update an existing raw invoice record by id."""
    service = RawInvoiceService(db)
    record = service.update_raw_invoice(record_id, payload)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Raw invoice record with id {record_id} not found",
        )
    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a raw invoice record",
)
def delete_raw_invoice(
    record_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a raw invoice record by id."""
    service = RawInvoiceService(db)
    if not service.delete_raw_invoice(record_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Raw invoice record with id {record_id} not found",
        )