from rest_framework import serializers
from rest_framework.views import exception_handler

from .models import *

from datetime import datetime


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoArticulo
        fields = ['nombre', 'descripcion']


class ArticuloCompletoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = ['id', 'nombre', 'idSimposio', 'idCongreso', 'responsable', 'url', 'observacion', 'esta_correcto', 'enviado_corregir','idEstado']

    def update(self, instance, validated_data):
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.id = validated_data.get('id', instance.id)
        instance.idCongreso = validated_data.get('idCongreso', instance.idCongreso)
        instance.idSimposio = validated_data.get('idSimposio', instance.idSimposio)
        instance.responsable = validated_data.get('responsable', instance.responsable)
        instance.url = validated_data.get('url', instance.url)
        instance.esta_correcto = validated_data.get('esta_correcto', instance.esta_correcto)
        instance.enviado_corregir = validated_data.get('enviado_corregir', instance.enviado_corregir)
        instance.idEstado = validated_data.get('idEstado', instance.idEstado)
        instance.observacion = validated_data.get('observacion', instance.observacion)
        
        instance.save()
        return instance

class ArticuloCameraReadySerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = ['id', 'url_camera_ready']


class ArticuloSerializer(serializers.ModelSerializer):
    idSimposio = serializers.CharField(read_only=True, source='idSimposio.nombre')
    idCongreso = serializers.CharField(read_only=True, source='idCongreso.año')
    idEstado = serializers.CharField(read_only=True, source='idEstado.nombre')
    responsable = serializers.CharField(read_only=True, source='responsable.nombre')

    class Meta:
        model = Articulo
        fields = ['nombre', 'idSimposio', 'responsable', 'idCongreso', 'url', 'observacion', 'idEstado']


class AutorxArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutorXArticulo
        fields = ['idArticulo', 'idUsuario']


class AutorxArticuloSinUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutorXArticuloSinUsuario
        fields = ['idArticulo', 'mailUsuario']


class EvaluadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluador
        fields = ['idUsuario', 'is_active']

class EvaluacionCanceladaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluacionCancelada
        fields = ['idUsuario', 'idArticulo','idCongreso']

class EvaluadorCalificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluador
        fields = ['idUsuario', 'is_active']

class EvaludorXCongresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluadorXCongreso
        fields = ['idCongreso', 'idUsuario']

class SimposiosXEvaluadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimposiosXEvaluador
        fields = ['idUsuario', 'idSimposio']

class ArticulosXEvaluadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticulosXEvaluador
        fields = ['idCongreso', 'idUsuario', 'idArticulo', 'estado', 'recomendacion', 'observaciones', 'observacionInterna', 'is_active']

class ItemEvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemEvaluacion
        fields = ['nombre', 'descripcion', 'idCongreso', 'is_active']

class EvaluacionXEvaluadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluacionXEvaluador
        fields = ['idCongreso','idUsuario', 'idArticulo','observaciones', 'recomendacion']

class ItemEvaluacionXEvaluadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemEvaluacionXEvaluador
        fields = ['idEvaluacion', 'idItem','puntuacion']

class ChairXSimposioXCongresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChairXSimposioXCongreso
        fields = ['idSimposio', 'idUsuario','idCongreso']


class EvaluadorXCongresoXChairSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluadorXCongresoXChair
        fields = ['idChair', 'idEvaluador','idCongreso']

