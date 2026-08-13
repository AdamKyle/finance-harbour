import PaydayDetailResponseDefinition from './payday-detail-response-definition';

export default interface UsePaydayDetailDefinition {
  detail: PaydayDetailResponseDefinition | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<PaydayDetailResponseDefinition | null>;
}
