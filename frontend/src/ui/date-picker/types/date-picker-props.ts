import { DatePickerTriggerVariant } from 'ui/date-picker/enums/date-picker-trigger-variant';

export default interface DatePickerProps {
  id: string;
  label: string;
  selected?: Date;
  representative_month: Date;
  minimum_date?: Date;
  on_change: (date: Date | undefined) => void;
  error?: string;
  help_text?: string;
  trigger_variant?: DatePickerTriggerVariant;
}
