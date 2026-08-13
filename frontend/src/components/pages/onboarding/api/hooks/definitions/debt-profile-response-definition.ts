import { DebtEntryDefinition } from './debt-entry-definition';
import ExpensePaymentScheduleDefinition from './expense-payment-schedule-definition';

import { PayPeriodType } from 'components/pages/onboarding/types/pay-period-type';

export default interface DebtProfileResponseDefinition {
  income_per_pay_period_cents: number;
  pay_period_type: PayPeriodType;
  debts: DebtEntryDefinition[];
  next_pay_date: string | null;
  payment_schedules: ExpensePaymentScheduleDefinition[];
}
