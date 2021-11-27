from django.urls import path


from .views import *

urlpatterns = [
    path('crearCertificado/', crearCertificado, name="crearCertificado"),
    path('crearCertificadoParametrizado/', crearCertificadoParametrizado, name="crearCertificadoParametrizado"),
    path('altaCertificado/', altaCertificado, name="altaCertificado"),
    path('altaDetalleCertificado/', altaDetalleCertificado, name="altaDetalleCertificado"),
    path('crearCertificadoParametrizado/', crearCertificadoParametrizado, name="crearCertificadoParametrizado"),
    path('pruebaCertificadoParametrizado/', PruebaCertificadoParametrizado, name="pruebaCertificadoParametrizado"),
    path('getArchivoTemplate/', getArchivoTemplate, name="getArchivoTemplate"),
    path('modifCertificado/', editarCertificado, name="modifCertificado"),
    path('crearCertificadoMasivo/', crearCertificadoMasivo, name="crearCertificadoMasivo"),
    path('bajaCertificado/', eliminarCertificado, name="bajaCertificado"),
    path('getCertificados/', devolverCertificados, name="getCertificados"),
    path('devolverDetallesCertificados/', devolverDetallesCertificados, name="devolverDetallesCertificados"),
]
