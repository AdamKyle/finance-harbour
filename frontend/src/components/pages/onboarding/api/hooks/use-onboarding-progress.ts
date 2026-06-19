import { AxiosError } from 'axios';
import { useCallback, useEffect, useState } from 'react';

import { OnboardingProgressRequestDefinition } from './definitions/onboarding-progress-request-definition';
import { OnboardingProgressResponseDefinition } from './definitions/onboarding-progress-response-definition';
import { UseOnboardingProgressDefinition } from './definitions/use-onboarding-progress-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';
import {
  createInitialOnboardingFormRequest,
  hydrateOnboardingFormRequest,
} from 'components/pages/onboarding/utils/onboarding-form-request';

export const useOnboardingProgress = (): UseOnboardingProgressDefinition => {
  const { apiHandler, getUrl } = useApiHandler();
  const [progress, setProgress] =
    useState<OnboardingProgressResponseDefinition | null>(null);
  const [requestData, setRequestData] = useState(
    createInitialOnboardingFormRequest
  );
  const [loading, setLoading] = useState(true);

  const url = getUrl(OnboardingApiUrls.PROGRESS);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiHandler.get<
          OnboardingProgressResponseDefinition,
          object
        >(url);

        setProgress(data);
        setRequestData(hydrateOnboardingFormRequest(data.form_data));
      } finally {
        setLoading(false);
      }
    };

    load().catch(() => {});
  }, [apiHandler, url]);

  const saveProgress = useCallback(
    async (
      data: OnboardingProgressRequestDefinition
    ): Promise<{ ok: boolean; error?: string }> => {
      try {
        const updated = await apiHandler.patch<
          OnboardingProgressResponseDefinition,
          object,
          OnboardingProgressRequestDefinition
        >(url, data);

        setProgress(updated);

        return { ok: true };
      } catch (err) {
        if (err instanceof AxiosError) {
          return {
            ok: false,
            error:
              err.response?.data?.detail ??
              'We could not save your onboarding progress. Please try again.',
          };
        }

        return {
          ok: false,
          error:
            'We could not save your onboarding progress. Please try again.',
        };
      }
    },
    [apiHandler, url]
  );

  return {
    progress,
    requestData,
    setRequestData,
    loading,
    saveProgress,
  };
};
