import { RecurringObligationKind } from 'components/side-peeks/add-bill/types/recurring-obligation-kind';

export default interface RecurringObligationResponseDefinition {
  kind: RecurringObligationKind;
  source_key: string;
  first_effective_budget_period_id: number;
}
