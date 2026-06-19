import { SaveMonthlyExpenseRequestDefinition } from './save-monthly-expense-request-definition';

export interface UseSaveMonthlyExpenseDefinition {
  save: (
    data: SaveMonthlyExpenseRequestDefinition
  ) => Promise<{ ok: boolean; error?: string }>;
  loading: boolean;
}
