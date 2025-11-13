from django.urls import path
from . import views

app_name = 'boletos'

urlpatterns = [
    path('comprar/<int:evento_id>/', views.comprar_boleto, name='comprar'),
    path('mis-boletos/', views.mis_boletos, name='mis_boletos'),
    path('validar/', views.validar_boleto, name='validar'),
]
