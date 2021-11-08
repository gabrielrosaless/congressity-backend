from rest_framework import serializers
from rest_framework.views import exception_handler

from .models import *

from datetime import datetime


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['title', 'content', 'start', 'end', 'idCongreso', 'idSimposio', 'idAula', 'idArticulo']
