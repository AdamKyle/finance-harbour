import { BudgetPayPeriodDefinition } from './budget-pay-period-definition';

import { AxiosErrorDefinition } from 'lib/api-handler/definitions/axios-error-definition';

export default interface UseBudgetTimelineDefinition {
  periods: BudgetPayPeriodDefinition[];
  loading: boolean;
  loading_previous: boolean;
  loading_next: boolean;
  error: AxiosErrorDefinition | null;
  can_load_previous: boolean;
  can_load_next: boolean;
  anchor_period_id: number | null;
  load_previous: () => Promise<void>;
  load_next: () => Promise<void>;
  refresh_loaded_pages: () => Promise<void>;
}
