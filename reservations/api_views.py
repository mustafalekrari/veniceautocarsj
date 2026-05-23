from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    car_name = serializers.CharField(source='car.__str__', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'


class ReservationListAPI(generics.ListAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ReservationDetailAPI(generics.RetrieveUpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
