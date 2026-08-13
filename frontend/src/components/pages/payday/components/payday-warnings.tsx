import PaydayWarningsProps from './types/payday-warnings-props';

import { PaydayWarningSeverity } from 'components/pages/payday/enums/payday-warning';
import { formatPaydayWarning } from 'components/pages/payday/utils/format-payday-warning';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';

const PaydayWarnings = ({ warnings }: PaydayWarningsProps) => {
  const getAlertVariant = (severity: PaydayWarningSeverity): AlertVariant => {
    if (severity === PaydayWarningSeverity.DANGER) {
      return AlertVariant.DANGER;
    }

    return AlertVariant.WARNING;
  };

  const renderWarnings = () => {
    if (warnings.length === 0) {
      return null;
    }

    return (
      <div className="space-y-3" aria-live="polite">
        {warnings.map((warning) => (
          <Alert
            key={`${warning.warning_type}-${warning.affected_period_id}`}
            variant={getAlertVariant(warning.severity)}
          >
            {formatPaydayWarning(warning)}
          </Alert>
        ))}
      </div>
    );
  };

  return renderWarnings();
};

export default PaydayWarnings;
