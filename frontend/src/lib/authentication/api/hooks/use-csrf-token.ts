import { AxiosError } from 'axios';
import { useCallback, useState } from 'react';

import UseCsrfTokenDefinition from './definitions/use-csrf-token-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

export const useCsrfToken = (): UseCsrfTokenDefinition => {
  const { apiHandler } = useApiHandler();

  const [error, setError] = useState<UseCsrfTokenDefinition['error']>(null);
  const [loading, setLoading] = useState(false);

  const fetchCsrfToken = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const csrfToken = await apiHandler.ensureCsrfToken();

      return { csrfToken };
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data || null);
      }

      return null;
    } finally {
      setLoading(false);
    }
  }, [apiHandler]);

  const refreshCsrfToken = useCallback(async () => {
    apiHandler.clearCsrfToken();

    return fetchCsrfToken();
  }, [apiHandler, fetchCsrfToken]);

  return {
    error,
    fetchCsrfToken,
    loading,
    refreshCsrfToken,
  };
};
