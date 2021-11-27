from django.conf.urls.static import static
from django.conf import settings
from django.urls import path


from .views import *


urlpatterns = [
    path('crear-evento/', crearEvento, name="crear-evento"),
    path('crear-breakCharla/', crearBreakCharla, name="crear-breakCharla"),
    path('consultar-eventosXAula/', getEventos, name="consultar-eventosXAula"),
    path('consultar-evento/', getEvento, name="consultar-evento"),
    path('eliminar-evento/', eliminarEvento, name="eliminar-evento"),
    path('lista-eventos/', getEventosPorDia, name="lista-eventos"),
    path('modificar-evento/', editarEvento, name="editar-evento"),
    path('getQrAulas/', getQrAulas, name="getQrAulas"),
    path('registarCalificacionEvento/', registarCalificacionEvento, name="registarCalificacionEvento"),
    path('proximo-evento/', getProximoEventoAula, name="proximo-evento"),
    path('devolverCalificacionEvento/', devolverCalificacionEvento, name="devolverCalificacionEvento"),
    path('modificar-breakCharla/', editarBreakCharla, name="editar-breakCharla")
]
