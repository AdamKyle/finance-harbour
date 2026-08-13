export enum PaydayReconciliationStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  REVIEWED = 'REVIEWED',
  INCOMPLETE = 'INCOMPLETE',
}

export enum PayChequeReviewStatus {
  UNREVIEWED = 'UNREVIEWED',
  CONFIRMED = 'CONFIRMED',
  UNKNOWN = 'UNKNOWN',
}

export enum PaymentReviewStatus {
  UNREVIEWED = 'UNREVIEWED',
  PAID = 'PAID',
  NOT_PAID = 'NOT_PAID',
  UNKNOWN = 'UNKNOWN',
  SCHEDULED = 'SCHEDULED',
}

export enum DebtBalanceReviewStatus {
  UNREVIEWED = 'UNREVIEWED',
  CONFIRMED = 'CONFIRMED',
  UNKNOWN = 'UNKNOWN',
}
