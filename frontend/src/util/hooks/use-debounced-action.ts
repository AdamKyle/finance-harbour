import { useCallback, useEffect, useRef } from 'react';

import UseDebouncedActionDefinition from './definitions/use-debounced-action-definition';
import UseDebouncedActionParams from './definitions/use-debounced-action-params';

export const useDebouncedAction = ({
  action,
  delay_ms,
}: UseDebouncedActionParams): UseDebouncedActionDefinition => {
  const actionRef = useRef(action);
  const timerRef = useRef<ReturnType<typeof globalThis.setTimeout> | null>(
    null
  );
  actionRef.current = action;

  const flush = useCallback(() => {
    if (timerRef.current === null) {
      return;
    }

    globalThis.clearTimeout(timerRef.current);
    timerRef.current = null;
    void actionRef.current();
  }, []);

  const schedule = useCallback(() => {
    if (timerRef.current !== null) {
      globalThis.clearTimeout(timerRef.current);
    }

    timerRef.current = globalThis.setTimeout(() => {
      timerRef.current = null;
      void actionRef.current();
    }, delay_ms);
  }, [delay_ms]);

  useEffect(() => {
    return flush;
  }, [flush]);

  return { flush, schedule };
};
