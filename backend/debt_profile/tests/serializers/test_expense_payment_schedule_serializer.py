from django.test import SimpleTestCase

from debt_profile.serializers.expense_payment_schedule_serializer import ExpensePaymentScheduleSerializer


class ExpensePaymentScheduleSerializerTest(SimpleTestCase):
    def test_every_paycheck_without_position_or_day_is_valid(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "food",
                "timing": "EVERY_PAYCHECK",
                "paycheck_position": None,
                "day_of_month": None,
                "auto_deducted": False,
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_every_paycheck_with_position_is_rejected(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "food",
                "timing": "EVERY_PAYCHECK",
                "paycheck_position": "FIRST",
                "day_of_month": None,
                "auto_deducted": False,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_every_paycheck_with_day_is_rejected(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "food",
                "timing": "EVERY_PAYCHECK",
                "paycheck_position": None,
                "day_of_month": 12,
                "auto_deducted": False,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_paycheck_position_with_position_and_null_day_is_valid(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "food_cents",
                "timing": "PAYCHECK_POSITION",
                "paycheck_position": "FIRST",
                "day_of_month": None,
                "auto_deducted": False,
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_day_of_month_with_day_is_valid(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "insurance_cents",
                "timing": "DAY_OF_MONTH",
                "paycheck_position": None,
                "day_of_month": 12,
                "auto_deducted": True,
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_day_below_one_is_rejected(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "insurance_cents",
                "timing": "DAY_OF_MONTH",
                "paycheck_position": None,
                "day_of_month": 0,
                "auto_deducted": False,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_day_above_thirty_one_is_rejected(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "insurance_cents",
                "timing": "DAY_OF_MONTH",
                "paycheck_position": None,
                "day_of_month": 32,
                "auto_deducted": False,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_paycheck_position_without_position_is_rejected(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "insurance_cents",
                "timing": "PAYCHECK_POSITION",
                "paycheck_position": None,
                "day_of_month": None,
                "auto_deducted": False,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_day_of_month_with_paycheck_position_is_rejected(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "insurance_cents",
                "timing": "DAY_OF_MONTH",
                "paycheck_position": "FIRST",
                "day_of_month": 12,
                "auto_deducted": False,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_paycheck_position_cannot_be_auto_deducted(self) -> None:
        serializer = ExpensePaymentScheduleSerializer(
            data={
                "source_key": "insurance_cents",
                "timing": "PAYCHECK_POSITION",
                "paycheck_position": "FIRST",
                "day_of_month": None,
                "auto_deducted": True,
            }
        )

        self.assertFalse(serializer.is_valid())
