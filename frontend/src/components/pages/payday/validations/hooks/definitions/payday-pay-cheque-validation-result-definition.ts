import PaydayPayChequeFieldErrorsDefinition from './payday-pay-cheque-field-errors-definition';

export default interface PaydayPayChequeValidationResultDefinition {
  is_valid: boolean;
  step_error: string | null;
  field_errors: PaydayPayChequeFieldErrorsDefinition;
}
