import { ChangeEvent, useEffect } from 'react';

import { ExpensePaymentTiming } from './enums/expense-payment-timing';
import { PayPeriodType } from './enums/pay-period-type';
import { PaycheckPosition } from './enums/paycheck-position';
import PaymentScheduleFieldsProps from './types/payment-schedule-fields-props';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import DatePicker from 'ui/date-picker/date-picker';
import Select from 'ui/form-elements/select';
import Tooltip from 'ui/tool-tip/tool-tip';

const PaymentScheduleFields = ({
  id,
  label,
  representative_date,
  pay_period_type,
  show_large_bill_hint = false,
  schedule,
  on_change,
  error,
}: PaymentScheduleFieldsProps) => {
  useEffect(() => {
    if (
      pay_period_type !== PayPeriodType.MONTHLY ||
      schedule.paycheck_position === PaycheckPosition.FIRST
    ) {
      return;
    }

    on_change({ ...schedule, paycheck_position: PaycheckPosition.FIRST });
  }, [on_change, pay_period_type, schedule]);

  const getRepresentativeDate = () => {
    const parsedDate = new Date(`${representative_date}T12:00:00`);

    if (Number.isNaN(parsedDate.getTime())) {
      return new Date();
    }

    return parsedDate;
  };

  const getSelectedDate = () => {
    if (schedule.day_of_month === '') {
      return undefined;
    }

    const selectedDay = Number.parseInt(schedule.day_of_month, 10);
    const representativeDate = getRepresentativeDate();

    for (let monthOffset = 0; monthOffset < 12; monthOffset += 1) {
      const candidate = new Date(
        representativeDate.getFullYear(),
        representativeDate.getMonth() + monthOffset,
        selectedDay,
        12
      );

      if (candidate.getDate() === selectedDay) {
        return candidate;
      }
    }

    return undefined;
  };

  const selectedDate = getSelectedDate();

  const handleTimingChange = (event: ChangeEvent<HTMLSelectElement>) => {
    if (event.target.value === ExpensePaymentTiming.DAY_OF_MONTH) {
      on_change({
        ...schedule,
        timing: ExpensePaymentTiming.DAY_OF_MONTH,
        auto_deducted: null,
      });

      return;
    }

    if (event.target.value === ExpensePaymentTiming.EVERY_PAYCHECK) {
      on_change({
        timing: ExpensePaymentTiming.EVERY_PAYCHECK,
        paycheck_position: PaycheckPosition.FIRST,
        day_of_month: '',
        auto_deducted: false,
      });

      return;
    }

    on_change({
      timing: ExpensePaymentTiming.PAYCHECK_POSITION,
      paycheck_position: PaycheckPosition.FIRST,
      day_of_month: '',
      auto_deducted: false,
    });
  };

  const handlePositionChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const positions = Object.values(PaycheckPosition);
    const paycheckPosition = positions.find(
      (position) => position === event.target.value
    );

    if (paycheckPosition === undefined) {
      return;
    }

    on_change({ ...schedule, paycheck_position: paycheckPosition });
  };

  const handleDayChange = (date: Date | undefined) => {
    on_change({ ...schedule, day_of_month: date?.getDate().toString() ?? '' });
  };

  const handleAutoDeductChange = (event: ChangeEvent<HTMLSelectElement>) => {
    if (event.target.value === 'yes') {
      on_change({ ...schedule, auto_deducted: true });

      return;
    }

    if (event.target.value === 'no') {
      on_change({ ...schedule, auto_deducted: false });

      return;
    }

    on_change({ ...schedule, auto_deducted: null });
  };

  const renderWeeklyPositions = () => {
    if (pay_period_type !== PayPeriodType.WEEKLY) {
      return null;
    }

    return (
      <>
        <option value={PaycheckPosition.THIRD}>Third paycheck</option>
        <option value={PaycheckPosition.FOURTH}>Fourth paycheck</option>
      </>
    );
  };

  const renderPositionInput = () => {
    if (pay_period_type === PayPeriodType.MONTHLY) {
      return (
        <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
          Your monthly paycheck
        </p>
      );
    }

    return (
      <Select
        id={`${id}-position`}
        name={`${id}_position`}
        label="Which paycheck should fund this payment?"
        value={schedule.paycheck_position}
        has_error={error !== undefined}
        onChange={handlePositionChange}
      >
        <option value={PaycheckPosition.FIRST}>
          First paycheck of the month
        </option>
        <option value={PaycheckPosition.SECOND}>
          Second paycheck of the month
        </option>
        {renderWeeklyPositions()}
        <option value={PaycheckPosition.LAST}>
          Last paycheck of the month
        </option>
      </Select>
    );
  };

  const renderPaycheckPosition = () => {
    if (schedule.timing !== ExpensePaymentTiming.PAYCHECK_POSITION) {
      return null;
    }

    return renderPositionInput();
  };

  const renderLargePaymentHint = () => {
    if (
      !show_large_bill_hint ||
      schedule.timing !== ExpensePaymentTiming.PAYCHECK_POSITION
    ) {
      return null;
    }

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Large fixed payments are often easier to place on the second or last
        paycheck of the month.
      </p>
    );
  };

  const renderWeekendAdjustment = () => {
    if (selectedDate === undefined) {
      return null;
    }

    const weekday = selectedDate.getDay();

    if (weekday !== 0 && weekday !== 6) {
      return null;
    }

    const adjustedDate = new Date(selectedDate);
    let daysToMonday = 1;

    if (weekday === 6) {
      daysToMonday = 2;
    }

    adjustedDate.setDate(selectedDate.getDate() + daysToMonday);
    const dateFormat: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    };

    return (
      <Alert variant={AlertVariant.INFO}>
        {selectedDate.toLocaleDateString('en-CA', dateFormat)} is a weekend.
        Finance Harbour will plan this payment for{' '}
        {adjustedDate.toLocaleDateString('en-CA', dateFormat)}.
      </Alert>
    );
  };

  const renderAutoDeductStatus = () => {
    if (schedule.auto_deducted !== true) {
      return null;
    }

    return (
      <p className="text-sweet-corn-900 dark:text-sweet-corn-100 text-sm font-semibold">
        Auto-deducted · Important
      </p>
    );
  };

  const renderDayInput = () => {
    if (schedule.timing !== ExpensePaymentTiming.DAY_OF_MONTH) {
      return null;
    }

    let autoDeductValue = '';

    if (schedule.auto_deducted === true) {
      autoDeductValue = 'yes';
    } else if (schedule.auto_deducted === false) {
      autoDeductValue = 'no';
    }

    return (
      <div className="flex flex-col gap-3">
        <DatePicker
          id={`${id}-day`}
          label="Choose a representative payment date"
          error={error}
          help_text="We'll use this day each month. Short months use their last valid day, and weekend payments move to Monday."
          selected={selectedDate}
          representative_month={getRepresentativeDate()}
          on_change={handleDayChange}
        />
        {renderWeekendAdjustment()}
        {renderPositionInput()}
        <Select
          id={`${id}-auto-deducted`}
          name={`${id}_auto_deducted`}
          label="Is this payment automatically deducted?"
          value={autoDeductValue}
          has_error={error !== undefined}
          onChange={handleAutoDeductChange}
        >
          <option value="">Select an answer</option>
          <option value="yes">Yes</option>
          <option value="no">No</option>
        </Select>
        {renderAutoDeductStatus()}
      </div>
    );
  };

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <div className="flex flex-col gap-3">
        <Select
          id={`${id}-timing`}
          name={`${id}_timing`}
          label={`How should ${label} be scheduled?`}
          value={schedule.timing}
          has_error={false}
          onChange={handleTimingChange}
        >
          <option value={ExpensePaymentTiming.EVERY_PAYCHECK}>
            Every paycheck
          </option>
          <option value={ExpensePaymentTiming.PAYCHECK_POSITION}>
            On a particular paycheck each month
          </option>
          <option value={ExpensePaymentTiming.DAY_OF_MONTH}>
            On a specific day of the month
          </option>
        </Select>
        <div className="text-storm-dust-600 dark:text-storm-dust-300 flex items-center gap-2 text-sm">
          <span>Which paycheck should normally cover this payment?</span>
          <Tooltip
            id={`${id}-paycheck-tooltip`}
            label="First, Second, Third, and Fourth refer to actual cadence paychecks in each calendar month. Last means the final paycheck, including extra-paycheck months."
          >
            <button
              type="button"
              aria-label="More information about paycheck-position scheduling"
              aria-describedby={`${id}-paycheck-tooltip`}
              className="focus-visible:ring-blue-bell-500 inline-flex h-11 w-11 items-center justify-center rounded-full focus-visible:ring-2 focus-visible:outline-none"
            >
              <i aria-hidden="true" className="fa-solid fa-circle-info" />
            </button>
          </Tooltip>
        </div>
        {renderPaycheckPosition()}
        {renderLargePaymentHint()}
      </div>
      {renderDayInput()}
    </div>
  );
};

export default PaymentScheduleFields;
