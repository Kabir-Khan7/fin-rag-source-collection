"""
API endpoints for the Master Directory (stg_master_directory) resource.

Defines full CRUD HTTP routes. Routes validate input against
master-directory-specific schemas and delegate to the service layer.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.master_directory import (
    MasterDirectoryCreate,
    MasterDirectoryResponse,
    MasterDirectoryUpdate,
)
from app.services.master_directory_service import MasterDirectoryService

router = APIRouter(prefix="/master-directory", tags=["Master Directory"])


@router.post(
    "",
    response_model=MasterDirectoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new master directory record",
)
def create_master_directory(
    payload: MasterDirectoryCreate,
    db: Session = Depends(get_db),
) -> MasterDirectoryResponse:
    """Insert a new raw master directory record into the Bronze staging table."""
    service = MasterDirectoryService(db)
    return service.create_master_directory(payload)


@router.get(
    "",
    response_model=list[MasterDirectoryResponse],
    summary="List master directory records",
)
def list_master_directory(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[MasterDirectoryResponse]:
    """Retrieve a paginated list of master directory records."""
    service = MasterDirectoryService(db)
    return service.get_master_directory_list(skip=skip, limit=limit)


@router.get(
    "/{record_id}",
    response_model=MasterDirectoryResponse,
    summary="Get a master directory record by id",
)
def get_master_directory(
    record_id: int,
    db: Session = Depends(get_db),
) -> MasterDirectoryResponse:
    """Retrieve a single master directory record by its surrogate id."""
    service = MasterDirectoryService(db)
    record = service.get_master_directory(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Master directory record with id {record_id} not found",
        )
    return record


@router.put(
    "/{record_id}",
    response_model=MasterDirectoryResponse,
    summary="Update a master directory record",
)
def update_master_directory(
    record_id: int,
    payload: MasterDirectoryUpdate,
    db: Session = Depends(get_db),
) -> MasterDirectoryResponse:
    """Update an existing master directory record by id."""
    service = MasterDirectoryService(db)
    record = service.update_master_directory(record_id, payload)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Master directory record with id {record_id} not found",
        )
    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a master directory record",
)
def delete_master_directory(
    record_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a master directory record by id."""
    service = MasterDirectoryService(db)
    if not service.delete_master_directory(record_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Master directory record with id {record_id} not found",
        )