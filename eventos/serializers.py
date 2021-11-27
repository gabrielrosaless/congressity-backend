from rest_framework import serializers
from rest_framework.views import exception_handler

from .models import *

from datetime import datetime


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['title', 'content', 'start', 'end', 'idCongreso', 'idSimposio', 'idAula', 'idArticulo']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('end', instance.end)
        instance.idCongreso = validated_data.get('idCongreso', instance.idCongreso)
        instance.idSimposio = validated_data.get('idSimposio', instance.idSimposio)
        instance.idAula = validated_data.get('idAula', instance.idAula)
        instance.idArticulo = validated_data.get('idArticulo', instance.idArticulo)

        instance.save()
        return instance

class CalificacionEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalificacionEvento
        fields = ['idEvento', 'puntuacion', 'calificacion']