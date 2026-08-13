import { RefObject } from 'react';

import { BudgetLineItemDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-line-item-definition';
import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';

export default interface BudgetCardEditorProps {
  period: BudgetPayPeriodDefinition;
  line_items: BudgetLineItemDefinition[];
  on_close: () => void;
  on_saved: () => void;
  on_pay_date_saved: (periodId: number) => Promise<void>;
  close_button_ref: RefObject<HTMLButtonElement | null>;
}
