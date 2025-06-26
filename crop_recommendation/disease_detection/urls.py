from django.urls import path
from .views import PredictDiseaseView  # <- Make sure this import is present

urlpatterns = [
    path("detect", PredictDiseaseView.as_view(), name="disease-detect"),
]
