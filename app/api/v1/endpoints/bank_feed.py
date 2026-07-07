"""
API endpoints for the Bank Feed (stg_bank_feed) resource.

Defines full CRUD HTTP routes for the bank feed staging table. Routes are
thin: they validate input against bank-feed-specific schemas, delegate to
the service layer, and shape HTTP responses.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.bank_feed import (
    BankFeedCreate,
    BankFeedResponse,
    BankFeedUpdate,
)
from app.services.bank_feed_service import BankFeedService
from fastapi import File, UploadFile
from pydantic import ValidationError

from app.schemas.bank_feed import BankFeedBulkResult
from app.utils.file_parser import FileParseError

router = APIRouter(prefix="/bank-feed", tags=["Bank Feed"])


@router.post(
    "",
    response_model=BankFeedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank feed record",
)
def create_bank_feed(
    payload: BankFeedCreate,
    db: Session = Depends(get_db),
) -> BankFeedResponse:
    """Insert a new raw bank feed record into the Bronze staging table."""
    service = BankFeedService(db)
    return service.create_bank_feed(payload)


@router.get(
    "",
    response_model=list[BankFeedResponse],
    summary="List bank feed records",
)
def list_bank_feeds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[BankFeedResponse]:
    """Retrieve a paginated list of bank feed records."""
    service = BankFeedService(db)
    return service.get_bank_feeds(skip=skip, limit=limit)


@router.get(
    "/{record_id}",
    response_model=BankFeedResponse,
    summary="Get a bank feed record by id",
)
def get_bank_feed(
    record_id: int,
    db: Session = Depends(get_db),
) -> BankFeedResponse:
    """Retrieve a single bank feed record by its surrogate id."""
    service = BankFeedService(db)
    record = service.get_bank_feed(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank feed record with id {record_id} not found",
        )
    return record


@router.put(
    "/{record_id}",
    response_model=BankFeedResponse,
    summary="Update a bank feed record",
)
def update_bank_feed(
    record_id: int,
    payload: BankFeedUpdate,
    db: Session = Depends(get_db),
) -> BankFeedResponse:
    """Update an existing bank feed record by id."""
    service = BankFeedService(db)
    record = service.update_bank_feed(record_id, payload)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank feed record with id {record_id} not found",
        )
    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bank feed record",
)
def delete_bank_feed(
    record_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a bank feed record by id."""
    service = BankFeedService(db)
    if not service.delete_bank_feed(record_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank feed record with id {record_id} not found",
        )
        
@router.post(
    "/bulk",
    response_model=BankFeedBulkResult,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk-create bank feed records from a JSON array",
)
def bulk_create_bank_feeds(
    payload: list[BankFeedCreate],
    db: Session = Depends(get_db),
) -> BankFeedBulkResult:
    """Insert multiple bank feed records from a JSON array (all-or-nothing)."""
    service = BankFeedService(db)
    count = service.bulk_create(payload)
    return BankFeedBulkResult(
        inserted_count=count,
        message=f"Successfully inserted {count} records.",
    )


@router.post(
    "/upload",
    response_model=BankFeedBulkResult,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk-create bank feed records from an uploaded .xlsx or .csv file",
)
async def upload_bank_feeds(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> BankFeedBulkResult:
    """
    Upload an Excel or CSV file and insert all rows (all-or-nothing).

    The file's header row must exactly match the table's column names.
    """
    content = await file.read()

    service = BankFeedService(db)
    try:
        count = service.create_from_file(file.filename, content)
    except FileParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        )

    return BankFeedBulkResult(
        inserted_count=count,
        message=f"Successfully inserted {count} records from {file.filename}.",
    )