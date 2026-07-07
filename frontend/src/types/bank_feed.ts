export interface BankFeedCreate {
  Bank_Row_ID?: string;
  Booking_Date?: string;
  Value_Date?: string;
  Transaction_Text_Narrative?: string;
  Amount?: string;
  Running_Balance?: string;
}

export interface BankFeedResponse extends BankFeedCreate {
  id: number;
}