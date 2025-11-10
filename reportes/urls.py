"""
URLs para el módulo de reportes
"""
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('historial/', views.historial_compras, name='historial'),
    path('ventas/', views.reporte_ventas, name='ventas'),
]
