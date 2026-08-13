import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';
import BudgetValueEditorValidationResultDefinition from 'components/pages/dashboard/validations/hooks/definitions/budget-value-editor-validation-result-definition';

export default interface UseBudgetValueEditorFormValidationDefinition {
  validateBudgetValueEditor: (
    field: BudgetValueField,
    amountDollars: string
  ) => BudgetValueEditorValidationResultDefinition;
}
