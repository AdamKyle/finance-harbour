import { UtilityType } from 'components/pages/onboarding/enums/utility-type';
import { DebtEntryFormState } from 'components/pages/onboarding/types/debt-entry-form-state';
import { DebtStepFormState } from 'components/pages/onboarding/types/debt-step-form-state';
import { ExpenseStepFormState } from 'components/pages/onboarding/types/expense-step-form-state';
import { ImportantExpensesStepFormState } from 'components/pages/onboarding/types/important-expenses-step-form-state';
import { IncomeStepFormState } from 'components/pages/onboarding/types/income-step-form-state';
import { LeftOverWarningStepFormState } from 'components/pages/onboarding/types/left-over-warning-step-form-state';
import { MiscExpenseEntryFormState } from 'components/pages/onboarding/types/misc-expense-entry-form-state';
import { OnboardingFormData } from 'components/pages/onboarding/types/onboarding-form-data';
import { ProfileStepFormState } from 'components/pages/onboarding/types/profile-step-form-state';
import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import { PayPeriodType } from 'components/payment-schedule/enums/pay-period-type';
import { PaycheckPosition } from 'components/payment-schedule/enums/paycheck-position';
import { PaymentScheduleFormState } from 'components/payment-schedule/types/payment-schedule-form-state';

const createPaycheckSchedule = (): PaymentScheduleFormState => ({
  timing: ExpensePaymentTiming.PAYCHECK_POSITION,
  paycheck_position: PaycheckPosition.FIRST,
  day_of_month: '',
  auto_deducted: false,
});

const createEveryPaycheckSchedule = (): PaymentScheduleFormState => ({
  timing: ExpensePaymentTiming.EVERY_PAYCHECK,
  paycheck_position: PaycheckPosition.FIRST,
  day_of_month: '',
  auto_deducted: false,
});

const createLastPaycheckSchedule = (): PaymentScheduleFormState => ({
  timing: ExpensePaymentTiming.PAYCHECK_POSITION,
  paycheck_position: PaycheckPosition.LAST,
  day_of_month: '',
  auto_deducted: false,
});

const hydratePaymentSchedule = (
  submittedValue: unknown
): PaymentScheduleFormState => {
  if (!isRecord(submittedValue)) {
    return createPaycheckSchedule();
  }

  let timing = ExpensePaymentTiming.PAYCHECK_POSITION;

  if (submittedValue.timing === ExpensePaymentTiming.DAY_OF_MONTH) {
    timing = ExpensePaymentTiming.DAY_OF_MONTH;
  } else if (submittedValue.timing === ExpensePaymentTiming.EVERY_PAYCHECK) {
    timing = ExpensePaymentTiming.EVERY_PAYCHECK;
  }

  return {
    timing,
    paycheck_position: getPaycheckPosition(submittedValue.paycheck_position),
    day_of_month: getStringValue(submittedValue, 'day_of_month'),
    auto_deducted: getNullableBooleanValue(submittedValue, 'auto_deducted'),
  };
};

const getPaycheckPosition = (submittedValue: unknown): PaycheckPosition => {
  if (submittedValue === PaycheckPosition.SECOND) {
    return PaycheckPosition.SECOND;
  }

  if (submittedValue === PaycheckPosition.THIRD) {
    return PaycheckPosition.THIRD;
  }

  if (submittedValue === PaycheckPosition.FOURTH) {
    return PaycheckPosition.FOURTH;
  }

  if (submittedValue === PaycheckPosition.LAST) {
    return PaycheckPosition.LAST;
  }

  return PaycheckPosition.FIRST;
};

const isRecord = (
  submittedValue: unknown
): submittedValue is Record<string, unknown> => {
  return (
    typeof submittedValue === 'object' &&
    submittedValue !== null &&
    !Array.isArray(submittedValue)
  );
};

const getStringValue = (
  submittedData: Record<string, unknown>,
  fieldName: string
): string => {
  const submittedValue = submittedData[fieldName];

  if (typeof submittedValue !== 'string') {
    return '';
  }

  return submittedValue;
};

const getPayPeriodType = (submittedValue: unknown): PayPeriodType | '' => {
  if (submittedValue === PayPeriodType.WEEKLY) {
    return PayPeriodType.WEEKLY;
  }

  if (submittedValue === PayPeriodType.BIWEEKLY) {
    return PayPeriodType.BIWEEKLY;
  }

  if (submittedValue === PayPeriodType.MONTHLY) {
    return PayPeriodType.MONTHLY;
  }

  return '';
};

const getUtilityType = (submittedValue: unknown): UtilityType | '' => {
  if (submittedValue === UtilityType.ELECTRICITY) {
    return UtilityType.ELECTRICITY;
  }

  if (submittedValue === UtilityType.WATER) {
    return UtilityType.WATER;
  }

  if (submittedValue === UtilityType.WATER_AND_ELECTRICITY) {
    return UtilityType.WATER_AND_ELECTRICITY;
  }

  if (submittedValue === UtilityType.UTILITIES) {
    return UtilityType.UTILITIES;
  }

  if (submittedValue === UtilityType.CUSTOM) {
    return UtilityType.CUSTOM;
  }

  return '';
};

const getBooleanValue = (
  submittedData: Record<string, unknown>,
  fieldName: string
): boolean => submittedData[fieldName] === true;

const getNullableBooleanValue = (
  submittedData: Record<string, unknown>,
  fieldName: string
): boolean | null => {
  const submittedValue = submittedData[fieldName];

  if (typeof submittedValue !== 'boolean') {
    return null;
  }

  return submittedValue;
};

const getProfilePhoto = (
  submittedData: Record<string, unknown>,
  defaultProfilePhoto: string
): string => {
  const submittedProfilePhoto = getStringValue(submittedData, 'profile_photo');

  if (submittedProfilePhoto === '') {
    return defaultProfilePhoto;
  }

  return submittedProfilePhoto;
};

const getStringList = (
  submittedData: Record<string, unknown>,
  fieldName: string
): string[] => {
  const submittedValue = submittedData[fieldName];

  if (!Array.isArray(submittedValue)) {
    return [];
  }

  return submittedValue.filter(
    (listValue): listValue is string => typeof listValue === 'string'
  );
};

/**
 * Creates the initial onboarding request data.
 *
 * The API hook uses this shape as the single source of truth before persisted
 * onboarding progress is available.
 *
 * @returns A complete empty onboarding request.
 * @throws This function does not throw.
 */
export const createInitialOnboardingFormRequest = (): OnboardingFormData => ({
  profile: {
    nickname: '',
    profile_photo: 'avatar-d',
  },
  debts: {
    debts: [],
  },
  income: {
    income_per_pay_period_dollars: '',
    pay_period_type: '',
    next_pay_date: '',
  },
  expenses: {
    rent_or_mortgage_dollars: '',
    utility_type: '',
    utility_custom_label: '',
    utilities_dollars: '',
    utilities_includes_internet: false,
    utilities_includes_cable: false,
    food_dollars: '',
    internet_dollars: '',
    phone_dollars: '',
    car_payment_dollars: '',
    insurance_dollars: '',
    misc_expenses: [],
    payment_schedules: {
      rent_or_mortgage: createLastPaycheckSchedule(),
      utilities: createPaycheckSchedule(),
      food: createEveryPaycheckSchedule(),
      internet: createPaycheckSchedule(),
      phone: createPaycheckSchedule(),
      car_payment: createPaycheckSchedule(),
      insurance: createPaycheckSchedule(),
    },
  },
  important_expenses: {
    selected_keys: [],
  },
  left_over_warning: {
    left_over_warning_amount_dollars: '0.00',
  },
});

/**
 * Hydrates the profile step from persisted onboarding progress.
 *
 * Invalid or missing values are replaced with the approved profile defaults.
 *
 * @param submittedValue - Persisted profile progress from the API.
 * @returns A safe profile request object.
 * @throws This function does not throw.
 */
export const hydrateProfileFormRequest = (
  submittedValue: unknown
): ProfileStepFormState => {
  const initialRequest = createInitialOnboardingFormRequest().profile;

  if (!isRecord(submittedValue)) {
    return initialRequest;
  }

  return {
    nickname: getStringValue(submittedValue, 'nickname'),
    profile_photo: getProfilePhoto(
      submittedValue,
      initialRequest.profile_photo
    ),
  };
};

/**
 * Hydrates debt rows from persisted onboarding progress.
 *
 * Each row is normalized to the editable debt request shape used by the form.
 *
 * @param submittedValue - Persisted debt progress from the API.
 * @returns A safe debt-step request object.
 * @throws This function does not throw.
 */
export const hydrateDebtFormRequest = (
  submittedValue: unknown
): DebtStepFormState => {
  if (!isRecord(submittedValue)) {
    return { debts: [] };
  }

  if (!Array.isArray(submittedValue.debts)) {
    return { debts: [] };
  }

  const debts: DebtEntryFormState[] = submittedValue.debts.map((debtEntry) => {
    if (!isRecord(debtEntry)) {
      return {
        label: '',
        current_balance_dollars: '',
        minimum_payment_dollars: '',
        current_payment_dollars: '',
        payment_schedule: createPaycheckSchedule(),
      };
    }

    return {
      label: getStringValue(debtEntry, 'label'),
      current_balance_dollars: getStringValue(
        debtEntry,
        'current_balance_dollars'
      ),
      minimum_payment_dollars: getStringValue(
        debtEntry,
        'minimum_payment_dollars'
      ),
      current_payment_dollars: getStringValue(
        debtEntry,
        'current_payment_dollars'
      ),
      payment_schedule: hydratePaymentSchedule(debtEntry.payment_schedule),
    };
  });

  return { debts };
};

/**
 * Hydrates income data from persisted onboarding progress.
 *
 * Missing values are normalized to empty controlled-field values.
 *
 * @param submittedValue - Persisted income progress from the API.
 * @returns A safe income-step request object.
 * @throws This function does not throw.
 */
export const hydrateIncomeFormRequest = (
  submittedValue: unknown
): IncomeStepFormState => {
  if (!isRecord(submittedValue)) {
    return createInitialOnboardingFormRequest().income;
  }

  return {
    income_per_pay_period_dollars: getStringValue(
      submittedValue,
      'income_per_pay_period_dollars'
    ),
    pay_period_type: getPayPeriodType(submittedValue.pay_period_type),
    next_pay_date: getStringValue(submittedValue, 'next_pay_date'),
  };
};

/**
 * Hydrates expense data from persisted onboarding progress.
 *
 * Common and miscellaneous expenses are normalized to controlled string
 * values without changing their API field names.
 *
 * @param submittedValue - Persisted expense progress from the API.
 * @returns A safe expense-step request object.
 * @throws This function does not throw.
 */
export const hydrateExpenseFormRequest = (
  submittedValue: unknown
): ExpenseStepFormState => {
  if (!isRecord(submittedValue)) {
    return createInitialOnboardingFormRequest().expenses;
  }

  let submittedMiscExpenses: unknown[] = [];

  if (Array.isArray(submittedValue.misc_expenses)) {
    submittedMiscExpenses = submittedValue.misc_expenses;
  }

  const miscExpenses: MiscExpenseEntryFormState[] = submittedMiscExpenses.map(
    (miscExpense) => {
      if (!isRecord(miscExpense)) {
        return {
          label: '',
          amount_dollars: '',
          payment_schedule: createPaycheckSchedule(),
        };
      }

      return {
        label: getStringValue(miscExpense, 'label'),
        amount_dollars: getStringValue(miscExpense, 'amount_dollars'),
        payment_schedule: hydratePaymentSchedule(miscExpense.payment_schedule),
      };
    }
  );
  let paymentScheduleValues: Record<string, unknown> | null = null;

  if (isRecord(submittedValue.payment_schedules)) {
    paymentScheduleValues = submittedValue.payment_schedules;
  }

  const getPaymentScheduleValue = (sourceKey: string) => {
    if (paymentScheduleValues === null) {
      return null;
    }

    return paymentScheduleValues[sourceKey];
  };

  return {
    rent_or_mortgage_dollars: getStringValue(
      submittedValue,
      'rent_or_mortgage_dollars'
    ),
    utility_type: getUtilityType(submittedValue.utility_type),
    utility_custom_label: getStringValue(
      submittedValue,
      'utility_custom_label'
    ),
    utilities_dollars: getStringValue(submittedValue, 'utilities_dollars'),
    utilities_includes_internet: getBooleanValue(
      submittedValue,
      'utilities_includes_internet'
    ),
    utilities_includes_cable: getBooleanValue(
      submittedValue,
      'utilities_includes_cable'
    ),
    food_dollars: getStringValue(submittedValue, 'food_dollars'),
    internet_dollars: getStringValue(submittedValue, 'internet_dollars'),
    phone_dollars: getStringValue(submittedValue, 'phone_dollars'),
    car_payment_dollars: getStringValue(submittedValue, 'car_payment_dollars'),
    insurance_dollars: getStringValue(submittedValue, 'insurance_dollars'),
    misc_expenses: miscExpenses,
    payment_schedules: {
      rent_or_mortgage: hydratePaymentSchedule(
        getPaymentScheduleValue('rent_or_mortgage')
      ),
      utilities: hydratePaymentSchedule(getPaymentScheduleValue('utilities')),
      food: hydratePaymentSchedule(getPaymentScheduleValue('food')),
      internet: hydratePaymentSchedule(getPaymentScheduleValue('internet')),
      phone: hydratePaymentSchedule(getPaymentScheduleValue('phone')),
      car_payment: hydratePaymentSchedule(
        getPaymentScheduleValue('car_payment')
      ),
      insurance: hydratePaymentSchedule(getPaymentScheduleValue('insurance')),
    },
  };
};

/**
 * Hydrates selected important-expense keys from persisted progress.
 *
 * Non-string values are discarded so selection state stays type safe.
 *
 * @param submittedValue - Persisted important-expense progress.
 * @returns A safe important-expense request.
 * @throws This function does not throw.
 */
export const hydrateImportantExpensesFormRequest = (
  submittedValue: unknown
): ImportantExpensesStepFormState => {
  if (!isRecord(submittedValue)) {
    return createInitialOnboardingFormRequest().important_expenses;
  }

  return {
    selected_keys: getStringList(submittedValue, 'selected_keys'),
  };
};

/**
 * Hydrates the left-over warning threshold from persisted progress.
 *
 * Missing values use the zero-dollar default.
 *
 * @param submittedValue - Persisted threshold progress.
 * @returns A safe warning-threshold request.
 * @throws This function does not throw.
 */
export const hydrateLeftOverWarningFormRequest = (
  submittedValue: unknown
): LeftOverWarningStepFormState => {
  if (!isRecord(submittedValue)) {
    return createInitialOnboardingFormRequest().left_over_warning;
  }

  const submittedAmount = getStringValue(
    submittedValue,
    'left_over_warning_amount_dollars'
  );

  if (submittedAmount === '') {
    return createInitialOnboardingFormRequest().left_over_warning;
  }

  return {
    left_over_warning_amount_dollars: submittedAmount,
  };
};

/**
 * Hydrates the complete onboarding request from persisted progress.
 *
 * The returned object is ready to become the API hook's editable request
 * state.
 *
 * @param submittedValue - Persisted onboarding form data from the API.
 * @returns A complete normalized onboarding request.
 * @throws This function does not throw.
 */
export const hydrateOnboardingFormRequest = (
  submittedValue: unknown
): OnboardingFormData => {
  if (!isRecord(submittedValue)) {
    return createInitialOnboardingFormRequest();
  }

  return {
    profile: hydrateProfileFormRequest(submittedValue.profile),
    debts: hydrateDebtFormRequest(submittedValue.debts),
    income: hydrateIncomeFormRequest(submittedValue.income),
    expenses: hydrateExpenseFormRequest(submittedValue.expenses),
    important_expenses: hydrateImportantExpensesFormRequest(
      submittedValue.important_expenses
    ),
    left_over_warning: hydrateLeftOverWarningFormRequest(
      submittedValue.left_over_warning
    ),
  };
};

/**
 * Builds persisted onboarding progress data from the current request.
 *
 * Fully blank miscellaneous rows are omitted while all other request data is
 * preserved.
 *
 * @param requestData - Current onboarding request data.
 * @returns Onboarding form data ready for the progress endpoint.
 * @throws This function does not throw.
 */
export const buildOnboardingProgressFormData = (
  requestData: OnboardingFormData
): OnboardingFormData => {
  const nonBlankMiscExpenses = requestData.expenses.misc_expenses.filter(
    (miscExpense) =>
      miscExpense.label.trim() !== '' ||
      miscExpense.amount_dollars.trim() !== ''
  );

  return {
    ...requestData,
    expenses: {
      ...requestData.expenses,
      misc_expenses: nonBlankMiscExpenses,
    },
  };
};
