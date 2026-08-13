import clsx from 'clsx';
import { KeyboardEvent, useRef, useState } from 'react';
import { type Matcher } from 'react-day-picker';

import DatePickerProps from './types/date-picker-props';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';
import Calendar from 'ui/calendar/calendar';
import { DatePickerTriggerVariant } from 'ui/date-picker/enums/date-picker-trigger-variant';
import FormError from 'ui/form-elements/form-error';

const DatePicker = ({
  id,
  label,
  selected,
  representative_month,
  minimum_date,
  on_change,
  error,
  help_text,
  trigger_variant = DatePickerTriggerVariant.ACTION,
}: DatePickerProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const errorId = `${id}-error`;
  const helpId = `${id}-help`;
  let disabledDates: Matcher | undefined;

  if (minimum_date !== undefined) {
    const minimumCalendarDate = new Date(
      minimum_date.getFullYear(),
      minimum_date.getMonth(),
      minimum_date.getDate()
    );

    disabledDates = { before: minimumCalendarDate };
  }

  const getButtonLabel = () => {
    if (selected === undefined) {
      return 'Choose date';
    }

    return selected.toLocaleDateString('en-CA', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getInputValue = () => {
    if (selected === undefined) {
      return '';
    }

    return selected.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  const getAriaDescription = () => {
    if (help_text === undefined && error === undefined) {
      return undefined;
    }

    if (help_text === undefined) {
      return errorId;
    }

    if (error === undefined) {
      return helpId;
    }

    return `${helpId} ${errorId}`;
  };

  const getTriggerAriaLabel = () => {
    return `${label}: ${getButtonLabel()}`;
  };

  const handleToggle = () => {
    setIsOpen((currentValue) => !currentValue);
  };

  const handleSelect = (date: Date | undefined) => {
    on_change(date);
    setIsOpen(false);

    if (trigger_variant === DatePickerTriggerVariant.INPUT) {
      inputRef.current?.focus();

      return;
    }

    triggerRef.current?.focus();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== 'Escape' || !isOpen) {
      return;
    }

    setIsOpen(false);

    if (trigger_variant === DatePickerTriggerVariant.INPUT) {
      inputRef.current?.focus();

      return;
    }

    triggerRef.current?.focus();
  };

  const handleInputKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key !== 'Enter' && event.key !== ' ') {
      return;
    }

    event.preventDefault();
    handleToggle();
  };

  const renderHelp = () => {
    if (help_text === undefined) {
      return null;
    }

    return (
      <p
        id={helpId}
        className="text-storm-dust-600 dark:text-storm-dust-300 text-sm"
      >
        {help_text}
      </p>
    );
  };

  const renderCalendar = () => {
    if (!isOpen) {
      return null;
    }

    return (
      <div
        id={`${id}-calendar`}
        className="border-storm-dust-200 dark:border-storm-dust-700 dark:bg-storm-dust-900 relative z-30 mt-2 rounded-xl border bg-white p-3 shadow-xl motion-reduce:transition-none"
      >
        <Calendar
          selected={selected}
          default_month={representative_month}
          disabled={disabledDates}
          on_select={handleSelect}
        />
      </div>
    );
  };

  const renderLabel = () => {
    const labelClassName =
      'text-storm-dust-800 dark:text-storm-dust-100 text-sm font-semibold';

    if (trigger_variant === DatePickerTriggerVariant.INPUT) {
      return (
        <label htmlFor={id} className={labelClassName}>
          {label}
        </label>
      );
    }

    return <span className={labelClassName}>{label}</span>;
  };

  const renderTrigger = () => {
    if (trigger_variant === DatePickerTriggerVariant.INPUT) {
      return (
        <div className="relative">
          <input
            ref={inputRef}
            id={id}
            type="text"
            readOnly
            value={getInputValue()}
            placeholder="MM/DD/YYYY"
            aria-describedby={getAriaDescription()}
            aria-invalid={error !== undefined}
            aria-controls={`${id}-calendar`}
            aria-expanded={isOpen}
            onClick={handleToggle}
            onKeyDown={handleInputKeyDown}
            className={clsx(
              'w-full cursor-pointer rounded-lg border bg-white py-3 pr-14 pl-4 text-base shadow-sm transition',
              'text-storm-dust-950 placeholder:text-storm-dust-500 focus-visible:ring-2 focus-visible:outline-none',
              'dark:bg-storm-dust-900 dark:text-storm-dust-50 dark:placeholder:text-storm-dust-400',
              {
                'border-persian-plum-500 focus-visible:border-persian-plum-500 focus-visible:ring-persian-plum-300 dark:border-persian-plum-400 dark:focus-visible:border-persian-plum-400 dark:focus-visible:ring-persian-plum-600':
                  error !== undefined,
                'border-storm-dust-300 focus-visible:border-blue-bell-500 focus-visible:ring-blue-bell-400 dark:border-storm-dust-700 dark:focus-visible:border-blue-bell-400 dark:focus-visible:ring-blue-bell-600':
                  error === undefined,
              }
            )}
          />
          <IconButton
            icon="fa-solid fa-calendar-days"
            label={`Open calendar for ${label}`}
            variant={ButtonVariant.GHOST}
            on_click={handleToggle}
            aria_controls={`${id}-calendar`}
            aria_expanded={isOpen}
            additional_css="absolute top-1/2 right-1 -translate-y-1/2 text-blue-bell-700 dark:text-blue-bell-300"
          />
        </div>
      );
    }

    return (
      <Button
        button_ref={triggerRef}
        label={getButtonLabel()}
        aria_label={getTriggerAriaLabel()}
        aria_describedby={getAriaDescription()}
        variant={ButtonVariant.PRIMARY}
        on_click={handleToggle}
        aria_expanded={isOpen}
        aria_controls={`${id}-calendar`}
        additional_css="w-full sm:w-fit"
      />
    );
  };

  return (
    <div className="flex flex-col gap-2" role="group" onKeyDown={handleKeyDown}>
      {renderLabel()}
      {renderTrigger()}
      {renderCalendar()}
      {renderHelp()}
      <FormError id={errorId} message={error} />
    </div>
  );
};

export default DatePicker;
