from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import MarketplaceItem

User = get_user_model()


class MarketplaceTests(APITestCase):
    url = "/market/items/"

    def setUp(self):
        self.seller = User.objects.create_user(
            "seller", "s@example.com", "pass", id_number="19900101123450000112"
        )
        self.other_seller = User.objects.create_user(
            "other", "o@example.com", "pass", id_number="19900101123450000113"
        )
        self.buyer = User.objects.create_user("buyer", "b@example.com", "pass")

    def login(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def item_data(self, **overrides):
        data = {
            "name": "Maize",
            "description": "Dry maize",
            "price": "1800",
            "category": "cereals",
            "quantity": 50,
            "region": "Dodoma",
            "location": "Kondoa",
            "contact_info": "0712345678",
        }
        data.update(overrides)
        return data

    def make_item(self, seller=None, **overrides):
        fields = self.item_data(**overrides)
        return MarketplaceItem.objects.create(seller=seller or self.seller, **fields)

    def test_anyone_can_browse(self):
        self.make_item()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_anonymous_cannot_post(self):
        res = self.client.post(self.url, self.item_data(), format="json")
        self.assertIn(res.status_code, (401, 403))

    def test_buyer_cannot_post(self):
        self.login(self.buyer)
        res = self.client.post(self.url, self.item_data(), format="json")
        self.assertEqual(res.status_code, 403)

    def test_seller_can_post_and_is_recorded_as_owner(self):
        self.login(self.seller)
        res = self.client.post(self.url, self.item_data(), format="json")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(MarketplaceItem.objects.get().seller, self.seller)

    def test_region_is_required(self):
        self.login(self.seller)
        res = self.client.post(self.url, self.item_data(region=""), format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("region", res.data)

    def test_only_owner_can_edit_or_delete(self):
        item = self.make_item()
        self.login(self.other_seller)
        self.assertEqual(
            self.client.patch(f"{self.url}{item.id}/", {"price": "1"}, format="json").status_code, 403
        )
        self.assertEqual(self.client.delete(f"{self.url}{item.id}/").status_code, 403)

        self.login(self.seller)
        self.assertEqual(
            self.client.patch(f"{self.url}{item.id}/", {"price": "2000"}, format="json").status_code, 200
        )
        self.assertEqual(self.client.delete(f"{self.url}{item.id}/").status_code, 204)

    def test_mine_returns_only_own_listings(self):
        self.make_item()
        self.make_item(seller=self.other_seller, name="Beans")
        self.login(self.seller)
        res = self.client.get(f"{self.url}mine/")
        self.assertEqual([i["name"] for i in res.data], ["Maize"])

    def test_filter_by_region(self):
        self.make_item(region="Dodoma")
        self.make_item(region="Mbeya", name="Wheat")
        res = self.client.get(self.url, {"region": "mbeya"})
        self.assertEqual([i["name"] for i in res.data], ["Wheat"])

    def test_region_summary_groups_crops(self):
        self.make_item(region="Dodoma", name="Maize", price="1000")
        self.make_item(region="Dodoma", name="MAIZE", price="2000")
        self.make_item(region="Mbeya", name="Wheat", price="900")
        res = self.client.get(f"{self.url}regions/")
        self.assertEqual(res.status_code, 200)
        dodoma = next(r for r in res.data if r["region"] == "Dodoma")
        self.assertEqual(dodoma["listings"], 2)
        self.assertEqual(dodoma["crops"], [{"name": "Maize", "listings": 2, "avg_price": 1500}])


class SeedDemoTests(APITestCase):
    def test_creates_working_demo_data_and_can_run_twice(self):
        from io import StringIO

        from django.core.management import call_command
        from education.models import Comment, Content

        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())  # running again must not duplicate

        self.assertEqual(User.objects.filter(username__in=["demo_buyer", "asha_farms", "baraka_mkulima"]).count(), 3)
        self.assertEqual(MarketplaceItem.objects.count(), 18)
        self.assertEqual(Content.objects.filter(status=Content.APPROVED).count(), 2)
        self.assertEqual(Comment.objects.count(), 3)

        # Demo accounts can log in, and the verified seller can post
        res = self.client.post("/api/auth/login/", {"username": "asha_farms", "password": "AgroSmart-demo-2026"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["user"]["is_seller"])
        self.assertTrue(res.data["user"]["nida_verified"])

        # The map summary groups the demo listings by region
        regions = {r["region"]: r for r in self.client.get("/market/items/regions/").data}
        self.assertEqual(regions["Dodoma"]["crops"][0]["listings"], 3)
