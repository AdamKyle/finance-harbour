import { MouseEventHandler, ReactNode, Ref } from 'react';

import type { ButtonVariant } from 'ui/buttons/enums/button-variant';

export default interface IconButtonProps {
  on_click: MouseEventHandler<HTMLButtonElement>;
  icon: ReactNode | string;
  label: string;
  variant: ButtonVariant;
  disabled?: boolean;
  additional_css?: string;
  aria_label?: string;
  aria_controls?: string;
  aria_expanded?: boolean;
  aria_current?: 'page';
  show_label?: boolean;
  button_ref?: Ref<HTMLButtonElement>;
}
