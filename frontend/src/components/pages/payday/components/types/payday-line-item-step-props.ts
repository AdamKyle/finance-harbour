import { StateSetter } from 'lib/types/state-setter-type';

import { BudgetLineItemDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-line-item-definition';
import PaydayLineItemUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-line-item-update-request-definition';
import PaydayLineItemFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-line-item-field-errors-definition';

export default interface PaydayLineItemStepProps {
  line_item: BudgetLineItemDefinition;
  request: PaydayLineItemUpdateRequestDefinition;
  set_request: StateSetter<PaydayLineItemUpdateRequestDefinition>;
  field_errors: PaydayLineItemFieldErrorsDefinition;
  allow_unknown: boolean;
  disabled: boolean;
}
