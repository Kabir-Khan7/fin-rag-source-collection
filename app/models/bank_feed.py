"""
SQLAlchemy ORM model for the Bronze-layer staging table dbo.stg_bank_feed.

Maps the raw bank feed staging table exactly as it exists in SQL Server.
All business columns are nullable varchar, consistent with Bronze-layer
design — raw data is captured as-is; type transformation happens later in
the Silver layer via SQL stored procedures.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BankFeed(Base):
    """ORM model mapping the dbo.stg_bank_feed staging table."""

    __tablename__ = "stg_bank_feed"
    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    Bank_Row_ID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Booking_Date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Value_Date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Transaction_Text_Narrative: Mapped[str | None] = mapped_column(String, nullable=True)  # varchar(MAX)
    Amount: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Running_Balance: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<BankFeed(id={self.id}, "
            f"Bank_Row_ID='{self.Bank_Row_ID}', "
            f"Amount='{self.Amount}')>"
        )