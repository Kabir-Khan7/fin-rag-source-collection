export interface RawInvoiceCreate {
  Vendor_ID?: string;
  Vendor_Name?: string;
  Invoice_Number?: string;
  Invoice_Date?: string;
  Line_Item_Description?: string;
  Line_Item_Quantity?: string;
  Line_Item_Unit_Price?: string;
  Total_Tax?: string;
  Grand_Total?: string;
  Raw_Text?: string;
}

export interface RawInvoiceResponse extends RawInvoiceCreate {
  id: number;
}