from django.urls import path
from . import views

urlpatterns = [
    path('reserver/<int:car_id>/', views.reservation_create, name='reservation_create'),
    path('confirmation/<int:pk>/', views.reservation_success, name='reservation_success'),
    path('paiement/<int:pk>/', views.submit_payment, name='submit_payment'),
    path('recu/<int:pk>/pdf/', views.download_receipt, name='download_receipt'),
    path('api/dates/<int:car_id>/', views.api_reserved_dates, name='api_reserved_dates'),
]
