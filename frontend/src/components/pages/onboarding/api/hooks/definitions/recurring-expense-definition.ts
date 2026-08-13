import { RecurringExpenseCategory } from 'components/pages/onboarding/enums/recurring-expense-category';
import { UtilityType } from 'components/pages/onboarding/enums/utility-type';

export default interface RecurringExpenseDefinition {
  source_key: string;
  category: RecurringExpenseCategory;
  label: string;
  amount_cents: number;
  utility_type: UtilityType | '';
  includes_internet: boolean;
  includes_cable: boolean;
}
