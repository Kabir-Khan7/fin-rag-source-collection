"""
Repository for the Bank Feed (stg_bank_feed) resource.

Handles all direct database access for bank feed records. Fully isolated —
bound only to the BankFeed model and the dbo.stg_bank_feed table.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bank_feed import BankFeed


class BankFeedRepository:
    """CRUD database operations for BankFeed (stg_bank_feed) records."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self.db = db

    def create(self, data: dict) -> BankFeed:
        """Insert a new bank feed record and return it with its generated id."""
        obj = BankFeed(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_all(self, skip: int = 0, limit: int = 100) -> list[BankFeed]:
        """Retrieve a paginated list of bank feed records."""
        stmt = (
            select(BankFeed)
            .order_by(BankFeed.id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, record_id: int) -> BankFeed | None:
        """Retrieve a single bank feed record by its surrogate id."""
        return self.db.get(BankFeed, record_id)

    def update(self, record_id: int, data: dict) -> BankFeed | None:
        """Update an existing bank feed record by id. Returns None if not found."""
        obj = self.db.get(BankFeed, record_id)
        if obj is None:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, record_id: int) -> bool:
        """Delete a bank feed record by id. Returns True if deleted, else False."""
        obj = self.db.get(BankFeed, record_id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
    
    def bulk_create(self, data_list: list[dict]) -> int:
        """
        Insert multiple bank feed records in a single database transaction.

        All rows are committed together; a failure rolls back the entire
        batch (all-or-nothing at the DB level).

        Args:
            data_list: A list of dictionaries, one per record.

        Returns:
            int: The number of records inserted.
        """
        objects = [BankFeed(**data) for data in data_list]
        self.db.add_all(objects)
        self.db.commit()
        return len(objects)