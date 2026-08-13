import { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import RegistrationRequestDefinition from './definitions/registration-request-definition';
import RegistrationResponseDefinition from './definitions/registration-response-definition';
import UseRegistrationDefinition from './definitions/use-register-definition';
import UseRegistrationParamsDefinition from './definitions/use-register-params-definition';
import { useCsrfToken } from './use-csrf-token';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { AuthenticationApiUrls } from 'lib/authentication/api/enums/authentication-api-urls';
import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { NavigationRoutes } from 'router/enums/navigation-routes';

export const useRegister = ({
  navigate_to_route,
}: UseRegistrationParamsDefinition): UseRegistrationDefinition => {
  const navigate = useNavigate();
  const { apiHandler, getUrl } = useApiHandler();
  const { fetchCsrfToken, refreshCsrfToken } = useCsrfToken();
  const { setAuthenticatedUser } = useAuthentication();

  const [error, setError] = useState<UseRegistrationDefinition['error']>(null);
  const [loading, setLoading] = useState(false);
  const [requestData, setRequestData] = useState<RegistrationRequestDefinition>(
    {
      email: '',
      password: '',
    }
  );

  const url = getUrl(AuthenticationApiUrls.REGISTER);

  const register = useCallback(async () => {
    setLoading(true);

    try {
      await fetchCsrfToken();

      const result = await apiHandler.post<
        RegistrationResponseDefinition,
        AxiosRequestConfig<AxiosResponse<RegistrationResponseDefinition>>,
        RegistrationRequestDefinition
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

    register().catch(() => {});
  }, [register, requestData]);

  return {
    error,
    loading,
    setRequestData,
  };
};
