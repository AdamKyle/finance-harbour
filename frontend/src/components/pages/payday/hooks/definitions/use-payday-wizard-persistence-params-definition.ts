import { BudgetLineItemDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-line-item-definition';
import PaydayDebtBalanceCheckDefinition from 'components/pages/payday/api/hooks/definitions/payday-debt-balance-check-definition';
import PaydayDetailResponseDefinition from 'components/pages/payday/api/hooks/definitions/payday-detail-response-definition';

export default interface UsePaydayWizardPersistenceParamsDefinition {
  detail: PaydayDetailResponseDefinition;
  period_id: number;
  line_items: BudgetLineItemDefinition[];
  debt_balance_checks: PaydayDebtBalanceCheckDefinition[];
  first_line_item_step_index: number;
  first_debt_balance_step_index: number;
  summary_step_index: number;
  refresh_detail: () => Promise<PaydayDetailResponseDefinition | null>;
  finish_payday: () => Promise<boolean>;
  focus_step_error: () => void;
}
