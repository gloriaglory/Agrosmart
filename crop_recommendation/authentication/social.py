"""
Google and Facebook login.

The website signs the user in with Google/Facebook in the browser, then POSTs
the resulting access token to /api/auth/google/ or /api/auth/facebook/.
We check the token with the provider, create or find the user, and return
our own login token, the same shape as /api/auth/login/.

Credentials come from .env (see GOOGLE_OAUTH_* and FACEBOOK_APP_* in
settings.py). Do not also add a "Social application" in the Django admin,
or allauth will find two configurations for the same provider.
"""
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework import permissions, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import UserSerializer

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class VerifiedGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    """
    Google's user-info endpoint accepts access tokens issued to any app, so first
    confirm the token was issued to our client ID. Otherwise a token obtained by
    some other website could be used to log in here as that Google user.
    """

    def complete_login(self, request, app, token, response, **kwargs):
        resp = get_adapter().get_requests_session().get(
            GOOGLE_TOKENINFO_URL, params={"access_token": token.token}, timeout=10
        )
        info = resp.json() if resp.ok else {}
        if info.get("aud") != app.client_id and info.get("azp") != app.client_id:
            raise serializers.ValidationError("This Google sign-in was not issued for AgroSmart.")
        return super().complete_login(request, app, token, response, **kwargs)


def _provider_configured(provider):
    app = settings.SOCIALACCOUNT_PROVIDERS.get(provider, {}).get("APP", {})
    return bool(app.get("client_id") and app.get("secret"))


class TokenSocialLoginView(SocialLoginView):
    """Social login that answers like our password login: {"user": ..., "token": ...}."""

    provider = None
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        if not _provider_configured(self.provider):
            return Response(
                {"error": f"{self.provider.title()} login is not set up yet."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return super().post(request, *args, **kwargs)

    def get_response(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        return Response({"user": UserSerializer(self.user).data, "token": token.key})


class GoogleLogin(TokenSocialLoginView):
    provider = "google"
    adapter_class = VerifiedGoogleOAuth2Adapter
    callback_url = f"{settings.BACKEND_URL}/api/auth/google/callback/"


class FacebookLogin(TokenSocialLoginView):
    provider = "facebook"
    adapter_class = FacebookOAuth2Adapter
    callback_url = f"{settings.BACKEND_URL}/api/auth/facebook/callback/"


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def social_config(request):
    """Public IDs the website needs to show the Google/Facebook buttons (never the secrets)."""
    providers = settings.SOCIALACCOUNT_PROVIDERS
    return Response({
        "google_client_id": providers["google"]["APP"]["client_id"] if _provider_configured("google") else None,
        "facebook_app_id": providers["facebook"]["APP"]["client_id"] if _provider_configured("facebook") else None,
    })
