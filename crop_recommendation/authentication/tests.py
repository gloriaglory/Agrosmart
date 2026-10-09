from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()

NIDA = "19900101-12345-00001-12"
NIDA_DIGITS = "19900101123450000112"


class RegistrationTests(APITestCase):
    url = "/api/auth/register/"

    def payload(self, **overrides):
        data = {
            "username": "asha",
            "email": "asha@example.com",
            "password": "Strong-pass-123",
            "password2": "Strong-pass-123",
            "first_name": "Asha",
            "last_name": "Juma",
            "phone_number": "0712345678",
            "account_type": "seller",
            "id_number": NIDA,
        }
        data.update(overrides)
        return data

    def test_seller_registers_with_valid_nida(self):
        res = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["user"]["id_number"], NIDA_DIGITS)
        self.assertTrue(res.data["user"]["is_seller"])

    def test_seller_without_nida_is_rejected(self):
        res = self.client.post(self.url, self.payload(id_number=""), format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("id_number", res.data)

    def test_invalid_nida_is_rejected(self):
        res = self.client.post(self.url, self.payload(id_number="12345"), format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("id_number", res.data)

    def test_seller_needs_name_and_phone(self):
        res = self.client.post(
            self.url, self.payload(first_name="", phone_number=""), format="json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("first_name", res.data)
        self.assertIn("phone_number", res.data)

    def test_nida_must_be_unique(self):
        self.client.post(self.url, self.payload(), format="json")
        res = self.client.post(
            self.url,
            self.payload(username="other", email="other@example.com", id_number=NIDA_DIGITS),
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("id_number", res.data)

    def test_buyer_registers_without_nida(self):
        res = self.client.post(
            self.url,
            self.payload(account_type="buyer", id_number="", first_name="", phone_number=""),
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertFalse(res.data["user"]["is_seller"])
        self.assertIsNone(User.objects.get(username="asha").id_number)

    def test_valid_nida_cannot_be_changed(self):
        res = self.client.post(self.url, self.payload(), format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {res.data['token']}")
        res = self.client.patch(
            "/api/auth/profile/update/", {"id_number": "20000101-11111-22222-33"}, format="json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(User.objects.get(username="asha").id_number, NIDA_DIGITS)


class BecomeSellerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("buyer", "b@example.com", "pass")
        self.client.force_authenticate(self.user)

    def test_adding_nida_requires_name_and_phone(self):
        res = self.client.patch("/api/auth/profile/update/", {"id_number": NIDA}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("first_name", res.data)

    def test_buyer_becomes_seller(self):
        res = self.client.patch(
            "/api/auth/profile/update/",
            {"id_number": NIDA, "first_name": "Ali", "last_name": "Said", "phone_number": "0711000000"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_seller)
        self.assertEqual(self.user.id_number, NIDA_DIGITS)


# --- Google / Facebook login -------------------------------------------------
from copy import deepcopy
from unittest import mock

from django.conf import settings as django_settings
from django.test import override_settings


def social_settings(google=True, facebook=True):
    providers = deepcopy(django_settings.SOCIALACCOUNT_PROVIDERS)
    if google:
        providers["google"]["APP"].update(client_id="test-google-client", secret="g-secret")
    if facebook:
        providers["facebook"]["APP"].update(client_id="test-fb-app", secret="fb-secret")
    return providers


class FakeResponse:
    def __init__(self, data, status=200):
        self._data, self.status_code = data, status
        self.ok = status < 400

    def json(self):
        return self._data

    def raise_for_status(self):
        if not self.ok:
            from requests import HTTPError
            raise HTTPError(f"{self.status_code}")


class FakeSession:
    """Answers the provider calls allauth makes, keyed by URL fragment."""

    def __init__(self, routes):
        self.routes = routes

    def get(self, url, *args, **kwargs):
        for fragment, response in self.routes.items():
            if fragment in url:
                return response
        raise AssertionError(f"Unexpected request to {url}")


def fake_session(routes):
    return mock.patch(
        "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_requests_session",
        return_value=FakeSession(routes),
    )


GOOGLE_USER = {
    "id": "1234567890", "sub": "1234567890", "email": "farmer@gmail.com",
    "verified_email": True, "email_verified": True,
    "given_name": "Neema", "family_name": "Mushi", "name": "Neema Mushi",
}


class SocialLoginTests(APITestCase):
    def test_not_configured_returns_503(self):
        res = self.client.post("/api/auth/google/", {"access_token": "x"}, format="json")
        self.assertEqual(res.status_code, 503)

    def test_config_hides_ids_when_not_configured(self):
        res = self.client.get("/api/auth/social/config/")
        self.assertEqual(res.data, {"google_client_id": None, "facebook_app_id": None})

    def test_config_exposes_public_ids_only(self):
        with override_settings(SOCIALACCOUNT_PROVIDERS=social_settings()):
            res = self.client.get("/api/auth/social/config/")
        self.assertEqual(res.data, {"google_client_id": "test-google-client", "facebook_app_id": "test-fb-app"})
        self.assertNotIn("secret", str(res.data))

    def test_google_login_creates_buyer_and_returns_token(self):
        routes = {
            "tokeninfo": FakeResponse({"aud": "test-google-client"}),
            "userinfo": FakeResponse(GOOGLE_USER),
        }
        with override_settings(SOCIALACCOUNT_PROVIDERS=social_settings()), fake_session(routes):
            res = self.client.post("/api/auth/google/", {"access_token": "good"}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertTrue(res.data["token"])
        self.assertEqual(res.data["user"]["email"], "farmer@gmail.com")
        self.assertFalse(res.data["user"]["is_seller"])

        # Logging in again finds the same user
        with override_settings(SOCIALACCOUNT_PROVIDERS=social_settings()), fake_session(routes):
            again = self.client.post("/api/auth/google/", {"access_token": "good"}, format="json")
        self.assertEqual(again.data["user"]["id"], res.data["user"]["id"])
        self.assertEqual(User.objects.filter(email="farmer@gmail.com").count(), 1)

    def test_google_token_for_another_app_is_rejected(self):
        routes = {
            "tokeninfo": FakeResponse({"aud": "someone-elses-app"}),
            "userinfo": FakeResponse(GOOGLE_USER),
        }
        with override_settings(SOCIALACCOUNT_PROVIDERS=social_settings()), fake_session(routes):
            res = self.client.post("/api/auth/google/", {"access_token": "stolen"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertFalse(User.objects.filter(email="farmer@gmail.com").exists())

    def test_email_already_registered_with_password(self):
        User.objects.create_user("neema", "farmer@gmail.com", "pass")
        routes = {
            "tokeninfo": FakeResponse({"aud": "test-google-client"}),
            "userinfo": FakeResponse(GOOGLE_USER),
        }
        with override_settings(SOCIALACCOUNT_PROVIDERS=social_settings()), fake_session(routes):
            res = self.client.post("/api/auth/google/", {"access_token": "good"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("already registered", str(res.data))

    def test_facebook_login_creates_buyer(self):
        routes = {
            "graph.facebook.com": FakeResponse({
                "id": "998877", "email": "mkulima@example.com",
                "name": "Juma Ali", "first_name": "Juma", "last_name": "Ali",
            }),
        }
        with override_settings(SOCIALACCOUNT_PROVIDERS=social_settings()), fake_session(routes):
            res = self.client.post("/api/auth/facebook/", {"access_token": "fb-token"}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["user"]["email"], "mkulima@example.com")
        self.assertEqual(res.data["user"]["first_name"], "Juma")
        self.assertFalse(res.data["user"]["is_seller"])


# --- NIDA checks and verification ---------------------------------------------
from datetime import date

from .nida import nida_birth_date, nida_problem


class NidaCheckTests(APITestCase):
    def test_birth_date_is_read_from_first_eight_digits(self):
        self.assertEqual(nida_birth_date("19900101-12345-00001-12"), date(1990, 1, 1))

    def test_impossible_birth_date_is_rejected(self):
        self.assertIn("date of birth", nida_problem("19901345-12345-00001-12"))  # month 13
        self.assertIn("date of birth", nida_problem("12345678-12345-00001-12"))  # year 1234

    def test_future_birth_date_is_rejected(self):
        self.assertIn("date of birth", nida_problem("20990101-12345-00001-12"))

    def test_under_18_is_rejected(self):
        problem = nida_problem("20150601-12345-00001-12", today=date(2026, 10, 9))
        self.assertIn("18", problem)

    def test_signup_rejects_fake_number(self):
        res = self.client.post("/api/auth/register/", {
            "username": "fake", "email": "fake@example.com",
            "password": "Strong-pass-123", "password2": "Strong-pass-123",
            "first_name": "A", "last_name": "B", "phone_number": "0700000000",
            "account_type": "seller", "id_number": "12345678901234567890",
        }, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("date of birth", str(res.data["id_number"]))

    def test_profile_shows_birth_date(self):
        user = User.objects.create_user("s", "s@example.com", "p", id_number=NIDA_DIGITS)
        self.client.force_authenticate(user)
        res = self.client.get("/api/auth/profile/")
        self.assertEqual(res.data["nida_birth_date"], "1990-01-01")


class VerifyNidaTests(APITestCase):
    url = "/api/auth/nida/verify/"

    def setUp(self):
        self.user = User.objects.create_user(
            "seller", "s@example.com", "p", id_number=NIDA_DIGITS, first_name="Asha", last_name="Juma"
        )
        self.client.force_authenticate(self.user)

    def test_unavailable_until_nida_is_connected(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 503)
        self.user.refresh_from_db()
        self.assertFalse(self.user.nida_verified)

    def test_confirmed_by_nida(self):
        with mock.patch("authentication.views.verify_nida", return_value=True) as verify:
            res = self.client.post(self.url)
        verify.assert_called_once_with(NIDA_DIGITS, "Asha", "Juma")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["user"]["nida_verified"])

    def test_rejected_by_nida(self):
        with mock.patch("authentication.views.verify_nida", return_value=False):
            res = self.client.post(self.url)
        self.assertEqual(res.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.nida_verified)

    def test_needs_a_number(self):
        buyer = User.objects.create_user("buyer", "b@example.com", "p")
        self.client.force_authenticate(buyer)
        self.assertEqual(self.client.post(self.url).status_code, 400)

    def test_name_change_resets_verification(self):
        self.user.nida_verified = True
        self.user.save()
        self.client.patch("/api/auth/profile/update/", {"first_name": "Someone"}, format="json")
        self.user.refresh_from_db()
        self.assertFalse(self.user.nida_verified)

    def test_phone_change_keeps_verification(self):
        self.user.nida_verified = True
        self.user.save()
        self.client.patch("/api/auth/profile/update/", {"phone_number": "0799999999"}, format="json")
        self.user.refresh_from_db()
        self.assertTrue(self.user.nida_verified)
