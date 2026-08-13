import { CompleteOnboardingResponseDefinition } from './complete-onboarding-response-definition';

import { AxiosErrorDefinition } from 'lib/api-handler/definitions/axios-error-definition';

export interface UseCompleteOnboardingDefinition {
  complete: () => Promise<CompleteOnboardingResponseDefinition | null>;
  loading: boolean;
  error: AxiosErrorDefinition | null;
}
