import { SaveProfileOnboardingRequestDefinition } from './save-profile-onboarding-request-definition';

export interface UseSaveProfileOnboardingDefinition {
  save: (
    data: SaveProfileOnboardingRequestDefinition
  ) => Promise<{ ok: boolean; error?: string }>;
  loading: boolean;
}
