import clsx from 'clsx';

import { baseStyles } from './styles/button/base-styles';
import { variantStyles } from './styles/button/variant-styles';
import type ButtonProps from './types/button-props';

const Button = ({
  on_click,
  label,
  variant,
  disabled,
  additional_css,
  aria_label,
  aria_pressed,
  aria_controls,
  aria_expanded,
  aria_describedby,
  type = 'button',
  button_ref,
}: ButtonProps) => {
  const getAriaLabel = () => {
    if (aria_label === undefined) {
      return label;
    }

    return aria_label;
  };

  return (
    <button
      aria-label={getAriaLabel()}
      aria-pressed={aria_pressed}
      aria-controls={aria_controls}
      aria-expanded={aria_expanded}
      aria-describedby={aria_describedby}
      className={clsx(baseStyles(), variantStyles(variant), additional_css)}
      disabled={disabled}
      onClick={on_click}
      type={type}
      ref={button_ref}
    >
      {label}
    </button>
  );
};

export default Button;
