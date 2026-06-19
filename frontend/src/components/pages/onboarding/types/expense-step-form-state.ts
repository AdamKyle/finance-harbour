import { MiscExpenseEntryFormState } from './misc-expense-entry-form-state';

export interface ExpenseStepFormState {
  rent_or_mortgage_dollars: string;
  water_dollars: string;
  electricity_dollars: string;
  food_dollars: string;
  internet_dollars: string;
  phone_dollars: string;
  car_payment_dollars: string;
  insurance_dollars: string;
  misc_expenses: MiscExpenseEntryFormState[];
}
