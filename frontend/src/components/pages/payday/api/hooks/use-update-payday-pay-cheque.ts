import { AxiosError } from 'axios';
import { useState } from 'react';

import PaydayMutationResponseDefinition from './definitions/payday-mutation-response-definition';
import UseUpdatePaydayPayChequeDefinition from './definitions/use-update-payday-pay-cheque-definition';
import UseUpdatePaydayPayChequeParamsDefinition from './definitions/use-update-payday-pay-cheque-params-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { PaydayApiUrls } from 'components/pages/payday/api/enums/payday-api-urls';

export const useUpdatePaydayPayCheque = ({
  period_id,
  initial_request,
}: UseUpdatePaydayPayChequeParamsDefinition): UseUpdatePaydayPayChequeDefinition => {
  const { apiHandler } = useApiHandler();
  const [request, setRequest] = useState(initial_request);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updatePayCheque = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = PaydayApiUrls.PAY_CHEQUE.replace(':periodId', `${period_id}`);
      const response = await apiHandler.patch<
        PaydayMutationResponseDefinition,
        object,
        typeof request
      >(url, request);

      return response;
    } catch (requestError) {
      if (requestError instanceof AxiosError) {
        setError('Your actual pay cheque could not be saved.');
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
    update_pay_cheque: updatePayCheque,
  };
};
