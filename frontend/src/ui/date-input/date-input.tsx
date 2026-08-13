import DateInputProps from './types/date-input-props';

import DatePicker from 'ui/date-picker/date-picker';
import { DatePickerTriggerVariant } from 'ui/date-picker/enums/date-picker-trigger-variant';

const DateInput = (props: DateInputProps) => {
  return (
    <DatePicker {...props} trigger_variant={DatePickerTriggerVariant.INPUT} />
  );
};

export default DateInput;
