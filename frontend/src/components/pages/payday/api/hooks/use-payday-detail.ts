import { AxiosError } from 'axios';
import { useCallback, useEffect, useState } from 'react';

import PaydayDetailResponseDefinition from './definitions/payday-detail-response-definition';
import UsePaydayDetailDefinition from './definitions/use-payday-detail-definition';
import UsePaydayDetailParamsDefinition from './definitions/use-payday-detail-params-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { PaydayApiUrls } from 'components/pages/payday/api/enums/payday-api-urls';

export const usePaydayDetail = ({
  period_id,
}: UsePaydayDetailParamsDefinition): UsePaydayDetailDefinition => {
  const { apiHandler } = useApiHandler();
  const [detail, setDetail] = useState<PaydayDetailResponseDefinition | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const url = PaydayApiUrls.DETAIL.replace(':periodId', `${period_id}`);
      const response = await apiHandler.get<
        PaydayDetailResponseDefinition,
        object
      >(url);

      setDetail(response);

      return response;
    } catch (requestError) {
      if (requestError instanceof AxiosError) {
        setError('This payday could not be loaded.');
      }

      return null;
    } finally {
      setLoading(false);
    }
  }, [apiHandler, period_id]);

  useEffect(() => {
    refresh().catch(() => {});
  }, [refresh]);

  return { detail, loading, error, refresh };
};
