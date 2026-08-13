import FinancialVarianceDefinition from 'lib/money/definitions/financial-variance-definition';
import InputValidationResultDefinition from 'lib/numeric/definitions/input-validation-result-definition';
import { parseDecimalInput } from 'lib/numeric/parse-decimal-input';

/**
 * Converts validated dollar text into integer cents for API boundaries.
 *
 * Invalid input remains invalid instead of silently becoming zero.
 *
 * @param value - Dollar text to convert.
 * @returns Rounded integer cents, or NaN when the input is invalid.
 * @throws This function does not throw.
 */
export const dollarsToCents = (value: string): number => {
  const parseResult = parseDecimalInput(value, false);

  if (!parseResult.is_valid || parseResult.parsed_value === undefined) {
    return Number.NaN;
  }

  return Math.round(parseResult.parsed_value * 100);
};

/**
 * Converts integer cents into editable two-decimal dollar text.
 *
 * The stable representation prevents persisted values from changing shape when
 * restored into money inputs.
 *
 * @param cents - Integer cents to convert.
 * @returns Dollar text with exactly two decimal places.
 * @throws This function does not throw.
 */
export const centsToDollars = (cents: number): string => {
  return (cents / 100).toFixed(2);
};

/**
 * Formats integer cents as a localized two-decimal numeric dollar amount.
 *
 * This intentionally excludes the currency symbol so callers can compose it
 * when their surrounding text already supplies currency context.
 *
 * @param cents - Integer cents to format.
 * @returns A comma-separated amount with two decimal places.
 * @throws This function does not throw.
 */
export const formatCentsAsDollars = (cents: number): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(cents / 100);
};

/**
 * Formats integer cents as signed US-dollar display text.
 *
 * The sign precedes the dollar symbol while commas and two decimal places remain
 * consistent across financial summaries.
 *
 * @param cents - Integer cents to format.
 * @returns Currency text such as `$1,234.00` or `-$25.00`.
 * @throws This function does not throw.
 */
export const formatCentsAsCurrency = (cents: number): string => {
  const formattedAmount = formatCentsAsDollars(Math.abs(cents));

  if (cents < 0) {
    return `-$${formattedAmount}`;
  }

  return `$${formattedAmount}`;
};

/**
 * Validates optional non-negative dollar text.
 *
 * Blank and zero values remain valid for optional fields while malformed and
 * negative amounts receive specific errors.
 *
 * @param value - Dollar text to validate.
 * @returns A validation result with an error for invalid input.
 * @throws This function does not throw.
 */
export const validateDollarInput = (
  value: string
): InputValidationResultDefinition => {
  if (value === '') {
    return { valid: true };
  }

  const parseResult = parseDecimalInput(value, false);

  if (!parseResult.is_valid || parseResult.parsed_value === undefined) {
    return { valid: false, error: 'Enter a valid dollar amount (e.g. 123.45)' };
  }

  if (parseResult.parsed_value < 0) {
    return { valid: false, error: 'Amount must be zero or more' };
  }

  return { valid: true };
};

/**
 * Validates required positive dollar text.
 *
 * Required income and debt amounts must be present, valid, and greater than
 * zero before their forms proceed.
 *
 * @param value - Dollar text to validate.
 * @param fieldLabel - Field name used in validation messages.
 * @returns A validation result with an error for invalid input.
 * @throws This function does not throw.
 */
export const validatePositiveDollarInput = (
  value: string,
  fieldLabel: string
): InputValidationResultDefinition => {
  if (value === '') {
    return { valid: false, error: `${fieldLabel} is required` };
  }

  const parseResult = parseDecimalInput(value, false);

  if (!parseResult.is_valid || parseResult.parsed_value === undefined) {
    return { valid: false, error: 'Enter a valid dollar amount (e.g. 123.45)' };
  }

  if (parseResult.parsed_value <= 0) {
    return { valid: false, error: `${fieldLabel} must be greater than zero` };
  }

  return { valid: true };
};

/**
 * Calculates a factual actual-versus-planned variance for shared financial displays.
 *
 * Planned zero values return an unplanned monetary difference without dividing by zero.
 *
 * @param plannedCents - Planned amount in integer cents.
 * @param actualCents - Actual amount in integer cents.
 * @returns Signed difference, optional percentage, and planned-zero state.
 * @throws This function does not throw.
 */
export const calculateFinancialVariance = (
  plannedCents: number,
  actualCents: number
): FinancialVarianceDefinition => {
  const differenceCents = actualCents - plannedCents;

  if (plannedCents === 0) {
    return {
      difference_cents: differenceCents,
      percentage: null,
      is_unplanned: true,
    };
  }

  return {
    difference_cents: differenceCents,
    percentage: (differenceCents / plannedCents) * 100,
    is_unplanned: false,
  };
};

/**
 * Formats a signed financial variance without assigning good or bad meaning.
 *
 * @param variance - Calculated financial variance.
 * @returns Signed percentage or planned-zero unplanned monetary text.
 * @throws This function does not throw.
 */
export const formatFinancialVariance = (
  variance: FinancialVarianceDefinition
): string => {
  const sign = variance.difference_cents >= 0 ? '+' : '';

  if (variance.is_unplanned) {
    return `${sign}${formatCentsAsCurrency(variance.difference_cents)} unplanned`;
  }

  return `${sign}${variance.percentage?.toFixed(1)}% vs planned`;
};
