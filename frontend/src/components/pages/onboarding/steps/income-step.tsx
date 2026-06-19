import React, { ChangeEvent } from 'react';

import IncomeStepProps from 'components/pages/onboarding/types/income-step-props';
import { PayPeriodType } from 'components/pages/onboarding/types/pay-period-type';

import Input from 'ui/form-elements/input';
import Select from 'ui/form-elements/select';

const IncomeStep = ({
  request,
  setRequest,
  fieldErrors = {},
}: IncomeStepProps) => {
  const isPayPeriodType = (value: string): value is PayPeriodType => {
    if (value === PayPeriodType.WEEKLY) {
      return true;
    }

    if (value === PayPeriodType.BIWEEKLY) {
      return true;
    }

    return value === PayPeriodType.MONTHLY;
  };

  const handleIncomeChange = (event: ChangeEvent<HTMLInputElement>) => {
    setRequest({
      ...request,
      income_per_pay_period_dollars: event.target.value,
    });
  };

  const handlePayPeriodChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const payPeriodType = event.target.value;

    if (payPeriodType === '') {
      setRequest({
        ...request,
        pay_period_type: '',
      });

      return;
    }

    if (!isPayPeriodType(payPeriodType)) {
      return;
    }

    setRequest({
      ...request,
      pay_period_type: payPeriodType,
    });
  };

  return (
    <div className="flex flex-col gap-6">
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Enter your take-home income per pay period in dollars. Both fields are
        required.
      </p>

      <Input
        id="income-amount"
        label="Income per pay period ($)"
        name="income_per_pay_period_dollars"
        type="text"
        placeholder="0.00"
        value={request.income_per_pay_period_dollars}
        error={fieldErrors.income_per_pay_period_dollars}
        has_error={fieldErrors.income_per_pay_period_dollars !== undefined}
        onChange={handleIncomeChange}
      />

      <Select
        id="pay-period-type"
        label="Pay period"
        name="pay_period_type"
        value={request.pay_period_type}
        error={fieldErrors.pay_period_type}
        has_error={fieldErrors.pay_period_type !== undefined}
        onChange={handlePayPeriodChange}
      >
        <option value="">Select a pay period</option>
        <option value={PayPeriodType.WEEKLY}>Weekly</option>
        <option value={PayPeriodType.BIWEEKLY}>Bi-weekly</option>
        <option value={PayPeriodType.MONTHLY}>Monthly</option>
      </Select>
    </div>
  );
};

export default IncomeStep;
