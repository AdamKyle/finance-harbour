import { SaveRequiredExpensesRequestDefinition } from './save-required-expenses-request-definition';

export interface UseSaveRequiredExpensesDefinition {
  save: (
    request: SaveRequiredExpensesRequestDefinition
  ) => Promise<{ ok: boolean; error?: string }>;
  loading: boolean;
}
