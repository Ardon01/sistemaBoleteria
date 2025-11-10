"""
URLs principales del proyecto Sistema de Boletería de Eventos
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/eventos/', permanent=False)),
    path('usuarios/', include('usuarios.urls')),
    path('eventos/', include('eventos.urls')),
    path('boletos/', include('boletos.urls')),
    path('pagos/', include('pagos.urls')),
    path('reportes/', include('reportes.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
