from django.urls import path
from .views import *

urlpatterns = [
    path('crear-tarifa/', crearTarifa, name="crear-tarifa"),
    path('editar-tarifa/', editarTarifa, name="editar-tarifa"),
    path('devolver-tarifas/', devolverTarifas, name="devolver-tarifas"),
    path('devolver-tarifas-activas/', devolverTarifasActivas, name="devolver-tarifas-activas"),
    path('eliminar-tarifa/', eliminarTarifa, name="eliminar-tarifa"),
    path('crear-cuponDescuento/', crearCuponDescuento, name="crear-cuponDescuento"),
    path('editar-cuponDescuento/', editarCuponDescuento, name="editar-cuponDescuento"),
    path('eliminar-cuponDescuento/', eliminarCuponDescuento, name="eliminar-cuponDescuento"),
    path('devolver-cuponDescuento/', getCuponDescuento, name="devolver-cuponDescuento"),
    path('lista-cuponesDescuento/', getCuponesDescuento, name="lista-cuponesDescuento"),
    path('crear-inscripcion/', crearInscripcion, name="crear-inscripcion"),
    path('editar-inscripcion/', editarInscripcion, name="editar-inscripcion"),
    path('eliminar-inscripcion/', eliminarInscripcion, name="eliminar-inscripcion"),
    path('devolver-inscripcion/', getInscripcion, name="devolver-inscripcion"),
    path('lista-inscripciones/', getInscripciones, name="lista-inscripciones"),
    path('registrar-asistencia/', registrar_asistencia, name="registrar-asistencia"),
    path('verificar-cuponDescuento/', verificarCuponDescuento, name="verificar-cuponDescuento"),
    path('create-preference/', create_preference, name="create-preference"),
    path('pruebaMercadoPago/', pruebaMercadoPago, name="pruebaMercadoPago"),
    path('pago-inscripcion-success/', pagoInscripcionSuccess, name="pago-inscripcion-success"),
    path('devolver-tarifa/', devolverTarifaPorId, name='devolver-tarifa'),
    path('verificar-codigoCupon/', verificarCodigoCupon, name="verificar-codigoCupon")
]
