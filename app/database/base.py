"""
SQLAlchemy declarative base.

Defines the Base class that all ORM models inherit from. This Base
maintains the metadata catalog describing all mapped tables.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Declarative base class for all ORM models.

    All database models in the application inherit from this class.
    SQLAlchemy uses it to track table metadata and enable ORM mapping.
    """

    pass