import AddBillFormRequestDefinition from './add-bill-form-request-definition';
import RecurringObligationConfigurationDefinition from './recurring-obligation-configuration-definition';
import RecurringObligationResponseDefinition from './recurring-obligation-response-definition';

export default interface UseRecurringObligationDefinition {
  requestData: AddBillFormRequestDefinition;
  setRequestData: (request: AddBillFormRequestDefinition) => void;
  configuration: RecurringObligationConfigurationDefinition | null;
  loading: boolean;
  error: string | null;
  save: () => Promise<RecurringObligationResponseDefinition | null>;
}
