"""
Generic base repository providing reusable CRUD operations.

This module defines a single, generic repository class that implements
Create, Read, Update, and Delete logic once. Concrete repositories for
specific models inherit from it, eliminating duplication across the
project's many staging tables. Writing CRUD logic in one audited place
is especially valuable for financial data, where correctness is critical.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base

# A type variable bound to our SQLAlchemy Base. Any concrete model
# (Transaction, BankFeed, etc.) can fill this placeholder.
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository implementing standard CRUD operations.

    Concrete repositories subclass this and supply their specific model,
    inheriting all CRUD methods automatically.

    Type Parameters:
        ModelType: The SQLAlchemy ORM model this repository manages.
    """

    def __init__(self, model: type[ModelType], db: Session) -> None:
        """
        Initialize the repository.

        Args:
            model: The ORM model class this repository operates on.
            db: The active SQLAlchemy session (injected per request).
        """
        self.model = model
        self.db = db

    def create(self, data: dict[str, Any]) -> ModelType:
        """
        Insert a new record.

        Args:
            data: A dictionary of column names to values.

        Returns:
            ModelType: The newly created record, including its generated id.
        """
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Retrieve a paginated list of records.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            list[ModelType]: The retrieved records.
        """
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, record_id: int) -> ModelType | None:
        """
        Retrieve a single record by its surrogate primary key.

        Args:
            record_id: The 'id' primary key value.

        Returns:
            ModelType | None: The record if found, otherwise None.
        """
        return self.db.get(self.model, record_id)

    def update(
        self, record_id: int, data: dict[str, Any]
    ) -> ModelType | None:
        """
        Update an existing record by id.

        Only the fields present in `data` are modified.

        Args:
            record_id: The primary key of the record to update.
            data: Dictionary of fields to update.

        Returns:
            ModelType | None: The updated record, or None if not found.
        """
        obj = self.get_by_id(record_id)
        if obj is None:
            return None

        for field, value in data.items():
            setattr(obj, field, value)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, record_id: int) -> bool:
        """
        Delete a record by id.

        Args:
            record_id: The primary key of the record to delete.

        Returns:
            bool: True if deleted, False if the record was not found.
        """
        obj = self.get_by_id(record_id)
        if obj is None:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True