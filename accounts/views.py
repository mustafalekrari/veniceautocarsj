from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
import json

from cars.models import Car, CarCategory
from reservations.models import Reservation
from .models import UserProfile


# ─── HELPERS ────────────────────────────────────────────────────────────────

def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    try:
        return user.profile.role == 'admin'
    except UserProfile.DoesNotExist:
        return False


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'admin' if (user.is_staff or user.is_superuser) else 'client'}
    )
    return profile


# ─── AUTH : INSCRIPTION / CONNEXION ─────────────────────────────────────────

def register_view(request):
    """Inscription client"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        cin = request.POST.get('cin', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validations
        if not all([first_name, last_name, email, password1]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'auth/register.html', {'cities': MOROCCAN_CITIES})

        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'auth/register.html', {'cities': MOROCCAN_CITIES})

        if len(password1) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
            return render(request, 'auth/register.html', {'cities': MOROCCAN_CITIES})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Un compte avec cet email existe déjà.')
            return render(request, 'auth/register.html', {'cities': MOROCCAN_CITIES})

        # Création utilisateur
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )
        profile = get_or_create_profile(user)
        profile.role = 'client'
        profile.phone = phone
        profile.city = city
        profile.cin = cin
        profile.save()

        login(request, user)
        messages.success(request, f'Bienvenue {first_name} ! Votre compte a été créé avec succès.')
        return redirect('home')

    return render(request, 'auth/register.html', {'cities': MOROCCAN_CITIES})


def login_view(request):
    """Connexion unifiée — redirige selon le rôle"""
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '')

        # Chercher par email ou username
        user = None
        if '@' in email_or_username:
            try:
                u = User.objects.get(email=email_or_username)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(request, username=email_or_username, password=password)

        if user:
            login(request, user)
            get_or_create_profile(user)
            if is_admin(user):
                messages.success(request, f'Bienvenue {user.first_name or user.username} !')
                return redirect(next_url or 'admin_dashboard')
            else:
                messages.success(request, f'Bienvenue {user.first_name or user.username} !')
                return redirect(next_url or 'home')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')

    next_url = request.GET.get('next', '')
    return render(request, 'auth/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('home')


# ─── ESPACE CLIENT ──────────────────────────────────────────────────────────

@login_required
def client_dashboard(request):
    """Tableau de bord du client connecté"""
    profile = get_or_create_profile(request.user)
    if is_admin(request.user):
        return redirect('admin_dashboard')

    my_reservations = Reservation.objects.filter(
        client_email=request.user.email
    ).select_related('car').order_by('-created_at')

    total_spent = my_reservations.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    context = {
        'profile': profile,
        'my_reservations': my_reservations,
        'total_spent': total_spent,
        'pending_count': my_reservations.filter(status='pending').count(),
        'confirmed_count': my_reservations.filter(status='confirmed').count(),
        'completed_count': my_reservations.filter(status='completed').count(),
    }
    return render(request, 'auth/client_dashboard.html', context)


@login_required
def profile_edit(request):
    """Modifier son profil"""
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        profile.phone = request.POST.get('phone', profile.phone)
        profile.city = request.POST.get('city', profile.city)
        profile.address = request.POST.get('address', profile.address)
        profile.cin = request.POST.get('cin', profile.cin)
        profile.save()
        messages.success(request, 'Profil mis à jour avec succès.')
        return redirect('client_dashboard')
    return render(request, 'auth/profile_edit.html', {'profile': profile, 'cities': MOROCCAN_CITIES})


# ─── ADMIN DASHBOARD ────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(is_available=True).count()
    total_reservations = Reservation.objects.count()
    pending_reservations = Reservation.objects.filter(status='pending').count()
    confirmed_reservations = Reservation.objects.filter(status='confirmed').count()

    total_revenue = Reservation.objects.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    monthly_revenue = Reservation.objects.filter(
        status__in=['confirmed', 'completed'],
        created_at__gte=month_start
    ).aggregate(total=Sum('total_price'))['total'] or 0

    recent_reservations = Reservation.objects.select_related('car').order_by('-created_at')[:8]

    top_cars = Car.objects.annotate(
        reservation_count=Count('reservations')
    ).order_by('-reservation_count')[:5]

    six_months_ago = today - timedelta(days=180)
    monthly_data = Reservation.objects.filter(
        created_at__gte=six_months_ago,
        status__in=['confirmed', 'completed']
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        revenue=Sum('total_price'),
        count=Count('id')
    ).order_by('month')

    chart_labels = [d['month'].strftime('%b %Y') for d in monthly_data]
    chart_revenue = [float(d['revenue']) for d in monthly_data]
    chart_counts = [d['count'] for d in monthly_data]

    # Nombre de clients enregistrés
    total_clients = UserProfile.objects.filter(role='client').count()

    # Reçus de paiement en attente de vérification
    from reservations.models import Reservation as Res
    receipts_list = Res.objects.filter(
        status='payment_submitted'
    ).select_related('car').order_by('-payment_submitted_at')
    receipts_pending = receipts_list.count()

    context = {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_reservations': recent_reservations,
        'top_cars': top_cars,
        'total_clients': total_clients,
        'receipts_pending': receipts_pending,
        'receipts_list': receipts_list[:5],
        'chart_labels': json.dumps(chart_labels),
        'chart_revenue': json.dumps(chart_revenue),
        'chart_counts': json.dumps(chart_counts),
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ─── GESTION VOITURES ───────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def car_list_admin(request):
    cars = Car.objects.select_related('category').all()
    return render(request, 'admin_panel/cars/list.html', {'cars': cars})


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def car_create(request):
    categories = CarCategory.objects.all()
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category')
            car = Car(
                brand=request.POST['brand'],
                model=request.POST['model'],
                year=int(request.POST['year']),
                price_per_day=request.POST['price_per_day'],
                seats=int(request.POST.get('seats', 5)),
                doors=int(request.POST.get('doors', 4)),
                transmission=request.POST.get('transmission', 'manual'),
                fuel=request.POST.get('fuel', 'essence'),
                mileage=int(request.POST.get('mileage', 0)),
                description=request.POST.get('description', ''),
                features=request.POST.get('features', ''),
                is_available=request.POST.get('is_available') == 'on',
            )
            if category_id:
                car.category_id = int(category_id)
            if 'image' in request.FILES:
                car.image = request.FILES['image']
            car.save()
            messages.success(request, f'Voiture {car.brand} {car.model} ajoutée avec succès.')
            return redirect('admin_car_list')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
    return render(request, 'admin_panel/cars/form.html', {'categories': categories, 'action': 'Ajouter'})


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def car_edit(request, pk):
    car = get_object_or_404(Car, pk=pk)
    categories = CarCategory.objects.all()
    if request.method == 'POST':
        try:
            car.brand = request.POST['brand']
            car.model = request.POST['model']
            car.year = int(request.POST['year'])
            car.price_per_day = request.POST['price_per_day']
            car.seats = int(request.POST.get('seats', 5))
            car.doors = int(request.POST.get('doors', 4))
            car.transmission = request.POST.get('transmission', 'manual')
            car.fuel = request.POST.get('fuel', 'essence')
            car.mileage = int(request.POST.get('mileage', 0))
            car.description = request.POST.get('description', '')
            car.features = request.POST.get('features', '')
            car.is_available = request.POST.get('is_available') == 'on'
            category_id = request.POST.get('category')
            car.category_id = int(category_id) if category_id else None
            if 'image' in request.FILES:
                car.image = request.FILES['image']
            car.save()
            messages.success(request, 'Voiture mise à jour avec succès.')
            return redirect('admin_car_list')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
    return render(request, 'admin_panel/cars/form.html', {
        'car': car, 'categories': categories, 'action': 'Modifier'
    })


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        name = str(car)
        car.delete()
        messages.success(request, f'{name} supprimée avec succès.')
        return redirect('admin_car_list')
    return render(request, 'admin_panel/cars/confirm_delete.html', {'car': car})


# ─── GESTION RÉSERVATIONS ───────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def reservation_list_admin(request):
    status_filter  = request.GET.get('status', '')
    payment_filter = request.GET.get('payment', '')
    reservations = Reservation.objects.select_related('car').all()

    if status_filter:
        reservations = reservations.filter(status=status_filter)
    if payment_filter == 'receipt':
        reservations = reservations.exclude(payment_receipt='').exclude(payment_receipt=None)
    elif payment_filter:
        reservations = reservations.filter(payment_method=payment_filter)

    return render(request, 'admin_panel/reservations/list.html', {
        'reservations': reservations,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'status_choices': Reservation.STATUS_CHOICES,
    })


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def reservation_detail_admin(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Reservation.STATUS_CHOICES):
            old_status = reservation.status
            reservation.status = new_status

            # Quand l'admin confirme → calculer la deadline de paiement (2 jours ouvrables)
            if new_status in ['confirmed', 'awaiting_payment'] and old_status == 'pending':
                if reservation.payment_method != 'livraison':
                    from datetime import timedelta
                    from django.utils import timezone
                    deadline = timezone.now()
                    days_added = 0
                    while days_added < 2:
                        deadline += timedelta(days=1)
                        if deadline.weekday() < 5:
                            days_added += 1
                    reservation.payment_deadline = deadline

            reservation.save()
            messages.success(request, 'Statut mis à jour.')
    return render(request, 'admin_panel/reservations/detail.html', {'reservation': reservation})


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def reservation_delete_admin(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Réservation supprimée.')
        return redirect('admin_reservation_list')
    return render(request, 'admin_panel/reservations/confirm_delete.html', {'reservation': reservation})


# ─── GESTION CLIENTS (ADMIN) ────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def client_list(request):
    clients = Reservation.objects.values(
        'client_name', 'client_email', 'client_phone'
    ).annotate(
        total_reservations=Count('id'),
        total_spent=Sum('total_price')
    ).order_by('-total_reservations')
    return render(request, 'admin_panel/clients/list.html', {'clients': clients})


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def client_history(request, email):
    reservations = Reservation.objects.filter(
        client_email=email
    ).select_related('car').order_by('-created_at')
    client_name = reservations.first().client_name if reservations.exists() else email
    total_spent = reservations.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    return render(request, 'admin_panel/clients/history.html', {
        'reservations': reservations,
        'client_name': client_name,
        'client_email': email,
        'total_spent': total_spent,
    })


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def admin_download_receipt(request, pk):
    from django.http import HttpResponse
    from reservations.pdf_utils import generate_receipt_pdf
    reservation = get_object_or_404(Reservation, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_{pk}.pdf"'
    generate_receipt_pdf(response, reservation)
    return response


# ─── GESTION UTILISATEURS (ADMIN) ───────────────────────────────────────────

@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def user_list_admin(request):
    """Liste de tous les utilisateurs avec leurs rôles"""
    profiles = UserProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'admin_panel/users/list.html', {'profiles': profiles})


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def user_toggle_role(request, pk):
    """Changer le rôle d'un utilisateur"""
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['admin', 'client']:
            profile.role = new_role
            profile.user.is_staff = (new_role == 'admin')
            profile.user.save()
            profile.save()
            messages.success(request, f'Rôle de {profile.user.username} mis à jour.')
    return redirect('admin_user_list')


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def user_delete_admin(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        if profile.user != request.user:
            profile.user.delete()
            messages.success(request, 'Utilisateur supprimé.')
        else:
            messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
    return redirect('admin_user_list')


# ─── DONNÉES MAROC ──────────────────────────────────────────────────────────

MOROCCAN_CITIES = [
    'Casablanca', 'Rabat', 'Marrakech', 'Fès', 'Tanger', 'Agadir',
    'Meknès', 'Oujda', 'Kénitra', 'Tétouan', 'Safi', 'El Jadida',
    'Béni Mellal', 'Nador', 'Mohammedia', 'Laâyoune', 'Khouribga',
    'Settat', 'Berrechid', 'Khémisset', 'Taza', 'Essaouira', 'Dakhla'
]


# ─── GESTION PAIEMENTS (ADMIN) ──────────────────────────────────────────────

@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def payment_methods_admin(request):
    """Gérer les méthodes de paiement"""
    from reservations.models import PaymentMethod
    methods = PaymentMethod.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            method_type = request.POST.get('method_type')
            if method_type and not PaymentMethod.objects.filter(method_type=method_type).exists():
                PaymentMethod.objects.create(
                    method_type=method_type,
                    instructions=request.POST.get('instructions', ''),
                    bank_name=request.POST.get('bank_name', ''),
                    account_number=request.POST.get('account_number', ''),
                    account_name=request.POST.get('account_name', ''),
                    is_active=request.POST.get('is_active') == 'on',
                )
                messages.success(request, 'Méthode de paiement ajoutée.')
            else:
                messages.error(request, 'Cette méthode existe déjà.')

        elif action == 'update':
            pk = request.POST.get('pk')
            pm = get_object_or_404(PaymentMethod, pk=pk)
            pm.instructions = request.POST.get('instructions', '')
            pm.bank_name = request.POST.get('bank_name', '')
            pm.account_number = request.POST.get('account_number', '')
            pm.account_name = request.POST.get('account_name', '')
            pm.is_active = request.POST.get('is_active') == 'on'
            pm.save()
            messages.success(request, 'Méthode mise à jour.')

        elif action == 'delete':
            pk = request.POST.get('pk')
            PaymentMethod.objects.filter(pk=pk).delete()
            messages.success(request, 'Méthode supprimée.')

        return redirect('admin_payment_methods')

    return render(request, 'admin_panel/payments/methods.html', {'methods': methods})


@login_required
@user_passes_test(is_admin, login_url='/auth/connexion/')
def verify_payment(request, pk):
    """Vérifier/rejeter un reçu de paiement"""
    from reservations.models import Reservation
    reservation = get_object_or_404(Reservation, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            reservation.status = 'payment_verified'
            reservation.save()
            messages.success(request, f'Paiement de la réservation #{pk} vérifié.')
        elif action == 'reject':
            reservation.status = 'awaiting_payment'
            reservation.payment_receipt = None
            reservation.payment_submitted_at = None
            reservation.save()
            messages.warning(request, f'Reçu rejeté. Le client doit soumettre un nouveau reçu.')
        return redirect('admin_reservation_detail', pk=pk)

    return redirect('admin_reservation_detail', pk=pk)
