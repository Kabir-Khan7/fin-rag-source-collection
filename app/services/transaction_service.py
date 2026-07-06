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