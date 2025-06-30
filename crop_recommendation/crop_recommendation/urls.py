import stat
from django.contrib import admin 
from django.urls import path, include
from django.conf.urls.static import static
from . import settings
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('crop_predictor.urls')),
    path('detector/', include('disease_detection.urls')),  
    path('market/', include('market_place.urls')),
    path('api/auth/', include('authentication.urls')),
    path('api/bot/', include('bot.urls')),
    path('api/education/', include('education.urls')),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

