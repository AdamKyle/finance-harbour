from typing import Any

from allauth.account.adapter import get_adapter
from dj_rest_auth.registration.serializers import RegisterSerializer as BaseRegisterSerializer
from rest_framework import serializers
from rest_framework.request import Request

from authentication.models import User
from authentication.views.request_validators import RegisterRequest


class RegisterSerializer(BaseRegisterSerializer):
    password = serializers.CharField(write_only=True)

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)
        self.fields.pop("password1", None)
        self.fields.pop("password2", None)

    def validate_password(self, password: str) -> str:
        return get_adapter().clean_password(password)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        register_request = RegisterRequest(data)
        register_request.validate()

        return data

    def get_cleaned_data(self) -> dict[str, Any]:
        return {
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password", ""),
        }

    def save(self, request: Request) -> User:
        return super().save(request)
