import PaydayMutationResponseDefinition from './payday-mutation-response-definition';

export default interface UseMarkPaydayIncompleteDefinition {
  loading: boolean;
  error: string | null;
  mark_incomplete: () => Promise<PaydayMutationResponseDefinition | null>;
}
