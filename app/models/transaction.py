"""
SQLAlchemy ORM model for the Bronze-layer staging table dbo.stg_subledger.

This model maps the raw staging table exactly as it exists in SQL Server.
All business columns are stored as strings (varchar), consistent with the
Bronze/raw layer of the medallion architecture — data is captured as-is,
and type transformation is handled later in the Silver layer via SQL
stored procedures.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Transaction(Base):
    """
    ORM model mapping the dbo.stg_subledger staging table.

    Represents a single raw subledger transaction record as ingested into
    the Bronze layer. The surrogate 'id' column is the primary key used for
    precise row-level CRUD operations; it is a technical column and does not
    carry business meaning.
    """

    __tablename__ = "stg_subledger"
    __table_args__ = {"schema": "dbo"}

    # Surrogate primary key — auto-incremented by SQL Server (IDENTITY).
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Business columns — all varchar, stored raw per Bronze-layer design.
    Transaction_ID: Mapped[str | None] = mapped_column(String(255), nullable=True)
    System_Timestamp: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Document_Date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    GL_Account_Code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Entity_ID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Amount: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Transaction_Type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    Status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Description: Mapped[str | None] = mapped_column(String, nullable=True)  # varchar(MAX)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the record."""
        return (
            f"<Transaction(id={self.id}, "
            f"Transaction_ID='{self.Transaction_ID}', "
            f"Status='{self.Status}')>"
        )