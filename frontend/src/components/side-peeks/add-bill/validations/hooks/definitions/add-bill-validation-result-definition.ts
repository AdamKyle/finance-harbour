import AddBillFieldErrorsDefinition from './add-bill-field-errors-definition';

export default interface AddBillValidationResultDefinition {
  is_valid: boolean;
  step_error: string;
  field_errors: AddBillFieldErrorsDefinition;
}
