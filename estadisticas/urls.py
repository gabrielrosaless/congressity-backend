from django.urls import path
from .views import *

urlpatterns = [
    path('devolverTopEvaluadores/', devolverTopEvaluadores, name="devolverTopEvaluadores"),
    path('devolverTopSimposiosXCongreso/',devolverTopSimposiosXCongreso, name="devolverTopSimposiosXCongreso"),
    path('devolverTopSimposiosGeneral/',devolverTopSimposiosGeneral,name="devolverTopSimposiosGeneral"),
    path('devolverTopSimposiosXEvaluadores/',devolverTopSimposiosXEvaluadores,name="devolverTopSimposiosXEvaluadores"),
    path('devolverEdadesXCongreso/',devolverEdadesXCongreso,name="devolverEdadesXCongreso"),
    path('devolverParticipantesXSede/', devolverParticipantesXSede, name="devolverParticipantesXSede"),
    path('devolverEvaluadoresCancelacionesCongreso/', devolverEvaluadoresCancelacionesCongreso, name="devolverEvaluadoresCancelacionesCongreso"),
    path('devolverEvaluadoresCancelacionesGeneral/', devolverEvaluadoresCancelacionesGeneral, name="devolverEvaluadoresCancelacionesGeneral"),
    path('devolverEstadosArticulos/', devolverEstadosArticulos, name="devolverEstadosArticulos"),
    path('devolverTopEventos/', devolverTopEventos, name="devolverTopEventos"),
    path('devolverPromedioItemsEvaluacion/', devolverPromedioItemsEvaluacion, name="devolverPromedioItemsEvaluacion"),
    path('devolverReporteEventos/', devolverReporteEventos, name="devolverReporteEventos"),
    path('devolverTopEvaluadoresCongreso/', devolverTopEvaluadoresCongreso, name="devolverTopEvaluadoresCongreso"),
    path('devolverSimposiosCalificaciones/', devolverSimposiosCalificaciones, name="devolverSimposiosCalificaciones"),
    path('devolverReporteEvaluadores/', devolverReporteEvaluadores, name="devolverReporteEvaluadores"),
    path('devolverReporteExpositores/', devolverReporteExpositores, name="devolverReporteExpositores"),
    path('devolverReporteArticulos/', devolverReporteArticulos, name="devolverReporteArticulos"),
    path('devolverReporteAsistentes/', devolverReporteAsistentes, name="devolverReporteAsistentes"),

]
