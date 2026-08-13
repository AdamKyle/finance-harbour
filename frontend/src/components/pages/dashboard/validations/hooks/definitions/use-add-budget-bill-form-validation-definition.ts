import AddBudgetBillRequestDefinition from 'components/pages/dashboard/api/hooks/definitions/add-budget-bill-request-definition';
import AddBudgetBillValidationResultDefinition from 'components/pages/dashboard/validations/hooks/definitions/add-budget-bill-validation-result-definition';

export default interface UseAddBudgetBillFormValidationDefinition {
  validateAddBudgetBill: (
    requestData: AddBudgetBillRequestDefinition
  ) => AddBudgetBillValidationResultDefinition;
}
