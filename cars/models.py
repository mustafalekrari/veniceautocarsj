from django.db import models


class CarCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"


class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('manual', 'Manuelle'),
        ('automatic', 'Automatique'),
    ]
    FUEL_CHOICES = [
        ('essence', 'Essence'),
        ('diesel', 'Diesel'),
        ('electric', 'Électrique'),
        ('hybrid', 'Hybride'),
    ]

    brand = models.CharField(max_length=100, verbose_name="Marque")
    model = models.CharField(max_length=100, verbose_name="Modèle")
    year = models.IntegerField(verbose_name="Année")
    category = models.ForeignKey(CarCategory, on_delete=models.SET_NULL, null=True, blank=True)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Prix/jour (DH)")
    seats = models.IntegerField(default=5, verbose_name="Places")
    doors = models.IntegerField(default=4, verbose_name="Portes")
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='manual')
    fuel = models.CharField(max_length=20, choices=FUEL_CHOICES, default='essence')
    mileage = models.IntegerField(default=0, verbose_name="Kilométrage")
    description = models.TextField(blank=True, verbose_name="Description")
    features = models.TextField(blank=True, verbose_name="Équipements (séparés par virgule)")
    image = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name="Image principale")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    def get_features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split(',')]
        return []

    class Meta:
        verbose_name = "Voiture"
        verbose_name_plural = "Voitures"
        ordering = ['-created_at']
