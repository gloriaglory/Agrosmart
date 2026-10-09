import time
import httpx
import json
from datetime import date, timedelta
from django.conf import settings

# API keys (loaded from .env via settings)
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY
ISDA_API_KEY = settings.ISDA_API_KEY

# Function to fetch latitude and longitude from Google Maps API
def get_lat_lon(address):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': GOOGLE_API_KEY}
    with httpx.Client() as client:
        response = client.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            lat = data['results'][0]['geometry']['location']['lat']
            lon = data['results'][0]['geometry']['location']['lng']
            return lat, lon
        else:
            print(f"Error from Google Maps API: {data['status']}")
            return None, None
    else:
        print(f"HTTP error {response.status_code} from Google Maps API")
        return None, None

# Function to fetch a single soil property
def get_soil_property(lat, lon, property, depth="0-20", retries=3, delay=3):
    url = (
        f"https://api.isda-africa.com/v1/soilproperty"
        f"?key={ISDA_API_KEY}&lat={lat}&lon={lon}&property={property}&depth={depth}"
    )
    
    for attempt in range(retries):
        try:
            with httpx.Client() as client:
                response = client.get(url, timeout=30.0)  # Added timeout
            if response.status_code == 200:
                try:
                    return response.json()["property"][property][0]["value"]["value"]
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Failed to decode or find {property}: {e}")
                    return None
            else:
                print(f"Failed to fetch {property} data, status code: {response.status_code}")
                return None
        except httpx.ReadTimeout:
            print(f"Timeout when fetching {property}. Retrying {retries - attempt - 1} more times...")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f"Failed to fetch {property} after retries.")
                return None
        except Exception as e:
            print(f"Unexpected error when fetching {property}: {e}")
            return None

# Function to fetch multiple soil properties
def get_soil_properties(lat, lon):
    properties = [
        ["nitrogen_total", "0-20"],
        ["potassium_extractable", "0-20"],
        ["phosphorous_extractable", "0-20"],
        ["ph", "0-20"],
        ["bulk_density", "0-20"],
        ["land_cover_2019", "0"],
        ["cation_exchange_capacity", "0-20"]
    ]

    results = []
    for prop, depth in properties:
        result = get_soil_property(lat, lon, prop, depth)
        results.append(result)

    return {
        "Nitrogen Total (0-20cm)": results[0],
        "Potassium Extractable (0-20cm)": results[1],
        "Phosphorus Extractable (0-20cm)": results[2],
        "Soil pH (0-20cm)": results[3],
        "Bulk Density (0-20cm)": results[4],
        "Land Cover (2019)": results[5],
        "Cation Exchange Capacity (0-20cm)": results[6]
    }

# Rainfall history from Open-Meteo (free, no API key needed)
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def get_monthly_rainfall(lat, lon):
    """
    Average monthly rainfall (mm) at this location over the last 12 months.

    Current-weather APIs only report rain that is falling right now, which is
    almost always 0. Crops depend on the rainfall over the seasons, so we use
    a year of daily totals instead. The archive lags a few days behind, so the
    window ends a week ago.
    """
    end = date.today() - timedelta(days=7)
    start = end - timedelta(days=365)
    try:
        response = httpx.get(
            OPEN_METEO_ARCHIVE_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "daily": "precipitation_sum",
                "timezone": "auto",
            },
            timeout=20.0,
        )
        response.raise_for_status()
        daily = [v for v in response.json()["daily"]["precipitation_sum"] if v is not None]
    except Exception as e:
        print(f"Rainfall history request failed: {e}")
        return None
    if not daily:
        return None
    return round(sum(daily) / len(daily) * 365 / 12, 1)


# Function to fetch weather data
def get_weather_data(lat, lon):
    """
    Returns (temperature °C, humidity %, average monthly rainfall mm).
    Temperature and humidity are current readings from OpenWeatherMap;
    rainfall is the 12-month average from get_monthly_rainfall.
    """
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric'
    with httpx.Client() as client:
        response = client.get(url)

    if response.status_code != 200:
        print(f"HTTP error {response.status_code} from OpenWeatherMap API")
        return None, None, None
    data = response.json()
    if data.get('cod') != 200:
        print(f"Error from OpenWeatherMap API: {data.get('message', 'Unknown error')}")
        return None, None, None

    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    rainfall = get_monthly_rainfall(lat, lon)
    return temperature, humidity, rainfall


# Main function
def main(address):
    lat, lon = get_lat_lon(address)
    if lat is not None and lon is not None:
        soil_properties = get_soil_properties(lat, lon)
        weather_data = get_weather_data(lat, lon)

        # Return the results nicely as a dict
        return {
            "latitude": lat,
            "longitude": lon,
            "soil_properties": soil_properties,
            "weather_data": {
                "temperature": weather_data[0],
                "humidity": weather_data[1],
                "avg_monthly_rainfall_mm": weather_data[2]
            }
        }
    else:
        print("Failed to get latitude and longitude for the given address.")
        return None


def get_district_and_region(address):
    # Dummy logic for example
    parts = address.split(",") 
    
    if len(parts) >= 2:
        district = parts[0].strip()
        region = parts[1].strip()
    else:
        district = ""
        region = ""
        
    return district, region


def get_crops_regional(address):  
    # function body
    pass


def reverse_geocode(lat: float, lon: float) -> str:
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        headers = {"User-Agent": "agrosmart-app/1.0"}  # Required by Nominatim
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()

        data = response.json()
        return data.get("address", {}).get("state", "Unknown Region")
    except Exception as e:
        print("Reverse geocoding failed:", e)
        return "Unknown Region"