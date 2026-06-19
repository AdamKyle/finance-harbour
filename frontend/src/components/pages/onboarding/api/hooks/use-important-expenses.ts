import { ImportantExpenseCardDefinition } from './definitions/important-expense-card-definition';
import { UseImportantExpensesDefinition } from './definitions/use-important-expenses-definition';

import UsePaginatedApiHandler from 'lib/api-handler/hooks/use-paginated-api-handler';

import { OnboardingApiUrls } from 'components/pages/onboarding/api/enums/onboarding-api-urls';

export const useImportantExpenses = (): UseImportantExpensesDefinition => {
  return UsePaginatedApiHandler<
    ImportantExpenseCardDefinition,
    Record<string, unknown>
  >(
    {
      url: OnboardingApiUrls.IMPORTANT_EXPENSES,
      enabled: true,
    },
    8,
    {}
  );
};
