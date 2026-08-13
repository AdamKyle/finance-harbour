import { useReducedMotion } from 'motion/react';
import { DayPicker } from 'react-day-picker';

import CalendarProps from './types/calendar-props';

const Calendar = ({
  selected,
  default_month,
  disabled,
  on_select,
  required = false,
}: CalendarProps) => {
  const shouldReduceMotion = useReducedMotion();
  const shouldAnimate = shouldReduceMotion !== true;

  return (
    <DayPicker
      animate={shouldAnimate}
      mode="single"
      selected={selected}
      defaultMonth={default_month}
      disabled={disabled}
      onSelect={on_select}
      required={required}
      classNames={{
        root: 'text-storm-dust-900 dark:text-storm-dust-50',
        months: 'flex flex-col',
        month_caption: 'mb-3 flex items-center justify-center font-semibold',
        nav: 'absolute inset-x-3 top-3 flex justify-between',
        button_previous:
          'rounded-md px-3 py-2 hover:bg-storm-dust-100 focus-visible:ring-2 focus-visible:ring-blue-bell-500 focus-visible:outline-none dark:hover:bg-storm-dust-800',
        button_next:
          'rounded-md px-3 py-2 hover:bg-storm-dust-100 focus-visible:ring-2 focus-visible:ring-blue-bell-500 focus-visible:outline-none dark:hover:bg-storm-dust-800',
        month_grid: 'w-full border-collapse',
        weekdays: 'text-storm-dust-500 dark:text-storm-dust-400',
        weekday: 'p-1 text-center text-xs font-medium',
        week: 'mt-1',
        day: 'p-0 text-center',
        day_button:
          'mx-auto flex h-10 w-10 items-center justify-center rounded-full hover:bg-storm-dust-100 focus-visible:ring-2 focus-visible:ring-blue-bell-500 focus-visible:outline-none dark:hover:bg-storm-dust-800',
        selected:
          '[&>button]:bg-blue-bell-600 [&>button]:text-white [&>button]:hover:bg-blue-bell-700 dark:[&>button]:bg-blue-bell-500',
        today:
          '[&>button]:font-bold [&>button]:ring-1 [&>button]:ring-blue-bell-500',
        outside: 'opacity-40',
        disabled: 'pointer-events-none opacity-30',
      }}
    />
  );
};

export default Calendar;
