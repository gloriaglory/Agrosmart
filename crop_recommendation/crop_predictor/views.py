from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import CROP_CONDITIONS
from .utils import get_lat_lon, get_soil_properties, get_weather_data
from .services import predict_crop_new

@api_view(['POST'])
def recommend_crop(request):
<<<<<<< HEAD
     """
   API endpoint to recommend crops based on location and environmental conditions.
     """
     address = request.data.get('address')
     lat = request.data.get('latitude')
     lon = request.data.get('longitude')

     if address and (not lat or not lon):
         lat, lon = get_lat_lon(address)
     if not lat or not lon:
         return Response({'error': 'Either an address or valid latitude and longitude are required.'}, status=400)

     # Get the soil properties based on lat and lon
     soil_data = get_soil_properties(lat, lon)
     if not soil_data:
         return Response({'error': 'Failed to retrieve soil properties.'}, status=400)

     # Get weather data
     temperature, humidity, rainfall = get_weather_data(lat, lon)
     if temperature is None or humidity is None or rainfall is None:
         return Response({'error': 'Failed to retrieve weather data.'}, status=400)

     # AI model-based crop recommendations
     N = soil_data.get("Nitrogen Total (0-20cm)")
     P = soil_data.get("Phosphorus Extractable (0-20cm)")
     K = soil_data.get("Potassium Extractable (0-20cm)")
     ph = soil_data.get("Soil pH (0-20cm)")

     print('Model Input:', N, P, K, temperature, humidity, ph, rainfall)

     try:
         ai_recommendations = predict_crop_new(
             N, P, K, temperature, humidity, ph, rainfall
         )
     except Exception as e:
         return Response({'error': f"Error in AI model prediction: {str(e)}"}, status=500)

     # crop details
     recommended_crops = ai_recommendations.get("recommended_crops", [])
     detailed_recommendations = {}

     for item in recommended_crops:
         crop_name = item.get("crop")
         score = item.get("score", 0)
         explanation = CROP_CONDITIONS.get(crop_name.title())

         if explanation:
          detailed_recommendations[crop_name.title()] = {
         "explanation": explanation,
         "score": score
         }
         else:
            detailed_recommendations[crop_name.title()] = {
            "explanation": "Hakuna maelezo yaliyopatikana kwa zao hili.",
            "score": score
         }


     response_data = {
         'location': {
             'latitude': lat,
             'longitude': lon,
             'address': address if address else 'N/A'
         },
         'soil_properties': soil_data,
         'weather': {
             'temperature': temperature,
             'humidity': humidity,
             'rainfall': rainfall,
         },
         'recommendations': detailed_recommendations
     }

     return Response(response_data, status=200)
=======
    """
    API endpoint to recommend crops based on location and environmental conditions.
    """
    address = request.data.get('address')
    lat = request.data.get('latitude')
    lon = request.data.get('longitude')

    if address and (not lat or not lon):
        lat, lon = get_lat_lon(address)

    if not lat or not lon:
        return Response({'error': 'Either an address or valid latitude and longitude are required.'}, status=400)

    # Get the soil properties based on lat and lon
    soil_data = get_soil_properties(lat, lon)
    if not soil_data:
        return Response({'error': 'Failed to retrieve soil properties.'}, status=400)

    # Get weather data
    temperature, humidity, rainfall = get_weather_data(lat, lon)
    if temperature is None or humidity is None or rainfall is None:
        return Response({'error': 'Failed to retrieve weather data.'}, status=400)

    # AI model-based crop recommendations
    N = soil_data.get("Nitrogen Total (0-20cm)")
    P = soil_data.get("Phosphorus Extractable (0-20cm)")
    K = soil_data.get("Potassium Extractable (0-20cm)")
    ph = soil_data.get("Soil pH (0-20cm)")

    print('Model Input:', N, P, K, temperature, humidity, ph, rainfall)

    try:
        ai_recommendations = predict_crop_new(
            N, P, K, temperature, humidity, ph, rainfall
        )
    except Exception as e:
        return Response({'error': f"Error in AI model prediction: {str(e)}"}, status=500)

    # crop details
    recommended_crops = ai_recommendations.get("recommended_crops", [])
    detailed_recommendations = {}

    for item in recommended_crops:
        crop_name = item.get("crop")
        score = item.get("score", 0)
        explanation = CROP_CONDITIONS.get(crop_name.title())

        if explanation:
         detailed_recommendations[crop_name.title()] = {
        "explanation": explanation,
        "score": score
        }
        else:
           detailed_recommendations[crop_name.title()] = {
           "explanation": "Hakuna maelezo yaliyopatikana kwa zao hili.",
           "score": score
        }


    response_data = {
        'location': {
            'latitude': lat,
            'longitude': lon,
            'address': address if address else 'N/A'
        },
        'soil_properties': soil_data,
        'weather': {
            'temperature': temperature,
            'humidity': humidity,
            'rainfall': rainfall,
        },
        'recommendations': detailed_recommendations
    }

    return Response(response_data, status=200)
>>>>>>> beb9e6f3902f60b23d0c278d47f70d33cfd52f70
