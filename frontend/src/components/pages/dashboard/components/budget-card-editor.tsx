import BudgetPayDateEditor from './budget-pay-date-editor';
import BudgetValueEditor from './budget-value-editor';
import BudgetCardEditorProps from './types/budget-card-editor-props';

import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';

import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';

const BudgetCardEditor = ({
  period,
  line_items,
  on_close,
  on_saved,
  on_pay_date_saved,
  close_button_ref,
}: BudgetCardEditorProps) => {
  const currentEntries = new Map(
    period.line_items.map((lineItem) => [lineItem.source_key, lineItem])
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold">Edit budget values</h3>
        <IconButton
          icon="fa-solid fa-xmark"
          label="Close budget editor"
          aria_label="Close budget editor"
          variant={ButtonVariant.GHOST}
          on_click={on_close}
          button_ref={close_button_ref}
        />
      </div>

      <BudgetPayDateEditor
        period={period}
        on_saved={on_pay_date_saved}
        on_close={on_close}
      />

      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.PAY_CHEQUE}
        label="Pay cheque"
        amount_cents={period.pay_cheque_cents}
        on_saved={on_saved}
      />
      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.CARRIED_LEFT_OVER}
        label="Previous period left over"
        amount_cents={period.carried_left_over_cents}
        on_saved={on_saved}
      />
      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.TOTAL_AVAILABLE}
        label="Your total"
        amount_cents={period.total_available_cents}
        on_saved={on_saved}
      />

      {line_items.map((lineItem) => {
        const currentEntry = currentEntries.get(lineItem.source_key);
        let amountCents = 0;

        if (currentEntry !== undefined) {
          amountCents = currentEntry.amount_cents;
        }

        return (
          <BudgetValueEditor
            key={lineItem.source_key}
            period_id={period.id}
            field={BudgetValueField.LINE_ITEM}
            source_key={lineItem.source_key}
            label={lineItem.title}
            amount_cents={amountCents}
            on_saved={on_saved}
          />
        );
      })}

      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.TOTAL_BILLS}
        label="Total bills"
        amount_cents={period.total_bills_cents}
        on_saved={on_saved}
      />
      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.LEFT_OVER}
        label="Left over"
        amount_cents={period.left_over_cents}
        on_saved={on_saved}
      />
    </div>
  );
};

export default BudgetCardEditor;
