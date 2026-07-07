export interface ChartOfAccountsCreate {
  GL_Account_Code?: string;
  Account_Name?: string;
  Account_Class?: string;
  Financial_Statement_Section?: string;
}

export interface ChartOfAccountsResponse extends ChartOfAccountsCreate {
  id: number;
}