
from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('procesar/<int:evento_id>/<int:categoria_id>/<int:cantidad>/', views.procesar_pago, name='procesar'),
    path('procesar/<int:evento_id>/<int:cantidad>/', views.procesar_pago_sin_categoria, name='procesar_sin_categoria'),
    path('confirmacion/<int:compra_id>/', views.confirmacion_pago, name='confirmacion'),
]
