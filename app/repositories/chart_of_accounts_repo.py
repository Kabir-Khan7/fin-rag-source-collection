"""
Repository for the Chart of Accounts (stg_chart_of_accounts) resource.

Handles all direct database access for chart of accounts records. Fully
isolated — bound only to the ChartOfAccounts model.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chart_of_accounts import ChartOfAccounts


class ChartOfAccountsRepository:
    """CRUD database operations for ChartOfAccounts records."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self.db = db

    def create(self, data: dict) -> ChartOfAccounts:
        """Insert a new record and return it with its generated id."""
        obj = ChartOfAccounts(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ChartOfAccounts]:
        """Retrieve a paginated list of records."""
        stmt = select(ChartOfAccounts).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, record_id: int) -> ChartOfAccounts | None:
        """Retrieve a single record by its surrogate id."""
        return self.db.get(ChartOfAccounts, record_id)

    def update(self, record_id: int, data: dict) -> ChartOfAccounts | None:
        """Update an existing record by id. Returns None if not found."""
        obj = self.db.get(ChartOfAccounts, record_id)
        if obj is None:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, record_id: int) -> bool:
        """Delete a record by id. Returns True if deleted, else False."""
        obj = self.db.get(ChartOfAccounts, record_id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True