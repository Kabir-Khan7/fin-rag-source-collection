"""
Service layer for the Chart of Accounts (stg_chart_of_accounts) resource.

Orchestrates calls to the repository and converts Pydantic schemas into
dictionaries. Bronze-layer logic is intentionally minimal.
"""

from sqlalchemy.orm import Session

from app.models.chart_of_accounts import ChartOfAccounts
from app.repositories.chart_of_accounts_repo import ChartOfAccountsRepository
from app.schemas.chart_of_accounts import (
    ChartOfAccountsCreate,
    ChartOfAccountsUpdate,
)


class ChartOfAccountsService:
    """Business-logic layer for chart of accounts operations."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.repository = ChartOfAccountsRepository(db)

    def create_chart_of_accounts(
        self, data: ChartOfAccountsCreate
    ) -> ChartOfAccounts:
        """Create a new chart of accounts record."""
        return self.repository.create(data.model_dump())

    def get_chart_of_accounts_list(
        self, skip: int = 0, limit: int = 100
    ) -> list[ChartOfAccounts]:
        """Retrieve a paginated list of records."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_chart_of_accounts(self, record_id: int) -> ChartOfAccounts | None:
        """Retrieve a single record by id."""
        return self.repository.get_by_id(record_id)

    def update_chart_of_accounts(
        self, record_id: int, data: ChartOfAccountsUpdate
    ) -> ChartOfAccounts | None:
        """Update an existing record."""
        return self.repository.update(record_id, data.model_dump(exclude_unset=True))

    def delete_chart_of_accounts(self, record_id: int) -> bool:
        """Delete a record by id."""
        return self.repository.delete(record_id)