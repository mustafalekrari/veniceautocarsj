from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Car
from .serializers import CarSerializer


class CarListAPI(generics.ListAPIView):
    queryset = Car.objects.filter(is_available=True)
    serializer_class = CarSerializer
    permission_classes = [AllowAny]


class CarDetailAPI(generics.RetrieveAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [AllowAny]
