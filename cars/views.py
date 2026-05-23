from django.shortcuts import render, get_object_or_404
from .models import Car, CarCategory


def home(request):
    """Page d'accueil avec voitures en vedette"""
    featured_cars = Car.objects.filter(is_available=True)[:6]
    categories = CarCategory.objects.all()
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(is_available=True).count()
    context = {
        'featured_cars': featured_cars,
        'categories': categories,
        'total_cars': total_cars,
        'available_cars': available_cars,
    }
    return render(request, 'home.html', context)


def car_list(request):
    """Liste de toutes les voitures avec filtres"""
    cars = Car.objects.all()
    categories = CarCategory.objects.all()

    # Filtres
    category_id = request.GET.get('category')
    available_only = request.GET.get('available')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search')

    if category_id:
        cars = cars.filter(category_id=category_id)
    if available_only:
        cars = cars.filter(is_available=True)
    if min_price:
        cars = cars.filter(price_per_day__gte=min_price)
    if max_price:
        cars = cars.filter(price_per_day__lte=max_price)
    if search:
        cars = cars.filter(brand__icontains=search) | cars.filter(model__icontains=search)

    context = {
        'cars': cars,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'cars/car_list.html', context)


def car_detail(request, pk):
    """Détail d'une voiture"""
    car = get_object_or_404(Car, pk=pk)
    similar_cars = Car.objects.filter(
        category=car.category, is_available=True
    ).exclude(pk=pk)[:3]
    context = {
        'car': car,
        'similar_cars': similar_cars,
    }
    return render(request, 'cars/car_detail.html', context)


def about(request):
    return render(request, 'about.html')


def contact(request):
    from django.contrib import messages
    if request.method == 'POST':
        messages.success(request, 'Votre message a été envoyé. Nous vous répondrons sous 24h.')
    return render(request, 'contact.html')
