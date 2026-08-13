import PaydayDetailResponseDefinition from 'components/pages/payday/api/hooks/definitions/payday-detail-response-definition';
import PaydayWarningDefinition from 'components/pages/payday/api/hooks/definitions/payday-warning-definition';

export default interface PaydaySummaryStepProps {
  detail: PaydayDetailResponseDefinition;
  warnings: PaydayWarningDefinition[];
}
