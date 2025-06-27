from django.contrib import admin
from django.urls import path, include
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('crop_predictor.urls')),
    path('detector/', include('disease_detection.urls')),  
    path('market/', include('market_place.urls')),
    path('api/auth/', include('authentication.urls')),
]
