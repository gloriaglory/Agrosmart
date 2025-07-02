from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from .utils import predict_disease

@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF for testing only; enable in production
class PredictDiseaseView(View):
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'error': 'No image file provided.'}, status=400)
        
        try:
            prediction = predict_disease(image_file)
            return JsonResponse(prediction)
        except ValueError as ve:
            # Raised when image is invalid (e.g., not enough green pixels)
            return JsonResponse({'error': str(ve)}, status=400)
        except RuntimeError as re:
            # Raised if model is not loaded or class names missing
            return JsonResponse({'error': str(re)}, status=500)
        except Exception as e:
            # Catch-all for unexpected errors
            return JsonResponse({'error': 'Prediction failed.', 'details': str(e)}, status=500)
