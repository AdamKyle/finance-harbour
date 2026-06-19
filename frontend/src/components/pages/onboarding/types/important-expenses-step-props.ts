import { ImportantExpensesStepFormState } from './important-expenses-step-form-state';

import { ImportantExpenseCardDefinition } from 'components/pages/onboarding/api/hooks/definitions/important-expense-card-definition';

export default interface ImportantExpensesStepProps {
  request: ImportantExpensesStepFormState;
  setRequest: (request: ImportantExpensesStepFormState) => void;
  cards: ImportantExpenseCardDefinition[];
  loading: boolean;
  is_loading_more: boolean;
  can_load_more: boolean;
  on_load_more: () => void;
}
