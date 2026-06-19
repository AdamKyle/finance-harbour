import { ChangeEventHandler } from 'react';

export default interface InputProps {
  id: string;
  label: string;
  name: string;
  type: 'email' | 'password' | 'text';
  additional_css?: string;
  autoComplete?: string;
  disabled?: boolean;
  error?: string;
  has_error: boolean;
  help_text?: string;
  inputMode?: 'decimal' | 'email' | 'numeric' | 'text';
  onChange?: ChangeEventHandler<HTMLInputElement>;
  placeholder?: string;
  required?: boolean;
  value?: string;
}
