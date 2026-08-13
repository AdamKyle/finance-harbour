import AddBudgetBillFieldErrorsDefinition from './add-budget-bill-field-errors-definition';

export default interface AddBudgetBillValidationResultDefinition {
  is_valid: boolean;
  step_error: string;
  field_errors: AddBudgetBillFieldErrorsDefinition;
}
