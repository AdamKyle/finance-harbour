from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse


class OwnershipMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable[..., HttpResponse],
        view_args: list[Any],
        view_kwargs: dict[str, Any],
    ) -> HttpResponse | None:
        user_id = view_kwargs.get("user_id")

        if user_id is None:
            return None

        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required."}, status=403)

        if request.user.id != user_id:
            return JsonResponse({"detail": "Forbidden."}, status=403)

        return None
