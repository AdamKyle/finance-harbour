import { BudgetLineItemDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-line-item-definition';
import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';

export default interface BudgetPayPeriodCardProps {
  period: BudgetPayPeriodDefinition;
  line_items: BudgetLineItemDefinition[];
  on_saved: () => void;
  on_pay_date_saved: (periodId: number) => Promise<void>;
  effective_payday_date: string | null;
  register_focus_target?: (element: HTMLButtonElement | null) => void;
}
