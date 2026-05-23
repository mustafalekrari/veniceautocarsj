import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from cars.models import Car
from .models import Reservation, PaymentMethod
from .pdf_utils import generate_receipt_pdf


def get_reserved_dates(car, exclude_pk=None):
    """Retourne la liste des dates déjà réservées pour une voiture (JSON)"""
    qs = Reservation.objects.filter(
        car=car,
        status__in=['pending', 'confirmed', 'awaiting_payment',
                    'payment_submitted', 'payment_verified', 'active']
    )
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    reserved = []
    for res in qs:
        current = res.start_date
        while current <= res.end_date:
            reserved.append(current.strftime('%Y-%m-%d'))
            from datetime import timedelta
            current += timedelta(days=1)
    return list(set(reserved))


def reservation_create(request, car_id):
    """Formulaire de réservation avec calendrier et carte"""
    car = get_object_or_404(Car, pk=car_id, is_available=True)
    reserved_dates = get_reserved_dates(car)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    today = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        # Récupération des données
        client_name = request.POST.get('client_name', '').strip()
        client_email = request.POST.get('client_email', '').strip()
        client_phone = request.POST.get('client_phone', '').strip()
        client_address = request.POST.get('client_address', '').strip()
        client_license = request.POST.get('client_license', '').strip()
        start_date_str = request.POST.get('start_date', '')
        end_date_str = request.POST.get('end_date', '')
        pickup_location = request.POST.get('pickup_location', '').strip()
        pickup_lat = request.POST.get('pickup_lat', '')
        pickup_lng = request.POST.get('pickup_lng', '')
        return_location = request.POST.get('return_location', '').strip()
        return_lat = request.POST.get('return_lat', '')
        return_lng = request.POST.get('return_lng', '')
        payment_method = request.POST.get('payment_method', '')
        notes = request.POST.get('notes', '').strip()

        errors = []
        if not all([client_name, client_email, client_phone, start_date_str, end_date_str]):
            errors.append('Veuillez remplir tous les champs obligatoires.')

        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if end_date <= start_date:
                errors.append('La date de fin doit être après la date de début.')
            if start_date < date.today():
                errors.append('La date de début ne peut pas être dans le passé.')
            # Vérifier chevauchement
            for d in get_reserved_dates(car):
                from datetime import datetime as dt
                d_obj = dt.strptime(d, '%Y-%m-%d').date()
                if start_date <= d_obj <= end_date:
                    errors.append('Ces dates chevauchent une réservation existante.')
                    break
        except ValueError:
            errors.append('Format de date invalide.')

        if not payment_method:
            errors.append('Veuillez choisir une méthode de paiement.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            reservation = Reservation(
                client_name=client_name,
                client_email=client_email,
                client_phone=client_phone,
                client_address=client_address,
                client_license=client_license,
                car=car,
                start_date=start_date,
                end_date=end_date,
                pickup_location=pickup_location or 'Agence Venice Autocars - Hay Azhar Bernoussi, Casablanca',
                return_location=return_location or 'Agence Venice Autocars - Hay Azhar Bernoussi, Casablanca',
                payment_method=payment_method,
                notes=notes,
                status='pending',
            )
            if request.user.is_authenticated:
                reservation.user = request.user
            try:
                reservation.pickup_lat = float(pickup_lat) if pickup_lat else None
                reservation.pickup_lng = float(pickup_lng) if pickup_lng else None
                reservation.return_lat = float(return_lat) if return_lat else None
                reservation.return_lng = float(return_lng) if return_lng else None
            except ValueError:
                pass
            reservation.save()
            messages.success(request, f'Réservation #{reservation.pk} créée ! En attente de confirmation admin.')
            return redirect('reservation_success', pk=reservation.pk)

    context = {
        'car': car,
        'reserved_dates_json': json.dumps(reserved_dates),
        'today': today,
        'payment_methods': payment_methods,
    }
    # Pré-remplir si connecté
    if request.user.is_authenticated:
        try:
            context['user_profile'] = request.user.profile
        except Exception:
            pass
    return render(request, 'reservations/reservation_form.html', context)


def reservation_success(request, pk):
    """Page de confirmation après réservation"""
    from datetime import timedelta
    from django.utils import timezone

    reservation = get_object_or_404(Reservation, pk=pk)
    payment_method_obj = None
    if reservation.payment_method:
        try:
            payment_method_obj = PaymentMethod.objects.get(method_type=reservation.payment_method)
        except PaymentMethod.DoesNotExist:
            pass

    # Calcul date limite paiement (2 jours ouvrables = skip sam/dim)
    payment_deadline = None
    deadline_hours = None
    if reservation.payment_deadline:
        payment_deadline = reservation.payment_deadline.strftime('%d/%m/%Y à %H:%M')
        remaining = reservation.payment_deadline - timezone.now()
        if remaining.total_seconds() > 0:
            deadline_hours = int(remaining.total_seconds() // 3600)
        else:
            deadline_hours = 0
    elif reservation.status in ['confirmed', 'awaiting_payment'] and reservation.payment_method != 'livraison':
        # Calculer 2 jours ouvrables depuis maintenant
        deadline = timezone.now()
        days_added = 0
        while days_added < 2:
            deadline += timedelta(days=1)
            if deadline.weekday() < 5:  # Lundi=0 ... Vendredi=4
                days_added += 1
        payment_deadline = deadline.strftime('%d/%m/%Y à %H:%M')
        remaining = deadline - timezone.now()
        deadline_hours = int(remaining.total_seconds() // 3600)

    return render(request, 'reservations/reservation_success.html', {
        'reservation': reservation,
        'payment_method_obj': payment_method_obj,
        'payment_deadline': payment_deadline,
        'deadline_hours': deadline_hours,
    })

@login_required
def submit_payment(request, pk):
    """Le client soumet son reçu de paiement"""
    reservation = get_object_or_404(Reservation, pk=pk)

    # Vérifier que c'est bien la réservation du client connecté
    if reservation.user != request.user and reservation.client_email != request.user.email:
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')

    if reservation.status not in ['confirmed', 'awaiting_payment']:
        messages.error(request, 'Cette réservation ne peut pas recevoir de paiement pour le moment.')
        return redirect('reservation_success', pk=pk)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', reservation.payment_method)
        payment_notes = request.POST.get('payment_notes', '')

        if reservation.payment_method == 'livraison':
            # Paiement à la livraison : pas de reçu requis
            reservation.payment_method = 'livraison'
            reservation.payment_notes = payment_notes
            reservation.status = 'payment_submitted'
            reservation.payment_submitted_at = timezone.now()
            reservation.save()
            messages.success(request, 'Paiement à la livraison confirmé. Votre réservation est en cours de traitement.')
            return redirect('reservation_success', pk=pk)

        if 'payment_receipt' not in request.FILES:
            messages.error(request, 'Veuillez joindre votre reçu de paiement.')
            return redirect('submit_payment', pk=pk)

        reservation.payment_receipt = request.FILES['payment_receipt']
        reservation.payment_method = payment_method
        reservation.payment_notes = payment_notes
        reservation.status = 'payment_submitted'
        reservation.payment_submitted_at = timezone.now()
        reservation.save()
        messages.success(request, 'Reçu de paiement soumis avec succès ! L\'admin va vérifier votre paiement.')
        return redirect('reservation_success', pk=pk)

    payment_method_obj = None
    if reservation.payment_method:
        try:
            payment_method_obj = PaymentMethod.objects.get(method_type=reservation.payment_method)
        except PaymentMethod.DoesNotExist:
            pass

    return render(request, 'reservations/submit_payment.html', {
        'reservation': reservation,
        'payment_method_obj': payment_method_obj,
    })


def download_receipt(request, pk):
    """Télécharger le reçu PDF"""
    reservation = get_object_or_404(Reservation, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_reservation_{pk}.pdf"'
    generate_receipt_pdf(response, reservation)
    return response


def api_reserved_dates(request, car_id):
    """API JSON : dates réservées pour une voiture"""
    car = get_object_or_404(Car, pk=car_id)
    return JsonResponse({'reserved_dates': get_reserved_dates(car)})
