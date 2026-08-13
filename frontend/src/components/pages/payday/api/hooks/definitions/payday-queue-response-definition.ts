import {
  PayChequeReviewStatus,
  PaydayReconciliationStatus,
} from 'components/pages/payday/enums/payday-status';

export interface PaydayQueuePeriodDefinition {
  id: number;
  pay_date: string;
  payday_reconciliation_status: PaydayReconciliationStatus;
  pay_cheque_review_status: PayChequeReviewStatus;
}

export interface PaydayQueueResponseDefinition {
  effective_date: string;
  unresolved_count: number;
  unresolved_periods: PaydayQueuePeriodDefinition[];
  oldest_unresolved_period: PaydayQueuePeriodDefinition | null;
  next_future_pay_date: string | null;
}
