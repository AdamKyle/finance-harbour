import { DebtEntryDefinition } from './debt-entry-definition';

export interface SaveDebtProfileRequestDefinition {
  income_per_pay_period_cents?: number;
  pay_period_type?: string;
  debts?: DebtEntryDefinition[];
}
