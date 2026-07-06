"""
Repository for the Master Directory (stg_master_directory) resource.

Handles all direct database access for master directory records. Fully
isolated — bound only to the MasterDirectory model.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.master_directory import MasterDirectory


class MasterDirectoryRepository:
    """CRUD database operations for MasterDirectory records."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self.db = db

    def create(self, data: dict) -> MasterDirectory:
        """Insert a new record and return it with its generated id."""
        obj = MasterDirectory(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_all(self, skip: int = 0, limit: int = 100) -> list[MasterDirectory]:
        """Retrieve a paginated list of records."""
        stmt = select(MasterDirectory).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, record_id: int) -> MasterDirectory | None:
        """Retrieve a single record by its surrogate id."""
        return self.db.get(MasterDirectory, record_id)

    def update(self, record_id: int, data: dict) -> MasterDirectory | None:
        """Update an existing record by id. Returns None if not found."""
        obj = self.db.get(MasterDirectory, record_id)
        if obj is None:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, record_id: int) -> bool:
        """Delete a record by id. Returns True if deleted, else False."""
        obj = self.db.get(MasterDirectory, record_id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True