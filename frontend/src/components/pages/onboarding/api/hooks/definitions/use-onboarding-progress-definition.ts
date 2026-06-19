import { OnboardingProgressRequestDefinition } from './onboarding-progress-request-definition';
import { OnboardingProgressResponseDefinition } from './onboarding-progress-response-definition';

import { StateSetter } from 'lib/types/state-setter-type';

import { OnboardingFormData } from 'components/pages/onboarding/types/onboarding-form-data';

export interface UseOnboardingProgressDefinition {
  progress: OnboardingProgressResponseDefinition | null;
  requestData: OnboardingFormData;
  setRequestData: StateSetter<OnboardingFormData>;
  loading: boolean;
  saveProgress: (
    data: OnboardingProgressRequestDefinition
  ) => Promise<{ ok: boolean; error?: string }>;
}
