"""
Script pour créer les données de démonstration Venice Autocars.
Exécuter avec: python manage.py shell < seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from cars.models import Car, CarCategory
from reservations.models import Reservation
from datetime import date, timedelta

# Superuser admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@venice-autocars.fr', 'admin123')
    print("✅ Superuser créé: admin / admin123")

# Catégories
cats = {}
for name in ['Berline', 'SUV', 'Sportive', 'Citadine', 'Utilitaire']:
    cat, _ = CarCategory.objects.get_or_create(name=name)
    cats[name] = cat
print("✅ Catégories créées")

# Voitures
cars_data = [
    {'brand': 'BMW', 'model': 'Série 3', 'year': 2023, 'category': 'Berline', 'price_per_day': 950,
     'seats': 5, 'doors': 4, 'transmission': 'automatic', 'fuel': 'essence', 'mileage': 15000,
     'description': 'Berline premium alliant confort et sportivité. Idéale pour les voyages d\'affaires au Maroc.',
     'features': 'GPS, Climatisation, Bluetooth, Sièges chauffants, Caméra de recul, Régulateur de vitesse'},
    {'brand': 'Mercedes', 'model': 'Classe C', 'year': 2023, 'category': 'Berline', 'price_per_day': 1100,
     'seats': 5, 'doors': 4, 'transmission': 'automatic', 'fuel': 'diesel', 'mileage': 12000,
     'description': 'L\'élégance allemande à son meilleur. Confort exceptionnel et finitions premium.',
     'features': 'GPS, Climatisation bi-zone, Bluetooth, Toit ouvrant, Sièges en cuir, Aide au stationnement'},
    {'brand': 'Audi', 'model': 'Q5', 'year': 2022, 'category': 'SUV', 'price_per_day': 1200,
     'seats': 5, 'doors': 5, 'transmission': 'automatic', 'fuel': 'diesel', 'mileage': 25000,
     'description': 'SUV premium spacieux et polyvalent. Parfait pour les familles et les longs trajets.',
     'features': 'GPS, Climatisation, 4x4, Toit panoramique, Bluetooth, Caméra 360°'},
    {'brand': 'Porsche', 'model': 'Cayenne', 'year': 2023, 'category': 'SUV', 'price_per_day': 1800,
     'seats': 5, 'doors': 5, 'transmission': 'automatic', 'fuel': 'hybrid', 'mileage': 8000,
     'description': 'Le SUV sportif par excellence. Performances exceptionnelles et luxe absolu.',
     'features': 'GPS, Climatisation 4 zones, Sport Chrono, Toit panoramique, Sièges massants'},
    {'brand': 'Renault', 'model': 'Clio', 'year': 2022, 'category': 'Citadine', 'price_per_day': 350,
     'seats': 5, 'doors': 5, 'transmission': 'manual', 'fuel': 'essence', 'mileage': 30000,
     'description': 'Citadine économique et maniable. Idéale pour les déplacements en ville au Maroc.',
     'features': 'Climatisation, Bluetooth, Régulateur de vitesse'},
    {'brand': 'Tesla', 'model': 'Model 3', 'year': 2023, 'category': 'Berline', 'price_per_day': 1300,
     'seats': 5, 'doors': 4, 'transmission': 'automatic', 'fuel': 'electric', 'mileage': 10000,
     'description': 'La berline électrique la plus avancée. Autonomie 500km, recharge rapide.',
     'features': 'Autopilot, Écran tactile 15", Climatisation, Supercharge, Caméras 360°'},
    {'brand': 'Volkswagen', 'model': 'Golf', 'year': 2022, 'category': 'Citadine', 'price_per_day': 450,
     'seats': 5, 'doors': 5, 'transmission': 'automatic', 'fuel': 'diesel', 'mileage': 22000,
     'description': 'La référence des compactes. Fiable, économique et confortable.',
     'features': 'GPS, Climatisation, Bluetooth, Régulateur adaptatif'},
    {'brand': 'Ferrari', 'model': '488 Spider', 'year': 2021, 'category': 'Sportive', 'price_per_day': 4500,
     'seats': 2, 'doors': 2, 'transmission': 'automatic', 'fuel': 'essence', 'mileage': 5000,
     'description': 'L\'expérience ultime. 670 chevaux de pur plaisir de conduite.',
     'features': 'Toit rétractable, Mode Sport, Sièges baquet, Système audio premium'},
]

for data in cars_data:
    if not Car.objects.filter(brand=data['brand'], model=data['model']).exists():
        car = Car.objects.create(
            brand=data['brand'], model=data['model'], year=data['year'],
            category=cats[data['category']], price_per_day=data['price_per_day'],
            seats=data['seats'], doors=data['doors'], transmission=data['transmission'],
            fuel=data['fuel'], mileage=data['mileage'], description=data['description'],
            features=data['features'], is_available=True
        )
        print(f"  🚗 {car}")

print("✅ Voitures créées")

# Réservations de démo
if Reservation.objects.count() == 0:
    cars = list(Car.objects.all()[:4])
    reservations_data = [
        {'client_name': 'Jean Dupont', 'client_email': 'jean.dupont@email.fr', 'client_phone': '+33 6 12 34 56 78',
         'car': cars[0], 'start_date': date.today() + timedelta(days=2), 'end_date': date.today() + timedelta(days=5),
         'status': 'confirmed'},
        {'client_name': 'Marie Martin', 'client_email': 'marie.martin@email.fr', 'client_phone': '+33 6 98 76 54 32',
         'car': cars[1], 'start_date': date.today() + timedelta(days=7), 'end_date': date.today() + timedelta(days=10),
         'status': 'pending'},
        {'client_name': 'Pierre Bernard', 'client_email': 'pierre.b@email.fr', 'client_phone': '+33 6 55 44 33 22',
         'car': cars[2] if len(cars) > 2 else cars[0],
         'start_date': date.today() - timedelta(days=10), 'end_date': date.today() - timedelta(days=7),
         'status': 'completed'},
    ]
    for r in reservations_data:
        res = Reservation(**r)
        res.save()
        print(f"  📅 Réservation #{res.pk} - {res.client_name}")
    print("✅ Réservations de démo créées")

print("\n🎉 Données de démo chargées avec succès!")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🌐 Site client  : http://127.0.0.1:8000/")
print("🔐 Admin panel  : http://127.0.0.1:8000/admin-panel/login/")
print("👤 Login        : admin / admin123")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
