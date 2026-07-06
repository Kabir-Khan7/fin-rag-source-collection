"""
Pydantic schemas for the Chart of Accounts (stg_chart_of_accounts) resource.

Defines this table's specific API data contracts. The JSON accepted and
returned matches only the chart of accounts columns.
"""

from pydantic import BaseModel, ConfigDict


class ChartOfAccountsBase(BaseModel):
    """Shared chart of accounts fields. All optional strings, per Bronze design."""

    GL_Account_Code: str | None = None
    Account_Name: str | None = None
    Account_Class: str | None = None
    Financial_Statement_Section: str | None = None


class ChartOfAccountsCreate(ChartOfAccountsBase):
    """Schema for creating a record (POST body). Excludes 'id'."""

    pass


class ChartOfAccountsUpdate(ChartOfAccountsBase):
    """Schema for updating a record (PUT body)."""

    pass


class ChartOfAccountsResponse(ChartOfAccountsBase):
    """Schema for data returned to the client. Includes 'id'."""

    id: int

    model_config = ConfigDict(from_attributes=True)