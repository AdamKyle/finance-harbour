import { AxiosError } from 'axios';
import { useCallback, useState } from 'react';

import UpdateBudgetPayDateApiRequestDefinition from './definitions/update-budget-pay-date-api-request-definition';
import UseUpdateBudgetPayDateDefinition from './definitions/use-update-budget-pay-date-definition';
import UseUpdateBudgetPayDateParamsDefinition from './definitions/use-update-budget-pay-date-params-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { BudgetApiUrls } from 'components/pages/dashboard/api/enums/budget-api-urls';
import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';
import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';

export const useUpdateBudgetPayDate = ({
  period_id,
}: UseUpdateBudgetPayDateParamsDefinition): UseUpdateBudgetPayDateDefinition => {
  const { apiHandler, getUrl } = useApiHandler();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updatePayDate = useCallback(
    async (payDate: string): Promise<BudgetPayPeriodDefinition | null> => {
      const request: UpdateBudgetPayDateApiRequestDefinition = {
        field: BudgetValueField.PAY_DATE,
        pay_date: payDate,
      };
      const url = getUrl(BudgetApiUrls.UPDATE_VALUE, { period_id });

      setLoading(true);
      setError(null);

      try {
        return await apiHandler.patch<
          BudgetPayPeriodDefinition,
          Record<string, never>,
          UpdateBudgetPayDateApiRequestDefinition
        >(url, request);
      } catch (requestError) {
        if (requestError instanceof AxiosError) {
          setError(
            'This pay date could not be saved. Your selected date is still here.'
          );
        } else {
          setError('This pay date could not be saved.');
        }

        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiHandler, getUrl, period_id]
  );

  return { loading, error, update_pay_date: updatePayDate };
};
