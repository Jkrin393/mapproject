 #use django-filters to define get request behavior at endpoints

import django_filters
from ..models import Map

class MapFilter(django_filters.FilterSet):
    title=django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Title contains'
    )
    tags=django_filters.CharFilter(
        field_name='tags',
        queryset=Map.objects.all(),
        label='Tag'
    )
    collection=django_filters.CharFilter(
        field_name='collection',
        queryset=Map.objects.values_list('collection'),
        label='Collection'
    )
