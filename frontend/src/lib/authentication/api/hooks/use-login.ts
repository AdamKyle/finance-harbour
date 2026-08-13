import { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import LoginRequestDefinition from './definitions/login-request-definition';
import LoginResponseDefinition from './definitions/login-response-definition';
import UseLoginDefinition from './definitions/use-login-definition';
import UseLoginParamsDefinition from './definitions/use-login-params-definition';
import { useCsrfToken } from './use-csrf-token';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { AuthenticationApiUrls } from 'lib/authentication/api/enums/authentication-api-urls';
import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { NavigationRoutes } from 'router/enums/navigation-routes';

export const useLogin = ({
  navigate_to_route,
}: UseLoginParamsDefinition): UseLoginDefinition => {
  const navigate = useNavigate();
  const { apiHandler, getUrl } = useApiHandler();
  const { fetchCsrfToken, refreshCsrfToken } = useCsrfToken();
  const { setAuthenticatedUser } = useAuthentication();

  const [error, setError] = useState<UseLoginDefinition['error']>(null);
  const [loading, setLoading] = useState(false);
  const [requestData, setRequestData] = useState<LoginRequestDefinition>({
    email: '',
    password: '',
  });

  const url = getUrl(AuthenticationApiUrls.LOGIN);

  const login = useCallback(async () => {
    setLoading(true);

    try {
      await fetchCsrfToken();

      const result = await apiHandler.post<
        LoginResponseDefinition,
        AxiosRequestConfig<AxiosResponse<LoginResponseDefinition>>,
        LoginRequestDefinition
      >(url, {
        email: requestData.email,
        password: requestData.password,
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
        setError(err.response?.data || null);
      }
    } finally {
      setLoading(false);
    }
  }, [
    apiHandler,
    fetchCsrfToken,
    navigate,
    navigate_to_route,
    requestData.email,
    requestData.password,
    setAuthenticatedUser,
    refreshCsrfToken,
    url,
  ]);

  useEffect(() => {
    if (requestData.email === '' || requestData.password === '') {
      return;
    }

    login().catch(() => {});
  }, [login, requestData]);

  return {
    error,
    loading,
    setRequestData,
  };
};
