from unittest import mock

from rest_framework.test import APITestCase

from . import services, utils


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


class MonthlyRainfallTests(APITestCase):
    def test_averages_a_year_of_daily_rain_into_mm_per_month(self):
        # 365 days of 2 mm/day = 730 mm/year = ~60.8 mm/month; missing days are ignored
        daily = [2.0] * 365 + [None]
        with mock.patch.object(utils.httpx, "get", return_value=FakeResponse({"daily": {"precipitation_sum": daily}})):
            self.assertEqual(utils.get_monthly_rainfall(-6.16, 35.75), 60.8)

    def test_returns_none_when_service_fails(self):
        with mock.patch.object(utils.httpx, "get", side_effect=Exception("offline")):
            self.assertIsNone(utils.get_monthly_rainfall(-6.16, 35.75))


class PredictionTests(APITestCase):
    def test_returns_top_three_crops_best_first(self):
        result = services.predict_crop_new(0.5, 50, 50, 28, 60, 6.5, 90)
        crops = result["recommended_crops"]
        self.assertEqual(len(crops), 3)
        scores = [c["score"] for c in crops]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_rainfall_is_given_to_model_in_metres(self):
        with mock.patch.object(services.scaler, "transform", wraps=services.scaler.transform) as transform:
            services.predict_crop_new(0.5, 50, 50, 28, 60, 6.5, 90)
        df = transform.call_args[0][0]
        self.assertAlmostEqual(df["Rainfall"].iloc[0], 0.09)


class RecommendEndpointTests(APITestCase):
    def test_returns_three_recommendations_and_monthly_rainfall(self):
        soil = {
            "Nitrogen Total (0-20cm)": 0.6,
            "Phosphorus Extractable (0-20cm)": 40,
            "Potassium Extractable (0-20cm)": 120,
            "Soil pH (0-20cm)": 6.4,
        }
        with mock.patch("crop_predictor.views.get_soil_properties", return_value=soil), \
             mock.patch("crop_predictor.views.get_weather_data", return_value=(27.0, 55, 75.5)), \
             mock.patch("crop_predictor.views.reverse_geocode", return_value="Dodoma"):
            res = self.client.post("/api/recommend/", {"latitude": -6.16, "longitude": 35.75}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["weather"]["rainfall"], 75.5)
        self.assertEqual(len(res.data["recommendations"]), 3)
