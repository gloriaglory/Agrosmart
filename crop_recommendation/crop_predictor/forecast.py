"""
Planting-time advice from the OpenWeather 5-day forecast.

Uses a common rule for the start of the rains: sow once about 20 mm has fallen within
three days and the soil is moist a hand's depth down, so seeds do not sprout and then dry out.
"""
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import httpx
from django.conf import settings
from django.core.cache import cache

from .climate import MONTHS

FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
PLANTING_RAIN_MM = 20   # rain within PLANTING_DAYS that makes sowing worthwhile
PLANTING_DAYS = 3
LIGHT_RAIN_MM = 5


def get_forecast(lat, lon):
    """Daily rain and temperature for the next 5 days, or None if unavailable."""
    if not settings.OPENWEATHER_API_KEY:
        return None
    lat, lon = round(float(lat), 2), round(float(lon), 2)
    key = "forecast:" + hashlib.md5(f"{lat}:{lon}".encode()).hexdigest()
    cached = cache.get(key)
    if cached:
        return cached
    try:
        response = httpx.get(FORECAST_URL, params={
            "lat": lat, "lon": lon, "units": "metric", "appid": settings.OPENWEATHER_API_KEY,
        }, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Weather forecast request failed: {e}")
        return None

    offset = timedelta(seconds=data.get("city", {}).get("timezone", 0))
    days = defaultdict(lambda: {"rain_mm": 0.0, "chance": 0.0, "temps": []})
    for step in data.get("list", []):
        day = (datetime.fromtimestamp(step["dt"], tz=timezone.utc) + offset).date().isoformat()
        days[day]["rain_mm"] += step.get("rain", {}).get("3h", 0.0)
        days[day]["chance"] = max(days[day]["chance"], step.get("pop", 0.0))
        days[day]["temps"].append(step["main"]["temp"])
    forecast = [{
        "date": day,
        "rain_mm": round(d["rain_mm"], 1),
        "chance": round(d["chance"] * 100),
        "temp_min": round(min(d["temps"])),
        "temp_max": round(max(d["temps"])),
    } for day, d in sorted(days.items())]
    cache.set(key, forecast, 60 * 60)
    return forecast


def wettest_window(days, length=PLANTING_DAYS):
    """The most rain falling within `length` consecutive days, and the day it starts."""
    best, start = 0.0, None
    for i in range(len(days)):
        total = sum(d["rain_mm"] for d in days[i:i + length])
        if total > best:
            best, start = total, days[i]["date"]
    return best, start


def planting_advice(days, recommendations, today=None):
    """One short paragraph on whether this week suits sowing the recommended crops."""
    if not days:
        return None
    today = today or datetime.now().date()
    this_month, next_month = MONTHS[today.month - 1], MONTHS[today.month % 12]
    due_now = [r["name"] for r in recommendations if r.get("planting_month") == this_month]
    due_soon = [r["name"] for r in recommendations if r.get("planting_month") == next_month]
    total = round(sum(d["rain_mm"] for d in days))
    window, start = wettest_window(days)

    if window >= PLANTING_RAIN_MM:
        when = datetime.fromisoformat(start).strftime("%a %d %b")
        text = (f"Planting rain is expected: about {window:.0f} mm within {PLANTING_DAYS} days from {when}. "
                "Sow once the soil is moist about a hand's depth (15 cm) down.")
    elif total >= LIGHT_RAIN_MM:
        text = (f"Only light rain is expected ({total} mm over 5 days). Wait for about {PLANTING_RAIN_MM} mm "
                f"within {PLANTING_DAYS} days before sowing, so seeds do not sprout and then dry out.")
    else:
        text = "No useful rain is expected in the next 5 days, so it is too early to sow rain-fed crops."

    if due_now:
        text += f" This is the usual planting month for {', '.join(due_now)}."
    elif due_soon:
        text += f" {', '.join(due_soon)} {'is' if len(due_soon) == 1 else 'are'} usually planted next month " \
                f"({next_month}), so prepare land, seed and fertiliser now."
    return text
