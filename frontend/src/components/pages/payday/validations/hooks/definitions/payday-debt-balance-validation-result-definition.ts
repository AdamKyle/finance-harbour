import PaydayDebtBalanceFieldErrorsDefinition from './payday-debt-balance-field-errors-definition';

export default interface PaydayDebtBalanceValidationResultDefinition {
  is_valid: boolean;
  step_error: string | null;
  field_errors: PaydayDebtBalanceFieldErrorsDefinition;
}
