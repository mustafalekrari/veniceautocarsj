from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.ReservationListAPI.as_view(), name='api_reservations'),
    path('<int:pk>/', api_views.ReservationDetailAPI.as_view(), name='api_reservation_detail'),
]
