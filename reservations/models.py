from django.db import models
from django.contrib.auth.models import User
from cars.models import Car


class PaymentMethod(models.Model):
    """Méthodes de paiement configurées par l'admin"""
    METHOD_CHOICES = [
        ('virement', 'Virement bancaire'),
        ('versement', 'Versement bancaire (dépôt agence)'),
        ('livraison', 'Paiement à la livraison'),
    ]
    method_type = models.CharField(max_length=20, choices=METHOD_CHOICES, unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Activée")
    instructions = models.TextField(verbose_name="Instructions pour le client")
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="Nom de la banque")
    account_number = models.CharField(max_length=100, blank=True, verbose_name="N° de compte / RIB")
    account_name = models.CharField(max_length=100, blank=True, verbose_name="Titulaire du compte")

    def __str__(self):
        return self.get_method_type_display()

    class Meta:
        verbose_name = "Méthode de paiement"
        verbose_name_plural = "Méthodes de paiement"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('awaiting_payment', 'En attente de paiement'),
        ('payment_submitted', 'Reçu soumis'),
        ('payment_verified', 'Paiement vérifié'),
        ('active', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('virement', 'Virement bancaire'),
        ('versement', 'Versement bancaire'),
        ('livraison', 'Paiement à la livraison'),
    ]

    # Client info
    client_name = models.CharField(max_length=200, verbose_name="Nom complet")
    client_email = models.EmailField(verbose_name="Email")
    client_phone = models.CharField(max_length=20, verbose_name="Téléphone")
    client_address = models.TextField(blank=True, verbose_name="Adresse")
    client_license = models.CharField(max_length=50, blank=True, verbose_name="N° Permis")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')

    # Reservation details
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reservations')
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")

    # Locations avec coordonnées GPS
    pickup_location = models.CharField(max_length=300, default="Agence Venice Autocars - Hay Azhar Bernoussi, Casablanca")
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)
    return_location = models.CharField(max_length=300, default="Agence Venice Autocars - Hay Azhar Bernoussi, Casablanca")
    return_lat = models.FloatField(null=True, blank=True)
    return_lng = models.FloatField(null=True, blank=True)

    # Pricing
    total_days = models.IntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Paiement
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES,
        blank=True, verbose_name="Méthode de paiement"
    )
    payment_receipt = models.ImageField(
        upload_to='payment_receipts/', blank=True, null=True,
        verbose_name="Reçu de paiement"
    )
    payment_notes = models.TextField(blank=True, verbose_name="Notes de paiement")
    payment_submitted_at = models.DateTimeField(null=True, blank=True)
    payment_deadline = models.DateTimeField(null=True, blank=True, verbose_name="Date limite de paiement")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.total_days = delta.days if delta.days > 0 else 1
            self.total_price = self.total_days * self.car.price_per_day
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Réservation #{self.pk} - {self.client_name} - {self.car}"

    @property
    def is_paid(self):
        return self.status in ['payment_verified', 'active', 'completed']

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-created_at']
