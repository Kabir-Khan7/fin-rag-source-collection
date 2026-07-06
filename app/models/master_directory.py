"""
SQLAlchemy ORM model for the Bronze-layer staging table dbo.stg_master_directory.

Maps the raw master directory (entity) staging table exactly as it exists
in SQL Server. All business columns are nullable varchar, per Bronze design.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MasterDirectory(Base):
    """ORM model mapping the dbo.stg_master_directory staging table."""

    __tablename__ = "stg_master_directory"
    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    Legal_Name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Trade_Name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Tax_Registration_Number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    Country_Code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    Account_Creation_Date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Is_Active: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Entity_ID: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<MasterDirectory(id={self.id}, "
            f"Entity_ID='{self.Entity_ID}', "
            f"Legal_Name='{self.Legal_Name}')>"
        )