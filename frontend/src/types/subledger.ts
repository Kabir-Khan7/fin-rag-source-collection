export interface SubledgerCreate {
  Transaction_ID?: string;
  System_Timestamp?: string;
  Document_Date?: string;
  GL_Account_Code?: string;
  Entity_ID?: string;
  Amount?: string;
  Transaction_Type?: string;
  Status?: string;
  Description?: string;
}

export interface SubledgerResponse extends SubledgerCreate {
  id: number;
}