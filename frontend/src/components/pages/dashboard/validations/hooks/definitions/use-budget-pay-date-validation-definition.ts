import BudgetPayDateValidationResultDefinition from './budget-pay-date-validation-result-definition';

export default interface UseBudgetPayDateValidationDefinition {
  validate_pay_date: (
    payDate: string,
    previousPayDate: string | null
  ) => BudgetPayDateValidationResultDefinition;
}
