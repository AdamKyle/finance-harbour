import type { ButtonHTMLAttributes, MouseEventHandler, RefObject } from 'react';

import type { ButtonVariant } from 'ui/buttons/enums/button-variant';

export default interface ButtonProps {
  label: string;
  variant: ButtonVariant;
  disabled?: boolean;
  additional_css?: string;
  aria_label?: string;
  aria_pressed?: boolean;
  aria_controls?: string;
  aria_expanded?: boolean;
  aria_describedby?: string;
  on_click?: MouseEventHandler<HTMLButtonElement>;
  type?: ButtonHTMLAttributes<HTMLButtonElement>['type'];
  button_ref?: RefObject<HTMLButtonElement | null>;
}
