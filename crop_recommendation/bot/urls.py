from django.urls import path
from .views import agro_bot, agro_bot_stream

urlpatterns = [
    path('ask/', agro_bot, name='agro_bot'),
    path('ask/stream/', agro_bot_stream, name='agro_bot_stream'),
]
