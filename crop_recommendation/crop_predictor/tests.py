from datetime import date
from unittest import mock

from django.core.cache import cache
from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from . import climate, forecast, market, prevalence, services, suitability

# Ten identical years with a single Dec–Apr rainy season (~720 mm/year)
RAIN_YEAR = [140, 130, 150, 100, 20, 0, 0, 0, 0, 10, 40, 130]


def make_climate(rain_year=RAIN_YEAR, temperature=23.0, elevation=1100.0, years=10):
    rain_by_year = [list(rain_year) for _ in range(years)]
    return {
        "period": "2016–2025",
        "elevation_m": elevation,
        "annual_rainfall_mm": round(sum(rain_year)),
        "rainfall_variability": 0.0,
        "mean_temperature": temperature,
        "humidity": 65,
        "monthly_rainfall": list(rain_year),
        "monthly_temperature": [temperature] * 12,
        "monthly_min_temperature": [temperature - 6] * 12,
        "rainy_seasons": climate.rainy_seasons(rain_year),
        "rain_by_year": rain_by_year,
    }


SOIL = {
    "ph": 6.3, "nitrogen_total": 0.8, "phosphorous_extractable": 9.0, "potassium_extractable": 150.0,
    "carbon_organic": 12.0, "texture_class": "Sandy Clay Loam", "bedrock_depth": 199, "slope_angle": 3.0,
    "land_cover_2019": "Cultivated and managed vegetation / agriculture",
}


class ClimateSummaryTests(SimpleTestCase):
    def test_rainy_seasons_join_across_new_year_and_list_the_wettest_first(self):
        self.assertEqual(climate.rainy_seasons(RAIN_YEAR), ["Dec–Apr"])
        bimodal = [30, 20, 150, 250, 120, 10, 5, 5, 10, 60, 110, 70]
        self.assertEqual(climate.rainy_seasons(bimodal), ["Mar–May", "Oct–Dec"])

    def test_summarises_daily_records_into_months(self):
        days = [f"2024-{m:02d}-01" for m in range(1, 13)]
        rain = {"elevation": 900.0, "daily": {"time": days, "precipitation_sum": [10.0] * 12}}
        temp = {"daily": {"time": days, "temperature_2m_mean": [20.0] * 12, "temperature_2m_min": [14.0] * 12,
                          "relative_humidity_2m_mean": [70.0] * 12}}
        result = climate.summarise(rain, temp)
        self.assertEqual(result["annual_rainfall_mm"], 120)
        self.assertEqual(result["elevation_m"], 900.0)
        self.assertEqual(result["mean_temperature"], 20.0)
        self.assertEqual(result["rain_by_year"], [[10.0] * 12])

    def test_returns_none_when_service_fails(self):
        cache.clear()
        with mock.patch.object(climate.httpx, "get", side_effect=Exception("offline")):
            self.assertIsNone(climate.get_climate(-6.16, 35.75))


class SuitabilityTests(SimpleTestCase):
    def crop(self, key):
        return next(c for c in suitability.CROPS if c["key"] == key)

    def test_ramp(self):
        self.assertEqual(suitability.ramp(5, 0, 10, 20, 30), 0.5)
        self.assertEqual(suitability.ramp(15, 0, 10, 20, 30), 1.0)
        self.assertEqual(suitability.ramp(35, 0, 10, 20, 30), 0.0)

    def test_dry_warm_place_prefers_sorghum_to_tea(self):
        place = make_climate(rain_year=[110, 75, 90, 55, 10, 0, 0, 0, 0, 5, 30, 100], temperature=23)
        scores = {r["crop"]["key"]: r["score"] for r in (suitability.score_crop(c, place, SOIL) for c in suitability.CROPS)}
        self.assertGreater(scores["sorghum"], 0.7)
        self.assertEqual(scores["tea"], 0.0)

    def test_planting_starts_in_a_rainy_month(self):
        result = suitability.score_crop(self.crop("maize"), make_climate(), SOIL)
        self.assertIn(result["planting_month"], ["Dec", "Jan", "Feb", "Mar", "Apr"])

    def test_altitude_limit_lowers_cashew_in_highlands(self):
        low = suitability.score_crop(self.crop("cashew"), make_climate(elevation=400), SOIL)
        high = suitability.score_crop(self.crop("cashew"), make_climate(elevation=1900), SOIL)
        self.assertEqual(high["factors"]["altitude"], 0.0)
        self.assertGreater(low["score"], high["score"])

    def test_unreliable_rain_lowers_the_score(self):
        steady = make_climate()
        failing = make_climate()
        failing["rain_by_year"] = [list(RAIN_YEAR) for _ in range(5)] + [[v * 0.4 for v in RAIN_YEAR] for _ in range(5)]
        maize = self.crop("maize")
        self.assertGreater(suitability.score_crop(maize, steady, SOIL)["factors"]["rainfall"],
                           suitability.score_crop(maize, failing, SOIL)["factors"]["rainfall"])

    def test_recommend_returns_three_explained_crops_best_first(self):
        crops = suitability.recommend(make_climate(), SOIL)
        self.assertEqual(len(crops), 3)
        scores = [c["score"] for c in crops]
        self.assertEqual(scores, sorted(scores, reverse=True))
        for c in crops:
            self.assertIn("Yearly rain averages", c["explanation"])

    def test_missing_soil_uses_climate_only(self):
        for crop in suitability.recommend(make_climate(), {}):
            self.assertFalse({"ph", "texture", "depth"} & set(crop["factors"]))
            self.assertIn("rainfall", crop["factors"])

    def test_soil_notes_flag_low_nutrients(self):
        notes = " ".join(suitability.soil_notes(SOIL))
        self.assertIn("Phosphorus is low", notes)
        self.assertIn("Nitrogen is low", notes)
        self.assertNotIn("Potassium", notes)


class LocalFarmingTests(SimpleTestCase):
    def test_shares_follow_known_farming_areas(self):
        dodoma = prevalence.local_shares(-6.10, 35.80)
        self.assertAlmostEqual(sum(dodoma.values()), 1.0, places=5)
        self.assertGreater(dodoma["sorghum"], dodoma["rice"])
        newala = prevalence.local_shares(-10.68, 39.28)
        self.assertGreater(newala["cashew"], dodoma["cashew"])

    def test_no_shares_in_the_ocean(self):
        self.assertIsNone(prevalence.local_shares(-7.0, 40.8))

    def test_every_recommended_crop_has_a_mapspam_label(self):
        for crop in suitability.CROPS:
            self.assertIn(prevalence.CROP_TO_LABEL[crop["key"]], prevalence.LABELS)

    def test_local_farming_lifts_crops_grown_nearby(self):
        place = make_climate()
        plain = {r["key"]: r["score"] for r in suitability.recommend(place, SOIL, top_n=36)}
        shares = {label: 0.0 for label in prevalence.LABELS} | {"sesame": 1.0}
        weighted = suitability.recommend(place, SOIL, shares, alpha=0.5, top_n=36)
        by_key = {r["key"]: r for r in weighted}
        self.assertAlmostEqual(by_key["sesame"]["score"], plain["sesame"], places=3)
        self.assertAlmostEqual(by_key["maize"]["score"], plain["maize"] * 0.5, places=2)
        self.assertIn("Widely grown around here", by_key["sesame"]["explanation"])


class MarketTests(SimpleTestCase):
    detail = {"region": "Dodoma", "current": {"price": 1000, "date": "2026-08"},
              "seasonality": {"best_month": 2, "spread_pct": 25}}

    def test_price_yield_and_income(self):
        with mock.patch.object(market, "commodity_detail", return_value=self.detail), \
             mock.patch.object(market, "typical_yield", return_value=800.0):
            info = market.market_info("sorghum", "Dodoma", -6.1, 35.8)
        self.assertEqual(info["price_tzs_per_kg"], 1000)
        self.assertEqual(info["best_month_to_sell"], "Feb")
        self.assertEqual(info["income_tzs_per_ha"], 800_000)

    def test_rice_income_uses_milled_weight(self):
        with mock.patch.object(market, "commodity_detail", return_value=self.detail), \
             mock.patch.object(market, "typical_yield", return_value=1000.0):
            self.assertEqual(market.market_info("rice", "Dodoma", -6.1, 35.8)["income_tzs_per_ha"], 650_000)

    def test_crop_without_prices_still_gets_yield(self):
        with mock.patch.object(market, "typical_yield", return_value=2100.0):
            info = market.market_info("banana", "Kagera", -1.4, 31.75)
        self.assertIsNone(info["price_tzs_per_kg"])
        self.assertIn("2.1 t/ha", info["summary"])


class PlantingAdviceTests(SimpleTestCase):
    def days(self, rain):
        return [{"date": f"2026-11-{10 + i:02d}", "rain_mm": r, "chance": 80, "temp_min": 18, "temp_max": 28}
                for i, r in enumerate(rain)]

    def test_enough_rain_to_sow(self):
        recs = [{"name": "Maize (Mahindi)", "planting_month": "Nov"}]
        text = forecast.planting_advice(self.days([0, 12, 15, 3, 0]), recs, today=date(2026, 11, 10))
        self.assertIn("Planting rain is expected", text)
        self.assertIn("usual planting month for Maize (Mahindi)", text)

    def test_light_rain_says_wait(self):
        text = forecast.planting_advice(self.days([2, 3, 1, 0, 2]), [], today=date(2026, 11, 10))
        self.assertIn("Wait for about 20 mm", text)

    def test_dry_week_before_planting_month_says_prepare(self):
        recs = [{"name": "Sorghum (Mtama)", "planting_month": "Dec"}]
        text = forecast.planting_advice(self.days([0, 0, 0, 0, 0]), recs, today=date(2026, 11, 10))
        self.assertIn("too early to sow", text)
        self.assertIn("prepare land", text)

    def test_no_forecast_without_api_key(self):
        self.assertIsNone(forecast.get_forecast(-6.1, 35.8))


class PredictionTests(APITestCase):
    """The earlier machine-learning model, kept for comparison until it is retrained."""

    def test_returns_top_three_crops_best_first(self):
        result = services.predict_crop_new(0.5, 50, 50, 28, 60, 6.5, 90)
        crops = result["recommended_crops"]
        self.assertEqual(len(crops), 3)
        scores = [c["score"] for c in crops]
        self.assertEqual(scores, sorted(scores, reverse=True))


class RecommendEndpointTests(APITestCase):
    def post(self, soil=SOIL, place=None):
        days = [{"date": "2026-11-10", "rain_mm": 25.0, "chance": 90, "temp_min": 18, "temp_max": 29}]
        with mock.patch("crop_predictor.views.get_soil", return_value=soil), \
             mock.patch("crop_predictor.views.get_climate", return_value=place or make_climate()), \
             mock.patch("crop_predictor.views.reverse_geocode", return_value="Dodoma"), \
             mock.patch("crop_predictor.views.get_forecast", return_value=days), \
             mock.patch("crop_predictor.market.commodity_detail", return_value=None):
            return self.client.post("/api/recommend/", {"latitude": -6.16, "longitude": 35.75}, format="json")

    def test_returns_three_recommendations_and_long_term_climate(self):
        res = self.post()
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["weather"]["rainfall"], sum(RAIN_YEAR))
        self.assertEqual(res.data["weather"]["rainy_seasons"], ["Dec–Apr"])
        self.assertEqual(len(res.data["recommendations"]), 3)
        first = next(iter(res.data["recommendations"].values()))
        self.assertTrue(first["explanation"])
        self.assertIn("Phosphorus is low", " ".join(res.data["notes"]))
        self.assertIn("weighted by what farmers nearby grow", res.data["method"])
        self.assertIn("market", first)
        self.assertIn("Planting rain is expected", res.data["forecast"]["advice"])

    def test_water_is_rejected(self):
        res = self.post(soil=dict(SOIL, land_cover_2019="Permanent water bodies"))
        self.assertEqual(res.status_code, 400)

    def test_town_gets_a_warning(self):
        res = self.post(soil=dict(SOIL, land_cover_2019="Urban / built up"))
        self.assertEqual(res.status_code, 200)
        self.assertIn("not farmland", res.data["notes"][0])

    def test_climate_outage_is_reported(self):
        with mock.patch("crop_predictor.views.get_soil", return_value=SOIL), \
             mock.patch("crop_predictor.views.get_climate", return_value=None), \
             mock.patch("crop_predictor.views.get_forecast", return_value=None), \
             mock.patch("crop_predictor.views.reverse_geocode", return_value="Dodoma"):
            res = self.client.post("/api/recommend/", {"latitude": -6.16, "longitude": 35.75}, format="json")
        self.assertEqual(res.status_code, 503)
