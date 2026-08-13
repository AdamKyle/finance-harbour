import { StateSetter } from 'lib/types/state-setter-type';

import PaydayDebtBalanceUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-debt-balance-update-request-definition';
import { PaydayDebtBalanceCheckDefinition } from 'components/pages/payday/api/hooks/definitions/payday-detail-response-definition';
import PaydayDebtBalanceFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-debt-balance-field-errors-definition';

export default interface PaydayDebtBalanceStepProps {
  balance_check: PaydayDebtBalanceCheckDefinition;
  request: PaydayDebtBalanceUpdateRequestDefinition;
  set_request: StateSetter<PaydayDebtBalanceUpdateRequestDefinition>;
  field_errors: PaydayDebtBalanceFieldErrorsDefinition;
  allow_unknown: boolean;
  disabled: boolean;
}
