import { MiscExpenseEntryFormState } from './misc-expense-entry-form-state';
import {
  CommonExpenseSourceKey,
  PaymentScheduleFormState,
} from './payment-schedule-form-state';

import { UtilityType } from 'components/pages/onboarding/enums/utility-type';

export interface ExpenseStepFormState {
  rent_or_mortgage_dollars: string;
  utility_type: UtilityType | '';
  utility_custom_label: string;
  utilities_dollars: string;
  utilities_includes_internet: boolean;
  utilities_includes_cable: boolean;
  food_dollars: string;
  internet_dollars: string;
  phone_dollars: string;
  car_payment_dollars: string;
  insurance_dollars: string;
  misc_expenses: MiscExpenseEntryFormState[];
  payment_schedules: Record<CommonExpenseSourceKey, PaymentScheduleFormState>;
}

export type ExpenseStringFieldName = keyof Pick<
  ExpenseStepFormState,
  | 'rent_or_mortgage_dollars'
  | 'utility_custom_label'
  | 'utilities_dollars'
  | 'food_dollars'
  | 'internet_dollars'
  | 'phone_dollars'
  | 'car_payment_dollars'
  | 'insurance_dollars'
>;
