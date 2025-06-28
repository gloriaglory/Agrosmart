from django.urls import path
from .views import agro_bot

urlpatterns = [
    path('ask/', agro_bot, name='agro_bot'),
]
