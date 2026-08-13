import PaydayLineItemFieldErrorsDefinition from './payday-line-item-field-errors-definition';

export default interface PaydayLineItemValidationResultDefinition {
  is_valid: boolean;
  step_error: string | null;
  field_errors: PaydayLineItemFieldErrorsDefinition;
}
