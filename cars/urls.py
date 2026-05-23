from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('voitures/', views.car_list, name='car_list'),
    path('voitures/<int:pk>/', views.car_detail, name='car_detail'),
    path('a-propos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
