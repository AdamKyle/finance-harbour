export interface DebtEntryDefinition {
  label: string;
  current_balance_cents: number;
  interest_rate_basis_points: number;
  minimum_payment_cents: number;
  current_payment_cents: number;
}
