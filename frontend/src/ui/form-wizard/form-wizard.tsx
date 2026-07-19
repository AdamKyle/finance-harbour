import { motion } from 'framer-motion';
import React, { useMemo, useRef, useState } from 'react';

import { useScrollToTop } from '../../util/hooks/use-scroll-to-top';

import ApiErrorAlert from 'lib/api-handler/components/api-error-alert';

import Card from 'ui/cards/card';
import FormWizardNav from 'ui/form-wizard/form-wizard-nav';
import FormWizardProps from 'ui/form-wizard/types/form-wizard-props';
import StepProps from 'ui/form-wizard/types/step-props';

const FormWizard = ({
  total_steps,
  initial_index = 0,
  name,
  is_loading,
  render_loading_icon,
  on_request_next,
  on_request_step_change,
  children,
  form_error,
  available_step_indexes,
}: FormWizardProps) => {
  const [current_index, set_current_index] = useState(initial_index);
  const step_refs = useRef<Array<HTMLDivElement | null>>([]);

  const step_elements = useMemo(
    () => React.Children.toArray(children).filter(React.isValidElement),
    [children]
  );

  const computed_total_steps = useMemo(
    () => step_elements.length || total_steps,
    [step_elements, total_steps]
  );

  const dot_labels = useMemo(
    () =>
      step_elements.map((element) => {
        const props = element.props as StepProps;
        return props.step_title ?? '';
      }),
    [step_elements]
  );

  const { scrollToTop } = useScrollToTop();

  const handlePreviousAsync = async () => {
    if (current_index === 0) {
      return;
    }

    if (is_loading) {
      return;
    }

    if (on_request_step_change) {
      const allowed = await on_request_step_change(
        current_index,
        current_index - 1
      );

      if (!allowed) {
        return;
      }
    }

    set_current_index((value) => value - 1);

    scrollToTop();
  };

  const handlePreviousClick = () => {
    handlePreviousAsync().catch(() => {});
  };

  const handleNextClick = async () => {
    if (is_loading) {
      return;
    }

    if (on_request_next) {
      const allowed = await on_request_next(current_index);

      if (!allowed) {
        return;
      }
    }

    if (current_index >= computed_total_steps - 1) {
      return;
    }

    set_current_index((value) => value + 1);

    scrollToTop();
  };

  const handleNextButtonClick = () => {
    handleNextClick().catch(() => {});
  };

  const handleDotClickAsync = async (target_index: number) => {
    if (is_loading) {
      return;
    }

    if (target_index === current_index) {
      return;
    }

    if (!available_step_indexes.includes(target_index)) {
      return;
    }

    if (on_request_step_change) {
      const allowed = await on_request_step_change(current_index, target_index);

      if (!allowed) {
        return;
      }
    }

    set_current_index(target_index);

    scrollToTop();
  };

  const handleDotClick = (target_index: number) => {
    handleDotClickAsync(target_index).catch(() => {});
  };

  const getStepXPosition = (is_active: boolean, index: number): number => {
    if (is_active) {
      return 0;
    }

    if (index < current_index) {
      return -32;
    }

    return 32;
  };

  const getStepOpacity = (is_active: boolean): number => {
    if (is_active) {
      return 1;
    }

    return 0;
  };

  const getStepClassName = (is_active: boolean): string => {
    if (is_active) {
      return 'relative';
    }

    return 'absolute inset-0';
  };

  const getStepPointerEvents = (is_active: boolean): 'auto' | 'none' => {
    if (is_active) {
      return 'auto';
    }

    return 'none';
  };

  const renderHeader = () => {
    if (!name) {
      return null;
    }

    return (
      <div className="flex items-center justify-between border-b border-gray-200 pb-4 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
          {name}
        </h2>
      </div>
    );
  };

  const renderTrack = () => {
    return (
      <div className="relative overflow-hidden">
        {step_elements.map((element, index) => {
          const is_active = index === current_index;

          return (
            <motion.div
              key={element.key ?? `step-${index}`}
              ref={(el) => {
                step_refs.current[index] = el;
              }}
              initial={false}
              animate={{
                x: getStepXPosition(is_active, index),
                opacity: getStepOpacity(is_active),
              }}
              transition={{ duration: 0.25 }}
              className={getStepClassName(is_active)}
              style={{ pointerEvents: getStepPointerEvents(is_active) }}
              aria-hidden={!is_active}
              inert={!is_active}
            >
              {element}
            </motion.div>
          );
        })}
      </div>
    );
  };

  const renderFormError = () => {
    if (!form_error) {
      return null;
    }

    return <ApiErrorAlert apiError={form_error.message} />;
  };

  const renderFooter = () => {
    return (
      <>
        {renderFormError()}
        <FormWizardNav
          current_index={current_index}
          total_steps={computed_total_steps}
          can_go_previous={current_index > 0}
          is_last_step={current_index === computed_total_steps - 1}
          is_loading={is_loading}
          on_previous_click={handlePreviousClick}
          on_next_click={handleNextButtonClick}
          on_dot_click={handleDotClick}
          render_loading_icon={render_loading_icon}
          available_step_indexes={available_step_indexes}
          dot_labels={dot_labels}
        />
      </>
    );
  };

  return (
    <div className="mx-auto my-4 w-full px-4 sm:px-6 lg:px-8">
      <div className="mx-auto w-full max-w-5xl">
        <Card>
          <div className="space-y-4">
            {renderHeader()}
            {renderTrack()}
            {renderFooter()}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default FormWizard;
