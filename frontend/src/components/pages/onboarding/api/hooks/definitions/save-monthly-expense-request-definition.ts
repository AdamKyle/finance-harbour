import { MiscExpenseEntryDefinition } from './misc-expense-entry-definition';

export interface SaveMonthlyExpenseRequestDefinition {
  rent_or_mortgage_cents?: number;
  water_cents?: number;
  electricity_cents?: number;
  food_cents?: number;
  internet_cents?: number;
  phone_cents?: number;
  car_payment_cents?: number;
  insurance_cents?: number;
  misc_expenses?: MiscExpenseEntryDefinition[];
}
