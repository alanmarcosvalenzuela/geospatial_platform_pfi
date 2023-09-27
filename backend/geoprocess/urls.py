from django.urls import path
from . import views

urlpatterns = [
    path('reports/<str:email>/', views.UserReportsAPIView.as_view(), name='reports'),
    path('report-download/<int:report_id>/', views.ReportDownloadView.as_view(), name='report-download'),
    path('geoprocess-status/<int:geoprocess_id>/', views.GeoProcessStatusAPIView.as_view(), name='geoprocess-status'),
    path('process', views.Process.as_view(), name='process'),
]
