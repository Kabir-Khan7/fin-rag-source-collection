"""
Pydantic schemas for the Master Directory (stg_master_directory) resource.

Defines this table's specific API data contracts. The JSON accepted and
returned matches only the master directory columns.
"""

from pydantic import BaseModel, ConfigDict


class MasterDirectoryBase(BaseModel):
    """Shared master directory fields. All optional strings, per Bronze design."""

    Legal_Name: str | None = None
    Trade_Name: str | None = None
    Tax_Registration_Number: str | None = None
    Country_Code: str | None = None
    Account_Creation_Date: str | None = None
    Is_Active: str | None = None
    Entity_ID: str | None = None


class MasterDirectoryCreate(MasterDirectoryBase):
    """Schema for creating a record (POST body). Excludes 'id'."""

    pass


class MasterDirectoryUpdate(MasterDirectoryBase):
    """Schema for updating a record (PUT body)."""

    pass


class MasterDirectoryResponse(MasterDirectoryBase):
    """Schema for data returned to the client. Includes 'id'."""

    id: int

    model_config = ConfigDict(from_attributes=True)