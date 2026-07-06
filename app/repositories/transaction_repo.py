"""
Repository for the Transaction (stg_subledger) resource.

Handles all direct database access for subledger transactions. This is the
only layer that touches the SQLAlchemy session for this resource. Written
explicitly (no shared base) so each table's data access is fully isolated
and independently auditable.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:
    """CRUD database operations for Transaction (stg_subledger) records."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self.db = db

    def create(self, data: dict) -> Transaction:
        """Insert a new subledger record and return it with its generated id."""
        obj = Transaction(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Transaction]:
        """Retrieve a paginated list of subledger records."""
        stmt = select(Transaction).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, record_id: int) -> Transaction | None:
        """Retrieve a single subledger record by its surrogate id."""
        return self.db.get(Transaction, record_id)

    def update(self, record_id: int, data: dict) -> Transaction | None:
        """Update an existing subledger record by id. Returns None if not found."""
        obj = self.db.get(Transaction, record_id)
        if obj is None:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, record_id: int) -> bool:
        """Delete a subledger record by id. Returns True if deleted, else False."""
        obj = self.db.get(Transaction, record_id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True