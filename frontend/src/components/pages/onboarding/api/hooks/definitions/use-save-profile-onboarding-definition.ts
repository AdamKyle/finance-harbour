import { SaveProfileOnboardingRequestDefinition } from './save-profile-onboarding-request-definition';

export interface SaveProfileOnboardingResponseDefinition {
  nickname: string;
  profile_photo: string;
  completed_onboarding: boolean;
}

export interface UseSaveProfileOnboardingDefinition {
  save: (data: SaveProfileOnboardingRequestDefinition) => Promise<{
    ok: boolean;
    data?: SaveProfileOnboardingResponseDefinition;
    error?: string;
  }>;
  loading: boolean;
}
