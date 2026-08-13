import { dollarsToCents } from 'lib/money/money';

import ExpensePaymentScheduleDefinition from 'components/pages/onboarding/api/hooks/definitions/expense-payment-schedule-definition';
import RecurringExpenseDefinition from 'components/pages/onboarding/api/hooks/definitions/recurring-expense-definition';
import { SaveDebtProfileRequestDefinition } from 'components/pages/onboarding/api/hooks/definitions/save-debt-profile-request-definition';
import { SaveLeftOverWarningThresholdRequestDefinition } from 'components/pages/onboarding/api/hooks/definitions/save-left-over-warning-threshold-request-definition';
import { SaveMonthlyExpenseRequestDefinition } from 'components/pages/onboarding/api/hooks/definitions/save-monthly-expense-request-definition';
import { SaveProfileOnboardingRequestDefinition } from 'components/pages/onboarding/api/hooks/definitions/save-profile-onboarding-request-definition';
import { RecurringExpenseCategory } from 'components/pages/onboarding/enums/recurring-expense-category';
import { UtilityType } from 'components/pages/onboarding/enums/utility-type';
import { DebtStepFormState } from 'components/pages/onboarding/types/debt-step-form-state';
import { ExpenseStepFormState } from 'components/pages/onboarding/types/expense-step-form-state';
import { IncomeStepFormState } from 'components/pages/onboarding/types/income-step-form-state';
import { LeftOverWarningStepFormState } from 'components/pages/onboarding/types/left-over-warning-step-form-state';
import { ProfileStepFormState } from 'components/pages/onboarding/types/profile-step-form-state';
import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import { PayPeriodType } from 'components/payment-schedule/enums/pay-period-type';
import { PaymentScheduleFormState } from 'components/payment-schedule/types/payment-schedule-form-state';

const getScheduleDay = (schedule: PaymentScheduleFormState): number | null => {
  if (schedule.day_of_month === '') {
    return null;
  }

  return Number.parseInt(schedule.day_of_month, 10);
};

const getPaycheckPosition = (schedule: PaymentScheduleFormState) => {
  if (schedule.timing === ExpensePaymentTiming.EVERY_PAYCHECK) {
    return null;
  }

  return schedule.paycheck_position;
};

const getAutoDeducted = (schedule: PaymentScheduleFormState) => {
  return schedule.auto_deducted === true;
};

const getUtilityLabel = (expenseRequest: ExpenseStepFormState): string => {
  if (expenseRequest.utility_type === UtilityType.ELECTRICITY) {
    return 'Electricity';
  }

  if (expenseRequest.utility_type === UtilityType.WATER) {
    return 'Water';
  }

  if (expenseRequest.utility_type === UtilityType.WATER_AND_ELECTRICITY) {
    return 'Water + electricity';
  }

  if (expenseRequest.utility_type === UtilityType.CUSTOM) {
    return expenseRequest.utility_custom_label.trim();
  }

  return 'Utilities';
};

/** Maps the profile form state to the profile onboarding request. */
export const mapProfileFormToApiRequest = (
  profileRequest: ProfileStepFormState
): SaveProfileOnboardingRequestDefinition => {
  let profilePhoto: string | undefined;

  if (profileRequest.profile_photo !== '') {
    profilePhoto = profileRequest.profile_photo;
  }

  return { nickname: profileRequest.nickname, profile_photo: profilePhoto };
};

/** Maps the warning threshold form state to integer cents. */
export const mapLeftOverWarningFormToApiRequest = (
  warningRequest: LeftOverWarningStepFormState
): SaveLeftOverWarningThresholdRequestDefinition => ({
  left_over_warning_amount_cents: dollarsToCents(
    warningRequest.left_over_warning_amount_dollars
  ),
});

/** Maps debt form values to the debt-profile request contract. */
export const mapDebtFormToApiRequest = (
  debtRequest: DebtStepFormState
): SaveDebtProfileRequestDefinition => ({
  debts: debtRequest.debts.map((debtEntry) => ({
    label: debtEntry.label,
    current_balance_cents: dollarsToCents(debtEntry.current_balance_dollars),
    minimum_payment_cents: dollarsToCents(debtEntry.minimum_payment_dollars),
    current_payment_cents: dollarsToCents(debtEntry.current_payment_dollars),
  })),
});

/** Maps income and payday context to the debt-profile request. */
export const mapIncomeFormToApiRequest = (
  incomeRequest: IncomeStepFormState
): SaveDebtProfileRequestDefinition => {
  let payPeriodType: PayPeriodType | undefined;
  let nextPayDate: string | null = incomeRequest.next_pay_date;

  if (incomeRequest.pay_period_type !== '') {
    payPeriodType = incomeRequest.pay_period_type;
  }

  if (nextPayDate === '') {
    nextPayDate = null;
  }

  return {
    income_per_pay_period_cents: dollarsToCents(
      incomeRequest.income_per_pay_period_dollars
    ),
    pay_period_type: payPeriodType,
    next_pay_date: nextPayDate,
  };
};

/** Maps expense form values to normalized recurring expenses. */
export const mapExpenseFormToApiRequest = (
  expenseRequest: ExpenseStepFormState
): SaveMonthlyExpenseRequestDefinition => {
  const recurringExpenses: RecurringExpenseDefinition[] = [];

  const appendExpense = (
    sourceKey: string,
    category: RecurringExpenseCategory,
    label: string,
    amount: string
  ) => {
    if (amount.trim() === '' || dollarsToCents(amount) <= 0) {
      return;
    }

    recurringExpenses.push({
      source_key: sourceKey,
      category,
      label,
      amount_cents: dollarsToCents(amount),
      utility_type: '',
      includes_internet: false,
      includes_cable: false,
    });
  };

  appendExpense(
    'rent_or_mortgage',
    RecurringExpenseCategory.RENT_OR_MORTGAGE,
    'Rent or mortgage',
    expenseRequest.rent_or_mortgage_dollars
  );

  if (
    expenseRequest.utility_type !== '' &&
    expenseRequest.utilities_dollars.trim() !== '' &&
    dollarsToCents(expenseRequest.utilities_dollars) > 0
  ) {
    recurringExpenses.push({
      source_key: 'utilities',
      category: RecurringExpenseCategory.UTILITIES,
      label: getUtilityLabel(expenseRequest),
      amount_cents: dollarsToCents(expenseRequest.utilities_dollars),
      utility_type: expenseRequest.utility_type,
      includes_internet: expenseRequest.utilities_includes_internet,
      includes_cable: expenseRequest.utilities_includes_cable,
    });
  }

  appendExpense(
    'food',
    RecurringExpenseCategory.FOOD,
    'Food',
    expenseRequest.food_dollars
  );

  if (!expenseRequest.utilities_includes_internet) {
    appendExpense(
      'internet',
      RecurringExpenseCategory.INTERNET,
      'Internet',
      expenseRequest.internet_dollars
    );
  }

  appendExpense(
    'phone',
    RecurringExpenseCategory.PHONE,
    'Phone',
    expenseRequest.phone_dollars
  );
  appendExpense(
    'car_payment',
    RecurringExpenseCategory.CAR_PAYMENT,
    'Car payment',
    expenseRequest.car_payment_dollars
  );
  appendExpense(
    'insurance',
    RecurringExpenseCategory.INSURANCE,
    'Insurance',
    expenseRequest.insurance_dollars
  );

  expenseRequest.misc_expenses.forEach((expense, index) => {
    appendExpense(
      `misc:${index}`,
      RecurringExpenseCategory.MISC,
      expense.label.trim(),
      expense.amount_dollars
    );
  });

  return { recurring_expenses: recurringExpenses };
};

/** Maps configured debt schedules to one bounded request payload. */
export const mapDebtSchedulesToApiRequest = (
  debtRequest: DebtStepFormState
): SaveDebtProfileRequestDefinition => {
  const paymentSchedules: ExpensePaymentScheduleDefinition[] = [];

  debtRequest.debts.forEach((debtEntry, index) => {
    if (dollarsToCents(debtEntry.current_payment_dollars) <= 0) {
      return;
    }

    paymentSchedules.push({
      source_key: `debt:${index}`,
      timing: debtEntry.payment_schedule.timing,
      paycheck_position: getPaycheckPosition(debtEntry.payment_schedule),
      day_of_month: getScheduleDay(debtEntry.payment_schedule),
      auto_deducted: getAutoDeducted(debtEntry.payment_schedule),
    });
  });

  return { payment_schedules: paymentSchedules };
};

/** Maps active recurring-expense schedules to one bounded request payload. */
export const mapExpenseSchedulesToApiRequest = (
  expenseRequest: ExpenseStepFormState
): SaveMonthlyExpenseRequestDefinition => {
  const paymentSchedules: ExpensePaymentScheduleDefinition[] = [];

  const appendSchedule = (
    sourceKey: string,
    amount: string,
    schedule: PaymentScheduleFormState
  ) => {
    if (amount.trim() === '' || dollarsToCents(amount) <= 0) {
      return;
    }

    paymentSchedules.push({
      source_key: sourceKey,
      timing: schedule.timing,
      paycheck_position: getPaycheckPosition(schedule),
      day_of_month: getScheduleDay(schedule),
      auto_deducted: getAutoDeducted(schedule),
    });
  };

  appendSchedule(
    'rent_or_mortgage',
    expenseRequest.rent_or_mortgage_dollars,
    expenseRequest.payment_schedules.rent_or_mortgage
  );
  appendSchedule(
    'utilities',
    expenseRequest.utilities_dollars,
    expenseRequest.payment_schedules.utilities
  );
  appendSchedule(
    'food',
    expenseRequest.food_dollars,
    expenseRequest.payment_schedules.food
  );

  if (!expenseRequest.utilities_includes_internet) {
    appendSchedule(
      'internet',
      expenseRequest.internet_dollars,
      expenseRequest.payment_schedules.internet
    );
  }

  appendSchedule(
    'phone',
    expenseRequest.phone_dollars,
    expenseRequest.payment_schedules.phone
  );
  appendSchedule(
    'car_payment',
    expenseRequest.car_payment_dollars,
    expenseRequest.payment_schedules.car_payment
  );
  appendSchedule(
    'insurance',
    expenseRequest.insurance_dollars,
    expenseRequest.payment_schedules.insurance
  );

  expenseRequest.misc_expenses.forEach((expense, index) => {
    appendSchedule(
      `misc:${index}`,
      expense.amount_dollars,
      expense.payment_schedule
    );
  });

  return { payment_schedules: paymentSchedules };
};
