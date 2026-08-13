import DecimalParseResultDefinition from 'lib/numeric/definitions/decimal-parse-result-definition';

/**
 * Parses a decimal text input without accepting malformed numeric content.
 *
 * Money and percentage utilities share this boundary so their validation and
 * conversion behavior does not drift while retaining their separate domains.
 *
 * @param submittedValue - User-entered decimal text.
 * @param allowLeadingDecimal - Whether values such as `.25` are accepted.
 * @returns A typed parse result containing a number only for valid input.
 * @throws This function does not throw.
 */
export const parseDecimalInput = (
  submittedValue: string,
  allowLeadingDecimal: boolean
): DecimalParseResultDefinition => {
  const valueWithoutCommas = submittedValue.replaceAll(',', '');

  if (valueWithoutCommas === '') {
    return { is_valid: false };
  }

  const isNegative = valueWithoutCommas.startsWith('-');
  let unsignedValue = valueWithoutCommas;

  if (isNegative) {
    unsignedValue = valueWithoutCommas.slice(1);
  }

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
    (wholePart !== '' && !/^\d+$/.test(wholePart)) ||
    (decimalPart !== undefined &&
      decimalPart !== '' &&
      !/^\d+$/.test(decimalPart))
  ) {
    return { is_valid: false };
  }

  let normalizedValue = unsignedValue;

  if (unsignedValue.startsWith('.')) {
    normalizedValue = `0${unsignedValue}`;
  }

  let signedValue = normalizedValue;

  if (isNegative) {
    signedValue = `-${normalizedValue}`;
  }

  const parsedValue = parseFloat(signedValue);

  if (Number.isNaN(parsedValue)) {
    return { is_valid: false };
  }

  return { is_valid: true, parsed_value: parsedValue };
};
