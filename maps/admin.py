from django.contrib import admin
from .models import Map, Collection, Tag
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here. Allows for editing in the web UI

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

@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display=['title','map_date','collection','tag_list','price']
    list_filter=['collection','tags__category']
    search_fields=['title','description']
    filter_horizontal=['tags']

    #fieldsets useful for organzing admin form
    fieldsets=(
        ('Simpe Map Info', {
            'fields':(
            'title',
            'description',
            'image')
        }),
        ('Detailed Info', {
            'fields':(
            'map_date',
            'price',
            'collection',
            'tags')
        }),
    )

    def tag_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()[:3]])
    tag_list.short_description='Tags'