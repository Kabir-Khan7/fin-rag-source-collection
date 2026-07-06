"""
Pydantic schemas for the Transaction (stg_subledger) resource.

These schemas define the API's data contracts — what clients send when
creating or updating records, and what the API returns in responses.
They are intentionally separate from the SQLAlchemy ORM model, since
the shape of API data differs from the database structure (e.g., clients
never supply the surrogate 'id' — the database generates it).
"""

from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    """
    Shared fields common to create and update operations.

    All fields are optional strings, mirroring the Bronze-layer table
    where every business column is a nullable varchar. Raw data is
    accepted as-is; transformation happens later in the Silver layer.
    """

    Transaction_ID: str | None = None
    System_Timestamp: str | None = None
    Document_Date: str | None = None
    GL_Account_Code: str | None = None
    Entity_ID: str | None = None
    Amount: str | None = None
    Transaction_Type: str | None = None
    Status: str | None = None
    Description: str | None = None


class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction (POST request body).

    Inherits all fields from TransactionBase. Notably, it does NOT include
    'id' — SQL Server generates that automatically via IDENTITY.
    """

    pass


class TransactionUpdate(TransactionBase):
    """
    Schema for updating an existing transaction (PUT request body).

    All fields remain optional so callers can update only what they need.
    """

    pass


class TransactionResponse(TransactionBase):
    """
    Schema for data returned to the client (API response body).

    Includes the surrogate 'id' so clients can reference the exact row
    for subsequent read, update, or delete operations.
    """

    id: int

    # Allows Pydantic to read data directly from ORM objects (not just dicts).
    model_config = ConfigDict(from_attributes=True)