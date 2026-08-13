def calculate_affects_important_expenses(
    has_negative_left_over: bool,
    has_important_on_card: bool,
    has_deferred_important: bool,
) -> bool:
    return (has_negative_left_over and has_important_on_card) or has_deferred_important
