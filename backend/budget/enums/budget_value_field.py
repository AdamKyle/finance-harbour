from enum import StrEnum


class BudgetValueField(StrEnum):
    PAY_DATE = "pay_date"
    PAY_CHEQUE = "pay_cheque_cents"
    CARRIED_LEFT_OVER = "carried_left_over_cents"
    TOTAL_AVAILABLE = "total_available_cents"
    TOTAL_BILLS = "total_bills_cents"
    LEFT_OVER = "left_over_cents"
    LINE_ITEM = "line_item"
