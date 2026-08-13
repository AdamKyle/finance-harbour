from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from debt_profile.views.request_validators import MonthlyExpensePatchRequest


class MonthlyExpensePatchRequestTest(SimpleTestCase):
    def test_accepts_electricity_utility(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "recurring_expenses": [
                    {
                        "source_key": "utilities",
                        "category": "UTILITIES",
                        "label": "Electricity",
                        "amount_cents": 9000,
                        "utility_type": "ELECTRICITY",
                    }
                ]
            }
        )

        request.validate()

        self.assertEqual(request.validated_data["recurring_expenses"][0]["utility_type"], "ELECTRICITY")

    def test_accepts_water_utility(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "recurring_expenses": [
                    {
                        "source_key": "utilities",
                        "category": "UTILITIES",
                        "label": "Water",
                        "amount_cents": 7000,
                        "utility_type": "WATER",
                    }
                ]
            }
        )

        request.validate()

        self.assertEqual(request.validated_data["recurring_expenses"][0]["utility_type"], "WATER")

    def test_accepts_water_and_electricity_utility(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "recurring_expenses": [
                    {
                        "source_key": "utilities",
                        "category": "UTILITIES",
                        "label": "Water + electricity",
                        "amount_cents": 18000,
                        "utility_type": "WATER_AND_ELECTRICITY",
                    }
                ]
            }
        )

        request.validate()

        self.assertEqual(request.validated_data["recurring_expenses"][0]["utility_type"], "WATER_AND_ELECTRICITY")

    def test_accepts_custom_utility_name(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "recurring_expenses": [
                    {
                        "source_key": "utilities",
                        "category": "UTILITIES",
                        "label": "Municipal utilities",
                        "amount_cents": 11000,
                        "utility_type": "CUSTOM",
                    }
                ]
            }
        )

        request.validate()

        self.assertEqual(request.validated_data["recurring_expenses"][0]["label"], "Municipal utilities")

    def test_accepts_combined_utilities_with_included_services(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "recurring_expenses": [
                    {
                        "source_key": "utilities",
                        "category": "UTILITIES",
                        "label": "Utilities",
                        "amount_cents": 18000,
                        "utility_type": "UTILITIES",
                        "includes_internet": True,
                        "includes_cable": True,
                    }
                ]
            }
        )

        request.validate()

        self.assertEqual(len(request.validated_data["recurring_expenses"]), 1)

    def test_rejects_included_and_standalone_internet(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "recurring_expenses": [
                    {
                        "source_key": "utilities",
                        "category": "UTILITIES",
                        "label": "Utilities",
                        "amount_cents": 18000,
                        "utility_type": "UTILITIES",
                        "includes_internet": True,
                    },
                    {
                        "source_key": "internet",
                        "category": "INTERNET",
                        "label": "Internet",
                        "amount_cents": 7000,
                    },
                ]
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()

    def test_rejects_custom_utility_without_label(self) -> None:
        request = MonthlyExpensePatchRequest(
            {
                "recurring_expenses": [
                    {
                        "source_key": "utilities",
                        "category": "UTILITIES",
                        "label": "",
                        "amount_cents": 10000,
                        "utility_type": "CUSTOM",
                    }
                ]
            }
        )

        with self.assertRaises(ValidationError):
            request.validate()
