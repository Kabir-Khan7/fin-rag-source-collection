"""
Service layer for the Bank Feed (stg_bank_feed) resource.

Orchestrates calls to the bank feed repository and converts Pydantic schemas
into dictionaries. Bronze-layer logic is intentionally minimal.
"""

from sqlalchemy.orm import Session

from app.models.bank_feed import BankFeed
from app.repositories.bank_feed_repo import BankFeedRepository
from app.schemas.bank_feed import BankFeedCreate, BankFeedUpdate
from pydantic import ValidationError

from app.utils.file_parser import parse_upload, FileParseError

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
    
    def bulk_create(self, records: list[BankFeedCreate]) -> int:
        """Insert multiple validated bank feed records in one transaction."""
        data_dicts = [record.model_dump() for record in records]
        return self.repository.bulk_create(data_dicts)

    def create_from_file(self, filename: str, content: bytes) -> int:
        """
        Parse an uploaded file and insert all rows (all-or-nothing).

        Every row is validated against BankFeedCreate before any insert.
        If any row is invalid, nothing is inserted.

        Args:
            filename: The uploaded file's name (for type detection).
            content: The raw bytes of the file.

        Returns:
            int: The number of records inserted.

        Raises:
            FileParseError: If the file cannot be parsed.
            ValidationError: If any row fails schema validation.
        """
        raw_rows = parse_upload(filename, content)

        validated: list[BankFeedCreate] = []
        for index, row in enumerate(raw_rows, start=1):
            try:
                validated.append(BankFeedCreate(**row))
            except ValidationError as exc:
                raise ValidationError.from_exception_data(
                    title=f"Row {index} is invalid",
                    line_errors=exc.errors(),
                ) from exc

        data_dicts = [record.model_dump() for record in validated]
        return self.repository.bulk_create(data_dicts)