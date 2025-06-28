import time
import httpx
import json
import os
import random

#  API keys
GOOGLE_API_KEY = 'AIzaSyBeBgRUcKlFwPOEZljE8JRmQ1qEZ1cQy04'
OPENWEATHER_API_KEY = '722c138f1e11e7581b0a3945f5845ee9'
ISDA_API_KEY = 'AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4'

# Check if we should skip external API calls
SKIP_EXTERNAL_APIS = os.environ.get('SKIP_EXTERNAL_APIS', '').lower() in ('true', '1', 't')

# Function to fetch latitude and longitude from Google Maps API
def get_lat_lon(address, retries=3, delay=2, timeout=10.0):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': GOOGLE_API_KEY}

    for attempt in range(retries):
        try:
            with httpx.Client() as client:
                response = client.get(base_url, params=params, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    lat = data['results'][0]['geometry']['location']['lat']
                    lon = data['results'][0]['geometry']['location']['lng']
                    return lat, lon
                else:
                    print(f"Error from Google Maps API: {data['status']}")
                    if attempt < retries - 1:
                        print(f"Retrying {retries - attempt - 1} more times...")
                        time.sleep(delay)
                    else:
                        return None, None
            else:
                print(f"HTTP error {response.status_code} from Google Maps API")
                if attempt < retries - 1:
                    print(f"Retrying {retries - attempt - 1} more times...")
                    time.sleep(delay)
                else:
                    return None, None
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ReadError, httpx.ConnectError) as e:
            print(f"Timeout or connection error when fetching geocoding data: {str(e)}")
            if attempt < retries - 1:
                print(f"Retrying {retries - attempt - 1} more times...")
                time.sleep(delay)
            else:
                print("Failed to fetch geocoding data after retries.")
                return None, None
        except Exception as e:
            print(f"Unexpected error when fetching geocoding data: {str(e)}")
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
def get_weather_data(lat, lon, retries=3, delay=2, timeout=10.0):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric'

    for attempt in range(retries):
        try:
            with httpx.Client() as client:
                response = client.get(url, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                if data['cod'] == 200:
                    temperature = data['main']['temp']
                    humidity = data['main']['humidity']
                    rainfall = data['rain'].get('1h', 0) if 'rain' in data else 0
                    return temperature, humidity, rainfall
                else:
                    print(f"Error from OpenWeatherMap API: {data.get('message', 'Unknown error')}")
                    if attempt < retries - 1:
                        print(f"Retrying {retries - attempt - 1} more times...")
                        time.sleep(delay)
                    else:
                        return None, None, None
            else:
                print(f"HTTP error {response.status_code} from OpenWeatherMap API")
                if attempt < retries - 1:
                    print(f"Retrying {retries - attempt - 1} more times...")
                    time.sleep(delay)
                else:
                    return None, None, None
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ReadError, httpx.ConnectError) as e:
            print(f"Timeout or connection error when fetching weather data: {str(e)}")
            if attempt < retries - 1:
                print(f"Retrying {retries - attempt - 1} more times...")
                time.sleep(delay)
            else:
                print("Failed to fetch weather data after retries.")
                return None, None, None
        except Exception as e:
            print(f"Unexpected error when fetching weather data: {str(e)}")
            return None, None, None

# Generate default values for testing/development
def get_default_values(address):
    # Generate random coordinates near Nairobi, Kenya
    lat = -1.2921 + (random.random() - 0.5) * 0.1
    lon = 36.8219 + (random.random() - 0.5) * 0.1

    # Default soil properties
    soil_properties = {
        "Nitrogen Total (0-20cm)": 0.5 + random.random() * 0.3,
        "Potassium Extractable (0-20cm)": 145.8 + random.random() * 20,
        "Phosphorus Extractable (0-20cm)": 35.2 + random.random() * 10,
        "Soil pH (0-20cm)": 6.2 + random.random() * 0.5,
        "Bulk Density (0-20cm)": 1.3 + random.random() * 0.2,
        "Land Cover (2019)": "Cropland",
        "Cation Exchange Capacity (0-20cm)": 15.5 + random.random() * 5
    }

    # Default weather data
    temperature = 22.5 + random.random() * 5
    humidity = 65 + random.random() * 15
    rainfall = 0.5 + random.random() * 2

    return lat, lon, soil_properties, temperature, humidity, rainfall

# Main function
def main(address):
    # If SKIP_EXTERNAL_APIS is True, use default values
    if SKIP_EXTERNAL_APIS:
        print("Skipping external API calls and using default values")
        lat, lon, soil_properties, temperature, humidity, rainfall = get_default_values(address)

        return {
            "latitude": lat,
            "longitude": lon,
            "soil_properties": soil_properties,
            "weather_data": {
                "temperature": temperature,
                "humidity": humidity,
                "rainfall_last_1h_mm": rainfall
            }
        }

    # Otherwise, try to get real data
    try:
        lat, lon = get_lat_lon(address)
        if lat is not None and lon is not None:
            try:
                soil_properties = get_soil_properties(lat, lon)
            except Exception as e:
                print(f"Error getting soil properties: {str(e)}")
                _, _, soil_properties, _, _, _ = get_default_values(address)

            try:
                weather_data = get_weather_data(lat, lon)
                temperature, humidity, rainfall = weather_data
            except Exception as e:
                print(f"Error getting weather data: {str(e)}")
                _, _, _, temperature, humidity, rainfall = get_default_values(address)

            # Return the results nicely as a dict
            return {
                "latitude": lat,
                "longitude": lon,
                "soil_properties": soil_properties,
                "weather_data": {
                    "temperature": temperature,
                    "humidity": humidity,
                    "rainfall_last_1h_mm": rainfall
                }
            }
        else:
            print("Failed to get latitude and longitude for the given address.")
            # Fall back to default values
            lat, lon, soil_properties, temperature, humidity, rainfall = get_default_values(address)

            return {
                "latitude": lat,
                "longitude": lon,
                "soil_properties": soil_properties,
                "weather_data": {
                    "temperature": temperature,
                    "humidity": humidity,
                    "rainfall_last_1h_mm": rainfall
                }
            }
    except Exception as e:
        print(f"Unexpected error in main function: {str(e)}")
        # Fall back to default values
        lat, lon, soil_properties, temperature, humidity, rainfall = get_default_values(address)

        return {
            "latitude": lat,
            "longitude": lon,
            "soil_properties": soil_properties,
            "weather_data": {
                "temperature": temperature,
                "humidity": humidity,
                "rainfall_last_1h_mm": rainfall
            }
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