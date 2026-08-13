import { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import GoogleSocialAuthRequestDefinition from './definitions/google-social-auth-request-definition';
import GoogleSocialAuthResponseDefinition from './definitions/google-social-auth-response-definition';
import UseGoogleSocialAuthCallbackDefinition from './definitions/use-google-social-auth-callback-definition';
import UseGoogleSocialAuthCallbackParamsDefinition from './definitions/use-google-social-auth-callback-params-definition';
import { useCsrfToken } from './use-csrf-token';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { AuthenticationApiUrls } from 'lib/authentication/api/enums/authentication-api-urls';
import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { NavigationRoutes } from 'router/enums/navigation-routes';

export const useGoogleSocialAuthCallback = ({
  navigate_to_route,
}: UseGoogleSocialAuthCallbackParamsDefinition): UseGoogleSocialAuthCallbackDefinition => {
  const navigate = useNavigate();
  const { apiHandler, getUrl } = useApiHandler();
  const { fetchCsrfToken, refreshCsrfToken } = useCsrfToken();
  const { setAuthenticatedUser } = useAuthentication();

  const [error, setError] =
    useState<UseGoogleSocialAuthCallbackDefinition['error']>(null);
  const [loading, setLoading] = useState(false);
  const [requestData, setRequestData] =
    useState<GoogleSocialAuthRequestDefinition>({
      code: '',
    });

  const url = getUrl(AuthenticationApiUrls.GOOGLE_SOCIAL_AUTH);

  const authenticateWithGoogle = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await fetchCsrfToken();

      const result = await apiHandler.post<
        GoogleSocialAuthResponseDefinition,
        AxiosRequestConfig<AxiosResponse<GoogleSocialAuthResponseDefinition>>,
        GoogleSocialAuthRequestDefinition
      >(url, {
        code: requestData.code,
      });

      await refreshCsrfToken();
      setAuthenticatedUser(result.user);

      if (!result.user.completed_onboarding) {
        navigate_to_route(navigate, NavigationRoutes.ONBOARDING);
        return;
      }

      navigate_to_route(navigate, NavigationRoutes.DASHBOARD);
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(
          err.response?.data || {
            detail: 'Google sign in failed. Please try signing in again.',
          }
        );

        return;
      }

      setError({
        detail: 'Google sign in failed. Please try signing in again.',
      });
    } finally {
      setLoading(false);
    }
  }, [
    apiHandler,
    fetchCsrfToken,
    navigate,
    navigate_to_route,
    requestData.code,
    refreshCsrfToken,
    setAuthenticatedUser,
    url,
  ]);

  useEffect(() => {
    if (requestData.code === '') {
      return;
    }

    authenticateWithGoogle().catch(() => {});
  }, [authenticateWithGoogle, requestData]);

  return {
    error,
    loading,
    setRequestData,
  };
};
