"""
Service layer for the Bank Feed (stg_bank_feed) resource.

Orchestrates calls to the bank feed repository and converts Pydantic schemas
into dictionaries. Bronze-layer logic is intentionally minimal.
"""

from sqlalchemy.orm import Session

from app.models.bank_feed import BankFeed
from app.repositories.bank_feed_repo import BankFeedRepository
from app.schemas.bank_feed import BankFeedCreate, BankFeedUpdate


class BankFeedService:
    """Business-logic layer for bank feed operations."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.repository = BankFeedRepository(db)

    def create_bank_feed(self, data: BankFeedCreate) -> BankFeed:
        """Create a new bank feed record."""
        return self.repository.create(data.model_dump())

    def get_bank_feeds(self, skip: int = 0, limit: int = 100) -> list[BankFeed]:
        """Retrieve a paginated list of bank feed records."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_bank_feed(self, record_id: int) -> BankFeed | None:
        """Retrieve a single bank feed record by id."""
        return self.repository.get_by_id(record_id)

    def update_bank_feed(
        self, record_id: int, data: BankFeedUpdate
    ) -> BankFeed | None:
        """Update an existing bank feed record."""
        return self.repository.update(record_id, data.model_dump(exclude_unset=True))

    def delete_bank_feed(self, record_id: int) -> bool:
        """Delete a bank feed record by id."""
        return self.repository.delete(record_id)