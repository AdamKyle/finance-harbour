from django.test import SimpleTestCase

from debt_profile.views.request_validators import ImportantExpensesIndexRequest


class ImportantExpensesIndexRequestTest(SimpleTestCase):
    def test_positive_page_is_preserved(self) -> None:
        request = ImportantExpensesIndexRequest({"page": "3"})

        request.validate()

        self.assertEqual(request.page, 3)

    def test_invalid_page_defaults_to_one(self) -> None:
        request = ImportantExpensesIndexRequest({"page": "invalid"})

        request.validate()

        self.assertEqual(request.page, 1)

    def test_negative_page_normalizes_to_one(self) -> None:
        request = ImportantExpensesIndexRequest({"page": "-2"})

        request.validate()

        self.assertEqual(request.page, 1)
