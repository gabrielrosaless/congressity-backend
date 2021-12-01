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
import qrcode
from django.db.models.expressions import RawSQL
from django.db import connection
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import io
from decouple import config


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
            simpxcongreso = SimposiosxCongreso.objects.filter(idSimposio=idSimposio, idCongreso=congreso.id).first()
            if simpxcongreso is None:
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
        elif articulo.idSimposio.id != int(simpxcongreso.id):
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
        # Envío de MAIL a responsable
        s = start.split(" ")[1]
        e = end.split(" ")[1]
        data = {'title': title, 'fecha': start.split(" ")[0], 'start': s[0:5], 'end': e[0:5], 'aula': aula.nombre, 'congreso': congreso.nombre, 'email': articulo.responsable, 'op': 'A'}
        res = send_mail(data)

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


@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def crearBreakCharla(request):
    """
    Registra un nuevo break o charla plenaria.
    """
    usuario = request.user
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    start = request.data['start']
    end = request.data['end']
    title = request.data['title']
    content = request.data['desc']

    congreso = Congreso.objects.filter(id=payload['idCongreso']).first()
    if congreso is None:
        return Response({
            'status': '400',
            'error': 'El congreso no existe o es inválido.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    # Podríamos agregar la validación de start y end

    datos = {
        'title': title,
        'content': content,
        'start': start,
        'end': end,
        'idCongreso': payload['idCongreso'],
        'idAula': None,
        'idSimposio': None,
        'idArticulo': None
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


@api_view(['PUT'])
@authentication_classes([AuthenticationChairPrincipal])
def editarEvento(request):
    """ Permite editar un evento. """

    idEvento = request.GET['idEvento']

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

    try:
        evento = Evento.objects.get(id=idEvento)
    except Evento.DoesNotExist:
        raise Http404("El evento no existe.")

    serializer = EventoSerializer(instance=evento, data=datos)

    if serializer.is_valid():
        serializer.save()

        s = start.split(" ")[1]
        e = end.split(" ")[1]
        data = {'title': title, 'fecha': start.split(" ")[0], 'start': s[0:5], 'end': e[0:5], 'aula': aula.nombre, 'congreso': congreso.nombre, 'email': articulo.responsable, 'op': 'M'}
        res = send_mail(data)
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)

    return Response({
        'status': '400',
        'error': serializer.errors,
        'data': []
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([AuthenticationChairPrincipal])
def editarBreakCharla(request):
    """ Permite editar un evento. """

    idEvento = request.GET['idEvento']

    usuario = request.user
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    start = request.data['start']
    end = request.data['end']
    title = request.data['title']
    content = request.data['desc']

    congreso = Congreso.objects.filter(id=payload['idCongreso']).first()
    if congreso is None:
        return Response({
            'status': '400',
            'error': 'El congreso no existe o es inválido.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    # Podríamos agregar la validación de start y end

    datos = {
        'title': title,
        'content': content,
        'start': start,
        'end': end,
        'idCongreso': payload['idCongreso'],
        'idAula': None,
        'idSimposio': None,
        'idArticulo': None
    }
    serializer = EventoSerializer(data=datos)

    try:
        evento = Evento.objects.get(id=idEvento)
    except Evento.DoesNotExist:
        raise Http404("El evento no existe.")

    serializer = EventoSerializer(instance=evento, data=datos)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)

    return Response({
        'status': '400',
        'error': serializer.errors,
        'data': []
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([AuthenticationChairPrincipal])
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
def getEventos(request):
    """ Devuelve la lista de eventos de un congreso por aulas. """

    id_congreso = request.GET['idCongreso']
    idAula = request.GET['idAula']
    datos = []
    try:
        eventos = Evento.objects.filter(idCongreso=id_congreso).all()
        for e in eventos:
            if e.idAula is not None:
                if e.idAula.id == int(idAula):
                    serializer = EventoSerializer(instance=e)
                    data = serializer.data
                    data["idEvento"] = e.id
                    if e.idAula is not None:
                        data["nombreAula"] = e.idAula.nombre
                    else:
                        data["nombreAula"] = None
                    if e.idSimposio is not None:
                        data["nombreSimposio"] = e.idSimposio.nombre
                    else:
                        data["nombreSimposio"] = None
                    # data["nombreCongreso"] = e.idCongreso.nombre
                    
                    datos.append(data)
            else:
                serializer = EventoSerializer(instance=e)
                data = serializer.data
                data["idEvento"] = e.id
                data["nombreAula"] = None
                data["nombreSimposio"] = None
                # data["nombreCongreso"] = e.idCongreso.nombre
                datos.append(data)
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


@api_view(['GET'])
def getEvento(request):
    """ Devuelve los datos de un evento en particular. """

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
    if parametros[0] is not None and parametros[1] is not None and parametros[2] is not None:
        return True
    return False

@api_view(['GET'])
@authentication_classes([AuthenticationChairPrincipal])
def getQrAulas(request):
    """ Devuelve los códigos qr de las aulas. """
    idCongreso = request.GET['idCongreso']
    try:
        congreso = Congreso.objects.filter(id=idCongreso).first()
        responsable = congreso.chairPrincipal
        with connection.cursor() as cursor:
            cursor.execute('''
                           SELECT distinct "idAula_id" FROM public.eventos_evento
                           WHERE "idAula_id" IS NOT NULL
                           ''')
            rows = cursor.fetchall()
            cursor.close()
        data = []
        codigos_aulas = []
        nombres_aulas = []
        for i in rows:
            # URL_FRONT/proximoEvento/idCongreso/idAula
            idAula = i[0]
            aula = Aula.objects.filter(id=idAula).first()
            nombres_aulas.append(aula.nombre)
            relative_link= 'proximoEvento/'
            current_site=  config('URL_FRONT_DEV')
            url= 'http://' + current_site + relative_link
            url = url +  str(idCongreso) + "/" + str(idAula)
            qr = qrcode.QRCode(
                version = 1,
                error_correction = qrcode.constants.ERROR_CORRECT_H,
                box_size = 10,
                border = 4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image()
            
            im_resize = img.resize((500, 500))
            buf = io.BytesIO()
            im_resize.save(buf, format='PNG')
            byte_im = buf.getvalue()
            
            codigos_aulas.append(byte_im)
            
        template = get_template('qr_aulas.html')
        correo = EmailMultiAlternatives(
            'Códigos QR Aulas - CoNaIISI',
            '',
            settings.EMAIL_HOST_USER,
            [responsable]
        )
        for i in range(len(codigos_aulas)):
            correo.attach("QR_Aula_" + str(nombres_aulas[i]) +  ".png", codigos_aulas[i], 'image/png')
        correo.send()
        return Response({
            'status': '200',
            'error': '',
            'data': [data]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def getProximoEventoAula(request):
    """ Devuelve la lista de eventos de un aula. """

    idAula = request.GET['idAula']
    idCongreso = request.GET['idCongreso']
    datos = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                           SELECT * FROM public.eventos_evento WHERE "start" > current_date 
                           AND "idAula_id" = ''' + str(idAula) + 
                           ''' AND "idCongreso_id" = ''' + str(idCongreso) + 
                           ''' ORDER BY "start" asc limit 1''')
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            simposio = Simposio.objects.filter(id=i[5]).first()
            aula = Aula.objects.filter(id=idAula).first()
            datos = {
                "Titulo": i[1],
                "Contenido":i[2],
                "Inicio": i[3],
                "Fin":i[4],
                "Aula": aula.nombre,
                "Simposio":simposio.nombre
            }
            data.append(datos)
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


@api_view(['POST'])
def registarCalificacionEvento(request):
    """ Registra la calificacion de un evento por parte de un asistente. """

    idEvento = request.data['idEvento']
    puntuacion = request.data['puntuacion']
    calificacion = request.data['calificacion']
    try:
        datos = {
            "idEvento":idEvento,
            "puntuacion":puntuacion,
            "calificacion":calificacion
        }
        serializer = CalificacionEventoSerializer(data=datos)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': '200',
                'error': '',
                'data': 'Se guardó con éxito la calificación'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': '400',
                'error': 'Error en los datos.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)   

@api_view(['GET'])
def devolverCalificacionEvento(request):
    """ Consulta las calificaciones de un evento por parte de los asistentes. """
    idEvento = request.GET['idEvento']
    try:
        calificaciones = CalificacionEvento.objects.filter(idEvento=idEvento).all()
        serializer = CalificacionEventoSerializer(calificaciones, many=True)
        return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST) 


def send_mail(data):
    mail = data['email']
    context = {'title': data['title'], 'fecha': data['fecha'], 'start': data['start'], 'end': data['end'], 'aula': data['aula'], 'congreso': data['congreso']}
    if data['op'] == 'A':
        template = get_template('plantilla_confirmar_evento.html')
    elif data['op'] == 'M':
        template = get_template('plantilla_modificar_evento.html')
    content = template.render(context)
    correo = EmailMultiAlternatives(
        'Cambio en la fecha y/o hora de presentación del articulo',
        '',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    correo.attach_alternative(content, 'text/html')
    correo.send()
    return True  
