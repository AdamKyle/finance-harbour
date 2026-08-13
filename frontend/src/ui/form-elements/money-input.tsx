import { ChangeEvent } from 'react';

import Input from './input';
import type MoneyInputProps from './types/money-input-props';

const MoneyInput = ({
  id,
  label,
  name,
  value,
  has_error,
  on_value_change,
  on_blur,
  disabled = false,
  error,
  help_text,
  placeholder = '0.00',
  required = false,
}: MoneyInputProps) => {
  const formatDisplayValue = (rawValue: string): string => {
    if (rawValue === '') {
      return '';
    }

    const [wholePart, decimalPart] = rawValue.split('.');
    const formattedWholePart = wholePart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');

    if (decimalPart === undefined) {
      return formattedWholePart;
    }

    return `${formattedWholePart}.${decimalPart}`;
  };

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const submittedValue = event.target.value.replaceAll(',', '');
    const decimalParts = submittedValue.split('.');

    if (decimalParts.length > 2) {
      return;
    }

    const [wholePart, decimalPart] = decimalParts;
    let unsignedWholePart = wholePart;

    if (wholePart.startsWith('-')) {
      unsignedWholePart = wholePart.slice(1);
    }
    const wholePartIsValid = Array.from(unsignedWholePart).every(
      (character) => character >= '0' && character <= '9'
    );
    const decimalPartIsValid =
      decimalPart === undefined ||
      (decimalPart.length <= 2 &&
        Array.from(decimalPart).every(
          (character) => character >= '0' && character <= '9'
        ));

    if (!wholePartIsValid || !decimalPartIsValid) {
      return;
    }

    on_value_change(submittedValue);
  };

  return (
    <Input
      id={id}
      label={label}
      name={name}
      type="text"
      inputMode="decimal"
      value={formatDisplayValue(value)}
      has_error={has_error}
      onChange={handleChange}
      onBlur={on_blur}
      disabled={disabled}
      error={error}
      help_text={help_text}
      placeholder={placeholder}
      required={required}
    />
  );
};

export default MoneyInput;
