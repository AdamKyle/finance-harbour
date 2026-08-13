import PaydayDebtBalanceUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-debt-balance-update-request-definition';
import PaydayLineItemUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-line-item-update-request-definition';
import PaydayPayChequeUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-pay-cheque-update-request-definition';
import PaydayDebtBalanceValidationResultDefinition from 'components/pages/payday/validations/hooks/definitions/payday-debt-balance-validation-result-definition';
import PaydayLineItemValidationResultDefinition from 'components/pages/payday/validations/hooks/definitions/payday-line-item-validation-result-definition';
import PaydayPayChequeValidationResultDefinition from 'components/pages/payday/validations/hooks/definitions/payday-pay-cheque-validation-result-definition';

export default interface UsePaydayFormValidationDefinition {
  validatePayChequeStep: (
    request: PaydayPayChequeUpdateRequestDefinition
  ) => PaydayPayChequeValidationResultDefinition;
  validateLineItemStep: (
    request: PaydayLineItemUpdateRequestDefinition
  ) => PaydayLineItemValidationResultDefinition;
  validateDebtBalanceStep: (
    request: PaydayDebtBalanceUpdateRequestDefinition
  ) => PaydayDebtBalanceValidationResultDefinition;
}
