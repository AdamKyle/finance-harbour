import { StateSetter } from 'lib/types/state-setter-type';

import PaydayPayChequeUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-pay-cheque-update-request-definition';
import PaydayPayChequeFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-pay-cheque-field-errors-definition';

export default interface PaydayPayChequeStepProps {
  planned_amount_cents: number;
  request: PaydayPayChequeUpdateRequestDefinition;
  set_request: StateSetter<PaydayPayChequeUpdateRequestDefinition>;
  field_errors: PaydayPayChequeFieldErrorsDefinition;
  allow_unknown: boolean;
  disabled: boolean;
}
