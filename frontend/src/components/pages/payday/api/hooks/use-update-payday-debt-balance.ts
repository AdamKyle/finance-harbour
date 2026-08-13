import { AxiosError } from 'axios';
import { useState } from 'react';

import PaydayMutationResponseDefinition from './definitions/payday-mutation-response-definition';
import UseUpdatePaydayDebtBalanceDefinition from './definitions/use-update-payday-debt-balance-definition';
import UseUpdatePaydayDebtBalanceParamsDefinition from './definitions/use-update-payday-debt-balance-params-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { PaydayApiUrls } from 'components/pages/payday/api/enums/payday-api-urls';

export const useUpdatePaydayDebtBalance = ({
  period_id,
  initial_request,
}: UseUpdatePaydayDebtBalanceParamsDefinition): UseUpdatePaydayDebtBalanceDefinition => {
  const { apiHandler } = useApiHandler();
  const [request, setRequest] = useState(initial_request);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateDebtBalance = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = PaydayApiUrls.DEBT_BALANCE.replace(
        ':periodId',
        `${period_id}`
      );
      const response = await apiHandler.patch<
        PaydayMutationResponseDefinition,
        object,
        typeof request
      >(url, request);

      return response;
    } catch (requestError) {
      if (requestError instanceof AxiosError) {
        setError('This debt balance could not be saved.');
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
    update_debt_balance: updateDebtBalance,
  };
};
