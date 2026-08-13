import { AxiosError } from 'axios';
import { useCallback, useRef, useState } from 'react';

import { CompleteOnboardingResponseDefinition } from './definitions/complete-onboarding-response-definition';
import { UseCompleteOnboardingDefinition } from './definitions/use-complete-onboarding-definition';

import { AxiosErrorDefinition } from 'lib/api-handler/definitions/axios-error-definition';
import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';

export const useCompleteOnboarding = (): UseCompleteOnboardingDefinition => {
  const { apiHandler, getUrl } = useApiHandler();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AxiosErrorDefinition | null>(null);
  const inFlightRef = useRef(false);

  const url = getUrl(OnboardingApiUrls.COMPLETE);

  const complete =
    useCallback(async (): Promise<CompleteOnboardingResponseDefinition | null> => {
      if (inFlightRef.current) {
        return null;
      }

      inFlightRef.current = true;
      setLoading(true);
      setError(null);

      try {
        const response = await apiHandler.post<
          CompleteOnboardingResponseDefinition,
          object,
          object
        >(url, {});

        return response;
      } catch (err) {
        if (err instanceof AxiosError) {
          setError({ message: err.response?.data?.detail ?? err.message });
        } else {
          setError({
            message:
              'We could not finish building your budget. Please try again.',
          });
        }

        return null;
      } finally {
        inFlightRef.current = false;
        setLoading(false);
      }
    }, [apiHandler, url]);

  return { complete, loading, error };
};
