from django.conf.urls.static import static
from django.conf import settings
from django.urls import path


from .views import *


urlpatterns = [
    path('crear-evento/', crearEvento, name="crear-evento"),
    path('consultar-eventosXAula/', getEventos, name="consultar-eventosXAula"),
    path('consultar-evento/', getEvento, name="consultar-evento"),
    path('eliminar-evento/', eliminarEvento, name="eliminar-evento"),
    path('lista-eventos/', getEventosPorDia, name="lista-eventos")
]
