
from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('procesar/<int:evento_id>/<int:categoria_id>/<int:cantidad>/', views.procesar_pago, name='procesar'),
    path('confirmacion/<int:compra_id>/', views.confirmacion_pago, name='confirmacion'),
]
