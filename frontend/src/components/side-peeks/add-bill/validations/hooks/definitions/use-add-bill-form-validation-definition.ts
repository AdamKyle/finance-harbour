import AddBillFormRequestDefinition from 'components/side-peeks/add-bill/api/hooks/definitions/add-bill-form-request-definition';
import AddBillValidationResultDefinition from 'components/side-peeks/add-bill/validations/hooks/definitions/add-bill-validation-result-definition';

export default interface UseAddBillFormValidationDefinition {
  validateStep: (
    step: number,
    request: AddBillFormRequestDefinition
  ) => AddBillValidationResultDefinition;
  validateAll: (
    request: AddBillFormRequestDefinition
  ) => AddBillValidationResultDefinition;
}
