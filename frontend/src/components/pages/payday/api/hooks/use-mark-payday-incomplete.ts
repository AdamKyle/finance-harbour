import { AxiosError } from 'axios';
import { useState } from 'react';

import PaydayMutationResponseDefinition from './definitions/payday-mutation-response-definition';
import UseMarkPaydayIncompleteDefinition from './definitions/use-mark-payday-incomplete-definition';
import UseMarkPaydayIncompleteParamsDefinition from './definitions/use-mark-payday-incomplete-params-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { PaydayApiUrls } from 'components/pages/payday/api/enums/payday-api-urls';

export const useMarkPaydayIncomplete = ({
  period_id,
}: UseMarkPaydayIncompleteParamsDefinition): UseMarkPaydayIncompleteDefinition => {
  const { apiHandler } = useApiHandler();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const markIncomplete = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = PaydayApiUrls.MARK_INCOMPLETE.replace(
        ':periodId',
        `${period_id}`
      );
      const response = await apiHandler.post<
        PaydayMutationResponseDefinition,
        object,
        object
      >(url, {});

      return response;
    } catch (requestError) {
      if (requestError instanceof AxiosError) {
        setError('This payday could not be marked incomplete.');
      }

      return null;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, mark_incomplete: markIncomplete };
};
