from rest_framework import serializers
from .models import Map, Collection, Tag

class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model=Map
        fields='__all__'