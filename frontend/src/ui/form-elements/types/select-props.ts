import type { ChangeEventHandler, ReactNode } from 'react';

export default interface SelectProps {
  children: ReactNode;
  id: string;
  label: string;
  name: string;
  value: string;
  additional_css?: string;
  disabled?: boolean;
  error?: string;
  has_error: boolean;
  help_text?: string;
  onChange?: ChangeEventHandler<HTMLSelectElement>;
  required?: boolean;
}
