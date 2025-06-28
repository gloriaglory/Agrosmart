from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import CROP_CONDITIONS
from .services import predict_crop_new
import random

@api_view(['POST'])
def simple_recommend_crop(request):
    """
    Simplified API endpoint to recommend crops based on location.
    Uses default values instead of making external API calls.
    """
    address = request.data.get('address')
    if not address:
        address = "Nairobi, Kenya"  # Default address if none provided
    
    print("Using default values for all requests")
    
    # Generate default values
    lat = -1.2921 + (random.random() - 0.5) * 0.1
    lon = 36.8219 + (random.random() - 0.5) * 0.1
    
    # Default soil properties
    soil_data = {
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