import math
from datetime import date
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from rest_framework.test import APITestCase

from . import analysis
from .importer import load_prices, parse_rows
from .models import MarketPrice

HEADER = "date,admin1,admin2,market,market_id,latitude,longitude,category,commodity,commodity_id,unit,priceflag,pricetype,currency,price,usdprice\n"
TAGS = "#date,#adm1+name,#adm2+name,#loc+market+name,#loc+market+code,#geo+lat,#geo+lon,#item+type,#item+name,#item+code,#item+unit,#item+price+flag,#item+price+type,#currency,#value,#value+usd\n"


def row(day, region, market, commodity, unit, price_type, price, category="cereals and tubers", currency="TZS"):
    return f"{day},{region},X,{market},1,-6.1,35.7,{category},{commodity},1,{unit},actual,{price_type},{currency},{price},1\n"


def synthetic_csv(years=12):
    """Maize in two regions with a clear seasonal cycle, plus rows that must be skipped."""
    lines = [HEADER, TAGS]
    for y in range(2015, 2015 + years):
        for m in range(1, 13):
            season = 1 + 0.1 * math.cos((m - 1) / 12 * 2 * math.pi)  # dearest in January
            for region, market, base in [("Dodoma", "Dodoma", 60000), ("Dar-es-salaam", "Kariakoo", 70000)]:
                lines.append(row(f"{y}-{m:02d}-15", region, market, "Maize", "100 KG", "Wholesale", round(base * season)))
    lines.append(row("2020-01-15", "Dodoma", "Dodoma", "Oil (sunflower)", "L", "Retail", 5000, "oil and fats"))
    lines.append(row("2020-01-15", "Dodoma", "Dodoma", "Maize", "KG", "Retail", 700, currency="USD"))
    return "".join(lines)


class ImportTests(APITestCase):
    def test_parses_units_regions_and_skips_unusable_rows(self):
        rows = list(parse_rows(synthetic_csv(years=1)))
        self.assertEqual(len(rows), 24)  # 12 months x 2 markets; litres and USD rows skipped
        dar = next(r for r in rows if r.market == "Kariakoo")
        self.assertEqual(dar.region, "Dar es Salaam")
        self.assertEqual(dar.date, date(2015, 1, 1))
        self.assertAlmostEqual(dar.price_per_kg, 770.0)  # 77,000 per 100 kg

    def test_reloading_updates_instead_of_duplicating(self):
        load_prices(synthetic_csv(years=1))
        load_prices(synthetic_csv(years=1).replace(",60000,", ",65000,"))
        self.assertEqual(MarketPrice.objects.count(), 24)

    def test_refresh_command_from_file(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "prices.csv"
            path.write_text(synthetic_csv(years=2))
            out = StringIO()
            call_command("refresh_prices", file=str(path), stdout=out)
        self.assertIn("Saved 48 prices", out.getvalue())


class AnalysisTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        load_prices(synthetic_csv())

    def setUp(self):
        analysis.clear_cache()

    def test_list_shows_current_crops(self):
        items = analysis.commodity_list()
        self.assertEqual([c["commodity"] for c in items], ["Maize"])
        self.assertEqual(items[0]["price_type"], "wholesale")

    def test_crops_no_longer_tracked_are_hidden(self):
        MarketPrice.objects.create(date=date(2018, 1, 1), region="Dodoma", market="Dodoma", category="vegetables and fruits",
                                   commodity="Tomatoes", price_type="retail", unit="KG", price=1000, price_per_kg=1000)
        self.assertNotIn("Tomatoes", [c["commodity"] for c in analysis.commodity_list()])

    def test_detail_outlook_and_regions(self):
        d = analysis.commodity_detail("Maize")
        self.assertEqual(d["region"], "Tanzania")
        self.assertEqual(len(d["outlook"]), 3)
        for month in d["outlook"]:
            self.assertLessEqual(month["low"], month["typical"])
            self.assertLessEqual(month["typical"], month["high"])
        self.assertEqual({r["region"] for r in d["regions"]}, {"Dodoma", "Dar es Salaam"})
        self.assertIsNotNone(d["outlook_hit_rate_pct"])

    def test_region_detail(self):
        d = analysis.commodity_detail("Maize", "Dodoma")
        self.assertEqual(d["current"]["markets"], 1)
        self.assertEqual(d["current"]["date"], "2026-12")

    def test_seasonality_finds_the_cycle(self):
        s = analysis.commodity_detail("Maize")["seasonality"]
        self.assertIn(s["best_month"], (12, 1, 2))
        self.assertIn(s["cheapest_month"], (6, 7, 8))
        self.assertGreater(s["spread_pct"], 10)


class ApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        load_prices(synthetic_csv())

    def setUp(self):
        analysis.clear_cache()

    def test_list_endpoint(self):
        res = self.client.get("/api/prices/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["commodities"][0]["commodity"], "Maize")
        self.assertIn("WFP", res.data["source"]["name"])

    def test_detail_endpoint(self):
        res = self.client.get("/api/prices/detail/", {"commodity": "Maize", "region": "Dar es Salaam"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["region"], "Dar es Salaam")

    def test_unknown_crop_and_region(self):
        self.assertEqual(self.client.get("/api/prices/detail/", {"commodity": "Gold"}).status_code, 404)
        self.assertEqual(self.client.get("/api/prices/detail/", {"commodity": "Maize", "region": "Mars"}).status_code, 404)
        self.assertEqual(self.client.get("/api/prices/detail/").status_code, 400)
