import PaydayDebtBalanceUpdateRequestDefinition from './payday-debt-balance-update-request-definition';
import PaydayMutationResponseDefinition from './payday-mutation-response-definition';

import { StateSetter } from 'lib/types/state-setter-type';

export default interface UseUpdatePaydayDebtBalanceDefinition {
  request: PaydayDebtBalanceUpdateRequestDefinition;
  set_request: StateSetter<PaydayDebtBalanceUpdateRequestDefinition>;
  loading: boolean;
  error: string | null;
  update_debt_balance: () => Promise<PaydayMutationResponseDefinition | null>;
}
