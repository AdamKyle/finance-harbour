import { AxiosError } from 'axios';
import { useCallback, useRef, useState } from 'react';

import AddBudgetBillApiRequestDefinition from './definitions/add-budget-bill-api-request-definition';
import AddBudgetBillRequestDefinition from './definitions/add-budget-bill-request-definition';
import UseAddBudgetBillDefinition from './definitions/use-add-budget-bill-definition';
import UseAddBudgetBillParamsDefinition from './definitions/use-add-budget-bill-params-definition';
import { useMountedRef } from '../../../../../util/hooks/use-mounted-ref';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { dollarsToCents } from 'lib/money/money';

import { BudgetApiUrls } from 'components/pages/dashboard/api/enums/budget-api-urls';
import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';

export const useAddBudgetBill = ({
  period_id,
}: UseAddBudgetBillParamsDefinition): UseAddBudgetBillDefinition => {
  const { apiHandler, getUrl } = useApiHandler();
  const [requestData, setStoredRequestData] =
    useState<AddBudgetBillRequestDefinition>({
      title: '',
      amount_dollars: '',
      is_required: false,
      going_forward: false,
    });
  const requestDataRef = useRef(requestData);
  const isMountedRef = useMountedRef();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setRequestData = (nextRequestData: AddBudgetBillRequestDefinition) => {
    requestDataRef.current = nextRequestData;
    setStoredRequestData(nextRequestData);
  };

  const addBill = useCallback(async (): Promise<boolean> => {
    const submittedRequest = requestDataRef.current;
    const apiRequest: AddBudgetBillApiRequestDefinition = {
      title: submittedRequest.title.trim(),
      amount_cents: dollarsToCents(submittedRequest.amount_dollars),
      is_required: submittedRequest.is_required,
      going_forward: submittedRequest.going_forward,
    };
    const url = getUrl(BudgetApiUrls.ADD_BILL, { period_id });
    setLoading(true);
    setError(null);

    try {
      await apiHandler.post<
        BudgetPayPeriodDefinition,
        Record<string, never>,
        AddBudgetBillApiRequestDefinition
      >(url, apiRequest);

      return true;
    } catch (requestError) {
      if (!isMountedRef.current) {
        return false;
      }

      if (requestError instanceof AxiosError) {
        setError('The new bill could not be saved.');
      } else {
        setError('The new bill could not be saved. Please try again.');
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
    setRequestData,
    loading,
    error,
    addBill,
  };
};
