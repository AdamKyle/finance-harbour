import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';

export default interface BudgetValueEditorProps {
  period_id: number;
  field: BudgetValueField;
  source_key?: string;
  label: string;
  amount_cents: number;
  on_saved: () => void;
}
