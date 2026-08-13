import PaydayDetailResponseDefinition from 'components/pages/payday/api/hooks/definitions/payday-detail-response-definition';

export default interface PaydayWizardProps {
  detail: PaydayDetailResponseDefinition;
  period_id: number;
  refresh_detail: () => Promise<PaydayDetailResponseDefinition | null>;
}
