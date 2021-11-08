from django.urls import path


from .views import *

urlpatterns = [
    path('crearCertificado/', crearCertificado, name="crearCertificado"),
    path('crearCertificadoParametrizado/', crearCertificadoParametrizado, name="crearCertificadoParametrizado"),
    path('altaCertificado/', altaCertificado, name="altaCertificado"),
    path('altaDetalleCertificado/', altaDetalleCertificado, name="altaDetalleCertificado"),
    path('crearCertificadoParametrizado/', crearCertificadoParametrizado, name="crearCertificadoParametrizado"),
    path('pruebaCertificadoParametrizado/', PruebaCertificadoParametrizado, name="pruebaCertificadoParametrizado"),
]
