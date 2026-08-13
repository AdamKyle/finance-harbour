from dataclasses import dataclass


@dataclass(frozen=True)
class RecurringObligationResult:
    kind: str
    source_key: str
    first_effective_budget_period_id: int
