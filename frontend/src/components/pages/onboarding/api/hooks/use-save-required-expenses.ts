import { AxiosError } from 'axios';
import { useCallback, useState } from 'react';

import { SaveRequiredExpensesRequestDefinition } from './definitions/save-required-expenses-request-definition';
import { UseSaveRequiredExpensesDefinition } from './definitions/use-save-required-expenses-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';

export const useSaveRequiredExpenses =
  (): UseSaveRequiredExpensesDefinition => {
    const { apiHandler, getUrl } = useApiHandler();
    const [loading, setLoading] = useState(false);
    const url = getUrl(OnboardingApiUrls.IMPORTANT_EXPENSES);

    const save = useCallback(
      async (
        request: SaveRequiredExpensesRequestDefinition
      ): Promise<{ ok: boolean; error?: string }> => {
        setLoading(true);

        try {
          await apiHandler.patch<
            { selected_keys: string[] },
            object,
            SaveRequiredExpensesRequestDefinition
          >(url, request);

          return { ok: true };
        } catch (errorInstance) {
          if (errorInstance instanceof AxiosError) {
            return {
              ok: false,
              error:
                errorInstance.response?.data?.detail ?? errorInstance.message,
            };
          }

          return { ok: false, error: 'Failed to save important expenses' };
        } finally {
          setLoading(false);
        }
      },
      [apiHandler, url]
    );

    return { save, loading };
  };
