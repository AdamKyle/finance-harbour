import { OnboardingStepId } from 'components/pages/onboarding/types/onboarding-step-id';

export interface OnboardingProgressResponseDefinition {
  current_step: OnboardingStepId;
  completed_steps: OnboardingStepId[];
  form_data: Record<string, unknown>;
  is_complete: boolean;
}
