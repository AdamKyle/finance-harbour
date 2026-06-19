import clsx from 'clsx';
import { useMemo } from 'react';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';
import FormWizardNavProps from 'ui/form-wizard/types/form-wizard-nav-props';

const FormWizardNav = ({
  current_index,
  total_steps,
  can_go_previous,
  is_last_step,
  is_loading,
  on_previous_click,
  on_next_click,
  on_dot_click,
  render_loading_icon,
}: FormWizardNavProps) => {
  const dots = useMemo(
    () => Array.from({ length: total_steps }, (_, i) => i),
    [total_steps]
  );

  const getIconNode = () => {
    if (!is_loading || !render_loading_icon) {
      return undefined;
    }

    return render_loading_icon();
  };

  const getActionLabel = (): string => {
    if (is_last_step) {
      return 'Finish';
    }

    return 'Next';
  };

  const getActionVariant = (): ButtonVariant => {
    if (is_last_step) {
      return ButtonVariant.PRIMARY;
    }

    return ButtonVariant.SUCCESS;
  };

  const getDotAriaCurrent = (is_active: boolean): 'true' | undefined => {
    if (is_active) {
      return 'true';
    }

    return undefined;
  };

  const getDotClassName = (is_active: boolean): string => {
    const base =
      'h-3 w-3 rounded-full transition-colors duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-danube-500';

    if (is_active) {
      return clsx(base, 'bg-gray-500 dark:bg-gray-400');
    }

    return clsx(base, 'bg-gray-300 dark:bg-gray-600');
  };

  const renderPrevious = () => {
    return (
      <Button
        on_click={on_previous_click}
        label="Previous"
        variant={ButtonVariant.PRIMARY}
        disabled={!can_go_previous}
      />
    );
  };

  const renderNext = () => {
    return (
      <IconButton
        disabled={is_loading === true}
        on_click={on_next_click}
        label={getActionLabel()}
        variant={getActionVariant()}
        icon={getIconNode()}
        show_label
      />
    );
  };

  const renderDots = () => {
    if (!dots.length) {
      return null;
    }

    return (
      <div
        className="flex items-center justify-center gap-2"
        role="tablist"
        aria-label="Wizard steps"
      >
        {dots.map((index_value) => {
          const is_active = index_value === current_index;
          const is_disabled = !is_active && index_value >= current_index;

          const handleDotClick = () => {
            on_dot_click(index_value);
          };

          return (
            <button
              key={`dot-${index_value}`}
              type="button"
              aria-current={getDotAriaCurrent(is_active)}
              aria-disabled={is_disabled}
              disabled={is_disabled}
              onClick={handleDotClick}
              className={getDotClassName(is_active)}
            />
          );
        })}
      </div>
    );
  };

  return (
    <div className="flex items-center justify-between border-t border-gray-200 px-6 py-4 dark:border-gray-700">
      <div className="shrink-0">{renderPrevious()}</div>
      <div className="flex-1">{renderDots()}</div>
      <div className="shrink-0">{renderNext()}</div>
    </div>
  );
};

export default FormWizardNav;
