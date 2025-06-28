from django.urls import path
from . import views
from . import simple_views

urlpatterns = [
    path('recommend/', views.recommend_crop, name='recommend_crop'),
    path('simple-recommend/', simple_views.simple_recommend_crop, name='simple_recommend_crop'),
 ]
