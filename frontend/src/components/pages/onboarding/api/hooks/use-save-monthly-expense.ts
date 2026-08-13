import { AxiosError } from 'axios';
import { useCallback, useState } from 'react';

import MonthlyExpenseResponseDefinition from './definitions/monthly-expense-response-definition';
import { SaveMonthlyExpenseRequestDefinition } from './definitions/save-monthly-expense-request-definition';
import { UseSaveMonthlyExpenseDefinition } from './definitions/use-save-monthly-expense-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';

export const useSaveMonthlyExpense = (): UseSaveMonthlyExpenseDefinition => {
  const { apiHandler, getUrl } = useApiHandler();
  const [loading, setLoading] = useState(false);

  const url = getUrl(OnboardingApiUrls.MONTHLY_EXPENSE);

  const save = useCallback(
    async (
      data: SaveMonthlyExpenseRequestDefinition
    ): Promise<{ ok: boolean; error?: string }> => {
      setLoading(true);

      try {
        await apiHandler.patch<
          MonthlyExpenseResponseDefinition,
          object,
          SaveMonthlyExpenseRequestDefinition
        >(url, data);

        return { ok: true };
      } catch (err) {
        if (err instanceof AxiosError) {
          return {
            ok: false,
            error: err.response?.data?.detail ?? err.message,
          };
        }

        return { ok: false, error: 'Failed to save expenses' };
      } finally {
        setLoading(false);
      }
    },
    [apiHandler, url]
  );

  return { save, loading };
};
