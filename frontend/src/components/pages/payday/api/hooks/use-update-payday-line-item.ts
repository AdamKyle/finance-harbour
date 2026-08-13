import { AxiosError } from 'axios';
import { useState } from 'react';

import PaydayMutationResponseDefinition from './definitions/payday-mutation-response-definition';
import UseUpdatePaydayLineItemDefinition from './definitions/use-update-payday-line-item-definition';
import UseUpdatePaydayLineItemParamsDefinition from './definitions/use-update-payday-line-item-params-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { PaydayApiUrls } from 'components/pages/payday/api/enums/payday-api-urls';

export const useUpdatePaydayLineItem = ({
  period_id,
  initial_request,
}: UseUpdatePaydayLineItemParamsDefinition): UseUpdatePaydayLineItemDefinition => {
  const { apiHandler } = useApiHandler();
  const [request, setRequest] = useState(initial_request);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateLineItem = async (lineItemId: number) => {
    setLoading(true);
    setError(null);

    try {
      const url = PaydayApiUrls.LINE_ITEM.replace(
        ':periodId',
        `${period_id}`
      ).replace(':lineItemId', `${lineItemId}`);
      const response = await apiHandler.patch<
        PaydayMutationResponseDefinition,
        object,
        typeof request
      >(url, request);

      return response;
    } catch (requestError) {
      if (requestError instanceof AxiosError) {
        setError('This payment result could not be saved.');
      }

      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    request,
    set_request: setRequest,
    loading,
    error,
    update_line_item: updateLineItem,
  };
};
