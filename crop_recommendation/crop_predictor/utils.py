import time
from concurrent.futures import ThreadPoolExecutor

import httpx
from django.conf import settings
from django.core.cache import cache

from .climate import get_climate

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

# iSDA soil layers used for recommendations: (property, depth)
SOIL_LAYERS = {
    "ph": "0-20",
    "nitrogen_total": "0-20",
    "phosphorous_extractable": "0-20",
    "potassium_extractable": "0-20",
    "carbon_organic": "0-20",
    "cation_exchange_capacity": "0-20",
    "bulk_density": "0-20",
    "clay_content": "0-20",
    "sand_content": "0-20",
    "texture_class": "0-20",
    "bedrock_depth": "0-200",
    "slope_angle": "0",
    "land_cover_2019": "0",
}

# How each layer is labelled in the API response
SOIL_LABELS = {
    "nitrogen_total": "Nitrogen Total (0-20cm, g/kg)",
    "phosphorous_extractable": "Phosphorus Extractable (0-20cm, mg/kg)",
    "potassium_extractable": "Potassium Extractable (0-20cm, mg/kg)",
    "ph": "Soil pH (0-20cm)",
    "carbon_organic": "Organic Carbon (0-20cm, g/kg)",
    "cation_exchange_capacity": "Cation Exchange Capacity (0-20cm, cmol/kg)",
    "bulk_density": "Bulk Density (0-20cm, g/cm3)",
    "clay_content": "Clay (0-20cm, %)",
    "sand_content": "Sand (0-20cm, %)",
    "texture_class": "Texture (0-20cm)",
    "bedrock_depth": "Depth to Bedrock (cm)",
    "slope_angle": "Slope (degrees)",
    "land_cover_2019": "Land Cover (2019)",
}


def get_soil_property(lat, lon, property, depth="0-20", retries=3, delay=3):
    """One iSDA soil value at a point, or None if it is unavailable."""
    url = "https://api.isda-africa.com/v1/soilproperty"
    params = {"key": ISDA_API_KEY, "lat": lat, "lon": lon, "property": property, "depth": depth}
    for attempt in range(retries):
        try:
            response = httpx.get(url, params=params, timeout=30.0)
        except httpx.TimeoutException:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            print(f"Failed to fetch {property} after retries.")
            return None
        except Exception as e:
            print(f"Unexpected error when fetching {property}: {e}")
            return None
        if response.status_code != 200:
            print(f"Failed to fetch {property} data, status code: {response.status_code}")
            return None
        try:
            return response.json()["property"][property][0]["value"]["value"]
        except (ValueError, KeyError, IndexError) as e:
            print(f"Failed to decode or find {property}: {e}")
            return None
    return None


def get_soil(lat, lon):
    """
    All soil layers at a point as {property: value}, fetched in parallel.
    Soil maps do not change, so results are cached for 30 days.
    """
    lat, lon = round(float(lat), 4), round(float(lon), 4)  # ~10 m, finer than iSDA's 30 m grid
    key = f"soil:{lat}:{lon}"
    cached = cache.get(key)
    if cached:
        return cached
    with ThreadPoolExecutor(max_workers=6) as pool:
        values = dict(zip(SOIL_LAYERS, pool.map(
            lambda item: get_soil_property(lat, lon, *item), SOIL_LAYERS.items())))
    if any(v is not None for v in values.values()):
        cache.set(key, values, 60 * 60 * 24 * 30)
    return values


def label_soil(soil):
    """Soil values with readable labels, for showing to people."""
    return {SOIL_LABELS[k]: soil.get(k) for k in SOIL_LABELS}


# Main function
def main(address):
    lat, lon = get_lat_lon(address)
    if lat is None or lon is None:
        print("Failed to get latitude and longitude for the given address.")
        return None
    return {
        "latitude": lat,
        "longitude": lon,
        "soil_properties": label_soil(get_soil(lat, lon)),
        "climate": get_climate(lat, lon),
    }


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