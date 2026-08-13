import ExpensePaymentScheduleDefinition from './expense-payment-schedule-definition';
import RecurringExpenseDefinition from './recurring-expense-definition';

export default interface MonthlyExpenseResponseDefinition {
  recurring_expenses: RecurringExpenseDefinition[];
  payment_schedules: ExpensePaymentScheduleDefinition[];
}
