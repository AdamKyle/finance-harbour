import UsePaydayQueueDefinition from 'components/pages/payday/api/hooks/definitions/use-payday-queue-definition';

export default interface PaydayQueueContextDefinition extends UsePaydayQueueDefinition {
  dismissed_effective_date: string | null;
  dismissed_user_id: number | null;
  dismiss: (user_id: number, effective_date: string) => void;
}
