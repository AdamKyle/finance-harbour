import { AxiosError } from 'axios';

import UseActivityTimeoutDefinitions from 'lib/api-handler/hooks/definitions/use-activity-timeout-definitions';
import UseActivityTimeoutParams from 'lib/api-handler/hooks/definitions/use-activity-timeout-params-definitions';

export const useActivityTimeout = (): UseActivityTimeoutDefinitions => {
  const handleInactivity = ({
    response,
    setError,
  }: UseActivityTimeoutParams) => {
    if (!(response instanceof AxiosError)) {
      return;
    }

    if (response.response?.status === 401) {
      setError({
        message:
          'You have been logged out due to inactivity. One moment while we redirect you.',
      });

      return;
    }
  };

  return {
    handleInactivity,
  };
};
