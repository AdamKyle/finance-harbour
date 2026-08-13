import { AxiosError } from 'axios';
import { useCallback, useEffect, useRef, useState } from 'react';

import AddBillFormRequestDefinition from './definitions/add-bill-form-request-definition';
import RecurringObligationApiRequestDefinition from './definitions/recurring-obligation-api-request-definition';
import RecurringObligationConfigurationDefinition from './definitions/recurring-obligation-configuration-definition';
import RecurringObligationResponseDefinition from './definitions/recurring-obligation-response-definition';
import UseRecurringObligationDefinition from './definitions/use-recurring-obligation-definition';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { dollarsToCents } from 'lib/money/money';

import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/payment-schedule/enums/paycheck-position';
import { AddBillApiUrls } from 'components/side-peeks/add-bill/api/enums/add-bill-api-urls';
import { RecurringObligationKind } from 'components/side-peeks/add-bill/types/recurring-obligation-kind';

import { useMountedRef } from 'util/hooks/use-mounted-ref';

export const useRecurringObligation = (): UseRecurringObligationDefinition => {
  const { apiHandler, getUrl } = useApiHandler();
  const isMountedRef = useMountedRef();
  const [configuration, setConfiguration] =
    useState<RecurringObligationConfigurationDefinition | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requestData, setStoredRequestData] =
    useState<AddBillFormRequestDefinition>({
      kind: '',
      label: '',
      amount_dollars: '',
      current_balance_dollars: '',
      minimum_payment_dollars: '',
      current_payment_dollars: '',
      is_required: false,
      payment_schedule: {
        timing: ExpensePaymentTiming.PAYCHECK_POSITION,
        paycheck_position: PaycheckPosition.FIRST,
        day_of_month: '',
        auto_deducted: false,
      },
    });
  const requestRef = useRef(requestData);
  const url = getUrl(AddBillApiUrls.RECURRING_OBLIGATIONS);

  const setRequestData = (request: AddBillFormRequestDefinition) => {
    requestRef.current = request;
    setStoredRequestData(request);
  };

  useEffect(() => {
    setLoading(true);
    setError(null);

    apiHandler
      .get<RecurringObligationConfigurationDefinition, Record<string, never>>(
        url
      )
      .then((response) => {
        if (isMountedRef.current) {
          setConfiguration(response);
        }
      })
      .catch(() => {
        if (isMountedRef.current) {
          setError('Payment scheduling could not be loaded.');
        }
      })
      .finally(() => {
        if (isMountedRef.current) {
          setLoading(false);
        }
      });
  }, [apiHandler, isMountedRef, url]);

  const save = useCallback(async () => {
    const request = requestRef.current;

    if (request.kind === '') {
      return null;
    }

    let paycheckPosition: PaycheckPosition | null =
      request.payment_schedule.paycheck_position;
    let dayOfMonth: number | null = null;

    if (
      request.payment_schedule.timing === ExpensePaymentTiming.EVERY_PAYCHECK
    ) {
      paycheckPosition = null;
    }

    if (request.payment_schedule.timing === ExpensePaymentTiming.DAY_OF_MONTH) {
      dayOfMonth = Number.parseInt(request.payment_schedule.day_of_month, 10);
    }

    const apiRequest: RecurringObligationApiRequestDefinition = {
      kind: request.kind,
      label: request.label.trim(),
      is_required: request.is_required,
      payment_schedule: {
        timing: request.payment_schedule.timing,
        paycheck_position: paycheckPosition,
        day_of_month: dayOfMonth,
        auto_deducted: request.payment_schedule.auto_deducted === true,
      },
    };

    if (request.kind === RecurringObligationKind.BILL) {
      apiRequest.amount_cents = dollarsToCents(request.amount_dollars);
    } else {
      apiRequest.current_balance_cents = dollarsToCents(
        request.current_balance_dollars
      );
      apiRequest.minimum_payment_cents = dollarsToCents(
        request.minimum_payment_dollars
      );
      apiRequest.current_payment_cents = dollarsToCents(
        request.current_payment_dollars
      );
    }

    setLoading(true);
    setError(null);

    try {
      return await apiHandler.post<
        RecurringObligationResponseDefinition,
        Record<string, never>,
        RecurringObligationApiRequestDefinition
      >(url, apiRequest);
    } catch (requestError) {
      if (isMountedRef.current) {
        let message =
          'The recurring payment could not be saved. Please try again.';

        if (requestError instanceof AxiosError) {
          message = 'The recurring payment could not be saved.';
        }

        setError(message);
      }

      return null;
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [apiHandler, isMountedRef, url]);

  return { requestData, setRequestData, configuration, loading, error, save };
};
