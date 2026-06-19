import clsx from 'clsx';

import FormError from './form-error';
import type SelectProps from './types/select-props';

const Select = ({
  children,
  id,
  label,
  name,
  value,
  additional_css,
  disabled = false,
  error,
  has_error,
  help_text,
  onChange,
  required = false,
}: SelectProps) => {
  const errorId = `${id}-error`;
  const helpTextId = `${id}-help`;

  const getDescribedBy = () => {
    if (!help_text && !has_error) {
      return undefined;
    }

    if (help_text && !has_error) {
      return helpTextId;
    }

    if (!help_text && has_error) {
      return errorId;
    }

    return `${helpTextId} ${errorId}`;
  };

  const renderHelpText = () => {
    if (!help_text) {
      return null;
    }

    return (
      <p
        className="text-storm-dust-600 dark:text-storm-dust-300 text-sm"
        id={helpTextId}
      >
        {help_text}
      </p>
    );
  };

  return (
    <div className="flex flex-col gap-2">
      <label
        className="text-storm-dust-800 dark:text-storm-dust-100 text-sm font-semibold"
        htmlFor={id}
      >
        {label}
      </label>

      <select
        aria-describedby={getDescribedBy()}
        aria-invalid={has_error}
        aria-required={required}
        className={clsx(
          'w-full rounded-lg border bg-white px-4 py-3',
          'text-storm-dust-950 text-base shadow-sm transition',
          'focus-visible:ring-2 focus-visible:outline-none',
          'disabled:cursor-not-allowed disabled:opacity-60',
          'dark:bg-storm-dust-900 dark:text-storm-dust-50',
          {
            'border-persian-plum-500 focus-visible:border-persian-plum-500 focus-visible:ring-persian-plum-300 dark:border-persian-plum-400 dark:focus-visible:border-persian-plum-400 dark:focus-visible:ring-persian-plum-600':
              has_error,
            'border-storm-dust-300 focus-visible:border-blue-bell-500 focus-visible:ring-blue-bell-400 dark:border-storm-dust-700 dark:focus-visible:border-blue-bell-400 dark:focus-visible:ring-blue-bell-600':
              !has_error,
          },
          additional_css
        )}
        disabled={disabled}
        id={id}
        name={name}
        onChange={onChange}
        required={required}
        value={value}
      >
        {children}
      </select>

      {renderHelpText()}
      <FormError id={errorId} message={error} />
    </div>
  );
};

export default Select;
