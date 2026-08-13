from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from authentication.models import User
from debt_profile.models import DebtProfile, ExpensePaymentSchedule, ExpensePaymentTiming, PaycheckPosition


class DebtProfileViewTest(APITestCase):
    def test_authenticated_user_can_save_debts(self) -> None:
        user = User.objects.create_user(
            email="savedebts@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/",
            {
                "debts": [
                    {
                        "label": "VISA",
                        "current_balance_cents": 100000,
                        "minimum_payment_cents": 5000,
                        "current_payment_cents": 5000,
                    }
                ]
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["debts"]), 1)
        self.assertEqual(response.data["debts"][0]["label"], "VISA")

    def test_authenticated_user_can_save_multiple_debts_in_debts_payload(self) -> None:
        user = User.objects.create_user(
            email="multidebts@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/",
            {
                "debts": [
                    {
                        "label": "VISA",
                        "current_balance_cents": 100000,
                        "minimum_payment_cents": 5000,
                        "current_payment_cents": 5000,
                    },
                    {
                        "label": "MasterCard",
                        "current_balance_cents": 200000,
                        "minimum_payment_cents": 8000,
                        "current_payment_cents": 10000,
                    },
                ]
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["debts"]), 2)

    def test_current_balance_cents_is_stored_as_cents(self) -> None:
        user = User.objects.create_user(
            email="balancecents@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/",
            {
                "debts": [
                    {
                        "label": "Test",
                        "current_balance_cents": 150000,
                        "minimum_payment_cents": 3000,
                        "current_payment_cents": 3000,
                    }
                ]
            },
            format="json",
            secure=True,
        )

        saved = DebtProfile.objects.get(user=user)
        self.assertEqual(saved.debts[0]["current_balance_cents"], 150000)

    def test_minimum_payment_cents_is_stored_as_cents(self) -> None:
        user = User.objects.create_user(
            email="minpaymentcents@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/",
            {
                "debts": [
                    {
                        "label": "Test",
                        "current_balance_cents": 100000,
                        "minimum_payment_cents": 7500,
                        "current_payment_cents": 7500,
                    }
                ]
            },
            format="json",
            secure=True,
        )

        saved = DebtProfile.objects.get(user=user)
        self.assertEqual(saved.debts[0]["minimum_payment_cents"], 7500)

    def test_current_payment_cents_is_stored_as_cents(self) -> None:
        user = User.objects.create_user(
            email="curpaymentcents@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        client.patch(
            "/api/debt-profile/",
            {
                "debts": [
                    {
                        "label": "Test",
                        "current_balance_cents": 100000,
                        "minimum_payment_cents": 7500,
                        "current_payment_cents": 9000,
                    }
                ]
            },
            format="json",
            secure=True,
        )

        saved = DebtProfile.objects.get(user=user)
        self.assertEqual(saved.debts[0]["current_payment_cents"], 9000)

    def test_negative_amounts_are_rejected(self) -> None:
        user = User.objects.create_user(
            email="negativeamount@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/",
            {
                "debts": [
                    {
                        "label": "Test",
                        "current_balance_cents": -100,
                        "minimum_payment_cents": 5000,
                        "current_payment_cents": 5000,
                    }
                ]
            },
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_pay_period_type_is_rejected(self) -> None:
        user = User.objects.create_user(
            email="invalidperiod@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/",
            {"pay_period_type": "QUARTERLY"},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_access_rejected(self) -> None:
        client = APIClient()

        response = client.patch(
            "/api/debt-profile/",
            {"income_per_pay_period_cents": 200000},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cross_user_access_rejected(self) -> None:
        user1 = User.objects.create_user(
            email="debtowner@example.com",
            password="StrongPassword123!",
        )
        user2 = User.objects.create_user(
            email="debtother@example.com",
            password="StrongPassword123!",
        )
        DebtProfile.objects.create(
            user=user1,
            income_per_pay_period_cents=200000,
            pay_period_type="BIWEEKLY",
            debts=[],
        )

        client = APIClient()
        client.force_authenticate(user=user2)
        client.patch(
            "/api/debt-profile/",
            {"income_per_pay_period_cents": 999999},
            format="json",
            secure=True,
        )

        user1_profile = DebtProfile.objects.get(user=user1)
        self.assertNotEqual(user1_profile.income_per_pay_period_cents, 999999)

    def test_authenticated_user_can_save_pay_period_type(self) -> None:
        user = User.objects.create_user(
            email="saveperiodtype@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            "/api/debt-profile/",
            {"pay_period_type": "BIWEEKLY"},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["pay_period_type"], "BIWEEKLY")
        self.assertEqual(DebtProfile.objects.get(user=user).pay_period_type, "BIWEEKLY")

    def test_response_returns_only_expected_fields(self) -> None:
        user = User.objects.create_user(
            email="debtfields@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/debt-profile/", secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {"income_per_pay_period_cents", "pay_period_type", "debts", "next_pay_date", "payment_schedules"},
        )

    def test_read_returns_only_owned_debt_payment_schedules(self) -> None:
        jane = User.objects.create_user(email="schedule-read-jane@example.com", password="StrongPassword123!")
        bob = User.objects.create_user(email="schedule-read-bob@example.com", password="StrongPassword123!")
        jane_profile = DebtProfile.objects.create(user=jane)
        bob_profile = DebtProfile.objects.create(user=bob)
        ExpensePaymentSchedule.objects.create(
            debt_profile=jane_profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.DAY_OF_MONTH,
            day_of_month=12,
        )
        ExpensePaymentSchedule.objects.create(
            debt_profile=bob_profile,
            source_key="debt:0",
            timing=ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position=PaycheckPosition.FIRST,
        )
        client = APIClient()
        client.force_authenticate(user=jane)

        response = client.get("/api/debt-profile/", secure=True)

        self.assertEqual(
            response.data["payment_schedules"],
            [
                {
                    "source_key": "debt:0",
                    "timing": "DAY_OF_MONTH",
                    "paycheck_position": None,
                    "day_of_month": 12,
                    "auto_deducted": False,
                }
            ],
        )

    def test_authenticated_user_can_save_next_pay_date(self) -> None:
        import datetime

        from django.utils import timezone

        user = User.objects.create_user(
            email="nextpaydate@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)
        future_date = (timezone.localdate() + datetime.timedelta(days=14)).isoformat()

        response = client.patch(
            "/api/debt-profile/",
            {"next_pay_date": future_date},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["next_pay_date"], future_date)
        self.assertEqual(DebtProfile.objects.get(user=user).next_pay_date.isoformat(), future_date)

    def test_past_next_pay_date_is_rejected(self) -> None:
        import datetime

        from django.utils import timezone

        user = User.objects.create_user(
            email="pastpaydate@example.com",
            password="StrongPassword123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)
        past_date = (timezone.localdate() - datetime.timedelta(days=1)).isoformat()

        response = client.patch(
            "/api/debt-profile/",
            {"next_pay_date": past_date},
            format="json",
            secure=True,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("next_pay_date", response.data)
