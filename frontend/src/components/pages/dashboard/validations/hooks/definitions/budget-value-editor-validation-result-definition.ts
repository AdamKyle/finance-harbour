import BudgetValueEditorFieldErrorsDefinition from 'components/pages/dashboard/validations/hooks/definitions/budget-value-editor-field-errors-definition';

export default interface BudgetValueEditorValidationResultDefinition {
  is_valid: boolean;
  step_error: string;
  field_errors: BudgetValueEditorFieldErrorsDefinition;
}
