import { SaveDebtProfileRequestDefinition } from 'components/pages/onboarding/api/hooks/definitions/save-debt-profile-request-definition';
import { SaveMonthlyExpenseRequestDefinition } from 'components/pages/onboarding/api/hooks/definitions/save-monthly-expense-request-definition';
import { SaveProfileOnboardingRequestDefinition } from 'components/pages/onboarding/api/hooks/definitions/save-profile-onboarding-request-definition';
import { DebtStepFormState } from 'components/pages/onboarding/types/debt-step-form-state';
import { ExpenseStepFormState } from 'components/pages/onboarding/types/expense-step-form-state';
import { IncomeStepFormState } from 'components/pages/onboarding/types/income-step-form-state';
import { ProfileStepFormState } from 'components/pages/onboarding/types/profile-step-form-state';
import {
  dollarsToCents,
  percentageToBasisPoints,
} from 'components/pages/onboarding/utils/money';

/**
 * Maps editable profile request data to the profile API payload.
 *
 * Blank optional values are omitted while backend field names are preserved.
 *
 * @param profileRequest - Current editable profile request.
 * @returns The profile onboarding API request.
 * @throws This function does not throw.
 */
export const mapProfileFormToApiRequest = (
  profileRequest: ProfileStepFormState
): SaveProfileOnboardingRequestDefinition => ({
  nickname: profileRequest.nickname || undefined,
  profile_photo: profileRequest.profile_photo || undefined,
});

/**
 * Maps editable debt rows to the debt-profile API payload.
 *
 * Validated dollar and percentage strings are converted to integer backend
 * units.
 *
 * @param debtRequest - Current editable debt request.
 * @returns The debt-profile API request.
 * @throws This function does not throw.
 */
export const mapDebtFormToApiRequest = (
  debtRequest: DebtStepFormState
): SaveDebtProfileRequestDefinition => ({
  debts: debtRequest.debts.map((debtEntry) => ({
    label: debtEntry.label,
    current_balance_cents: dollarsToCents(debtEntry.current_balance_dollars),
    interest_rate_basis_points: percentageToBasisPoints(
      debtEntry.interest_rate_percent
    ),
    minimum_payment_cents: dollarsToCents(debtEntry.minimum_payment_dollars),
    current_payment_cents: dollarsToCents(debtEntry.current_payment_dollars),
  })),
});

/**
 * Maps editable income data to the debt-profile API payload.
 *
 * The validated dollar string is converted to cents before submission.
 *
 * @param incomeRequest - Current editable income request.
 * @returns The income portion of the debt-profile API request.
 * @throws This function does not throw.
 */
export const mapIncomeFormToApiRequest = (
  incomeRequest: IncomeStepFormState
): SaveDebtProfileRequestDefinition => ({
  income_per_pay_period_cents: dollarsToCents(
    incomeRequest.income_per_pay_period_dollars
  ),
  pay_period_type: incomeRequest.pay_period_type || undefined,
});

/**
 * Maps editable expense data to the monthly-expense API payload.
 *
 * Optional blank common expenses become zero cents and fully blank
 * miscellaneous rows are omitted.
 *
 * @param expenseRequest - Current editable expense request.
 * @returns The monthly-expense API request.
 * @throws This function does not throw.
 */
export const mapExpenseFormToApiRequest = (
  expenseRequest: ExpenseStepFormState
): SaveMonthlyExpenseRequestDefinition => {
  const toOptionalExpenseCents = (submittedValue: string): number =>
    submittedValue !== '' ? dollarsToCents(submittedValue) : 0;
  const nonBlankMiscExpenses = expenseRequest.misc_expenses.filter(
    (miscExpense) =>
      miscExpense.label.trim() !== '' ||
      miscExpense.amount_dollars.trim() !== ''
  );

  return {
    rent_or_mortgage_cents: toOptionalExpenseCents(
      expenseRequest.rent_or_mortgage_dollars
    ),
    water_cents: toOptionalExpenseCents(expenseRequest.water_dollars),
    electricity_cents: toOptionalExpenseCents(
      expenseRequest.electricity_dollars
    ),
    food_cents: toOptionalExpenseCents(expenseRequest.food_dollars),
    internet_cents: toOptionalExpenseCents(expenseRequest.internet_dollars),
    phone_cents: toOptionalExpenseCents(expenseRequest.phone_dollars),
    car_payment_cents: toOptionalExpenseCents(
      expenseRequest.car_payment_dollars
    ),
    insurance_cents: toOptionalExpenseCents(expenseRequest.insurance_dollars),
    misc_expenses: nonBlankMiscExpenses.map((miscExpense) => ({
      label: miscExpense.label,
      amount_cents: toOptionalExpenseCents(miscExpense.amount_dollars),
    })),
  };
};
