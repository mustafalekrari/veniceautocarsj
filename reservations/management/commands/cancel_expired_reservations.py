"""
Commande Django : annule automatiquement les réservations dont la deadline
de paiement est dépassée (virement/versement uniquement).

Usage :
  python manage.py cancel_expired_reservations

Planifier avec cron (toutes les heures) :
  0 * * * * /path/to/python /path/to/manage.py cancel_expired_reservations
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from reservations.models import Reservation


class Command(BaseCommand):
    help = 'Annule les réservations dont le délai de paiement est dépassé'

    def handle(self, *args, **options):
        now = timezone.now()

        # Réservations confirmées, avec deadline dépassée, paiement non soumis
        expired = Reservation.objects.filter(
            status__in=['confirmed', 'awaiting_payment'],
            payment_deadline__lt=now,
            payment_method__in=['virement', 'versement'],
        )

        count = expired.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Aucune réservation expirée.'))
            return

        for res in expired:
            res.status = 'cancelled'
            res.notes = (res.notes or '') + (
                f'\n[AUTO] Annulée le {now.strftime("%d/%m/%Y %H:%M")} '
                f'— délai de paiement de 2 jours ouvrables dépassé.'
            )
            res.save()
            self.stdout.write(
                self.style.WARNING(f'  ❌ Réservation #{res.pk} ({res.client_name}) annulée.')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ {count} réservation(s) annulée(s) automatiquement.')
        )
