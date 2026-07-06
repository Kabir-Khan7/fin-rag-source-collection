"""
SQLAlchemy ORM model for the Bronze-layer staging table dbo.stg_raw_invoices.

Maps the raw invoices staging table exactly as it exists in SQL Server. All
business columns are nullable varchar, per Bronze design. Note that
Line_Item_Description and Raw_Text are varchar(MAX) free-text fields.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RawInvoice(Base):
    """ORM model mapping the dbo.stg_raw_invoices staging table."""

    __tablename__ = "stg_raw_invoices"
    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    Vendor_ID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Vendor_Name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Invoice_Number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    Invoice_Date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Line_Item_Description: Mapped[str | None] = mapped_column(String, nullable=True)  # varchar(MAX)
    Line_Item_Quantity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Line_Item_Unit_Price: Mapped[str | None] = mapped_column(String(255), nullable=True)
    Total_Tax: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Grand_Total: Mapped[str | None] = mapped_column(String(50), nullable=True)
    Raw_Text: Mapped[str | None] = mapped_column(String, nullable=True)  # varchar(MAX)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<RawInvoice(id={self.id}, "
            f"Invoice_Number='{self.Invoice_Number}', "
            f"Vendor_Name='{self.Vendor_Name}')>"
        )