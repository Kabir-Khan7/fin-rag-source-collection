"""
SQLAlchemy ORM model for the Bronze-layer staging table dbo.stg_chart_of_accounts.

Maps the raw chart of accounts staging table exactly as it exists in SQL
Server. All business columns are nullable varchar, per Bronze-layer design.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ChartOfAccounts(Base):
    """ORM model mapping the dbo.stg_chart_of_accounts staging table."""

    __tablename__ = "stg_chart_of_accounts"
    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    GL_Account_Code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Account_Name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Account_Class: Mapped[str | None] = mapped_column(String(100), nullable=True)
    Financial_Statement_Section: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<ChartOfAccounts(id={self.id}, "
            f"GL_Account_Code='{self.GL_Account_Code}', "
            f"Account_Name='{self.Account_Name}')>"
        )