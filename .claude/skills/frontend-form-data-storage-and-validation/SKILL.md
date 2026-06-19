---
name: frontend-form-data-storage-and-validation
description: Use when editing front end forms, form components, onboarding steps, API hooks, or validation flow to define how form data is stored, retrieved, validated, and submitted.
---

# Frontend Form Data Storage and Validation

Use this skill when editing any frontend form, onboarding step, form API hook, validation hook, or component that collects data for a backend request.

## Core rule

Form data must be stored as the request object that will eventually be submitted to the backend.

Do not create separate local component state shapes, empty object factories, duplicated form objects, or temporary structures that drift away from the API request payload.

The API hook owns the request object.

The component updates that request object.

The validation layer validates that request object.

The API hook submits that request object.

## Props interfaces

Component props interfaces must not be defined inside the component file.

For a component named DebtStep, the props interface must be named DebtStepProps.

The props interface must live in a dedicated type file:

types/debt-step-props.ts

The component should import the props interface from that file.

Use an interface for component props.

Do not define ComponentNameProps directly inside the component file.

## No functions outside the component

Never define functions outside the component body.

Do not define standalone helper functions above the component.

This includes:

- empty form object builders
- default row builders
- field mappers
- component-only submit handlers
- component-only validation helpers
- component-only formatter helpers
- component-only event handlers

Do not do this:

const emptyDebt = (): DebtEntryFormState => ({
label: '',
current_balance_dollars: '',
interest_rate_percent: '',
minimum_payment_dollars: '',
current_payment_dollars: '',
});

If the logic only belongs to the component, keep it inside the component.

If the logic is shared across multiple places, move it to the correct dedicated file, such as a utility, validation, type, or hook file.

## Form data storage

Form data must be stored in the API hook request object.

The API hook should expose a way to set the request object and retrieve the current request object.

Expected shape:

const {
formRequest,
setFormRequest,
submitFormRequest,
} = useOnboardingFormApi();

Components must update form data through setFormRequest.

Do not create duplicate local state just to mirror the backend request payload.

Do not keep form data in component-only state if that data belongs to the request being submitted.

## Dynamic form rows

Dynamic rows must be appended directly to the request object through setFormRequest.

Do not create external empty-row factory functions.

Correct pattern:

const handleAddDebt = () => {
setFormRequest({
...formRequest,
debts: [
...formRequest.debts,
{
label: '',
current_balance_dollars: '',
interest_rate_percent: '',
minimum_payment_dollars: '',
current_payment_dollars: '',
},
],
});
};

The row object should match the backend request shape.

## Field updates

Field changes must update the API hook request object.

Correct pattern:

const handleDebtChange = (
index: number,
field: keyof DebtEntryFormState,
value: string
) => {
setFormRequest({
...formRequest,
debts: formRequest.debts.map((debt, debtIndex) =>
debtIndex === index ? { ...debt, [field]: value } : debt
),
});
};

The component should not maintain a second copy of this form data.

## Validation responsibility

Validation must not happen inside the form API hook.

The API hook is responsible for:

- storing request data
- exposing request data
- updating request data
- submitting the request
- exposing loading state
- exposing API errors
- exposing response data

The API hook is not responsible for:

- frontend validation rules
- field validation
- step validation
- deciding whether the user can proceed
- deciding whether the request is ready to submit

Validation must happen when the user clicks the action that moves the form forward, such as Next, Continue, Save, or Submit.

## Submit flow

The correct flow is:

1. Get the current request data from the API hook.
2. Run frontend validation against that request data.
3. If validation fails, set frontend validation errors and bail.
4. If validation passes, call the API hook submit method.

Example:

const handleNext = async () => {
const validationResult = validateDebtStep(formRequest.debts);

if (!validationResult.valid) {
setFieldErrors(validationResult.fieldErrors);
setStepError(validationResult.stepError);
return;
}

await submitFormRequest(formRequest);
};

Never submit before frontend validation passes.

## Error handling

Frontend validation errors must be separate from API/server errors.

Frontend validation state is for:

- field errors
- step errors
- required field messages
- invalid dollar amounts
- invalid percentages
- missing dynamic rows

API hook error state is for:

- failed requests
- backend validation responses
- network failures
- server failures

Do not mix frontend validation errors with API hook errors.

## Component rules

A form component may:

- render fields
- render frontend validation errors
- update the API hook request object
- retrieve request data from the API hook
- run validation on Next, Continue, Save, or Submit
- call the API hook submit method after validation passes

A form component must not:

- define ComponentNameProps inline
- define functions outside the component body
- keep duplicate form request state
- define empty form object factory functions
- validate inside the API hook
- submit before frontend validation passes
- store request-shaped form data outside the API hook
