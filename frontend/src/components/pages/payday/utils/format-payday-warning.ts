import { formatCentsAsCurrency } from 'lib/money/money';

import PaydayWarningDefinition from 'components/pages/payday/api/hooks/definitions/payday-warning-definition';
import { PaydayWarningType } from 'components/pages/payday/enums/payday-warning';

/**
 * Formats a structured Payday warning without adding unsupported financial facts.
 *
 * @param warning - Backend-provided consequence and its factual fields.
 * @returns Accessible user-facing warning text.
 * @throws This function does not throw.
 */
export const formatPaydayWarning = (
  warning: PaydayWarningDefinition
): string => {
  const affectedDate = new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${warning.affected_pay_date}T00:00:00Z`));

  if (warning.warning_type === PaydayWarningType.NEGATIVE_LEFT_OVER) {
    if (warning.amount_cents === null) {
      return `Left over will be negative on ${affectedDate}.`;
    }

    return `Left over will be ${formatCentsAsCurrency(warning.amount_cents)} on ${affectedDate}.`;
  }

  if (
    warning.warning_type ===
    PaydayWarningType.IMPORTANT_PAYMENT_MISSED_OR_UNDERPAID
  ) {
    if (warning.important_titles.length === 0) {
      return `An Important expense is affected on ${affectedDate}.`;
    }

    return `${warning.important_titles.join(', ')} is affected on ${affectedDate}.`;
  }

  if (warning.warning_type === PaydayWarningType.IMPORTANT_EXPENSE_AFFECTED) {
    return `An Important expense is affected on ${affectedDate}.`;
  }

  if (warning.amount_cents === null) {
    return `The warning threshold is crossed on ${affectedDate}.`;
  }

  return `Left over will be ${formatCentsAsCurrency(warning.amount_cents)} on ${affectedDate}.`;
};
