"""
Pydantic schemas for the Raw Invoices (stg_raw_invoices) resource.

Defines this table's specific API data contracts. The JSON accepted and
returned matches only the raw invoices columns.
"""

from pydantic import BaseModel, ConfigDict


class RawInvoiceBase(BaseModel):
    """Shared raw invoice fields. All optional strings, per Bronze design."""

    Vendor_ID: str | None = None
    Vendor_Name: str | None = None
    Invoice_Number: str | None = None
    Invoice_Date: str | None = None
    Line_Item_Description: str | None = None
    Line_Item_Quantity: str | None = None
    Line_Item_Unit_Price: str | None = None
    Total_Tax: str | None = None
    Grand_Total: str | None = None
    Raw_Text: str | None = None


class RawInvoiceCreate(RawInvoiceBase):
    """Schema for creating a record (POST body). Excludes 'id'."""

    pass


class RawInvoiceUpdate(RawInvoiceBase):
    """Schema for updating a record (PUT body)."""

    pass


class RawInvoiceResponse(RawInvoiceBase):
    """Schema for data returned to the client. Includes 'id'."""

    id: int

    model_config = ConfigDict(from_attributes=True)