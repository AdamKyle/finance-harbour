export interface DebtFieldErrorsDefinition {
  label?: string;
  current_balance_dollars?: string;
  minimum_payment_dollars?: string;
  current_payment_dollars?: string;
}

export interface IncomeFieldErrorsDefinition {
  income_per_pay_period_dollars?: string;
  pay_period_type?: string;
  next_pay_date?: string;
}

export interface MiscExpenseFieldErrorsDefinition {
  label?: string;
  amount_dollars?: string;
}

export interface ExpenseFieldErrorsDefinition {
  rent_or_mortgage_dollars?: string;
  utility_type?: string;
  utility_custom_label?: string;
  utilities_dollars?: string;
  food_dollars?: string;
  internet_dollars?: string;
  phone_dollars?: string;
  car_payment_dollars?: string;
  insurance_dollars?: string;
  misc_expenses?: MiscExpenseFieldErrorsDefinition[];
}

export interface PaymentScheduleFieldErrorsDefinition {
  [sourceKey: string]: string | undefined;
}

export interface OnboardingFormErrorsDefinition {
  debts: DebtFieldErrorsDefinition[];
  income: IncomeFieldErrorsDefinition;
  expenses: ExpenseFieldErrorsDefinition;
}

export interface ProfileFieldErrorsDefinition {
  nickname?: string;
}

export interface LeftOverWarningFieldErrorsDefinition {
  left_over_warning_amount_dollars?: string;
}
