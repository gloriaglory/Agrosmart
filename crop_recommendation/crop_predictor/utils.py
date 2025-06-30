import time
import httpx
import json

#  API keys
GOOGLE_API_KEY = 'AIzaSyANcz1bAZ8ZFZLHZIEhkb1lZIk45eGNOwQ'
OPENWEATHER_API_KEY = '722c138f1e11e7581b0a3945f5845ee9'
ISDA_API_KEY = 'AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4'

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

# Function to fetch weather data
def get_weather_data(lat, lon):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric'
    with httpx.Client() as client:
        response = client.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['cod'] == 200:
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            rainfall = 0
            if 'rain' in data:
                rainfall = data['rain'].get('1h', 0) or data['rain'].get('3h', 0)
            return temperature, humidity, rainfall
        else:
            print(f"Error from OpenWeatherMap API: {data.get('message', 'Unknown error')}")
            return None, None, None
    else:
        print(f"HTTP error {response.status_code} from OpenWeatherMap API")
        return None, None, None


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
                "rainfall_last_1h_mm": weather_data[2]
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