from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('admin', 'Administrateur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    address = models.TextField(blank=True, verbose_name="Adresse")
    cin = models.CharField(max_length=20, blank=True, verbose_name="N° CIN")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff or self.user.is_superuser

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil à la création d'un utilisateur"""
    if created:
        role = 'admin' if (instance.is_staff or instance.is_superuser) else 'client'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
