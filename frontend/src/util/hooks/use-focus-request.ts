import { useEffect, useState } from 'react';

import UseFocusRequestDefinition from './definitions/use-focus-request-definition';
import UseFocusRequestParams from './definitions/use-focus-request-params';

export const useFocusRequest = ({
  target_ref,
  scroll_into_view = false,
}: UseFocusRequestParams): UseFocusRequestDefinition => {
  const [focusRequest, setFocusRequest] = useState(0);

  useEffect(() => {
    if (focusRequest === 0 || target_ref.current === null) {
      return;
    }

    if (scroll_into_view) {
      target_ref.current.scrollIntoView({ behavior: 'auto', block: 'nearest' });
    }

    target_ref.current.focus({ preventScroll: true });
  }, [focusRequest, scroll_into_view, target_ref]);

  return { request_focus: () => setFocusRequest((value) => value + 1) };
};
