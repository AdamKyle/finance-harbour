import { AxiosError } from 'axios';
import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router';

import { UseCompleteOnboardingDefinition } from './definitions/use-complete-onboarding-definition';
import { UseCompleteOnboardingParamsDefinition } from './definitions/use-complete-onboarding-params-definition';

import { AxiosErrorDefinition } from 'lib/api-handler/definitions/axios-error-definition';
import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';

import { NavigationRoutes } from 'router/enums/navigation-routes';

export const useCompleteOnboarding = ({
  navigate_to_route,
}: UseCompleteOnboardingParamsDefinition): UseCompleteOnboardingDefinition => {
  const navigate = useNavigate();
  const { apiHandler, getUrl } = useApiHandler();
  const { setAuthenticatedUser } = useAuthentication();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AxiosErrorDefinition | null>(null);

  const url = getUrl(OnboardingApiUrls.COMPLETE);

  const complete = useCallback(async (): Promise<boolean> => {
    setLoading(true);

    setError(null);

    try {
      await apiHandler.post<{ detail: string }, object, object>(url, {});

      setAuthenticatedUser((prev) =>
        prev ? { ...prev, completed_onboarding: true } : null
      );

      navigate_to_route(navigate, NavigationRoutes.HOME);

      return true;
    } catch (err) {
      if (err instanceof AxiosError) {
        setError({ message: err.response?.data?.detail ?? err.message });
      }

      return false;
    } finally {
      setLoading(false);
    }
  }, [apiHandler, navigate, navigate_to_route, setAuthenticatedUser, url]);

  return { complete, loading, error };
};
