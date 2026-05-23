from django.urls import path
from . import views

urlpatterns = [
    # ─── AUTH ───────────────────────────────────────────────────────────────
    path('connexion/', views.login_view, name='login'),
    path('inscription/', views.register_view, name='register'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('mon-compte/', views.client_dashboard, name='client_dashboard'),
    path('mon-profil/', views.profile_edit, name='profile_edit'),

    # ─── ADMIN DASHBOARD ────────────────────────────────────────────────────
    path('dashboard/', views.dashboard, name='admin_dashboard'),

    # Voitures
    path('voitures/', views.car_list_admin, name='admin_car_list'),
    path('voitures/ajouter/', views.car_create, name='admin_car_create'),
    path('voitures/<int:pk>/modifier/', views.car_edit, name='admin_car_edit'),
    path('voitures/<int:pk>/supprimer/', views.car_delete, name='admin_car_delete'),

    # Réservations
    path('reservations/', views.reservation_list_admin, name='admin_reservation_list'),
    path('reservations/<int:pk>/', views.reservation_detail_admin, name='admin_reservation_detail'),
    path('reservations/<int:pk>/supprimer/', views.reservation_delete_admin, name='admin_reservation_delete'),
    path('reservations/<int:pk>/recu/', views.admin_download_receipt, name='admin_download_receipt'),

    # Clients
    path('clients/', views.client_list, name='admin_client_list'),
    path('clients/<str:email>/', views.client_history, name='admin_client_history'),

    # Utilisateurs
    path('utilisateurs/', views.user_list_admin, name='admin_user_list'),
    path('utilisateurs/<int:pk>/role/', views.user_toggle_role, name='admin_user_toggle_role'),
    path('utilisateurs/<int:pk>/supprimer/', views.user_delete_admin, name='admin_user_delete'),

    # Paiements
    path('paiements/', views.payment_methods_admin, name='admin_payment_methods'),
    path('paiements/verifier/<int:pk>/', views.verify_payment, name='admin_verify_payment'),
]
