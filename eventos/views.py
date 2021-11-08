from django.shortcuts import render
from django.utils import timezone
from usuarios.authentication import *
from congresos.models import *
from congresos.serializers import *
from articulos.models import *
from rest_framework.decorators import api_view, authentication_classes
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.http import Http404
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt

# Create your views here.
@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def crearEvento(request):
    """
    Registra un nuevo evento.
    """
    usuario = request.user
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    start = request.data['start']
    end = request.data['end']
    idAula = request.data['idAula']
    idSimposio = request.data['idSimposio']
    idArticulo = request.data['idArticulo']
    title = request.data['title']
    content = request.data['desc']
    parametros = [idAula, idSimposio, idArticulo]

    if not validarParametros(parametros):
        return Response({
            'status': '400',
            'error': 'Los datos enviados no son correctos.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    congreso = Congreso.objects.filter(id=payload['idCongreso']).first()
    if congreso is None:
        return Response({
            'status': '400',
            'error': 'El congreso no existe o es inválido.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    if idAula is not None:
        aula = Aula.objects.filter(id=idAula).first()
        if aula is None:
            return Response({
                'status': '400',
                'error': 'El aula no existe.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        elif aula.sede.id != congreso.sede:
            return Response({
                'status': '400',
                'error': 'El aula no pertenece a la sede del congreso.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    if idSimposio is not None:
        simposio = Simposio.objects.filter(id=idSimposio).first()
        if simposio is None:
            return Response({
                'status': '400',
                'error': 'El simposio no existe.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            s = SimposiosxCongreso.objects.filter(idSimposio=idSimposio, idCongreso=congreso.id).first()
            if s is None:
                return Response({
                    'status': '400',
                    'error': 'El simposio no pertence al congreso.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)

    if idArticulo is not None:
        articulo = Articulo.objects.filter(id=idArticulo).first()
        if articulo is None:
            return Response({
                'status': '400',
                'error': 'El artículo no existe.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        elif articulo.idCongreso.id != congreso.id:
            return Response({
                'status': '400',
                'error': 'El artículo no pertence al congreso.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        elif articulo.idSimposio.id != int(idSimposio):
            return Response({
                'status': '400',
                'error': 'El artículo no pertence al simposio.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

    # Podríamos agregar la validación de start y end

    datos = {
        'title': title,
        'content': content,
        'start': start,
        'end': end,
        'idCongreso': payload['idCongreso'],
        'idAula': idAula,
        'idSimposio': idSimposio,
        'idArticulo': idArticulo
    }
    serializer = EventoSerializer(data=datos)

    if serializer.is_valid() and usuario.is_authenticated:
        serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': '400',
            'error': serializer.errors,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminarEvento(request):
    """ Permite eliminar un evento. """
    usuario = request.user

    idEvento = request.GET['idEvento']

    evento = Evento.objects.filter(id=idEvento).first()
    if evento is not None:
        evento.delete()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': '400',
            'error': 'El evento no existe.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def getEventos(request):
    """ Devuelve la lista de eventos de un congreso por aulas. """

    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    id_congreso = payload['idCongreso']
    idAula = request.GET['idAula']
    datos = []
    try:
        eventos = Evento.objects.filter(idCongreso=id_congreso, idAula=idAula).all()
        for e in eventos:
            serializer = EventoSerializer(instance=e)
            data = serializer.data
            data["idEvento"] = e.id
            data["nombreAula"] = e.idAula.nombre
            data["nombreSimposio"] = e.idSimposio.nombre
            # data["nombreCongreso"] = e.idCongreso.nombre
            datos.append(data)
        return Response({
            'status': '200',
            'error': '',
            'data': datos
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver la lista de eventos.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def getEvento(request):
    """ Devuelve los datos de una inscripción. """

    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    idEvento = request.GET['idEvento']
    try:
        evento = Evento.objects.filter(id=idEvento).first()
        if evento is None:
            return Response({
                'status': '400',
                'error': "El evento no existe.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = EventoSerializer(instance=evento)
        data = serializer.data
        data["idEvento"] = e.id
        data["nombreAula"] = evento.idAula.nombre
        data["nombreSimposio"] = evento.idSimposio.nombre
        # data["nombreCongreso"] = evento.idCongreso.nombre
        return Response({
            'status': '200',
            'error': '',
            'data': [data]
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver los datos del evento.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def getEventosPorDia(request):
    """ Devuelve la lista de eventos de un congreso por aulas. """

    idCongreso = request.GET['idCongreso']
    fechaActual = Congreso.objects.filter(id=idCongreso).first().fechaInCongreso.date()
    print(fechaActual)
    datos = []
    try:
        eventos = Evento.objects.filter(idCongreso=idCongreso).all().order_by('start')
        evs = None
        for e in eventos:
            if e.start.date() > fechaActual:
                if evs is not None:
                    dia["eventos"] = evs
                    datos.append(dia)
                fechaActual = e.start.date()
                dia = {
                    'fecha': fechaActual,
                }
                evs = []

            expositores = []
            autores = AutorXArticulo.objects.filter(idArticulo=e.idArticulo.id).all()
            for a in autores:
                nombre = a.idUsuario.nombre + ' ' + a.idUsuario.apellido
                expositores.append(nombre)

            evento = {
                'nombre': e.title,
                'horarioInicio': e.start.time(),
                'horarioFin': e.end.time(),
                'aula': e.idAula.nombre,
                'expositores': expositores
            }

            evs.append(evento)
        dia["eventos"] = evs
        datos.append(dia)
        return Response({
            'status': '200',
            'error': '',
            'data': datos
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


def validarParametros(parametros):
    if parametros[0] is None and parametros[1] is None and parametros[2] is None:
        return True
    if parametros[0] is not None and parametros[1] is not None and parametros[2] is not None:
        return True
    return False