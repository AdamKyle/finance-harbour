from django.conf import settings
from django.db import models


class OnboardingProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding_progress",
    )
    current_step = models.CharField(max_length=50, default="profile")
    completed_steps = models.JSONField(default=list)
    form_data = models.JSONField(default=dict)
    is_complete = models.BooleanField(default=False)
    last_saved_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"OnboardingProgress({self.user_id})"
