 #use django-filters to define get request behavior at endpoints

import django_filters
from ..models import Map, Collection, Tag

class MapFilter(django_filters.FilterSet):
    title=django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Title contains'
    )
    map_maker=django_filters.CharFilter(
        field_name='map_maker',
        lookup_expr='icontains',
        label='Map maker'
    )
    year_from = django_filters.NumberFilter(
        method='filter_year_from',
        label='Year from'
    )
    year_to = django_filters.NumberFilter(
        method='filter_year_to',
        label='Year to'
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
    ##need a function for filtering year range: filter maps with year <= value, >= value, and <=value<=value2

    class Meta:
        model = Map
        fields = ['title',
                  'map_maker',
                  'year_from',
                  'year_to',
                  'tags',
                  'collection',
                  ]
