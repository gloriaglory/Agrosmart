from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarketplaceItemViewSet

router = DefaultRouter()
router.register(r'items', MarketplaceItemViewSet, basename='marketplaceitem')

urlpatterns = [
    path('', include(router.urls)),  
]
