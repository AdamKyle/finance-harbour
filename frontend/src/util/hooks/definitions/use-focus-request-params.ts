import { RefObject } from 'react';

export default interface UseFocusRequestParams {
  target_ref: RefObject<HTMLElement | null>;
  scroll_into_view?: boolean;
}
