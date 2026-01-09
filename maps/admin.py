from django.contrib import admin
from .models import Map, Collection, Tag
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here. 
###Allows for editing in the web UI
###reference regarding inner Meta "classes" "https://docs.djangoproject.com/en/5.2/ref/models/options/"
    #abstract class for specifying how Django should handle the returned data, similar to a "Settings" menu.
    #allows for shorter syntax [Map.objects.all().order_by('-upload_date') can be shortened to Map.obects.all() with predefined ordering.

###map admin modules
class MapResource(resources.ModelResource):
    class Meta:
        model=Map
        skip_unchanged=True
        report_skipped=True
        fields=(
            'external_map_id',
            'map_maker',
            'map_year', 
            'map_height',
            'map_width',
            'map_title', 
            'description',
            'map_price',
            'map_info_memo',
            'planned_use',
        )


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    resource_class=MapResource
    list_display=[
        'map_title',
        'map_maker',
        'map_year', 
        'display_sorting_year', 
        'collection', 
        'tag_list',
        #year_is_estimated_or_range
    ]
    list_filter=['collection', 'tags__category', 'planned_use']
    search_fields=['map_title', 'description', 'map_maker', 'map_year']
    filter_horizontal=['tags']

    #fieldsets: for organzing admin form "https://stackoverflow.com/questions/1437991/django-admin-fieldsets"
    fieldsets=(
        ('Basic Information', {
            'fields': ('external_map_id', 'map_title', 'map_maker', 'map_year')
        }),
        ('Physical Details', {
            'fields': ('map_height', 'map_width', 'image')
        }),
        ('Description', {
            'fields': ('description', 'map_info_memo')
        }),
        ('Business Details', {
            'fields': ('map_price', 'planned_use')
        }),
        ('Organization', {
            'fields': ('collection', 'tags')
        }),
    )

    def display_sorting_year(self, obj):
        year = obj.get_sort_year()
        return year if year else '----'
    ##short_desc and admin_order_field are admin specific attributes recognized by django-admin. specifies how to sort and column name
    display_sorting_year.short_description='Sorting Year'
    display_sorting_year.admin_order_field='map_year'

    def tag_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()[:3]])
    tag_list.short_description='Tags'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display=['name','category']
    list_filter=['category']
    search_fields=['name']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display=['name','map_count']
    search_fields=['name','description']
    

    def map_count(self,obj):
        return obj.maps.count()
    map_count.short_description='Number of Maps'





