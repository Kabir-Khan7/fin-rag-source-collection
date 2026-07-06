"""
Service layer for the Master Directory (stg_master_directory) resource.

Orchestrates calls to the repository and converts Pydantic schemas into
dictionaries. Bronze-layer logic is intentionally minimal.
"""

from sqlalchemy.orm import Session

from app.models.master_directory import MasterDirectory
from app.repositories.master_directory_repo import MasterDirectoryRepository
from app.schemas.master_directory import (
    MasterDirectoryCreate,
    MasterDirectoryUpdate,
)


class MasterDirectoryService:
    """Business-logic layer for master directory operations."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.repository = MasterDirectoryRepository(db)

    def create_master_directory(
        self, data: MasterDirectoryCreate
    ) -> MasterDirectory:
        """Create a new master directory record."""
        return self.repository.create(data.model_dump())

    def get_master_directory_list(
        self, skip: int = 0, limit: int = 100
    ) -> list[MasterDirectory]:
        """Retrieve a paginated list of records."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_master_directory(self, record_id: int) -> MasterDirectory | None:
        """Retrieve a single record by id."""
        return self.repository.get_by_id(record_id)

    def update_master_directory(
        self, record_id: int, data: MasterDirectoryUpdate
    ) -> MasterDirectory | None:
        """Update an existing record."""
        return self.repository.update(record_id, data.model_dump(exclude_unset=True))

    def delete_master_directory(self, record_id: int) -> bool:
        """Delete a record by id."""
        return self.repository.delete(record_id)