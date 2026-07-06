"""
Service layer for the Raw Invoices (stg_raw_invoices) resource.

Orchestrates calls to the repository and converts Pydantic schemas into
dictionaries. Bronze-layer logic is intentionally minimal.
"""

from sqlalchemy.orm import Session

from app.models.raw_invoices import RawInvoice
from app.repositories.raw_invoices_repo import RawInvoiceRepository
from app.schemas.raw_invoices import RawInvoiceCreate, RawInvoiceUpdate


class RawInvoiceService:
    """Business-logic layer for raw invoice operations."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.repository = RawInvoiceRepository(db)

    def create_raw_invoice(self, data: RawInvoiceCreate) -> RawInvoice:
        """Create a new raw invoice record."""
        return self.repository.create(data.model_dump())

    def get_raw_invoices(self, skip: int = 0, limit: int = 100) -> list[RawInvoice]:
        """Retrieve a paginated list of records."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_raw_invoice(self, record_id: int) -> RawInvoice | None:
        """Retrieve a single record by id."""
        return self.repository.get_by_id(record_id)

    def update_raw_invoice(
        self, record_id: int, data: RawInvoiceUpdate
    ) -> RawInvoice | None:
        """Update an existing record."""
        return self.repository.update(record_id, data.model_dump(exclude_unset=True))

    def delete_raw_invoice(self, record_id: int) -> bool:
        """Delete a record by id."""
        return self.repository.delete(record_id)