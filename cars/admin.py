from django.contrib import admin
from .models import Car, CarCategory

admin.site.register(CarCategory)
admin.site.register(Car)
