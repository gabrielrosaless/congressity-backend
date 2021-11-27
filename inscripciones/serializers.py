
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
        fields = ['id','idUsuario', 'idTarifa', 'idCongreso', 'fechaPago', 'fechaInscripcion', 'idCupon', 'precioFinal','asistio']


class InscripcionSinCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InscripcionSinCuenta
        fields = ['email','nombre','apellido','dni','tipoDni','fechaNacimiento', 'idTarifa', 'idCongreso', 'fechaPago', 'fechaInscripcion', 'precioFinal','asistio']


class AyudanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ayudante
        fields = ['id','idUsuario','idCongreso','is_active']