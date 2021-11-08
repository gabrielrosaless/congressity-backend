
from rest_framework import serializers
from .models import *

class TarifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = ['idCongreso','nombre','precio','fechaDesde','fechaHasta']

class CuponDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuponDescuento
        fields = ['codigo', 'porcentajeDesc', 'idTarifa', 'usosRestantes']

class InscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscripcion
        fields = ['id','idUsuario', 'idTarifa', 'idCongreso', 'fechaPago', 'fechaInscripcion', 'idCupon', 'precioFinal']






