import { AxiosError } from 'axios';
import { useCallback, useRef, useState } from 'react';

import UpdateBudgetValueApiRequestDefinition from './definitions/update-budget-value-api-request-definition';
import UpdateBudgetValueRequestDefinition from './definitions/update-budget-value-request-definition';
import UseUpdateBudgetValueDefinition from './definitions/use-update-budget-value-definition';
import UseUpdateBudgetValueParamsDefinition from './definitions/use-update-budget-value-params-definition';
import { useMountedRef } from '../../../../../util/hooks/use-mounted-ref';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { dollarsToCents } from 'lib/money/money';

import { BudgetApiUrls } from 'components/pages/dashboard/api/enums/budget-api-urls';
import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';

export const useUpdateBudgetValue = ({
  period_id,
  initial_request,
}: UseUpdateBudgetValueParamsDefinition): UseUpdateBudgetValueDefinition => {
  const { apiHandler, getUrl } = useApiHandler();
  const [requestData, setStoredRequestData] =
    useState<UpdateBudgetValueRequestDefinition>(initial_request);
  const requestDataRef = useRef(requestData);
  const isMountedRef = useMountedRef();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setRequestData = useCallback(
    (nextRequestData: UpdateBudgetValueRequestDefinition) => {
      requestDataRef.current = nextRequestData;
      setStoredRequestData(nextRequestData);
    },
    []
  );

  const getRequestData = useCallback(() => requestDataRef.current, []);

  const updateValue = useCallback(async (): Promise<boolean> => {
    const submittedRequest = requestDataRef.current;
    const apiRequest: UpdateBudgetValueApiRequestDefinition = {
      field: submittedRequest.field,
      source_key: submittedRequest.source_key,
      amount_cents: dollarsToCents(submittedRequest.amount_dollars),
      going_forward: submittedRequest.going_forward,
    };
    const url = getUrl(BudgetApiUrls.UPDATE_VALUE, { period_id });

    if (isMountedRef.current) {
      setLoading(true);
      setError(null);
    }

    try {
      await apiHandler.patch<
        BudgetPayPeriodDefinition,
        Record<string, never>,
        UpdateBudgetValueApiRequestDefinition
      >(url, apiRequest);

      return true;
    } catch (requestError) {
      if (!isMountedRef.current) {
        return false;
      }

      if (requestError instanceof AxiosError) {
        setError(
          'This amount could not be saved. Your entered value is still here.'
        );
      } else {
        setError('This amount could not be saved.');
      }

      return false;
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [apiHandler, getUrl, isMountedRef, period_id]);

  return {
    requestData,
    getRequestData,
    setRequestData,
    loading,
    error,
    updateValue,
  };
};
