import { AxiosError } from 'axios';
import { useCallback, useState } from 'react';

import { SaveProfileOnboardingRequestDefinition } from './definitions/save-profile-onboarding-request-definition';
import {
  SaveProfileOnboardingResponseDefinition,
  UseSaveProfileOnboardingDefinition,
} from './definitions/use-save-profile-onboarding-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';

export const useSaveProfileOnboarding =
  (): UseSaveProfileOnboardingDefinition => {
    const { apiHandler, getUrl } = useApiHandler();
    const [loading, setLoading] = useState(false);

    const url = getUrl(OnboardingApiUrls.PROFILE_ONBOARDING);

    const save = useCallback(
      async (
        data: SaveProfileOnboardingRequestDefinition
      ): Promise<{
        ok: boolean;
        data?: SaveProfileOnboardingResponseDefinition;
        error?: string;
      }> => {
        setLoading(true);

        try {
          const response = await apiHandler.patch<
            SaveProfileOnboardingResponseDefinition,
            object,
            SaveProfileOnboardingRequestDefinition
          >(url, data);

          return { ok: true, data: response };
        } catch (err) {
          if (err instanceof AxiosError) {
            return {
              ok: false,
              error: err.response?.data?.detail ?? err.message,
            };
          }

          return { ok: false, error: 'Failed to save profile' };
        } finally {
          setLoading(false);
        }
      },
      [apiHandler, url]
    );

    return { save, loading };
  };
