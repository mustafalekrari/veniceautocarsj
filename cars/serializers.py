from rest_framework import serializers
from .models import Car, CarCategory


class CarCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CarCategory
        fields = '__all__'


class CarSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    features_list = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = '__all__'

    def get_features_list(self, obj):
        return obj.get_features_list()
