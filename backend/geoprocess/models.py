from django.db import models
from django.conf import settings

class GeoProcess(models.Model):
    STATUS_CHOICES = (
        ('En curso', 'En curso'),
        ('Error', 'Error'),
        ('Finalizado', 'Finalizado'),
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='En curso')
    bbox = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"GeoProcess - {self.get_status_display()} - {self.user}"


class Report(models.Model):
    geo_process = models.ForeignKey(GeoProcess, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='reports/')

    def __str__(self):
        return f"Report - {self.title}"

class Layer(models.Model):
    geo_process = models.ForeignKey(GeoProcess, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    type_layer = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return f"Layer - {self.title}"


class Metadata(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    layer = models.OneToOneField(Layer, on_delete=models.CASCADE)
    keywords = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=200, null=True, blank=True)
    attribution = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creation_date = models.DateField(null=True, blank=True)
    license = models.CharField(max_length=100, null=True, blank=True)
    resolution = models.CharField(max_length=50, null=True, blank=True)
    zoom = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Metadata - {self.title}"