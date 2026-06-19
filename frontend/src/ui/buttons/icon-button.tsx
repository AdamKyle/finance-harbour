import clsx from 'clsx';
import React from 'react';

import {
  iconButtonBaseStyles,
  iconButtonIconBaseStyles,
} from './styles/icon-button/base-styles';
import { iconButtonVariantStyles } from './styles/icon-button/variant-styles';
import type IconButtonProps from './types/icon-button-props';

const IconButton = ({
  on_click,
  icon,
  label,
  variant,
  disabled,
  additional_css,
  aria_label,
  aria_controls,
  aria_expanded,
  show_label = false,
}: IconButtonProps) => {
  const variantClasses = iconButtonVariantStyles(variant);

  const renderIcon = () => {
    if (typeof icon === 'string') {
      return <i className={icon} aria-hidden="true" />;
    }

    return icon;
  };

  return (
    <button
      type="button"
      onClick={on_click}
      className={clsx(
        iconButtonBaseStyles(show_label),
        variantClasses.button,
        additional_css
      )}
      aria-label={aria_label || (!show_label ? label : undefined)}
      aria-controls={aria_controls}
      aria-expanded={aria_expanded}
      disabled={disabled}
    >
      <span className={clsx(iconButtonIconBaseStyles(), variantClasses.icon)}>
        {renderIcon()}
      </span>

      {show_label && <span>{label}</span>}
    </button>
  );
};

export default IconButton;
