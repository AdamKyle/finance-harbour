import PaydayLineItemUpdateRequestDefinition from './payday-line-item-update-request-definition';
import PaydayMutationResponseDefinition from './payday-mutation-response-definition';

import { StateSetter } from 'lib/types/state-setter-type';

export default interface UseUpdatePaydayLineItemDefinition {
  request: PaydayLineItemUpdateRequestDefinition;
  set_request: StateSetter<PaydayLineItemUpdateRequestDefinition>;
  loading: boolean;
  error: string | null;
  update_line_item: (
    lineItemId: number
  ) => Promise<PaydayMutationResponseDefinition | null>;
}
