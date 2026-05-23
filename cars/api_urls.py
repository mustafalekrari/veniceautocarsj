from django.urls import path
from . import api_views

urlpatterns = [
    path('cars/', api_views.CarListAPI.as_view(), name='api_cars'),
    path('cars/<int:pk>/', api_views.CarDetailAPI.as_view(), name='api_car_detail'),
]
