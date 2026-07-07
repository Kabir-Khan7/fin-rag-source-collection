"""
Service layer for the Transaction (stg_subledger) resource.

Contains business logic and orchestrates calls to the repository. Converts
Pydantic schemas into plain dictionaries before passing them to the generic
repository. For Bronze-layer ingestion this logic is intentionally minimal.
"""

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.transaction_repo import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.utils.file_parser import parse_upload, FileParseError
from pydantic import ValidationError

class TransactionService:
    """Business-logic layer for transaction operations."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.repository = TransactionRepository(db)

    def create_transaction(self, data: TransactionCreate) -> Transaction:
        """Create a new transaction record."""
        return self.repository.create(data.model_dump())

    def get_transactions(self, skip: int = 0, limit: int = 100) -> list[Transaction]:
        """Retrieve a paginated list of transactions."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_transaction(self, transaction_id: int) -> Transaction | None:
        """Retrieve a single transaction by id."""
        return self.repository.get_by_id(transaction_id)

    def update_transaction(
        self, transaction_id: int, data: TransactionUpdate
    ) -> Transaction | None:
        """Update an existing transaction."""
        return self.repository.update(
            transaction_id, data.model_dump(exclude_unset=True)
        )

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by id."""
        return self.repository.delete(transaction_id)
    
    def bulk_create(self, records: list[TransactionCreate]) -> int:
        """
        Insert multiple validated transaction records in one transaction.

        Args:
            records: A list of validated TransactionCreate schemas.

        Returns:
            int: The number of records inserted.
        """
        data_dicts = [record.model_dump() for record in records]
        return self.repository.bulk_create(data_dicts)

    def create_from_file(self, filename: str, content: bytes) -> int:
        """
        Parse an uploaded file and insert all rows (all-or-nothing).

        Every row is validated against the TransactionCreate schema BEFORE
        any insert occurs. If any row is invalid, the entire operation is
        rejected and nothing is inserted.

        Args:
            filename: The uploaded file's name (for type detection).
            content: The raw bytes of the file.

        Returns:
            int: The number of records inserted.

        Raises:
            FileParseError: If the file cannot be parsed.
            ValidationError: If any row fails schema validation.
        """
        # 1. Parse the file into raw row dicts.
        raw_rows = parse_upload(filename, content)

        # 2. Validate EVERY row first (all-or-nothing).
        validated: list[TransactionCreate] = []
        for index, row in enumerate(raw_rows, start=1):
            try:
                validated.append(TransactionCreate(**row))
            except ValidationError as exc:
                # Fail the whole file, pointing to the offending row.
                raise ValidationError.from_exception_data(
                    title=f"Row {index} is invalid",
                    line_errors=exc.errors(),
                ) from exc

        # 3. All valid — insert them.
        data_dicts = [record.model_dump() for record in validated]
        return self.repository.bulk_create(data_dicts)