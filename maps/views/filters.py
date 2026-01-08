 #use django-filters to define get request behavior at endpoints

import django_filters
from ..models import Map, Collection, Tag

class MapFilter(django_filters.FilterSet):
    title=django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Title contains'
    )
    tags=django_filters.ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Tag.objects.all(),
        label='Tags'
    )
    collection=django_filters.ModelMultipleChoiceFilter(
        field_name='collection',
        queryset=Collection.objects.all(),
        label='Collection'
    )
