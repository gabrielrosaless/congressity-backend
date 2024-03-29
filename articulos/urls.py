from django.conf.urls.static import static
from django.conf import settings
from django.urls import path


from .views import *


urlpatterns = [
    path('editarEntrega/', editarEntrega, name="editarEntrega"),
    path('realizarEntrega/', realizarEntrega, name="realizarEntrega"),
    path('enviarEntrega/', enviarEntrega, name="enviarEntrega"),
    path('consultaArticuloXId/', consultaArticuloXId, name="consultaArticuloXId"),
    path('consultaArticuloXResponsable/', consultaArticuloXResponsable, name="consultaArticuloXResponsable"),
    path('consultaArticuloXAutor/', consultaArticuloXAutor, name="consultaArticuloXAutor"),
    path('rechazar-autoria/', rechazarAutoria, name="rechazar-autoria"),
    path('reentregarArticulo/', reentregarArticulo, name="reentregarArticulo"),
    path('consultarEstadoArticulos/', getEstadoArticulosAutor, name="consultarEstadoArticulos"),
    path('consultarArticulosXSimposio/', getArticulos, name="consultarArticulosXSimposio"),
    path('asignarRolEvaluador/', asignarRolEvaluador, name="asignarRolEvaluador"),
    path('aceptar-evaluador/', aceptarEvaluador, name="aceptar-evaluador"),
    path('rechazar-evaluador',rechazarEvaluador, name="rechazar-evaluador"),
    path('lista-evaluadores/', devolverEvaluadores, name="lista-evaluadores"),
    path('eliminarEvaluador/<int:id>', eliminarEvaluador, name="eliminarEvaluador"),
    path('consultarEvaluadores/', getEvaluadores, name="consultarEvaluadores"),
    path('consultarEvaluador/', getEvaluadorById, name="consultarEvaluador"),
    path('asignarSimposioEvaluador/', asignarSimposioEvaluador, name="asignarSimposioEvaluador"),
    path('asignarArticuloEvaluador/', asignarArticuloEvaluador, name="asignarArticuloEvaluador"),
    path('rechazar-evaluacion/', rechazarEvaluacion, name="rechazar-evaluacion"),
    path('aceptar-evaluacion/', aceptarEvaluacion, name="aceptar-evaluacion"),
    path('consulta-evaluaciones/', getEvaluacionesEvaluador, name="consulta-evaluaciones"),
    path('consulta-evaluacion/', getDetalleEvaluacion, name="consulta-evaluacion"),
    path('consulta-archivo/', getArchivoArticulo, name="consulta-archivo"),
    path('guardar-evaluacion/', guardarEvaluacion, name="guardar-evaluacion"),
    path('editar-evaluacion/', editarEvaluacion, name="editar-evaluacion"),
    path('enviar-evaluacion/', enviarEvaluacion, name="enviar-evaluacion"),
    path('consultarArticulosEvaluados/', getArticulosEvaluados, name="consultarArticulosEvaluados"),
    path('calificarArticulo/', calificarArticulo, name="calificarArticulo"),
    path('consultarAutoresArticulo/', listaAutoresXArticulo, name="consultarAutoresArticulo"),
    path('deleteEntregaArticulo/', deleteEntrega, name="deleteEntregaArticulo"),
    path('consultarEvaluadoresArticulo/', getEvaluadoresXArticulo, name="consultarEvaluadoresArticulo"),
    path('getItemsEvaluacion/', getItemsEvaluacion, name="getItemsEvaluacion"),
    path('getItemEvaluacion/', getItemEvaluacion, name="getItemEvaluacion"),
    path('eliminarItemEvaluacion/', eliminarItemEvaluacion, name="eliminarItemEvaluacion"),
    path('editarItemEvaluacion/', editarItemEvaluacion, name="editarItemEvaluacion"),
    path('altaItemEvaluacion/', altaItemEvaluacion, name="altaItemEvaluacion"),
    path('getEvaluadoresBySimposio/', getEvaluadoresBySimposio, name="getEvaluadoresBySimposio"),
    path('consultaDetalleEvaluacion/', getDetalleEvaluaciones, name="getDetalleEvaluaciones"),
    path('calificarEvaluador/', calificarEvaluador, name="calificarEvaluador"),
    path('getArticulosEvaluadoresCompleto/', getArticulosEvaluadoresCompleto, name="getArticulosEvaluadoresCompleto"),
    path('asignarArticuloEvaluadorMasivo/', asignarArticuloEvaluadorMasivo, name="asignarArticuloEvaluadorMasivo"),
    path('asignarPoolEvaluadores/', asignarPoolEvaluadores, name="asignarPoolEvaluadores"),
    path('eliminarEvaluadorPoolEvaluadores/', eliminarEvaluadorPoolEvaluadores, name="eliminarEvaluadorPoolEvaluadores"),
    path('getPoolEvaluadores/', getPoolEvaluadores, name="getPoolEvaluadores"),
    path('getEvaluadoresSimposio/', getEvaluadoresSimposio, name="getEvaluadoresSimposio"),
    path('getEvaluadoresFueraSimposio/', getEvaluadoresFueraSimposio, name="getEvaluadoresFueraSimposio"),
    path('consulta-articulosXChair/', getArticulosXChair, name="consulta-articulosXChair"),
    path('getEvaluacion/', getEvaluacion, name="getEvaluacion"),
    path('realizarEntregaFinal/', realizarEntregaFinal, name="realizarEntregaFinal"),
    path('getArchivoArticuloCameraReady/', getArchivoArticuloCameraReady, name="getArchivoArticuloCameraReady"),
    path('consultar-simposiosEvaluador/', getSimposiosxEvaluador, name="consultar-simposiosEvaluador"),
    path('eliminar-simposioEvaluador/', eliminarSimposioEvaluador, name="eliminar-simposioEvaluador"),
    path('lista-evaluadoresCongreso/', devolverEvaluadoresCongreso, name="lista-evaluadoresCongreso"),
    path('es-evaluador/', esEvaluador, name="es-evaluador"),
    path('consultarArticulosCameraReady/', getArticulosCameraReady, name="consultarArticulosCameraReady"),
    path('consultarArticulosCameraReadyPublico/', getArticulosCameraReadyPublico, name="consultarArticulosCameraReadyPublico"),
    path('consultarArticulosParaEventos/', getArticulosParaEventos, name="consultarArticulosParaEventos")
]
