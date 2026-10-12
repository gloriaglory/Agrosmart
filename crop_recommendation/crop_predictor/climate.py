"""
Long-term climate for a location, from Open-Meteo daily history (ERA5, adjusted to the
local altitude). Crops depend on the usual seasons, not on today's weather, so
recommendations use these averages.

Open-Meteo counts long requests as many calls, so rainfall, which varies a lot from
year to year, uses 10 years, and temperature, which barely does, uses 3.
"""
import hashlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from statistics import mean, pstdev

import httpx
from django.core.cache import cache

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
RAIN_YEARS = 10
TEMPERATURE_YEARS = 3
RAINY_MONTH_MM = 50  # a month with at least this much rain on average counts as rainy
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _fetch_daily(lat, lon, variables, years):
    last_year = date.today().year - 1
    response = httpx.get(ARCHIVE_URL, params={
        "latitude": lat,
        "longitude": lon,
        "start_date": f"{last_year - years + 1}-01-01",
        "end_date": f"{last_year}-12-31",
        "daily": variables,
        "timezone": "auto",
    }, timeout=40.0)
    response.raise_for_status()
    return response.json()


def rainy_seasons(monthly_rain):
    """Runs of rainy months, e.g. ['Mar–May', 'Oct–Dec']; longest season first."""
    rainy = [r >= RAINY_MONTH_MM for r in monthly_rain]
    if all(rainy):
        return ["All year"]
    if not any(rainy):
        return []
    start = rainy.index(False)  # begin scanning after a dry month so seasons over New Year stay whole
    runs, current = [], []
    for i in range(1, 13):
        m = (start + i) % 12
        if rainy[m]:
            current.append(m)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    runs.sort(key=lambda run: -sum(monthly_rain[m] for m in run))
    return [MONTHS[run[0]] if len(run) == 1 else f"{MONTHS[run[0]]}–{MONTHS[run[-1]]}" for run in runs]


def summarise(rain_daily, temp_daily):
    """Turn daily records into monthly rainfall per year and average monthly temperatures."""
    rain = defaultdict(float)
    d = rain_daily["daily"]
    for day, p in zip(d["time"], d["precipitation_sum"]):
        if p is not None:
            rain[(int(day[:4]), int(day[5:7]) - 1)] += p

    temps, mins, humidity = defaultdict(list), defaultdict(list), []
    d = temp_daily["daily"]
    for day, t, tmin, rh in zip(d["time"], d["temperature_2m_mean"], d["temperature_2m_min"],
                                d["relative_humidity_2m_mean"]):
        month = int(day[5:7]) - 1
        if t is not None:
            temps[month].append(t)
        if tmin is not None:
            mins[month].append(tmin)
        if rh is not None:
            humidity.append(rh)

    years = sorted({y for y, _ in rain})
    rain_by_year = [[round(rain[(y, m)], 1) for m in range(12)] for y in years]
    totals = [sum(row) for row in rain_by_year]
    monthly_rain = [round(mean(row[m] for row in rain_by_year), 1) for m in range(12)]
    return {
        "period": f"{years[0]}–{years[-1]}",
        "elevation_m": rain_daily.get("elevation"),
        "annual_rainfall_mm": round(mean(totals)),
        # How much yearly rainfall swings from year to year (0.25 = typically ±25%)
        "rainfall_variability": round(pstdev(totals) / mean(totals), 2) if mean(totals) else None,
        "mean_temperature": round(mean(t for m in range(12) for t in temps[m]), 1),
        "humidity": round(mean(humidity)) if humidity else None,
        "monthly_rainfall": monthly_rain,
        "monthly_temperature": [round(mean(temps[m]), 1) for m in range(12)],
        "monthly_min_temperature": [round(mean(mins[m]), 1) for m in range(12)],
        "rainy_seasons": rainy_seasons(monthly_rain),
        "rain_by_year": rain_by_year,
    }


def get_climate(lat, lon):
    """Climate summary for a location, or None if the climate service is unavailable."""
    lat, lon = round(float(lat), 2), round(float(lon), 2)  # ~1 km; nearby clicks share the cache
    key = "climate:" + hashlib.md5(f"{lat}:{lon}:{date.today().year}".encode()).hexdigest()
    cached = cache.get(key)
    if cached:
        return cached
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            rain = pool.submit(_fetch_daily, lat, lon, "precipitation_sum", RAIN_YEARS)
            temp = pool.submit(_fetch_daily, lat, lon,
                               "temperature_2m_mean,temperature_2m_min,relative_humidity_2m_mean",
                               TEMPERATURE_YEARS)
            climate = summarise(rain.result(), temp.result())
    except Exception as e:
        print(f"Climate history request failed: {e}")
        return None
    cache.set(key, climate, 60 * 60 * 24 * 30)
    return climate
