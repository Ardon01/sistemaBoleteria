
from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    path('', views.lista_eventos, name='lista'),
    path('detalle/<int:evento_id>/', views.detalle_evento, name='detalle'),
    path('crear/', views.crear_evento, name='crear'),
    path('editar/<int:evento_id>/', views.editar_evento, name='editar'),
    path('eliminar/<int:evento_id>/', views.eliminar_evento, name='eliminar'),
]
