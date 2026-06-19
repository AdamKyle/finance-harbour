import { AxiosError } from 'axios';
import { useCallback, useState } from 'react';

import { SaveDebtProfileRequestDefinition } from './definitions/save-debt-profile-request-definition';
import { UseSaveDebtProfileDefinition } from './definitions/use-save-debt-profile-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';

export const useSaveDebtProfile = (): UseSaveDebtProfileDefinition => {
  const { apiHandler, getUrl } = useApiHandler();
  const [loading, setLoading] = useState(false);

  const url = getUrl(OnboardingApiUrls.DEBT_PROFILE);

  const save = useCallback(
    async (
      data: SaveDebtProfileRequestDefinition
    ): Promise<{ ok: boolean; error?: string }> => {
      setLoading(true);

      try {
        await apiHandler.patch<
          object,
          object,
          SaveDebtProfileRequestDefinition
        >(url, data);

        return { ok: true };
      } catch (err) {
        if (err instanceof AxiosError) {
          return {
            ok: false,
            error: err.response?.data?.detail ?? err.message,
          };
        }

        return { ok: false, error: 'Failed to save debt profile' };
      } finally {
        setLoading(false);
      }
    },
    [apiHandler, url]
  );

  return { save, loading };
};
