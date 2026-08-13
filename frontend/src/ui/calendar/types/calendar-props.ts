import { Matcher } from 'react-day-picker';

export default interface CalendarProps {
  selected?: Date;
  default_month: Date;
  disabled?: Matcher | Matcher[];
  on_select: (date: Date | undefined) => void;
  required?: boolean;
}
