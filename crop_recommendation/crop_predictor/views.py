from concurrent.futures import ThreadPoolExecutor

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import prevalence
from .climate import get_climate
from .forecast import get_forecast, planting_advice
from .market import market_info
from .suitability import recommend, soil_notes
from .utils import get_lat_lon, get_soil, label_soil, reverse_geocode

# iSDA land cover classes where nothing can be planted, and ones worth a warning
NO_FARMING = ("water", "open sea", "snow")
NOT_FARMLAND = ("urban", "built up", "forest", "wetland", "bare")


def land_cover_note(land_cover):
    """None if the land is usable; otherwise (blocking, message)."""
    cover = (land_cover or "").lower()
    if any(word in cover for word in NO_FARMING):
        return True, f"This point is mapped as {land_cover.lower()}. Choose a spot on land."
    if any(word in cover for word in NOT_FARMLAND):
        return False, (f"This point is mapped as {land_cover.lower()}, not farmland. The results describe "
                       "the soil and climate here; check the land can actually be farmed.")
    return None


@api_view(['POST'])
@permission_classes([AllowAny])
def recommend_crop(request):
    address = request.data.get('address')
    lat = request.data.get('latitude')
    lon = request.data.get('longitude')

    if address and (not lat or not lon):
        lat, lon = get_lat_lon(address)

    if not lat or not lon:
        return Response({'error': 'Either an address or valid latitude and longitude are required.'}, status=400)
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return Response({'error': 'Latitude and longitude must be numbers.'}, status=400)

    with ThreadPoolExecutor(max_workers=4) as pool:
        climate_job = pool.submit(get_climate, lat, lon)
        soil_job = pool.submit(get_soil, lat, lon)
        region_job = pool.submit(reverse_geocode, lat, lon)
        forecast_job = pool.submit(get_forecast, lat, lon)
        climate, soil, region = climate_job.result(), soil_job.result(), region_job.result()
        forecast = forecast_job.result()

    if climate is None:
        return Response({'error': 'Climate data is unavailable right now. Please try again in a minute.'},
                        status=503)

    notes = []
    land = land_cover_note(soil.get("land_cover_2019"))
    if land:
        blocking, message = land
        if blocking:
            return Response({'error': message}, status=400)
        notes.append(message)
    if all(soil.get(k) is None for k in ("ph", "texture_class", "bedrock_depth")):
        notes.append("Soil data is unavailable for this point, so only climate was used.")
    notes += soil_notes(soil)

    # Weight suitability by what farmers around here grow (MapSPAM model), when installed
    try:
        shares = prevalence.local_shares(lat, lon)
    except Exception as e:
        print(f"Local farming model failed: {e}")
        shares = None
    recommendations = recommend(climate, soil, shares, prevalence.ecocrop_weight() if shares else 1.0)
    with ThreadPoolExecutor(max_workers=3) as pool:
        markets = list(pool.map(lambda r: market_info(r["key"], region, lat, lon), recommendations))

    return Response({
        'location': {
            'latitude': lat,
            'longitude': lon,
            'region': region,
            'address': address if address else 'N/A',
        },
        'soil_properties': label_soil(soil),
        # Long-term averages, not today's weather
        'weather': {
            'temperature': climate['mean_temperature'],
            'humidity': climate['humidity'],
            'rainfall': climate['annual_rainfall_mm'],
            'rainfall_variability': climate['rainfall_variability'],
            'rainy_seasons': climate['rainy_seasons'],
            'monthly_rainfall': climate['monthly_rainfall'],
            'elevation': climate['elevation_m'],
            'period': climate['period'],
        },
        'recommendations': {
            r['name']: {
                **{key: r[key] for key in ('explanation', 'score', 'suitability', 'local_share',
                                           'planting_month', 'limiting_factor', 'factors')},
                'market': market,
            }
            for r, market in zip(recommendations, markets)
        },
        'forecast': None if not forecast else {
            'days': forecast,
            'advice': planting_advice(forecast, recommendations),
        },
        'notes': notes,
        'method': ('Crop needs (FAO ECOCROP) scored against iSDA soil and Open-Meteo climate history, '
                   'weighted by what farmers nearby grow (LightGBM on MapSPAM).'
                   if shares else 'Crop needs (FAO ECOCROP) scored against iSDA soil and Open-Meteo climate history.'),
    }, status=200)
