import clsx from 'clsx';

import { formatCentsAsDollars } from 'lib/money/money';

import ImportantExpensesStepProps from 'components/pages/onboarding/types/important-expenses-step-props';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';

const ImportantExpensesStep = ({
  request,
  setRequest,
  cards,
  loading,
  is_loading_more,
  can_load_more,
  on_load_more,
}: ImportantExpensesStepProps) => {
  const handleToggle = (expenseKey: string) => {
    if (request.selected_keys.includes(expenseKey)) {
      setRequest({
        selected_keys: request.selected_keys.filter(
          (selectedKey) => selectedKey !== expenseKey
        ),
      });

      return;
    }

    setRequest({
      selected_keys: [...request.selected_keys, expenseKey],
    });
  };

  const renderCards = () => {
    if (loading) {
      return <p role="status">Loading expenses...</p>;
    }

    if (cards.length === 0) {
      return <p>All saved monthly expenses are already handled.</p>;
    }

    return (
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {cards.map((card) => {
          const isSelected = request.selected_keys.includes(card.key);
          let selectedLabel = 'not selected';
          let visibleSelectedLabel = 'Not selected';

          if (isSelected) {
            selectedLabel = 'selected';
            visibleSelectedLabel = 'Selected';
          }

          return (
            <button
              key={card.key}
              type="button"
              aria-pressed={isSelected}
              aria-label={`${card.title}, $${formatCentsAsDollars(card.amount_cents)}, ${selectedLabel}`}
              onClick={() => {
                handleToggle(card.key);
              }}
              className={clsx(
                'flex min-h-32 flex-col items-center justify-center gap-2 rounded-lg border p-4 text-center',
                'focus-visible:ring-blue-bell-500 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none',
                {
                  'border-blue-bell-600 bg-blue-bell-50 dark:bg-blue-bell-950':
                    isSelected,
                  'border-storm-dust-300 dark:border-storm-dust-700 dark:bg-storm-dust-900 bg-white':
                    !isSelected,
                }
              )}
            >
              <h2 className="text-base font-semibold">{card.title}</h2>
              <span className="text-storm-dust-600 dark:text-storm-dust-300">
                ${formatCentsAsDollars(card.amount_cents)}
              </span>
              <span className="text-sm font-medium">
                {visibleSelectedLabel}
              </span>
            </button>
          );
        })}
      </div>
    );
  };

  const renderLoadMore = () => {
    if (!can_load_more) {
      return null;
    }

    let buttonLabel = 'Load more';

    if (is_loading_more) {
      buttonLabel = 'Loading...';
    }

    return (
      <Button
        label={buttonLabel}
        variant={ButtonVariant.PRIMARY}
        disabled={is_loading_more}
        on_click={on_load_more}
      />
    );
  };

  return (
    <div className="flex flex-col gap-6">
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Choose any remaining expenses that must be protected. Bills already
        marked Important because they are required or automatically deducted are
        handled for you.
      </p>

      <div>{renderCards()}</div>

      {renderLoadMore()}
    </div>
  );
};

export default ImportantExpensesStep;
