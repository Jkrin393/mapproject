from django.views.generic import ListView, DetailView
from ..models import Map, Collection
from .filters import MapFilter

class MapListView(ListView):
    model=Map
    context_object_name='maps'
    paginate_by=20
    #template_name='maps/map_list.html'
    
    def get_queryset(self):#override of ListView get_queryset()
        all_maps=Map.objects.all()
        self.filtered_results=MapFilter(self.request.GET, queryset=all_maps)
        return self.filtered_results.qs

    def get_context_data(self, **kwargs):#override of ListView get_context_data()
        context=super().get_context_data(**kwargs)#call parent to get list of kwargs
        context['filtered_results']=self.filtered_results #add filtered_results to kwargs
        return context

class DetailedMapView(DetailView):
    model=Map
    context_object_name='map'