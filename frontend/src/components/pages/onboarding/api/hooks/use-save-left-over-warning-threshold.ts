import { AxiosError } from 'axios';
import { useCallback, useState } from 'react';

import { SaveLeftOverWarningThresholdRequestDefinition } from './definitions/save-left-over-warning-threshold-request-definition';
import { UseSaveLeftOverWarningThresholdDefinition } from './definitions/use-save-left-over-warning-threshold-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';

export const useSaveLeftOverWarningThreshold =
  (): UseSaveLeftOverWarningThresholdDefinition => {
    const { apiHandler, getUrl } = useApiHandler();
    const [loading, setLoading] = useState(false);
    const url = getUrl(OnboardingApiUrls.LEFT_OVER_WARNING_THRESHOLD);

    const save = useCallback(
      async (
        request: SaveLeftOverWarningThresholdRequestDefinition
      ): Promise<{ ok: boolean; error?: string }> => {
        setLoading(true);

        try {
          await apiHandler.patch<
            SaveLeftOverWarningThresholdRequestDefinition,
            object,
            SaveLeftOverWarningThresholdRequestDefinition
          >(url, request);

          return { ok: true };
        } catch (errorInstance) {
          if (errorInstance instanceof AxiosError) {
            return {
              ok: false,
              error:
                errorInstance.response?.data?.detail ?? errorInstance.message,
            };
          }

          return { ok: false, error: 'Failed to save warning threshold' };
        } finally {
          setLoading(false);
        }
      },
      [apiHandler, url]
    );

    return { save, loading };
  };
