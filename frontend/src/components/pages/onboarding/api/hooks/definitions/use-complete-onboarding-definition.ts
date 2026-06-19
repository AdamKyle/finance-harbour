import { AxiosErrorDefinition } from 'lib/api-handler/definitions/axios-error-definition';

export interface UseCompleteOnboardingDefinition {
  complete: () => Promise<boolean>;
  loading: boolean;
  error: AxiosErrorDefinition | null;
}
