"""
Pydantic schemas for the Bank Feed (stg_bank_feed) resource.

Defines the API's data contracts for bank feed records. These schemas are
specific to this table — the JSON accepted and returned matches only the
bank feed columns, ensuring no cross-table data contamination.
"""

from pydantic import BaseModel, ConfigDict


class BankFeedBase(BaseModel):
    """Shared bank feed fields. All optional strings, per Bronze design."""

    Bank_Row_ID: str | None = None
    Booking_Date: str | None = None
    Value_Date: str | None = None
    Transaction_Text_Narrative: str | None = None
    Amount: str | None = None
    Running_Balance: str | None = None


class BankFeedCreate(BankFeedBase):
    """Schema for creating a bank feed record (POST body). Excludes 'id'."""

    pass


class BankFeedUpdate(BankFeedBase):
    """Schema for updating a bank feed record (PUT body)."""

    pass


class BankFeedResponse(BankFeedBase):
    """Schema for bank feed data returned to the client. Includes 'id'."""

    id: int

    model_config = ConfigDict(from_attributes=True)