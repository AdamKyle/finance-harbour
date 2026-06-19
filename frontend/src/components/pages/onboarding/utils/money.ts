interface DecimalParseResult {
  is_valid: boolean;
  parsed_value?: number;
}

interface ValidationResult {
  valid: boolean;
  error?: string;
}

const containsOnlyDigits = (submittedValue: string): boolean => {
  return Array.from(submittedValue).every(
    (digit) => digit >= '0' && digit <= '9'
  );
};

const parseDecimalInput = (
  submittedValue: string,
  allowLeadingDecimal: boolean
): DecimalParseResult => {
  const valueWithoutCommas = submittedValue.replaceAll(',', '');

  if (valueWithoutCommas === '') {
    return { is_valid: false };
  }

  const isNegative = valueWithoutCommas.startsWith('-');
  const unsignedValue = isNegative
    ? valueWithoutCommas.slice(1)
    : valueWithoutCommas;
  const decimalParts = unsignedValue.split('.');

  if (decimalParts.length > 2) {
    return { is_valid: false };
  }

  const [wholePart, decimalPart] = decimalParts;
  const hasWholeDigits = wholePart.length > 0;
  const hasFractionDigits = decimalPart !== undefined && decimalPart.length > 0;

  if (!hasWholeDigits && !(allowLeadingDecimal && hasFractionDigits)) {
    return { is_valid: false };
  }

  if (decimalPart !== undefined && decimalPart.length > 2) {
    return { is_valid: false };
  }

  if (
    (wholePart && !containsOnlyDigits(wholePart)) ||
    (decimalPart && !containsOnlyDigits(decimalPart))
  ) {
    return { is_valid: false };
  }

  const normalizedValue = unsignedValue.startsWith('.')
    ? `0${unsignedValue}`
    : unsignedValue;
  const parsedValue = parseFloat(
    isNegative ? `-${normalizedValue}` : normalizedValue
  );

  if (Number.isNaN(parsedValue)) {
    return { is_valid: false };
  }

  return { is_valid: true, parsed_value: parsedValue };
};

/**
 * Converts a validated dollar input into integer cents.
 *
 * This keeps API money payloads in cents without silently replacing invalid
 * values with zero.
 *
 * @param value - A previously validated dollar input.
 * @returns The rounded integer number of cents, or NaN for invalid input.
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
 * Formats integer cents as a two-decimal dollar string.
 *
 * This provides a consistent display value when persisted cent amounts are
 * restored into onboarding forms.
 *
 * @param cents - The integer cent amount to format.
 * @returns A dollar string with exactly two decimal places.
 * @throws This function does not throw.
 */
export const centsToDollars = (cents: number): string => {
  return (cents / 100).toFixed(2);
};

/**
 * Formats integer cents for user-facing dollar display.
 *
 * Thousands separators and two decimal places keep expense-card amounts easy
 * to scan without changing the stored integer value.
 *
 * @param cents - The integer cent amount to format.
 * @returns A comma-separated dollar amount with two decimal places.
 * @throws This function does not throw.
 */
export const formatCentsAsDollars = (cents: number): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(cents / 100);
};

/**
 * Converts a human percentage into integer basis points.
 *
 * Users enter percentage values such as 25 or .25 while the API receives the
 * equivalent basis-point value.
 *
 * @param percent - A previously validated human percentage input.
 * @returns The rounded integer basis points, or NaN for invalid input.
 * @throws This function does not throw.
 */
export const percentageToBasisPoints = (percent: string): number => {
  const parseResult = parseDecimalInput(percent, true);

  if (!parseResult.is_valid || parseResult.parsed_value === undefined) {
    return Number.NaN;
  }

  return Math.round(parseResult.parsed_value * 100);
};

/**
 * Validates an optional non-negative dollar input.
 *
 * Blank and zero values are allowed for optional expense fields, while invalid
 * numeric formats and negative amounts are rejected.
 *
 * @param value - The submitted dollar input.
 * @returns A validation result with an error message when invalid.
 * @throws This function does not throw.
 */
export const validateDollarInput = (value: string): ValidationResult => {
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
 * Validates a required positive dollar input.
 *
 * Required debt and income amounts must use a valid dollar format and be
 * greater than zero before the onboarding flow can continue.
 *
 * @param value - The submitted dollar input.
 * @param fieldLabel - The field name used in required and positive errors.
 * @returns A validation result with an error message when invalid.
 * @throws This function does not throw.
 */
export const validatePositiveDollarInput = (
  value: string,
  fieldLabel: string
): ValidationResult => {
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
 * Validates a required human interest percentage.
 *
 * Standard percentage entries, including values without a leading zero such
 * as .25, are accepted while invalid and negative percentages are rejected.
 *
 * @param value - The submitted human percentage input.
 * @returns A validation result with an error message when invalid.
 * @throws This function does not throw.
 */
export const validateInterestRateInput = (value: string): ValidationResult => {
  if (value === '') {
    return { valid: false, error: 'Enter an interest rate.' };
  }

  const parseResult = parseDecimalInput(value, true);

  if (!parseResult.is_valid || parseResult.parsed_value === undefined) {
    return { valid: false, error: 'Enter a valid interest rate.' };
  }

  if (parseResult.parsed_value < 0) {
    return { valid: false, error: 'Interest rate cannot be negative.' };
  }

  return { valid: true };
};
