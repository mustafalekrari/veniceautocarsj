from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('cars.urls')),
    path('reservations/', include('reservations.urls')),
    path('auth/', include('accounts.urls')),          # auth + espace client
    path('admin-panel/', include('accounts.urls')),   # dashboard admin
    path('api/', include('cars.api_urls')),
    path('api/reservations/', include('reservations.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
