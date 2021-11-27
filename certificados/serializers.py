from rest_framework import serializers
from rest_framework.views import exception_handler
from .models import *

class CertificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificado
        fields = ['id','template', 'nombre', 'descripcion']

class DetalleCertificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCertificado
        fields = ['nombre', 'tipoLetra', 'tamañoLetra','posX','posY','idCerificado','atributo_usuario']