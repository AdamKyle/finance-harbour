import { PaginatedApiResponseDefinition } from 'lib/api-handler/definitions/paginated-api-response-definition';

import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';
import BudgetTimelineResponseMetaDefinition from 'components/pages/dashboard/api/hooks/definitions/budget-timeline-response-meta-definition';

export default interface BudgetTimelineResponseDefinition extends Omit<
  PaginatedApiResponseDefinition<BudgetPayPeriodDefinition[]>,
  'meta'
> {
  meta: BudgetTimelineResponseMetaDefinition;
}
