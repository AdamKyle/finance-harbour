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
  aria_current,
  show_label = false,
  button_ref,
}: IconButtonProps) => {
  const variantClasses = iconButtonVariantStyles(variant);

  const getAccessibleLabel = () => {
    if (aria_label !== undefined) {
      return aria_label;
    }

    if (show_label) {
      return undefined;
    }

    return label;
  };

  const accessibleLabel = getAccessibleLabel();

  const renderIcon = () => {
    if (typeof icon !== 'string') {
      return icon;
    }

    return <i className={icon} aria-hidden="true" />;
  };

  const renderLabel = () => {
    if (!show_label) {
      return null;
    }

    return <span>{label}</span>;
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
      aria-label={accessibleLabel}
      aria-controls={aria_controls}
      aria-expanded={aria_expanded}
      aria-current={aria_current}
      disabled={disabled}
      ref={button_ref}
    >
      <span className={clsx(iconButtonIconBaseStyles(), variantClasses.icon)}>
        {renderIcon()}
      </span>

      {renderLabel()}
    </button>
  );
};

export default IconButton;
