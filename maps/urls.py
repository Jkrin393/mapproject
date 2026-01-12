from django.urls import path
from .views import MapListView, DetailedMapView

app_name='maps'
url_patterns=[
    path('', MapListView.as_view(), name='map-list'),
    path('<int:pk>/', DetailedMapView.as_view(), name='map-detail'),
]

