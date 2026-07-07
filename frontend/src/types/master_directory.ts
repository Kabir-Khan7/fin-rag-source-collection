export interface MasterDirectoryCreate {
  Legal_Name?: string;
  Trade_Name?: string;
  Tax_Registration_Number?: string;
  Country_Code?: string;
  Account_Creation_Date?: string;
  Is_Active?: string;
  Entity_ID?: string;
}

export interface MasterDirectoryResponse extends MasterDirectoryCreate {
  id: number;
}