from django.contrib import admin
from .models import GeoProcess, Report, Layer, Metadata

class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'geo_process', 'created_at', 'last_modified')
    search_fields = ['title', 'description']

class LayerAdmin(admin.ModelAdmin):
    list_display = ('title', 'geo_process', 'type_layer', 'created_at', 'last_modified')
    list_filter = ['geo_process', 'type_layer']
    search_fields = ['title', 'description']

class MetadataAdmin(admin.ModelAdmin):
    list_display = ('name', 'layer', 'created_by', 'creation_date')
    list_filter = ['layer__geo_process', 'created_by']
    search_fields = ['name', 'description', 'keywords', 'source', 'attribution']

admin.site.register(GeoProcess)
admin.site.register(Report, ReportAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(Metadata, MetadataAdmin)
