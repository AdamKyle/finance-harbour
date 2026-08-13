import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';

export default interface BudgetPayDateEditorProps {
  period: BudgetPayPeriodDefinition;
  on_saved: (periodId: number) => Promise<void>;
  on_close: () => void;
}
