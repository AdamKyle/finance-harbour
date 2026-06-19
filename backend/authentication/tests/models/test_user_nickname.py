from django.db import IntegrityError, transaction
from django.test import TestCase

from authentication.models import User


class UserNicknameTest(TestCase):
    def test_nickname_field_accepts_a_unique_value(self) -> None:
        user = User.objects.create_user(
            email="nickname@example.com",
            password="StrongPassword123!",
            nickname="TestNick",
        )

        self.assertEqual(user.nickname, "TestNick")

    def test_nickname_is_optional(self) -> None:
        user = User.objects.create_user(
            email="nonickname@example.com",
            password="StrongPassword123!",
        )

        self.assertEqual(user.nickname, "")

    def test_database_rejects_duplicate_non_empty_nickname(self) -> None:
        User.objects.create_user(
            email="first-nickname@example.com",
            password="StrongPassword123!",
            nickname="DuplicateNick",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                email="second-nickname@example.com",
                password="StrongPassword123!",
                nickname="DuplicateNick",
            )

        self.assertEqual(User.objects.filter(nickname="DuplicateNick").count(), 1)

    def test_database_rejects_case_variant_duplicate_non_empty_nickname(self) -> None:
        User.objects.create_user(
            email="first-case-nickname@example.com",
            password="StrongPassword123!",
            nickname="CaseNick",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                email="second-case-nickname@example.com",
                password="StrongPassword123!",
                nickname="casenick",
            )

        self.assertEqual(User.objects.filter(nickname__iexact="CaseNick").count(), 1)

    def test_database_allows_multiple_blank_nicknames(self) -> None:
        User.objects.create_user(
            email="first-blank-nickname@example.com",
            password="StrongPassword123!",
        )
        User.objects.create_user(
            email="second-blank-nickname@example.com",
            password="StrongPassword123!",
        )

        self.assertEqual(User.objects.filter(nickname="").count(), 2)
