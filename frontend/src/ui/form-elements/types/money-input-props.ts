export default interface MoneyInputProps {
  id: string;
  label: string;
  name: string;
  value: string;
  has_error: boolean;
  on_value_change: (value: string) => void;
  on_blur?: () => void;
  disabled?: boolean;
  error?: string;
  help_text?: string;
  placeholder?: string;
  required?: boolean;
}
