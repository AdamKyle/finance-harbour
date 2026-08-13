export enum PaydayApiUrls {
  QUEUE = '/budget/payday/queue/',
  DETAIL = '/budget/payday/pay-periods/:periodId/',
  PAY_CHEQUE = '/budget/payday/pay-periods/:periodId/pay-cheque/',
  LINE_ITEM = '/budget/payday/pay-periods/:periodId/line-items/:lineItemId/',
  DEBT_BALANCE = '/budget/payday/pay-periods/:periodId/debt-balance/',
  MARK_INCOMPLETE = '/budget/payday/pay-periods/:periodId/mark-incomplete/',
}
