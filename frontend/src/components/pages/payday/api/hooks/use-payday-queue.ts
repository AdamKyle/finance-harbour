import { AxiosError } from 'axios';
import { useCallback, useEffect, useState } from 'react';

import { PaydayQueueResponseDefinition } from './definitions/payday-queue-response-definition';
import UsePaydayQueueDefinition from './definitions/use-payday-queue-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { PaydayApiUrls } from 'components/pages/payday/api/enums/payday-api-urls';

export const usePaydayQueue = (): UsePaydayQueueDefinition => {
  const { apiHandler } = useApiHandler();
  const { authenticatedUser } = useAuthentication();
  const [queue, setQueue] = useState<PaydayQueueResponseDefinition | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (authenticatedUser?.completed_onboarding !== true) {
      setQueue(null);
      setLoading(false);
      return null;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await apiHandler.get<
        PaydayQueueResponseDefinition,
        object
      >(PaydayApiUrls.QUEUE);
      setQueue(response);
      return response;
    } catch (requestError) {
      if (requestError instanceof AxiosError) {
        setError('Payday information could not be loaded.');
      }
      return null;
    } finally {
      setLoading(false);
    }
  }, [apiHandler, authenticatedUser?.completed_onboarding]);

  useEffect(() => {
    refresh().catch(() => {});
  }, [refresh]);

  return { queue, loading, error, refresh };
};
