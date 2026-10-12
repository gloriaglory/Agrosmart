from django.urls import path

from . import views

urlpatterns = [
    path("", views.commodity_list, name="price-list"),
    path("detail/", views.commodity_detail, name="price-detail"),
]
