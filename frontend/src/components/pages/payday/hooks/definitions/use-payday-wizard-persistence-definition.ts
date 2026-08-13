import PaydayWarningDefinition from 'components/pages/payday/api/hooks/definitions/payday-warning-definition';
import UseUpdatePaydayDebtBalanceDefinition from 'components/pages/payday/api/hooks/definitions/use-update-payday-debt-balance-definition';
import UseUpdatePaydayLineItemDefinition from 'components/pages/payday/api/hooks/definitions/use-update-payday-line-item-definition';
import UseUpdatePaydayPayChequeDefinition from 'components/pages/payday/api/hooks/definitions/use-update-payday-pay-cheque-definition';
import PaydayDebtBalanceFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-debt-balance-field-errors-definition';
import PaydayLineItemFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-line-item-field-errors-definition';
import PaydayPayChequeFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-pay-cheque-field-errors-definition';

export default interface UsePaydayWizardPersistenceDefinition {
  warnings: PaydayWarningDefinition[];
  displayed_error: string | null;
  pay_cheque_errors: PaydayPayChequeFieldErrorsDefinition;
  line_item_errors: PaydayLineItemFieldErrorsDefinition;
  debt_balance_errors: PaydayDebtBalanceFieldErrorsDefinition;
  pay_cheque_mutation: UseUpdatePaydayPayChequeDefinition;
  line_item_mutation: UseUpdatePaydayLineItemDefinition;
  debt_balance_mutation: UseUpdatePaydayDebtBalanceDefinition;
  is_loading: boolean;
  requested_step_index: number | undefined;
  persist_step: (current_index: number) => Promise<boolean>;
  handle_step_change: (
    current_index: number,
    target_index: number
  ) => Promise<boolean>;
}
