import { DebtEntryDefinition } from './debt-entry-definition';
import ExpensePaymentScheduleDefinition from './expense-payment-schedule-definition';

import { PayPeriodType } from 'components/pages/onboarding/types/pay-period-type';

export interface SaveDebtProfileRequestDefinition {
  income_per_pay_period_cents?: number;
  pay_period_type?: PayPeriodType;
  next_pay_date?: string | null;
  debts?: DebtEntryDefinition[];
  payment_schedules?: ExpensePaymentScheduleDefinition[];
}
