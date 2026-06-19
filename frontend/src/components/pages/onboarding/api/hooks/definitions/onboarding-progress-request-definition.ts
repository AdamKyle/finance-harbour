import { OnboardingFormData } from 'components/pages/onboarding/types/onboarding-form-data';

export interface OnboardingProgressRequestDefinition {
  current_step?: string;
  completed_steps?: string[];
  form_data?: OnboardingFormData;
}
