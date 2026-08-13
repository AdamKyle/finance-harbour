import clsx from 'clsx';
import { useId, useMemo } from 'react';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';
import FormWizardNavProps from 'ui/form-wizard/types/form-wizard-nav-props';
import ToolTip from 'ui/tool-tip/tool-tip';

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
  available_step_indexes,
  dot_labels,
}: FormWizardNavProps) => {
  const base_id = useId();

  const dots = useMemo(
    () => Array.from({ length: total_steps }, (_, i) => i),
    [total_steps]
  );

  const getTooltipId = (index: number) => `${base_id}-tooltip-${index}`;

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

  const getDotVisualClassName = (
    is_active: boolean,
    is_available: boolean
  ): string => {
    const base = 'h-3 w-3 rounded-full transition-colors duration-300';

    if (is_active) {
      return clsx(
        base,
        'bg-storm-dust-600 dark:bg-storm-dust-300',
        'ring-2 ring-storm-dust-600 ring-offset-1 ring-offset-white dark:ring-storm-dust-300 dark:ring-offset-storm-dust-800'
      );
    }

    if (is_available) {
      return clsx(
        base,
        'bg-storm-dust-400 dark:bg-storm-dust-500',
        'group-hover/dot:bg-storm-dust-500 dark:group-hover/dot:bg-storm-dust-400'
      );
    }

    return clsx(base, 'bg-storm-dust-200 dark:bg-storm-dust-700 opacity-50');
  };

  const renderPrevious = () => {
    return (
      <Button
        on_click={on_previous_click}
        label="Previous"
        variant={ButtonVariant.PRIMARY}
        disabled={!can_go_previous || is_loading === true}
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
      <ol className="flex items-center gap-1">
        {dots.map((index_value) => {
          const is_active = index_value === current_index;
          const is_available = available_step_indexes.includes(index_value);
          const is_disabled = !is_available || is_loading === true;
          const label = dot_labels[index_value] ?? '';
          const tooltip_id = getTooltipId(index_value);

          const getAriaCurrent = (): 'step' | undefined => {
            if (!is_active) {
              return undefined;
            }

            return 'step';
          };

          const getDotButtonClassName = () => {
            if (is_disabled) {
              return clsx(
                'group/dot flex min-h-8 min-w-8 cursor-not-allowed items-center justify-center rounded-full',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
                'focus-visible:ring-blue-bell-500'
              );
            }

            return clsx(
              'group/dot flex min-h-8 min-w-8 cursor-pointer items-center justify-center rounded-full',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
              'focus-visible:ring-blue-bell-500'
            );
          };

          const handleDotClick = () => {
            on_dot_click(index_value);
          };

          return (
            <li key={`dot-${index_value}`}>
              <ToolTip id={tooltip_id} label={label}>
                <button
                  type="button"
                  aria-label={`${label}, step ${index_value + 1} of ${total_steps}`}
                  aria-describedby={tooltip_id}
                  aria-current={getAriaCurrent()}
                  disabled={is_disabled}
                  onClick={handleDotClick}
                  className={getDotButtonClassName()}
                >
                  <span
                    className={getDotVisualClassName(is_active, is_available)}
                  />
                </button>
              </ToolTip>
            </li>
          );
        })}
      </ol>
    );
  };

  return (
    <div className="border-t border-gray-200 px-6 py-4 dark:border-gray-700">
      <div className="grid grid-cols-2 gap-y-3 sm:flex sm:items-center">
        <nav
          aria-label="Wizard steps"
          className="col-span-2 flex justify-center sm:order-2 sm:flex-1"
        >
          {renderDots()}
        </nav>
        <div className="col-start-1 row-start-2 flex justify-start sm:order-1 sm:shrink-0">
          {renderPrevious()}
        </div>
        <div className="col-start-2 row-start-2 flex justify-end sm:order-3 sm:shrink-0">
          {renderNext()}
        </div>
      </div>
    </div>
  );
};

export default FormWizardNav;
