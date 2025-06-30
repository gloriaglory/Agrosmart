from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import AllowAny
from .utils import predict_disease


class PredictDiseaseView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        file_obj = request.FILES.get("file")

        if not file_obj:
            return Response(
                {"error": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if file_obj.size > 5 * 1024 * 1024:  
            return Response(
                {"error": "File too large. Max size is 5MB."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not file_obj.content_type.startswith("image/"):
            return Response(
                {"error": "Unsupported file type. Please upload an image."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = predict_disease(file_obj)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to predict disease: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
