"""
Repository for the Raw Invoices (stg_raw_invoices) resource.

Handles all direct database access for raw invoice records. Fully isolated —
bound only to the RawInvoice model.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.raw_invoices import RawInvoice


class RawInvoiceRepository:
    """CRUD database operations for RawInvoice records."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self.db = db

    def create(self, data: dict) -> RawInvoice:
        """Insert a new record and return it with its generated id."""
        obj = RawInvoice(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_all(self, skip: int = 0, limit: int = 100) -> list[RawInvoice]:
        """Retrieve a paginated list of records."""
        stmt = select(RawInvoice).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, record_id: int) -> RawInvoice | None:
        """Retrieve a single record by its surrogate id."""
        return self.db.get(RawInvoice, record_id)

    def update(self, record_id: int, data: dict) -> RawInvoice | None:
        """Update an existing record by id. Returns None if not found."""
        obj = self.db.get(RawInvoice, record_id)
        if obj is None:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, record_id: int) -> bool:
        """Delete a record by id. Returns True if deleted, else False."""
        obj = self.db.get(RawInvoice, record_id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True