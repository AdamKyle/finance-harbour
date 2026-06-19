from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from authentication.managers.user_manager import UserManager


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    profile_photo = models.CharField(max_length=100, blank=True, default="")
    nickname = models.CharField(max_length=100, blank=True, default="")
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    completed_onboarding = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="unique_user_email_case_insensitive",
            ),
            models.UniqueConstraint(
                Lower("nickname"),
                condition=~models.Q(nickname=""),
                name="unique_user_nickname_case_insensitive_when_present",
            ),
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.email = User.objects.normalize_email(self.email)
        super().save(*args, **kwargs)
