import { PaydayQueueResponseDefinition } from './payday-queue-response-definition';

export default interface UsePaydayQueueDefinition {
  queue: PaydayQueueResponseDefinition | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<PaydayQueueResponseDefinition | null>;
}
