from collections.abc import Mapping


class ImportantExpensesIndexRequest:
    def __init__(self, query_params: Mapping[str, object]) -> None:
        self.query_params = query_params
        self.page = 1

    def validate(self) -> None:
        submitted_page = self.query_params.get("page", "1")

        if not isinstance(submitted_page, (int, str)) or isinstance(submitted_page, bool):
            return

        try:
            parsed_page = int(submitted_page)
        except TypeError, ValueError:
            return

        self.page = max(parsed_page, 1)
