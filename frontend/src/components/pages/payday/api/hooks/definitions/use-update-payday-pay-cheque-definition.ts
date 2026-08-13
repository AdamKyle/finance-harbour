import PaydayMutationResponseDefinition from './payday-mutation-response-definition';
import PaydayPayChequeUpdateRequestDefinition from './payday-pay-cheque-update-request-definition';

import { StateSetter } from 'lib/types/state-setter-type';

export default interface UseUpdatePaydayPayChequeDefinition {
  request: PaydayPayChequeUpdateRequestDefinition;
  set_request: StateSetter<PaydayPayChequeUpdateRequestDefinition>;
  loading: boolean;
  error: string | null;
  update_pay_cheque: () => Promise<PaydayMutationResponseDefinition | null>;
}
