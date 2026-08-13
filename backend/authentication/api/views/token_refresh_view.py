from dj_rest_auth.jwt_auth import JWTCookieAuthentication, get_refresh_view
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

BaseTokenRefreshView = get_refresh_view()


class TokenRefreshView(BaseTokenRefreshView):
    permission_classes = [AllowAny]
    throttle_scope = "dj_rest_auth"

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        JWTCookieAuthentication().enforce_csrf(request)

        return super().post(request, *args, **kwargs)

    def finalize_response(
        self,
        request: Request,
        response: Response,
        *args: object,
        **kwargs: object,
    ) -> Response:
        finalized_response = super().finalize_response(request, response, *args, **kwargs)
        finalized_response.data.pop("access", None)
        finalized_response.data.pop("refresh", None)

        return finalized_response
