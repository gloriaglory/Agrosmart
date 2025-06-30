
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from .utils import predict_disease

class PredictDiseaseView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        file_obj = request.FILES.get("file", None)
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size
        if file_obj.size > 5 * 1024 * 1024:  # 5MB
            return Response({"error": "File size exceeds 5MB"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        if not file_obj.content_type.startswith("image/"):
            return Response({"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = predict_disease(file_obj)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)