# Create your views here.

# from backendTesis.usuarios.authentication import AuthenticationChairSecundario, AuthenticationEvaluador

import sys
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
sys.path.append("..")
#from datetime import datetime

from django.db.models.query import FlatValuesListIterable
from django.utils.functional import partition

from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
from usuarios.serializers import UsuarioSerializer
from .models import Articulo, AutorXArticulo, AutorXArticuloSinUsuario, ChairXSimposioXCongreso
from rest_framework.decorators import api_view, authentication_classes
from usuarios.authentication import *
from usuarios.models import *
from eventos.models import *
from usuarios.serializers import RolxUsuarioxCongresoSerializer
from congresos.models import *
from congresos.serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os.path
from django.conf import settings
from django.core.files.storage import default_storage, FileSystemStorage
import json
import jwt, datetime
from datetime import timedelta
from datetime import datetime as datetimecongreso
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.http import FileResponse
from django.utils import timezone, dateformat
from decouple import config

# Create your views here.


@swagger_auto_schema(method='post',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idCongreso:':openapi.Schema(type=openapi.TYPE_INTEGER),'simposio:':openapi.Schema(type=openapi.TYPE_STRING),'articulo:':openapi.Schema(type=openapi.TYPE_FILE) , 'responsable:':openapi.Schema(type=openapi.TYPE_STRING), 'autores:':openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))}),
        responses={'200': 'Se subió correctamente el paper','400': openapi.Response('Error')})
@api_view(['POST'])
@authentication_classes([Authentication])
def realizarEntrega(request):
    """
    Permite subir un paper a un congreso a un simposio determinado.
    """
    idCongreso = request.data['idCongreso']
    idSimposio = request.data['simposio']
    autores = request.data['autores']
    autores = autores.split(',')
    archivo = request.FILES['articulo']
    responsable = request.data['responsable']
    usuario = Usuario.objects.filter(id=responsable).first()
    responsable = usuario.email
    idArticulo = None
    try:
        if not Usuario.objects.filter(email=responsable).exists():
            return Response({
                'status': '400',
                'error': 'No se encuentra registrado el usuario responsable del artículo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        if not Congreso.objects.filter(id=idCongreso).exists():
            return Response({
                'status': '400',
                'error': 'No existe el congreso ingresado.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        if idSimposio == None or not (SimposiosxCongreso.objects.filter(idSimposio=idSimposio,idCongreso=idCongreso).exists()):
            return Response({
                'status': '400',
                'error': 'No existe el simposio ingresado.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        if archivo == None:
            return Response({
                'status': '400',
                'error': 'No se subió el archivo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        extension_archivo = request.FILES['articulo'].name.split('.')[-1]
        if extension_archivo.upper() != 'PDF':
            return Response({
                'status': '400',
                'error': 'El archivo no tiene el formato PDF.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        congreso = Congreso.objects.get(id=idCongreso)
        # simposio = SimposiosxCongreso.objects.get(id=idSimposio)
        if not congreso.is_active:
            return Response({
                'status': '400',
                'error': 'No se encuentra activo el congreso.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        if congreso.fechaLimPapers != None:
            limite = (datetimecongreso.date(congreso.fechaLimPapers))
            hoy = (datetimecongreso.date(datetimecongreso.now()))
            if limite < hoy:
                return Response({
                    'status': '400',
                    'error': 'El congreso no recibe más papers.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                    'status': '400',
                    'error': 'El congreso no esta activo aun.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
        if Articulo.objects.all().count() > 0:
            idArticulo = Articulo.objects.latest('id').id + 1
        else:
            idArticulo = 1
        filename =  'A_' + str(idCongreso) + '_' + str(idSimposio) + '_' + str(idArticulo) + '_' + 'V1' + ".pdf"
        fs = FileSystemStorage()
        if fs.exists(filename):
            return Response({
                'status': '400',
                'error': 'Error.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        file = fs.save(filename, archivo)
        file_url = filename
        
        simposioxcongreso = SimposiosxCongreso.objects.filter(idSimposio=idSimposio,idCongreso=idCongreso).first()
        
        datos = {
                "id": int(idArticulo),
                "idCongreso": int(idCongreso),
                "idSimposio": int(simposioxcongreso.id),
                "responsable": str(responsable),
                "nombre": str(request.data['nombre']),
                "url": str(file_url),
                "observacion": None,
                "esta_correcto": bool(False),
                "enviado_corregir": bool(False),
                "idEstado" : 1
                }
        serializer = ArticuloCompletoSerializer(data=datos)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({
                'status': '400',
                'error': 'Error en datos.',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        print(1)
        bandera = True
        if len(autores) > 0:
            current_site= config('URL_FRONT_DEV')
            # current_site = get_current_site(request).domain
            relative_link = 'cancelarAutoria/'
            registro_link = 'login' #reverse('registrar')
            url_registrar = current_site + registro_link
            for autor in autores:
                if not Usuario.objects.filter(email=autor).exists():
                    ## -------------------ENVIO DE MAIL--------------------------------##
                    payload = {
                        'email': autor,
                        'idArticulo': idArticulo,
                        'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
                        'iat': datetime.datetime.utcnow()
                    }

                    token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
                    url_envio = current_site + relative_link + token

                    datosInvitacion = {
                        'nombreArticulo': str(request.data['nombre']),
                        'año': str(congreso.año),
                        'nombreCongreso': str(congreso.nombre),
                        'email': autor,
                        'link': url_envio,
                        'linkRegistrar':url_registrar
                    }

                    send_mail_invitacion(datosInvitacion)

                    ## ---------------------------------------------------##
                    datos = {
                    "idArticulo": idArticulo,
                    "mailUsuario": autor,
                    }
                    serializer = AutorxArticuloSinUsuarioSerializer(data=datos)
                    if serializer.is_valid():
                        serializer.save()
                    bandera = False
                else:
                    idAutor = Usuario.objects.get(email=autor).id
                    ## -------------------ENVIO DE MAIL--------------------------------##
                    payload = {
                        'email': autor,
                        'idArticulo': idArticulo,
                        'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
                        'iat': datetime.datetime.utcnow()
                    }

                    token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
                    url_envio = current_site + relative_link + token

                    datosInvitacion = {
                        'nombreArticulo': str(request.data['nombre']),
                        'año': str(congreso.año),
                        'nombreCongreso': str(congreso.nombre),
                        'email': autor,
                        'link': url_envio,
                        'linkRegistrar':url_registrar
                    }

                    send_mail_invitacion(datosInvitacion)

                    ## ---------------------------------------------------##
                    datos = {
                    "idArticulo": idArticulo,
                    "idUsuario": idAutor,
                    }
                    serializer = AutorxArticuloSerializer(data=datos)
                    if serializer.is_valid():
                        serializer.save()

        else:
            return Response({
                'status': '400',
                'error': 'No se encontraron autores asociados autores para el articulo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        if bandera:
            articulo = Articulo.objects.get(id=idArticulo)
            articulo.esta_correcto = True
            articulo.save()
            return Response({
                'status': '200',
                'error': 'Se guardó correctamente el Artículo.',
                'data': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': '200',
                'error': 'Se guardó correctamente el Artículo, pero existen Autores que no estan registrados.',
                'data': []
            }, status=status.HTTP_200_OK)
    except:
        return Response({
                'status': '400',
                'error': 'No se pudo guardar el Artículo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='put',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idArticulo':openapi.Schema(type=openapi.TYPE_INTEGER),'idCongreso:':openapi.Schema(type=openapi.TYPE_INTEGER),'simposio:':openapi.Schema(type=openapi.TYPE_STRING),'articulo:':openapi.Schema(type=openapi.TYPE_FILE), 'autores:':openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))}),
        responses={'200': 'Se subió correctamente el paper','400': openapi.Response('Error')})
@api_view(['PUT'])
@authentication_classes([Authentication])
def editarEntrega(request):
    """
    Permite editar una entrega.
    """

    idCongreso = request.data['idCongreso']
    idSimposio = request.data['simposio']
    autores = request.data['autores']
    autores = autores.split(',')
    try:
        archivo = request.FILES['articulo']
    except:
        archivo = None
    idArticulo = request.data['idArticulo']
    try:
        if not Articulo.objects.filter(id=idArticulo).exists():
            return Response({
                'status': '400',
                'error': 'No existe el artículo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        if idCongreso == None or not (Congreso.objects.filter(id=idCongreso).exists()):
            return Response({
                'status': '400',
                'error': 'No existe el congreso ingresado.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        if idSimposio == None or not (SimposiosxCongreso.objects.filter(idSimposio=idSimposio,idCongreso=idCongreso).exists()):
            return Response({
                'status': '400',
                'error': 'No existe el simposio ingresado.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        congreso = Congreso.objects.get(id=idCongreso)
        #simposio = SimposiosxCongreso.objects.get(id= idSimposio)
        articulo = Articulo.objects.get(id = idArticulo)

        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        idUusario = payload['id']        
        usuario = Usuario.objects.filter(id=idUusario).first()
        if articulo.responsable != usuario.email:
            return Response({
                    'status': '400',
                    'error': 'Error, no es responsable del articulo',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)

        if not congreso.is_active:
            return Response({
                'status': '400',
                'error': 'No se encuentra activo el congreso.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        if congreso.fechaLimPapers != None:
            limite = (datetimecongreso.date(congreso.fechaLimPapers))
            hoy = (datetimecongreso.date(datetimecongreso.now()))
            if limite < hoy:
                return Response({
                    'status': '400',
                    'error': 'El congreso no recibe más papers.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                    'status': '400',
                    'error': 'El congreso no esta activo aun.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
        if archivo != None:
            extension_archivo = request.FILES['articulo'].name.split('.')[-1]
            if extension_archivo.upper() != 'PDF':
                return Response({
                'status': '400',
                'error': 'El archivo no tiene el formato PDF.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

            filename = articulo.url
            filename = filename.split('/')[-1]
            fs = FileSystemStorage()
            if fs.exists(filename):
                os.remove(os.path.join(settings.MEDIA_ROOT + filename))
            file = fs.save(filename, archivo)
            file_url = fs.url(file)

        if len(autores) == 0:
            return Response({
                'status': '400',
                'error': 'No se encontraron autores asociados autores para el articulo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        lista_autores_sin_reg = []
        lista_autores_con_reg = []
        bandera = True
        for autor in autores:
            if Usuario.objects.filter(email=autor).exists():
                idAutor = Usuario.objects.get(email=autor).id
                if AutorXArticulo.objects.filter(idUsuario=idAutor,idArticulo=idArticulo).exists():
                    lista_autores_con_reg.append(idAutor)
                else:
                    datos = {
                    "idArticulo": idArticulo,
                    "idUsuario": idAutor,
                    }
                    serializer_autor = AutorxArticuloSerializer(data=datos)
                    if serializer_autor.is_valid():
                        serializer_autor.save()
                        lista_autores_con_reg.append(idAutor)
            else:
                bandera = False
                if AutorXArticuloSinUsuario.objects.filter(mailUsuario=autor, idArticulo=idArticulo).exists():
                    lista_autores_sin_reg.append(autor)
                else:
                    datos_autor = {
                            "idArticulo": int(idArticulo),
                            "mailUsuario":autor,
                    }
                    serializer_autor_sin_reg = AutorxArticuloSinUsuarioSerializer(data=datos_autor)
                    if serializer_autor_sin_reg.is_valid():
                        serializer_autor_sin_reg.save()
                        print(serializer_autor_sin_reg.data)
                        lista_autores_sin_reg.append(autor)
                    #Enviar Mail de Validación
        AutorXArticuloSinUsuario.objects.exclude(mailUsuario__in=lista_autores_sin_reg).filter(idArticulo=idArticulo).delete()
        AutorXArticulo.objects.exclude(idUsuario__in=lista_autores_con_reg).filter(idArticulo=idArticulo).delete()
        simposioxcongreso = SimposiosxCongreso.objects.filter(idSimposio=idSimposio,idCongreso=idCongreso).first()
        datos = {
                "id": int(idArticulo),
                "idCongreso": int(idCongreso),
                "idSimposio": int(simposioxcongreso.id),
                "responsable": articulo.responsable,
                "nombre": str(request.data['nombre']),
                "url": articulo.url,
                "observacion": 1649,
                "esta_correcto": bool(bandera),
                "enviado_corregir": bool(False),
                "idEstado" : 1
                }
        serializer = ArticuloCompletoSerializer(instance=articulo,data=datos)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({
                'status': '400',
                'error': 'Error en datos.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        if bandera:
            return Response({
                'status': '200',
                'error': 'Se guardó correctamente el Artículo.',
                'data': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': '200',
                'error': 'Se guardó correctamente el Artículo, pero existen Autores que no estan registrados.',
                'data': []
            }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='post',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idArticulo':openapi.Schema(type=openapi.TYPE_INTEGER)},
        responses={'200': 'Enviado para ser corregido','400': openapi.Response('Error')}))
@api_view(['POST'])
@authentication_classes([Authentication])
def enviarEntrega(request):
    """
    Permite subir un paper a un congreso a un simposio determinado.
    """
    try:
        idArticulo = int(request.data['idArticulo'])
        articulo = Articulo.objects.filter(id=idArticulo).first()
        if articulo == None:
            return Response({
                    'status': '400',
                    'error': 'Error, existen autores que no se han registrado',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        idUusario = payload['id']        
        usuario = Usuario.objects.filter(id=idUusario).first()
        if articulo.responsable != usuario.email:
            return Response({
                    'status': '400',
                    'error': 'Error, no es responsable del articulo',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
        bandera = True
        usuarios_sin_registro = AutorXArticuloSinUsuario.objects.filter(idArticulo=idArticulo).all()
        if usuarios_sin_registro != None:
            for usu in usuarios_sin_registro:
                if not Usuario.objects.filter(email=usu.mailUsuario).exists():
                    print("ok4")
                    bandera = False
                else:
                    id_usu  = Usuario.objects.filter(email=usu.mailUsuario).id
                    datos = {
                        "idArticulo": idArticulo,
                        "idUsuario": id_usu,
                        }
                    serializer =  AutorxArticuloSerializer(data = datos)
                    if serializer.is_valid():
                        serializer.save()
        if bandera:
            estado = EstadoArticulo.objects.filter(id=2).first()
            articulo.idEstado = estado
            articulo.esta_correcto = True
            articulo.enviado_corregir  = True
            articulo.save()
            return Response({
                    'status': '200',
                    'error': 'Enviado para ser corregido',
                    'data': []
                }, status=status.HTTP_200_OK)
        else:
            articulo.esta_correcto = False
            articulo.enviado_corregir  = False
            articulo.save()
            return Response({
                    'status': '400',
                    'error': 'Existen autores sin registrarse',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get',
    manual_parameters=[openapi.Parameter('idArticulo', openapi.IN_QUERY, description="idArticulo", type=openapi.TYPE_INTEGER)],
    responses={200: ArticuloCompletoSerializer })
@api_view(['GET'])
@authentication_classes([Authentication])
def consultaArticuloXId(request):
    """
    Permite consultar un articulo en especifico.
    """
    try:
        usuario = request.user
        if usuario.is_authenticated:
            articuloId = int(request.GET['idArticulo'])
            articulo = Articulo.objects.filter(id=articuloId).first()
            if articulo != None:
                serializer = ArticuloCompletoSerializer(articulo)
                simposio_id = SimposiosxCongreso.objects.filter(id=serializer.data['idSimposio']).first().idSimposio.id
                simposio_nombre = Simposio.objects.get(id=simposio_id).nombre
                congreso_nombre = Congreso.objects.get(id=serializer.data['idCongreso']).nombre
                data = serializer.data
                data['nombre_simposio'] = simposio_nombre
                data['nombre_congreso'] = congreso_nombre
                return Response({
                'status': '200',
                'error': '',
                'data': [data]
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                        'status': '400',
                        'error': 'No existe el Artículo',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={'200': ArticuloCompletoSerializer ,'400': 'Error.'})
@api_view(['GET'])
@authentication_classes([Authentication])
def consultaArticuloXResponsable(request):
    """
    Permite consultar los articulos de un usuario logueado en el que sea responsable.
    """
    try:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token,settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        usuario = Usuario.objects.filter(id=payload['id']).first()
        articulos = Articulo.objects.filter(responsable=usuario.email).all()
        data = []
        if len(articulos) > 0:
            for articulo in articulos:
                serializer = ArticuloCompletoSerializer(articulo)
                simposio_id = SimposiosxCongreso.objects.filter(id=serializer.data['idSimposio']).first().idSimposio.id
                simposio_nombre = Simposio.objects.get(id=simposio_id).nombre
                congreso_nombre = Congreso.objects.get(id=serializer.data['idCongreso']).nombre
                estado_nombre = articulo.idEstado.nombre
                data_art = serializer.data
                data_art['nombre_simposio'] = simposio_nombre
                data_art['nombre_estado'] = estado_nombre
                data_art['nombre_congreso'] = congreso_nombre
                data_art['url_camera_ready'] = articulo.url_camera_ready
                autores_con_reg = []
                autores_reg = AutorXArticulo.objects.filter(idArticulo=articulo.id).all()
                if len(autores_reg) > 0:
                    for autor in autores_reg:
                        usuario = autor.idUsuario
                        print(usuario.email)
                        autores_con_reg.append(usuario.email)
                    data_art['autores_registrados'] = autores_con_reg
                autores_sin_reg = []
                autores_no_reg = AutorXArticuloSinUsuario.objects.filter(idArticulo=articulo.id).all()
                if len(autores_no_reg) > 0:
                    for autor in autores_no_reg:
                        print(autor.mailUsuario)
                        autores_sin_reg.append(autor.mailUsuario)
                    data_art['autores_no_registrados'] = autores_sin_reg
                data.append(data_art)
            return Response({
                'status': '200',
                'error': '',
                'data': data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                    'status': '200',
                    'error': '',
                    'data': []
                }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get', responses={'200': ArticuloCompletoSerializer ,'400': 'Error.'})
@api_view(['GET'])
@authentication_classes([Authentication])
def consultaArticuloXAutor(request):
    """
    Permite consultar los articulos de un usuario logueado en el que sea responsable.
    """
    try:
        usuario = request.user
        if usuario.is_authenticated:
            token = request.headers['Authorization']

            if not token:
                raise AuthenticationFailed('Usuario no autenticado!')
            try:
                payload = jwt.decode(token,'secret',algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Usuario no autenticado!')
            usuario = Usuario.objects.filter(id=payload['id']).first()
            articulos_autor = AutorXArticulo.objects.filter(idUsuario=usuario.id)
            articulos = []
            for art in articulos_autor:
                articulos.append(art.idArticulo)
            data = []
            if len(articulos) > 0:
                for articulo in articulos:
                    serializer = ArticuloCompletoSerializer(articulo)
                    simposio_id = SimposiosxCongreso.objects.filter(id=serializer.data['idSimposio']).first().id
                    simposio_nombre = Simposio.objects.get(id=simposio_id).nombre
                    congreso_nombre = Congreso.objects.get(id=serializer.data['idCongreso']).nombre
                    data_art = serializer.data
                    data_art['nombre_simposio'] = simposio_nombre
                    data_art['nombre_congreso'] = congreso_nombre
                    data.append(data_art)
                return Response({
                    'status': '200',
                    'error': '',
                    'data': data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                        'status': '400',
                        'error': 'No existen artículos para este usuario',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


def send_mail_invitacion(request):

    nombre = request['nombreArticulo']
    email = request['email']
    nombreCongreso = request['nombreCongreso']
    año = request['año']
    link = request['link']
    linkRegistro = request['linkRegistrar']

    context = {'nombreArticulo': nombre ,'linkRechazo': link,
        'linkRegistrar': linkRegistro, 'año':año, 'nombreCongreso': nombreCongreso}

    template = get_template('invitacion_autoria.html')

    content = template.render(context)
    correo = EmailMultiAlternatives(
        'Confirmacion de Autoria - CoNaIISI',
        '',
        settings.EMAIL_HOST_USER,
        [email]
    )
    correo.attach_alternative(content, 'text/html')
    correo.send()
    return True



@swagger_auto_schema(method='delete',
manual_parameters=[openapi.Parameter('token', openapi.IN_QUERY, description="token encriptado armado desde el mail", type=openapi.TYPE_STRING)],
responses={'200': openapi.Response('Se rechazo correctamente la autoria.'),'400': openapi.Response('Error')})
@api_view(['DELETE'])
def rechazarAutoria(request):
    """Este endpoint es el que se usa cuando le llega el mail a una autor para que pueda rechazar su autoria. 
    Lo que hace es eliminar de la bd fisicamente la relacion entre ese autor y el articulo"""
    token = request.GET.get('token')

    try:
        payload = jwt.decode(token, settings.SECRET_KEY)

        autoria = AutorXArticuloSinUsuario.objects.filter(idArticulo=payload['idArticulo'], mailUsuario=payload['email']).first()

        if autoria != None:
            autoria.delete()
            return Response({'error': False, 'mensaje': 'Se rechazo correctamente la autoria.'}, status=status.HTTP_200_OK)
        else:

            usuario = Usuario.objects.filter(email=payload['email']).first()
            autoria = AutorXArticulo.objects.filter(idArticulo=payload['idArticulo'], idUsuario=usuario.id).first()

            if autoria != None:
                autoria.delete()
                return Response({'error': False, 'mensaje': 'Se rechazo correctamente la autoria.'}, status=status.HTTP_200_OK)
        return Response({'error': True, 'mensaje': 'El articulo no existe o el usuario no fue ingresado como autor.'}, status=status.HTTP_400_BAD_REQUEST)
    except jwt.ExpiredSignatureError as identifier:
        return Response({'error': 'El link expiró'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
        return Response({'error': 'Token Inválido'}, status= status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def probar_mail(request):
    email = request.data['email']
    nombre = request.data['nombre']

    current_site = get_current_site(request).domain
    relative_link = reverse('rechazar-autoria')
    registro_link = reverse('registrar')

    payload = {
            'email': email,
            'idArticulo': 1,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
            'iat': datetime.datetime.utcnow()
        }

    token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
    url_envio = current_site + relative_link + "?token=" + token

    url_registrar = current_site + registro_link
    data = {'nombreArticulo': nombre,'email':email ,'link': url_envio, 'linkRegistrar':url_registrar}

    send_mail_invitacion(data)
    return Response("mail enviado")


@swagger_auto_schema(method='get', responses={'200': ArticuloSerializer, '400': 'Error.'})
@api_view(['GET'])
@authentication_classes([Authentication])
def getArticulos(request):
    """
    Permite obtener los artículos de un simposio, con la posibilidad de filtrar por estado.
    """
    simposio = request.GET['idSimposio']
    estado = int(request.GET['idEstado'])
    if simposio != "":
        if estado == 0:
            articulos = Articulo.objects.filter(idSimposio=simposio)
            serializer = ArticuloSerializer(articulos, many=True)
        else:
            articulos = Articulo.objects.filter(idSimposio=simposio).filter(idEstado_id=estado)
            serializer = ArticuloSerializer(articulos, many=True)
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': '400',
            'error': 'Debe especificar el simposio.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={'200': ArticuloSerializer, '400': 'Error.'})
@api_view(['GET'])
@authentication_classes([Authentication])
def getEstadoArticulosAutor(request):
    """
    Permite al autor ver el estado de sus artículos.
    """
    usuario = request.user.email
    articulos = Articulo.objects.filter(responsable=usuario)
    serializer = ArticuloSerializer(articulos, many=True)
    return Response({
        'status': '200',
        'error': '',
        'data': [serializer.data]
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(method='put',
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties={'idArticulo': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                             'articulo:': openapi.Schema(type=openapi.TYPE_FILE)}),
                     responses={'200': 'Se subió correctamente el paper', '400': openapi.Response('Error')})
@api_view(['PUT'])
@authentication_classes([Authentication])
def reentregarArticulo(request):
    """
    Permite reentregar un artículo con correcciones.
    """

    idArticulo = request.data['idArticulo']

    if not Articulo.objects.filter(id=idArticulo).exists():
        return Response({
            'status': '400',
            'error': 'No existe el artículo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    articulo = Articulo.objects.get(id=idArticulo)
    idCongreso = articulo.idCongreso.id
    idSimposio = articulo.idSimposio.id
    archivo = request.FILES['paper']
    congreso = Congreso.objects.get(id=idCongreso)
    simposio = Simposio.objects.get(id=idSimposio)

    if not congreso.is_active:
        return Response({
            'status': '400',
            'error': 'No se encuentra activo el congreso.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    if congreso.fechaProrrogaPapers != None: # Arreglar fechas
        limite = (datetimecongreso.date(congreso.fechaProrrogaPapers))
        hoy = (datetimecongreso.date(datetimecongreso.now()))
        if limite < hoy:
            return Response({
                'status': '400',
                'error': 'El congreso no recibe más papers.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'status': '400',
            'error': 'El congreso no está recibiendo reentregas por el momento.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


    if archivo is not None:
        extension_archivo = request.FILES['paper'].name.split('.')[-1]
        if extension_archivo.upper() != 'PDF':
            return Response({
                'status': '400',
                'error': 'El archivo no tiene el formato PDF.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        filename = 'A_' + str(idCongreso) + '_' + str(idSimposio) + '_' + str(idArticulo) + '_' + 'V2' + ".pdf"
        fs = FileSystemStorage()
        if fs.exists(filename):
            os.remove(os.path.join(settings.MEDIA_ROOT + filename))
        file = fs.save(filename, archivo)
        file_url = fs.url(file)

    datos = {
        "id": int(idArticulo),
        "idCongreso": int(idCongreso),
        "idSimposio": int(idSimposio),
        "responsable": articulo.responsable,
        "nombre": str(request.data['nombre']),
        "url": filename,
        "observacion": articulo.observacion,
        "esta_correcto": bool(True),
        "enviado_corregir": bool(False),
    }
    serializer = ArticuloCompletoSerializer(instance=articulo, data=datos)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    else:
        return Response({
            'status': '400',
            'error': 'Error en datos.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'status': '200',
        'error': 'Se guardó correctamente el Artículo.',
        'data': []
    }, status=status.HTTP_200_OK)



@swagger_auto_schema(method='post',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idUsuarios:':openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))}),
        responses={ '200': 'El mail ha sido enviado.',
                    '400': openapi.Response('Alguno de los usuarios que desea asignar como evaluador no existe en la base de datos.'),
                    '400': openapi.Response('El usuario {nombre} (id: {id}) ya es un evaluador.'),
                    '401': openapi.Response('El usuario no posee los permisos necesarios.')})
@api_view(['POST'])
@authentication_classes([AuthenticationChairSecundario])
def asignarRolEvaluador(request):
    """
    Permite enviar un mail a un conjunto de usuarios para avisarle que fueron asignados como evaluadores. 
    Para que funcione el metodo todos los Ids del array deben ser usuarios del sistema y no ser evaluadores actualmente.
    Los usuarios deben aceptar luego en el mail para confirmar.
    """
    usuarioLogueado = request.user      #Usuario logueado
    idUsuarios = request.data['idUsuarios']      #Id del usuario al que quiero hacer evaluador
    usuarios = idUsuarios.split(",")
    try:
        for us in usuarios:
            if not Usuario.objects.filter(id=us).exists():
                return Response({
                    'status': '400',
                    'error': 'Alguno de los usuarios que desea asignar como evaluador no existe en la base de datos.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
        for ev in usuarios:
            evaluador = Evaluador.objects.filter(idUsuario=ev).first()
            if evaluador != None:
                usuario = Usuario.objects.filter(id=evaluador.idUsuario_id).first()
                id = usuario.id
                nombre = usuario.nombre
                res = {
                        'status': '400',
                        'error': 'El usuario {} (id: {}) ya es un evaluador.'.format(nombre,id),
                        'data': []
                }
                return Response(res, status= status.HTTP_400_BAD_REQUEST)
        #rol = RolxUsuarioxCongreso.objects.filter(idUsuario=idUsuarioLogueado).filter(idCongreso=congreso.id).first()

        if usuarioLogueado.is_authenticated: ################ ACA EN REALIDAD DEBERIA SER ROL CHAIR PRINCIPAL
            for user in usuarios:
                usuario = Usuario.objects.filter(id=user).first()
                
                # Agrego el usuario a la tabla Evaluadores, con el campo activo en False
                evaluador = {
                    'idUsuario':usuario.id,
                    'is_active': False
                }

                serializer = EvaluadorSerializer(data=evaluador)

                serializer.is_valid(raise_exception=True)

                serializer.save()

                ##--------------- ARMO EL MAIL --------------------------------##
                email = usuario.email
                current_site= config('URL_FRONT_DEV')
                # link_aceptar = reverse('aceptar-evaluador')
                # link_rechazar = reverse('rechazar-evaluador')
                link_aceptar = 'aceptacionRolEvaluador/'
                link_rechazar = 'cancelacionEvaluador/'
                payload = {
                        'email': email,
                        'idUsuario':usuario.id,
                        'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=15),
                        'iat': datetime.datetime.utcnow()
                }

                token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')

                url_aceptacion = current_site + link_aceptar + token
                url_rechazo = current_site + link_rechazar + token

                data = {'email':email ,'url_aceptacion': url_aceptacion, 'url_rechazo':url_rechazo}

                send_mail_evaluador1(data)

            return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                        'status': '401',
                        'error': 'El usuario no posee los permisos necesarios.',
                        'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({
                        'status': '500',
                        'error': e.args,
                        'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_mail_evaluador1(request):

    try:
        email = request['email']
        linkAceptacion = request['url_aceptacion']
        linkRechazo = request['url_rechazo']
        fecha = timezone.now() + timedelta(30)
        fechaLimite = dateformat.format(fecha, 'd/m/Y')
        context = {'linkRechazo': linkRechazo, 'linkAceptacion': linkAceptacion, 'fechaLimite': fechaLimite}

        template = get_template('invitacion_rol_evaluador.html')

        content = template.render(context)
        correo = EmailMultiAlternatives(
            'Solicitud de Evaluador - CoNaIISI',
            '',
            settings.EMAIL_HOST_USER,
            [email]
        )
        correo.attach_alternative(content, 'text/html')
        correo.send()
        return True
    except:
        return Response({
            'status': '500',
            'error': 'Error durante el envio de mail.',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method='put',
    responses={ '200': 'Se acepto correcamente el evaluador.',
                '400': openapi.Response('El usuario no se encuentra solicitado como evaluador o no existe.')})
@api_view(['PUT'])
def aceptarEvaluador(request):
    """
    Endpoint que se llama desde el mail que le llega al evaluador. 
    Permite activar el campo is_active de la tabla Evaluadores.
    """
    token = request.GET.get('token')

    try:
        payload = jwt.decode(token, settings.SECRET_KEY)

        evaluador = Evaluador.objects.filter(idUsuario=payload['idUsuario']).first()

        if evaluador != None:
            evaluador.is_active = True
            evaluador.save()
            return Response({'error': False, 'mensaje': 'Se acepto correcamente el evaluador.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': True, 'mensaje': 'El usuario no se encuentra solicitado como evaluador o no existe.'}, status=status.HTTP_400_BAD_REQUEST)
        
    except jwt.ExpiredSignatureError as identifier:
      return Response({'error': 'El link expiró'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
      return Response({'error': 'Token Inválido'}, status= status.HTTP_400_BAD_REQUEST)

# Posiblemente filtrar por simposio?
@swagger_auto_schema(method='get', responses={'200': EvaluadorSerializer, '400': 'Error.'})
@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getEvaluadores(request):
    """
    Permite obtener una lista de todos los evaluadores.
    """
    usuario = request.user
    activos = int(request.GET['activos'])
    if usuario.is_superuser:
        if activos == 1:
            evaluadores = Evaluador.objects.filter(is_active=True).all()
        else:
            evaluadores = Evaluador.objects.all()
        arrayEvaluadores = []
        for e in evaluadores:
            usuarioAux = Usuario.objects.filter(id=e.idUsuario.id).first()
            sede = Sede.objects.filter(id=usuarioAux.sede.id).first()
            nombre = e.idUsuario.apellido + ' ' + e.idUsuario.nombre
            simposios = []
            simposiosXEvaluador = SimposiosXEvaluador.objects.filter(idUsuario=e.idUsuario.id)
            for s in simposiosXEvaluador:
                simposios.append({'idSimposio':s.idSimposio.id, 'simposio':s.idSimposio.descripcion})
            articulosAsignados = ArticulosXEvaluador.objects.filter(idUsuario=e.idUsuario.id).all().count()
            articulosAceptados = ArticulosXEvaluador.objects.filter(idUsuario=e.idUsuario.id).filter(is_active=True).all().count()
            articulosCorregidos = ArticulosXEvaluador.objects.filter(idUsuario=e.idUsuario.id).filter(estado=3).all().count()
            if articulosAsignados != 0:
                aceptadosSobreAsignados = round(articulosAceptados / articulosAsignados, 2)
                corregidosSobreAsignados = round(articulosCorregidos / articulosAsignados, 2)
            else:
                aceptadosSobreAsignados = 0
                corregidosSobreAsignados = 0
            if articulosAceptados != 0:
                corregidosSobreAceptados = round(articulosCorregidos / articulosAceptados, 2)
            else:
                corregidosSobreAceptados = 0
            evaluador = {'idUsuario': e.idUsuario.id,
                         'nombre': nombre,
                         'email': e.idUsuario.email,
                         'estado': e.is_active,
                         'simposios': simposios,
                         'asignados': articulosAsignados,
                         'aceptados': articulosAceptados,
                         'corregidos': articulosCorregidos,
                         'aceptadosSobreAsignados': aceptadosSobreAsignados,
                         'corregidosSobreAceptados': corregidosSobreAceptados,
                         'corregidosSobreAsignados': corregidosSobreAsignados,
                         'sedeEvaluador':sede.nombre
                         }
            arrayEvaluadores.append(evaluador)
        return Response({
            'status': '200',
            'error': '',
            'data': arrayEvaluadores
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': '400',
            'error': 'Se necesitan permisos de administrador.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={'200': EvaluadorSerializer, '400': 'Error.'})
@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getEvaluadoresXArticulo(request):
    """
    Permite obtener una lista de los evaluadores de un artículo.
    """
    usuario = request.user
    idArticulo = request.GET['idArticulo']
    articulosXEvaluador = ArticulosXEvaluador.objects.filter(idArticulo=idArticulo).all()
    evaluadores = []
    for a in articulosXEvaluador:
        nombre = a.idUsuario.apellido + ' ' + a.idUsuario.nombre
        evaluador = {
            'idUsuario': a.idUsuario.id,
            'nombre': nombre
        }
        evaluadores.append(evaluador)
    return Response({
        'status': '200',
        'error': '',
        'data': evaluadores
    }, status=status.HTTP_200_OK)



@swagger_auto_schema(method='get',
responses={'200': openapi.Response('Datos del evaluador.'),'400': openapi.Response('Error')})
@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getEvaluadorById(request):
    """
    Muestra los datos del evaluador.
    """
    usuario = request.user.id
    try:
        evaluador = Evaluador.objects.filter(idUsuario=usuario)
        datos = {
            "idUsuario": usuario,
            "activo": True,
        }
        return Response({
            'status': '200',
            'error': '',
            'data': [datos]
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': 'Usted no es evaluador.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post',
request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idEvaluador:':openapi.Schema(type=openapi.TYPE_INTEGER), 'idCongreso:':openapi.Schema(type=openapi.TYPE_INTEGER), 'articulos:':openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))}),
responses={'200': openapi.Response('Simposio eliminado.'),'400': openapi.Response('Error')})
@api_view(['POST'])
@authentication_classes([AuthenticationChairSecundario])
def asignarArticuloEvaluador(request):
    """
    Permite asignar artículos a un evaluador.
    """
    usuario = request.user
    if usuario.is_superuser:
        try:
            idEvaluador = request.data['idUsuario']
            articulos = request.data['articulos']
            articulos = articulos.split(',')
            idCongreso = request.data['idCongreso']

            if not Congreso.objects.filter(id=idCongreso).exists():
                return Response({
                    'status': '400',
                    'error': 'El congreso no existe.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)

            if not Evaluador.objects.filter(idUsuario=idEvaluador).exists():
                return Response({
                    'status': '400',
                    'error': 'El usuario no es evaluador.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)

            for a in articulos:

                if not Articulo.objects.filter(id=a).exists():
                    return Response({
                        'status': '400',
                        'error': 'El artículo no existe.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                if ArticulosXEvaluador.objects.filter(idCongreso=idCongreso).filter(idUsuario=idEvaluador).filter(idArticulo=a).exists():
                    return Response({
                        'status': '400',
                        'error': 'El artículo ya está asignado al evaluador.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                serializer = ArticulosXEvaluadorSerializer(
                    data={'idCongreso': idCongreso, 'idUsuario': idEvaluador, 'idArticulo': a, 'is_active':False})
                if serializer.is_valid():
                    serializer.save()
                ## -------------------ENVIO DE MAIL--------------------------------##
                current_site = config('URL_FRONT_DEV')
                relative_link = 'cancelacionEvaluacionPaper/'
                aceptar_link = 'aceptarEvaluacionPaper/'
                payload = {
                    'idEvaluador': idEvaluador,
                    'idArticulo': a,
                    'idCongreso': idCongreso,
                    'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
                    'iat': datetime.datetime.utcnow()
                    }
                token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
                url_envio = current_site + relative_link + token
                url_aceptar = current_site + aceptar_link + token
                congre = Congreso.objects.filter(id=idCongreso).first()
                usuario = Usuario.objects.filter(id=idEvaluador).first()
                datosInvitacion = {
                    'año': str(congre.año),
                    'nombreCongreso': str(congre.nombre),
                    'email': usuario.email,
                    'linkRechazo': url_envio,
                    'linkAceptar': url_aceptar
                }
                send_mail_evaluador(datosInvitacion)
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
    else:
        return Response({
            'status': '400',
            'error': 'Se necesitan permisos de administrador.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='post',
request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'simposios:':openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))}),
responses={'200': openapi.Response('Simposio eliminado.'),'400': openapi.Response('Error')})
@api_view(['POST'])
@authentication_classes([Authentication])
def asignarSimposioEvaluador(request):
    """
    Permite al evaluador elegir sus simposios preferidos.
    """
    try:
        usuario = request.user.id
        simposios = request.data['simposios']
        simposios = simposios.split(",")
        for s in simposios:
            serializer = SimposiosXEvaluadorSerializer(
                data={'idUsuario': usuario, 'idSimposio': s})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': 'Hubo un problema con la asignación.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

def send_mail_evaluador(request):

    email = request['email']
    nombreCongreso = request['nombreCongreso']
    año = request['año']
    linkRechazo = request['linkRechazo']
    linkAceptar = request['linkAceptar']
    fecha = timezone.now() + timedelta(30)
    fechaLimite = dateformat.format(fecha, 'd/m/Y')

    context = {'linkAceptar':linkAceptar,'linkRechazo': linkRechazo,
                'año':año, 'nombreCongreso': nombreCongreso, 'fechaLimite': fechaLimite}

    template = get_template('invitacion_evaluador.html')

    content = template.render(context)
    correo = EmailMultiAlternatives(
        'Confirmacion de Evaluador - CoNaIISI',
        '',
        settings.EMAIL_HOST_USER,
        [email]
    )
    correo.attach_alternative(content, 'text/html')
    correo.send()
    return True

@swagger_auto_schema(method='GET',
manual_parameters=[openapi.Parameter('token', openapi.IN_QUERY, description="token encriptado armado desde el mail", type=openapi.TYPE_STRING)],
responses={'200': openapi.Response('Se rechazo correctamente la evaluacion.'),'400': openapi.Response('Error')})
@api_view(['GET'])
def rechazarEvaluacion(request):
    """Este endpoint es el que se usa cuando le llega un articulo para evaluar
    y no desea ser evaluador del mismo"""
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        evaluacion = ArticulosXEvaluador.objects.filter(idArticulo=payload['idArticulo'], idUsuario =payload['idEvaluador']).first()
        if evaluacion != None:
            evaluador = Usuario.objects.filter(id = payload['idEvaluador'] ).first()
            articulo = Articulo.objects.filter(id=payload['idArticulo']).first()
            chair_simposio = ChairXSimposioXCongreso.objects.filter(idSimposio=articulo.idSimposio.id, idCongreso =payload['idCongreso']).first()
            evaluacion.delete()
            cancelacion = {
                "idArticulo":articulo.id,
                "idUsuario":payload['idEvaluador'],
                "idCongreso":payload['idCongreso']
            }
            registrarCancelacion(cancelacion)
            datos = {
                "evaluador": evaluador.email,
                "articulo": articulo.nombre,
                "email": chair_simposio.idUsuario.email,
                }
            print(datos)
            send_mail_chair_cancelar_evaluador(datos)
            return Response({'error': False, 'mensaje': 'Se rechazo la evaluacion.'}, status=status.HTTP_200_OK)
        return Response({'error': True, 'mensaje': 'El articulo no existe o el usuario no fue ingresado como evaluador.'}, status=status.HTTP_400_BAD_REQUEST)
    except jwt.ExpiredSignatureError as identifier:
      return Response({'error': 'El link expiró'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
      return Response({'error': 'Token Inválido'}, status= status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='delete',
    manual_parameters=[openapi.Parameter('token', openapi.IN_QUERY, description="token encriptado armado desde el mail", type=openapi.TYPE_STRING)],
    responses={ '200': openapi.Response('Se rechazo correctamente la invitacion para ser evaluador.'),
                '400': openapi.Response('No se pudo rechazar correctamente la invitación.')})
@api_view(['DELETE'])
def rechazarEvaluador(request):
    """
    Este metodo se llama tambien desde el mail con el link que le llega al usuario como invitacion para ser evaluador.
    """
    token = request.GET.get('token')

    try:
        payload = jwt.decode(token, settings.SECRET_KEY)

        evaluador = Evaluador.objects.filter(idUsuario=payload['idUsuario']).first()

        if evaluador != None:
            evaluador.delete()
            return Response({'error': False, 'mensaje': 'Se rechazo correctamente la invitacion para ser evaluador.'}, status=status.HTTP_200_OK)

        return Response({'error': True, 'mensaje': 'No se pudo rechazar correctamente la invitación.'}, status=status.HTTP_400_BAD_REQUEST)
    except jwt.ExpiredSignatureError as identifier:
        return Response({'error': 'El link expiró'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
        return Response({'error': 'Token Inválido'}, status= status.HTTP_400_BAD_REQUEST)

def send_mail_chair_cancelar_evaluador(request):
    evaluador = request['evaluador']
    articulo = request['articulo']
    email = request['email']
    context = {'evaluador':evaluador,'articulo': articulo}
    template = get_template('notificacion_baja_evaluador.html')
    content = template.render(context)
    correo = EmailMultiAlternatives(
        'Cancelación de Evaluador a corregir paper - CoNaIISI',
        '',
        settings.EMAIL_HOST_USER,
        [email]
    )
    correo.attach_alternative(content, 'text/html')
    correo.send()
    return True

@swagger_auto_schema(method='GET',responses={'200': openapi.Response('Evaluacion Aceptada.'), '400': 'Error.'})
@api_view(['GET'])
def aceptarEvaluacion(request):
    """
    Permite aceptar evaluar un articulo.
    """
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        evaluacion = ArticulosXEvaluador.objects.filter(idArticulo=payload['idArticulo'], idUsuario =payload['idEvaluador']).first()
        if evaluacion != None:
            evaluacion.is_active = True
            evaluacion.save()
        else:
            return Response({'error': True, 'mensaje': 'El articulo no existe o el usuario no fue ingresado como evaluador.'}, status=status.HTTP_400_BAD_REQUEST)
        articulo = Articulo.objects.filter(id=payload['idArticulo']).first()
        rol = Rol.objects.filter(id=3).first()
        if RolxUsuarioxCongreso.objects.filter(idCongreso=articulo.idCongreso.id,idUsuario=evaluacion.idUsuario.id,idRol=rol).count() == 0:
            data = {
                    'idCongreso': articulo.idCongreso.id,
                    'idUsuario': evaluacion.idUsuario.id,
                    'idRol': 3
                }
            serializer = RolxUsuarioxCongresoSerializer(data = data)
            if serializer.is_valid():
                    serializer.save()
        return Response({'error': False, 'mensaje': 'Se acepto la evaluacion.'}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError as identifier:
        return Response({'error': 'El link expiró'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
        return Response({'error': 'Token Inválido'}, status= status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get',
    manual_parameters=[openapi.Parameter('is_active', openapi.IN_QUERY, description="Es activo el evaluador", type=openapi.TYPE_BOOLEAN)],
    responses={ '200': EvaluadorSerializer,
                '400':'Error al devolver la lista de evaluadores.'})
@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def devolverEvaluadores(request):
    """
    Devuelve una lista de los evaluadores actuales (recibe un parametro para saber si son todos o solo los activos).
    Devuelve la calificacion calculada, en ves de los dos atributos del model
    """
    # active = request.GET['is_active']
    try:
        evaluadores = Evaluador.objects.filter(is_active=True)
        data = []
        if len(evaluadores) > 0:
            for ev in evaluadores:
                serializer = EvaluadorCalificacionSerializer(ev)
                usuario = Usuario.objects.filter(id=ev.idUsuario_id).first()
                data_con = serializer.data
                data_con['nombre'] = str(usuario.nombre) + ' ' + str(usuario.apellido)
                data_con['email'] = str(usuario.email)
                sede = Sede.objects.filter(id=usuario.sede.id).first()
                if sede is None:
                    nombreSede = None
                else:
                    nombreSede = sede.nombre
                data_con['sede'] = str(nombreSede)
                data.append(data_con)

        return Response({
                'status': '200',
                'error': '',
                'data': data
        }, status=status.HTTP_200_OK)

    except Exception as e:
         return Response({
                'status': '400',
                'error': e.args,
                'data': []
         }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='delete',
    manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description="id", type=openapi.TYPE_INTEGER)],
    responses={ '200': openapi.Response('El evaluador ha sido dado de baja.'),
                '401': openapi.Response('No posee los permisos para dar de baja al evaluador.'),
                '404': openapi.Response('El usuario no se encuentra asignado como evaluador.')})
@api_view(['DELETE'])
@authentication_classes([AuthenticationChairSecundario])
def eliminarEvaluador(request,id):
    """
    Permite dar de baja un evaluador ( Elimina el evaluador de la tabla evaluadores, pero no de la tabla usuarios.)
    """
    usuario = request.user

    evaluador = Evaluador.objects.filter(idUsuario_id=id).first()
    if evaluador is None:
        return Response({
            'status': '400',
            'error': 'El evaluador no existe.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    if usuario.is_authenticated:
        evaluador.delete()
        return Response({
                'status': '200',
                'error': '',
                'data': "El evaluador ha sido dado de baja."
        }, status=status.HTTP_200_OK)
    else:
        return Response({
                'status': '401',
                'error': 'No posee los permisos para dar de baja al evaluador.',
                'data': []
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def altaItemEvaluacion(request):
    """
    Permite dar de alta un nuevo item de evaluación
    """
    usuario = request.user
    if usuario.is_authenticated:
        serializer = ItemEvaluacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': '401',
            'error': 'No se pudo cargar el item de evaluación: se necesitan permisos de Chair Principal.',
            'data': []
    }, status=status.HTTP_401_UNAUTHORIZED)



@swagger_auto_schema(method='put',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'id':openapi.Schema(type=openapi.TYPE_INTEGER),'idCongreso:':openapi.Schema(type=openapi.TYPE_INTEGER),'nombre:':openapi.Schema(type=openapi.TYPE_STRING)}),
        responses={'200': 'Se subió correctamente el paper','400': openapi.Response('Error')})
@api_view(['PUT'])
@authentication_classes([Authentication])
def editarItemEvaluacion(request):
    """
    Permite editar un item de evaluación
    """
    id = request.data['id']
    try:
        itemEvaluacion = ItemEvaluacion.objects.get(pk=id)
    except ObjectDoesNotExist:
        return Response({
            'status': '400',
            'error': 'No existe el item de evaluación.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
    serializer = ItemEvaluacionSerializer(instance=itemEvaluacion, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    return Response({
        'status': '400',
        'error': 'No se pudo modificar el item de evaluación: faltan datos.',
        'data': []
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def getItemsEvaluacion(request):
    """
    Devuelve una lista con todos los items de evaluación
    """
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    activos = int(request.GET['activos'])
    if activos == 1:
        items = ItemEvaluacion.objects.filter(idCongreso=payload['idCongreso']).filter(is_active=True).all()
    else:
        items = ItemEvaluacion.objects.filter(idCongreso=payload['idCongreso']).all()
    vectorItems = []
    for i in items:
        datos = {
            'id': i.id,
            'nombre': i.nombre,
            'descripcion': i.descripcion,
            'idCongreso': i.idCongreso.id,
            'is_active': i.is_active
        }
        vectorItems.append(datos)
    return Response({
        'status': '200',
        'error': '',
        'data': vectorItems
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([Authentication])
def getItemEvaluacion(request):
    """
    Devuelve el item de evaluación solicitado.
    """
    idItemEvaluacion = request.GET['idItem']
    try:
        itemEvaluacion = ItemEvaluacion.objects.get(pk=idItemEvaluacion)
    except ObjectDoesNotExist:
        return Response({
            'status': '400',
            'error': 'No existe el item de evaluación.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
    serializer = ItemEvaluacionSerializer(instance=itemEvaluacion)

    return Response({
        'status': '200',
        'error': '',
        'data': [serializer.data]
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(method='delete',
manual_parameters=[openapi.Parameter('idItem', openapi.IN_QUERY, description="idItem", type=openapi.TYPE_INTEGER)],
responses={ 200: openapi.Response('Elimina el item solicitado.'),'400': openapi.Response('Error.')})
@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminarItemEvaluacion(request):
    """
    Permite dar de baja lógica un item de evaluación
    """
    usuario = request.user
    idItemEvaluacion = request.GET['idItem']
    itemEvaluacion = ItemEvaluacion.objects.filter(pk=idItemEvaluacion).first()
    if itemEvaluacion is None:
        return Response({
            'status': '400',
            'error': 'El item de evaluación no existe.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    if usuario.is_authenticated:
        itemEvaluacion.is_active = False
        itemEvaluacion.save()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)

    return Response({
        'status': '400',
        'error': 'Error al dar de baja el item de evaluación.',
        'data': []
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([Authentication])
def guardarEvaluacion(request):
    """
    Permite grabar una evaluacion de un articulo
    """
    try:
        token = request.headers['Authorization']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        idArticulo = request.data['idArticulo']
        idCongreso = payload['idCongreso']
        if Congreso.objects.filter(id=idCongreso).count() == 0:
            return Response({
            'status': '400',
            'error': 'No existe el congreso.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        if Articulo.objects.filter(id=idArticulo).count() == 0:
            return Response({
            'status': '400',
            'error': 'No existe el artículo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

        idUsuario = payload['id']
        if ArticulosXEvaluador.objects.filter(idArticulo=idArticulo,idUsuario=idUsuario).count() == 0:
            return Response({
            'status': '400',
            'error': 'El evaluador no tiene asignado ese articulo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        # if EvaluacionXEvaluador.objects.filter(idUsuario=idUsuario,idArticulo=idArticulo).count() > 0:
        #     return Response({
        #     'status': '400',
        #     'error': 'Ya existe esta evaluacion.',
        #     'data': []
        # }, status=status.HTTP_400_BAD_REQUEST)

        evaluacion = ArticulosXEvaluador.objects.filter(idUsuario=idUsuario, idArticulo=idArticulo, idCongreso=idCongreso).first()
        datos = {
            'idUsuario': evaluacion.idUsuario.id,
            'idArticulo': evaluacion.idArticulo.id,
            'estado': 2,
            'recomendacion': request.data['idRecomendacion'],
            'observaciones': request.data['observacion'],
            'observacionInterna': request.data['observacionInterna'],
            'idCongreso': evaluacion.idCongreso.id,
            'is_active': True
        }
        serializer = ArticulosXEvaluadorSerializer(instance=evaluacion, data=datos)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({
                'status': '400',
                'error': 'Error en datos.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        idEvaluacion = evaluacion.id
        items = request.data['itemsEvaluacion']
        items = items.split(',')
        for item in items:
            item_evaluado = item.split('-')
            data = {
                'idItem' : item_evaluado[0],
                'puntuacion' : item_evaluado[1],
                'idEvaluacion' : idEvaluacion
            }
            serializer = ItemEvaluacionXEvaluadorSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                'status': '400',
                'error': e.args,
                'data': []
         }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([Authentication])
def editarEvaluacion(request):
    """
    Permite grabar una evaluacion de un articulo
    """
    try:
        idArticulo = request.GET['idArticulo']
        if Articulo.objects.filter(id=idArticulo).count() == 0:
            return Response({
            'status': '400',
            'error': 'No existe el artículo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        token = request.headers['Authorization']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        idUsuario = payload['id']
        idCongreso = payload['idCongreso']
        evaluacion = ArticulosXEvaluador.objects.filter(idUsuario=idUsuario, idArticulo=idArticulo,
                                                        idCongreso=idCongreso).first()
        if evaluacion == None:
            return Response({
            'status': '400',
            'error': 'No existe la evaluacion',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        # if evaluacion.estado.id != 1:
        #     return Response({
        #     'status': '400',
        #     'error': 'La evaluacion ya no acepta edicion',
        #     'data': []
        # }, status=status.HTTP_400_BAD_REQUEST)
        if request.data['idRecomendacion'] == '' or request.data['idRecomendacion'] is None:
            recomendacion = evaluacion.recomendacion
        else:
            recomendacion = request.data['idRecomendacion']
        if request.data['observacion'] == '' or request.data['observacion'] is None:
            observacion = evaluacion.observaciones
        else:
            observacion = request.data['observacion']
        if request.data['observacionInterna'] == '' or request.data['observacionInterna'] is None:
            observacionInterna = evaluacion.observacionInterna
        else:
            observacionInterna = request.data['observacionInterna']
        datos = {
            'idUsuario': evaluacion.idUsuario.id,
            'idArticulo': evaluacion.idArticulo.id,
            'estado': 2,
            'recomendacion': recomendacion,
            'observaciones': observacion,
            'observacionInterna': observacionInterna,
            'idCongreso': evaluacion.idCongreso.id,
            'is_active': True
        }
        serializer = ArticulosXEvaluadorSerializer(instance=evaluacion, data=datos)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            return Response({
                'status': '400',
                'error': 'Error al editar la instancia de evaluación.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        idEvaluacion = evaluacion.id
        items = request.data['itemsEvaluacion']
        items = items.split(',')
        for item in items:
            item_evaluado = item.split('-')
            item = ItemEvaluacionXEvaluador.objects.filter(idItem=item_evaluado[0],idEvaluacion=idEvaluacion).first()
            if item == None:
                data = {
                    'idItem' : item_evaluado[0],
                    'puntuacion' : item_evaluado[1],
                    'idEvaluacion' : idEvaluacion
                }

                serializer = ItemEvaluacionXEvaluadorSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
            else:
                item.puntuacion = item_evaluado[1]
                item.save()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                'status': '400',
                'error': e.args,
                'data': []
         }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([Authentication])
def enviarEvaluacion(request):
    """
    Permite grabar una evaluacion de un articulo
    """
    try:
        idArticulo = request.data['idArticulo']
        if Articulo.objects.filter(id=idArticulo).count() == 0:
            return Response({
            'status': '400',
            'error': 'No existe el artículo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        token = request.headers['Authorization']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        idUsuario = payload['id']
        if ArticulosXEvaluador.objects.filter(idArticulo=idArticulo,idUsuario=idUsuario).count() == 0:
            return Response({
            'status': '400',
            'error': 'El evaluador no tiene asignado ese articulo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        evaluacion = ArticulosXEvaluador.objects.filter(idUsuario=idUsuario,idArticulo=idArticulo).first()
        if evaluacion == None:
            return Response({
            'status': '400',
            'error': 'No existe la evaluacion',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        if evaluacion.estado.id == 3:
            return Response({
            'status': '400',
            'error': 'Ya fue enviada esta evaluacion',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        evaluacion.estado = EstadoEvaluacion.objects.filter(id=3).first()
        evaluacion.save()
        if ArticulosXEvaluador.objects.filter(idArticulo=idArticulo).count() == 3:
            if ArticulosXEvaluador.objects.filter(idArticulo=idArticulo, estado=3).count() == 3:
                articulo = Articulo.objects.filter(id=idArticulo).first()
                estado = EstadoArticulo.objects.filter(id=4).first()
                articulo.idEstado = estado
                articulo.save()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                'status': '400',
                'error': e.args,
                'data': []
         }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([Authentication])
def getArchivoArticulo(request):
    idArticulo = request.GET['idArticulo']
    try:
        articulo = Articulo.objects.filter(id=idArticulo).first()
        if articulo == None:
            return Response({
            'status': '400',
            'error': 'No existe el artículo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        url = articulo.url
        url_completa = settings.MEDIA_ROOT + url
        archivo = open(url_completa, 'rb')
        response = FileResponse(archivo)
        return response
    except:
        return Response({
            'status': '400',
            'error': 'Error.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([Authentication])
def getEvaluacionesEvaluador(request):
    try:
        token = request.headers['Authorization']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        idCongreso = payload['idCongreso']
        if Congreso.objects.filter(id=idCongreso).count() == 0:
            return Response({
            'status': '400',
            'error': 'No existe el congreso.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        token = request.headers['Authorization']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        idUsuario = payload['id']
        evaluaciones = ArticulosXEvaluador.objects.filter(idCongreso=idCongreso, idUsuario=idUsuario).all()
        datos = []
        print(evaluaciones)
        for evaluacion in evaluaciones:
            serializer = ArticulosXEvaluadorSerializer(instance=evaluacion)
            # if serializer.is_valid():
            data = serializer.data
            articulo = Articulo.objects.filter(id=evaluacion.idArticulo.id).first()
            data["nombreArticulo"] = articulo.nombre
            estado = EstadoEvaluacion.objects.filter(id=evaluacion.estado.id).first()
            data["nombreEstado"] = estado.nombre
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
@authentication_classes([Authentication])
def getEvaluacion(request):

    usuario = request.user
    if usuario.is_authenticated:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        idCongreso = payload['idCongreso']
        idArticulo = request.GET['idArticulo']

        try:
            evaluacion = ArticulosXEvaluador.objects.filter(idCongreso=idCongreso).filter(idArticulo=idArticulo).filter(idUsuario=usuario.id).first()
            detallesEvaluacion = ItemEvaluacionXEvaluador.objects.filter(idEvaluacion=evaluacion.id)
            vectorItems = []
            for i in detallesEvaluacion:
                vectorItems.append({'idItemEvaluacion': i.idItem.id, 'itemEvaluacion': i.idItem.nombre, 'calificacion': i.puntuacion})
            return Response({
                'status': '200',
                'error': '',
                'data': vectorItems
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'status': '400',
                'error': 'Este artículo no tiene evaluaciones asignadas o aún no ha sido evaluado.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={'200': ArticuloSerializer ,'400': 'Error.'})
@api_view(['GET'])
@authentication_classes([Authentication])
def getArticulosEvaluados(request):

    usuario = request.user
    if usuario.is_authenticated:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        idCongreso = payload['idCongreso']
        try:
            chairxsimposio = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso).filter(idUsuario=usuario.id).first()
        except:
            return Response({
                'status': '400',
                'error': 'Usted no es el chair responsable de ningún simposio.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            idSimposio = chairxsimposio.idSimposio.id

        articulos = Articulo.objects.filter(idCongreso=idCongreso).filter(idSimposio=idSimposio).filter(idEstado="4")
        serializer = ArticuloSerializer(articulos, many=True)

        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)


@swagger_auto_schema(method='put',
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties={'idArticulo:': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                             'calificacion:': openapi.Schema(type=openapi.TYPE_INTEGER)}),
                     responses={'200': openapi.Response('Artículo calificado.'), '400': 'Error.'})
@api_view(['PUT'])
@authentication_classes([AuthenticationChairSecundario])
def calificarArticulo(request):
    id = request.data['idArticulo']
    calificacion = request.data['calificacion']
    observacion = request.data['observacion']

    usuario = request.user
    if usuario.is_authenticated:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')

        try:
            articulo = Articulo.objects.get(pk=id)
        except Articulo.DoesNotExist:
            return Response({
                'status': '400',
                'error': 'No existe el artículo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        datos = {
            "id": id,
            "idCongreso": articulo.idCongreso.id,
            "idSimposio": articulo.idSimposio.id,
            "responsable": articulo.responsable,
            "nombre": articulo.nombre,
            "url": articulo.url,
            "observacion": observacion,
            "esta_correcto": True,
            "enviado_corregir": True,
            "idEstado": calificacion
        }
        serializer = ArticuloCompletoSerializer(instance=articulo, data=datos)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)
        return Response({
            'status': '400',
            'error': 'No se pudo calificar el artículo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def getDetalleEvaluacion(request):
    """
    Método GET para la pantalla de evaluación para el Evaluador: devuelve los items a evaluar y sus recomendaciones si las hubiere
    """
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    items = ItemEvaluacion.objects.filter(idCongreso=payload['idCongreso']).filter(is_active=True).all()
    idArticulo = request.GET['idArticulo']
    evaluacion = ArticulosXEvaluador.objects.filter(idArticulo=idArticulo, idUsuario=request.user.id).first()
    vectorItems = []
    for i in items:
        criterio = ItemEvaluacionXEvaluador.objects.filter(idItem=i.id, idEvaluacion=evaluacion.id).first()
        puntuacion = None
        if criterio is not None:
            puntuacion = criterio.puntuacion
        datos = {
            'id': i.id,
            'nombre': i.nombre,
            'descripcion': i.descripcion,
            'idCongreso': i.idCongreso.id,
            'is_active': i.is_active,
            'puntuacion': puntuacion
        }
        vectorItems.append(datos)
    return Response({
        'status': '200',
        'error': '',
        'data': vectorItems
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(method='get', responses={'200': ArticulosXEvaluadorSerializer ,'400': 'Error.'})
@api_view(['GET'])
@authentication_classes([Authentication])
def getDetalleEvaluaciones(request):

    usuario = request.user
    if usuario.is_authenticated:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        idCongreso = payload['idCongreso']
        idArticulo = request.GET['idArticulo']

        try:
            evaluaciones = ArticulosXEvaluador.objects.filter(idCongreso=idCongreso).filter(idArticulo=idArticulo)
            vectorEvaluaciones = []
            for e in evaluaciones:
                detallesEvaluacion = ItemEvaluacionXEvaluador.objects.filter(idEvaluacion=e.id)
                vectorItems = []
                for i in detallesEvaluacion:
                    vectorItems.append({'idItemEvaluacion': i.idItem.id, 'itemEvaluacion': i.idItem.nombre, 'calificacion': i.puntuacion})
                nombre = e.idUsuario.nombre + ' ' + e.idUsuario.apellido
                recomendacion = e.recomendacion.nombre
                evaluacion = {'idEvaluador': e.idUsuario.id, 'evaluador': nombre, 'recomendacion': recomendacion,
                              'observacion': e.observaciones, 'observacionInterna': e.observacionInterna, 'itemsEvaluados': vectorItems}
                vectorEvaluaciones.append(evaluacion)
            return Response({
                'status': '200',
                'error': '',
                'data': vectorEvaluaciones
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'status': '400',
                'error': 'Este artículo no tiene evaluaciones asignadas o aún no ha sido evaluado.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='put',
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties={'idEvaluador:': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                             'calificacion:': openapi.Schema(type=openapi.TYPE_INTEGER)}),
                     responses={'200': openapi.Response('Evaluador calificado.'), '400': 'Error.'})
@api_view(['PUT'])
@authentication_classes([Authentication])
def calificarEvaluador(request):
    idEvaluador = request.data['idEvaluador']
    calificacion = request.data['calificacion']

    usuario = request.user
    if usuario.is_authenticated:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')

        try:
            evaluador = Evaluador.objects.get(pk=idEvaluador)
        except Evaluador.DoesNotExist:
            return Response({
                'status': '400',
                'error': 'No existe el evaluador.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        datos = {
            "idUsuario": idEvaluador,
            "is_active": True,
            "califAcumulada": int(evaluador.califAcumulada + int(calificacion)),
            "califContador": int(evaluador.califContador + 1)
        }
        serializer = EvaluadorSerializer(instance=evaluador, data=datos)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)
        return Response({
            'status': '400',
            'error': 'No se pudo calificar al evaluador.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get',
manual_parameters=[openapi.Parameter('idArticulo', openapi.IN_QUERY, description="idArticulo", type=openapi.TYPE_INTEGER)],
responses={ 200: openapi.Response('Devuelve una lista de los autores x articulo (no me sale todavia mostrarla aca)'),'400': openapi.Response('Error.')})
@api_view(['GET'])
@authentication_classes([Authentication])
def listaAutoresXArticulo(request):
    """
    Devuelve una lista de autores de x articulo.
    """
    idArticulo = request.GET['idArticulo']
    autores_reg = AutorXArticulo.objects.filter(idArticulo = idArticulo).all()
    autores_sin_reg = AutorXArticuloSinUsuario.objects.filter(idArticulo = idArticulo).all()

    data_reg = []
    for aut in autores_reg:
        autor = aut.idUsuario
        data = {
            'id': autor.id,
            'email':autor.email
        }
        data_reg.append(data)

    data_sinreg = []
    for aut in autores_sin_reg:
        autor = aut.mailUsuario
        data_sinreg.append(autor)

    respuesta = {
        'Autores_Regitrados' : data_reg,
        'Autores_No_Regitrados' : data_sinreg,
    }

    return Response({
        'status': '200',
        'error': '',
        'data': respuesta
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(method='delete',
manual_parameters=[openapi.Parameter('idArticulo', openapi.IN_QUERY, description="idArticulo", type=openapi.TYPE_INTEGER)],
responses={'200': openapi.Response('Se elimino correctamente la entrega del articulo..'),'400': openapi.Response('No se pudo eliminar el articulo.')})
@api_view(['DELETE'])
@authentication_classes([Authentication])
def deleteEntrega(request):
    """ Permite eliminar una entrega """
    token = request.headers['Authorization']
    idArticulo = request.GET['idArticulo']

    try:
        payload = jwt.decode(token, settings.SECRET_KEY)

        usuario = Usuario.objects.filter(id=payload['id']).first()

        articulo = Articulo.objects.filter(responsable=usuario.email, id=idArticulo).first()
        if articulo != None:
            autores = AutorXArticulo.objects.filter(idArticulo=idArticulo).all()
            autores_sin_usuario = AutorXArticuloSinUsuario.objects.filter(idArticulo=idArticulo).all()
            #Elimino el articulo y sus autores
            autores.delete()
            autores_sin_usuario.delete()
            articulo.delete()
            os.remove(settings.MEDIA_ROOT + articulo.url)
            return Response({
                'status': '200',
                'error': 'Se elimino correctamente la entrega del articulo.',
                'data': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': '400',
                'error': 'No se pudo eliminar el articulo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': '500',
            'error': e.args,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

@swagger_auto_schema(method='get',
responses={'200': openapi.Response('Datos del evaluador por simposio.'),'400': openapi.Response('Error')})
@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getEvaluadoresBySimposio(request):
    """
    Devuelve los evaluadores de un simposio
    """
    idChair = request.GET['idChair']
    try:
        chair = SimposiosxCongreso.objects.filter(id=idChair).first()
        simposio = Simposio.objects.filter(id=chair.idSimposio.id).first()
        evaluadores = SimposiosXEvaluador.objects.filter(idSimposio=simposio.id).all()
        respuesta = []
        for evaluador in evaluadores:
            datos = Evaluador.objects.filter(id=evaluador.idUsuario.id).first()
            usuario = Usuario.objects.filter(id=datos.idUsuario.id).first()
            data = {
                'idEvaluador':usuario.id,
                'idSimposio':simposio.id,
                'nombreEv':usuario.nombre,
                'apellidoEv': usuario.apellido,
                'nomSimp': simposio.nombre,
                'descSimp': simposio.descripcion
            }
            respuesta.append(data)
            return Response({
            'status': '200',
            'error': '',
            'data': respuesta
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={'200': ArticulosXEvaluadorSerializer ,'400': 'Error.'})
@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getArticulosEvaluadoresCompleto(request):

    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    idCongreso = payload['idCongreso']
    chairxsimposio = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso).filter(idUsuario=payload["id"]).first()
    try:
        simposioC = SimposiosxCongreso.objects.filter(idCongreso=idCongreso,idSimposio=chairxsimposio.idSimposio).first()
        articulos = Articulo.objects.filter(idCongreso=idCongreso,idSimposio=simposioC.id).all()
        simposio = simposioC.idSimposio
        if len(articulos) > 0:
            respuesta = []
            for art in articulos:
                usuarioResponsable = Usuario.objects.filter(email=art.responsable).first()
                sedeArticulo = Sede.objects.filter(id=usuarioResponsable.sede.id).first()
                cantidad = 3
                estado = art.idEstado
                eval = []
                evaluadores = ArticulosXEvaluador.objects.filter(idArticulo=art.id).all()
                for evaluador in evaluadores:
                    usuario = evaluador.idUsuario
                    usuarioAux = Usuario.objects.filter(id=usuario.id).first()
                    sedeEvaluador = Sede.objects.filter(id=usuarioAux.sede.id).first()
                    if ArticulosXEvaluador.objects.filter().exists():
                        ev = ArticulosXEvaluador.objects.filter(idArticulo=art.id,idUsuario=usuario.id).first()
                        estado = ev.estado
                        datos_eval = {
                            "nombre": usuario.nombre,
                            "id": usuario.id,
                            "apellido": usuario.apellido,
                            "is_active": evaluador.is_active,
                            "idEstadoEvaluacion": estado.id,
                            "descripcionEstadoEvaluacion": estado.descripcion,
                            "nombreEstadoEvaluacion": estado.nombre,
                            "sedeEvaluador":sedeEvaluador.nombre
                        }
                        eval.append(datos_eval)
                    else:
                        datos_eval = {
                            "nombre": usuario.nombre,
                            "id": usuario.id,
                            "apellido": usuario.apellido,
                            "is_active": evaluador.is_active,
                            "idEstadoEvaluacion": None,
                            "descripcionEstadoEvaluacion": "Aun no comenzó su evaluación",
                            "nombreEstadoEvaluacion": "Sin Evaluacion",
                            "sedeEvaluador":sedeEvaluador.nombre
                        }
                        eval.append(datos_eval)
                    cantidad = cantidad - 1
                if cantidad > 0:
                    for i in range(cantidad):
                        eval.append({"ideval": None})
                data = {
                "idArticulo": art.id,
                "estadoArticuloNombre": estado.nombre,
                "estadoArticuloDescripcion": estado.descripcion,
                "nombreArticulo": art.nombre,
                "idSimposio":simposio.id,
                "nombreSimposio": simposio.nombre,
                "descSimposio": simposio.descripcion,
                "evaluadores":eval,
                "sedeArticulo":sedeArticulo.nombre
                }
                respuesta.append(data)
            return Response({
            'status': '200',
            'error': '',
            'data': respuesta
        }, status=status.HTTP_200_OK)
        else:
            return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={'200': ArticulosXEvaluadorSerializer ,'400': 'Error.'})
@api_view(['GET'])
@authentication_classes([AuthenticationChairPrincipal])
def getArticulosCameraReady(request):

    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    idCongreso = payload['idCongreso']
    # chairxsimposio = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso).filter(idUsuario=payload["id"]).first()
    try:
        # simposioC = SimposiosxCongreso.objects.filter(idCongreso=idCongreso,idSimposio=chairxsimposio.idSimposio).first()
        articulos = Articulo.objects.filter(idCongreso=idCongreso).all()
        # simposio = simposioC.idSimposio
        if len(articulos) > 0:
            respuesta = []
            for art in articulos:
                vectorAutores = []
                autores = AutorXArticulo.objects.filter(idArticulo=art.id).all()
                for a in autores:
                    dataAutor = {
                        "id": a.idUsuario.id,
                        "nombre": a.idUsuario.nombre,
                        "apellido": a.idUsuario.apellido,
                        "email": a.idUsuario.email,
                        "idSede": a.idUsuario.sede.id,
                        "nombreSede": a.idUsuario.sede.nombre
                    }
                    vectorAutores.append(dataAutor)
                if art.url_camera_ready is not None:
                    autor = Usuario.objects.filter(email=art.responsable).first()
                    estado = art.idEstado
                    data = {
                    "idArticulo": art.id,
                    "idEstado": estado.id,
                    "estadoArticuloNombre": estado.nombre,
                    "estadoArticuloDescripcion": estado.descripcion,
                    "nombreArticulo": art.nombre,
                    "idSimposio": art.idSimposio.idSimposio.id,
                    "nombreSimposio": art.idSimposio.idSimposio.nombre,
                    "descSimposio": art.idSimposio.idSimposio.descripcion,
                    "idSimposio": autor.sede.id,
                    "sedeArticulo": autor.sede.nombre,
                    "urlCameraReady": art.url_camera_ready,
                    "autores": vectorAutores
                    }
                    respuesta.append(data)
            return Response({
            'status': '200',
            'error': '',
            'data': respuesta
        }, status=status.HTTP_200_OK)
        else:
            return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={'200': ArticulosXEvaluadorSerializer ,'400': 'Error.'})
@api_view(['GET'])
def getArticulosCameraReadyPublico(request):

    idCongreso = request.GET['idCongreso']
    # chairxsimposio = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso).filter(idUsuario=payload["id"]).first()
    try:
        # simposioC = SimposiosxCongreso.objects.filter(idCongreso=idCongreso,idSimposio=chairxsimposio.idSimposio).first()
        articulos = Articulo.objects.filter(idCongreso=idCongreso).all()
        # simposio = simposioC.idSimposio
        if len(articulos) > 0:
            respuesta = []
            for art in articulos:
                vectorAutores = []
                autores = AutorXArticulo.objects.filter(idArticulo=art.id).all()
                for a in autores:
                    dataAutor = {
                        "id": a.idUsuario.id,
                        "nombre": a.idUsuario.nombre,
                        "apellido": a.idUsuario.apellido,
                        "email": a.idUsuario.email,
                        "idSede": a.idUsuario.sede.id,
                        "nombreSede": a.idUsuario.sede.nombre
                    }
                    vectorAutores.append(dataAutor)
                if art.url_camera_ready is not None:
                    autor = Usuario.objects.filter(email=art.responsable).first()
                    estado = art.idEstado
                    data = {
                    "idArticulo": art.id,
                    "idEstado": estado.id,
                    "estadoArticuloNombre": estado.nombre,
                    "estadoArticuloDescripcion": estado.descripcion,
                    "nombreArticulo": art.nombre,
                    "idSimposio": art.idSimposio.idSimposio.id,
                    "nombreSimposio": art.idSimposio.idSimposio.nombre,
                    "descSimposio": art.idSimposio.idSimposio.descripcion,
                    "idSimposio": autor.sede.id,
                    "sedeArticulo": autor.sede.nombre,
                    "urlCameraReady": art.url_camera_ready,
                    "autores": vectorAutores
                    }
                    respuesta.append(data)
            return Response({
            'status': '200',
            'error': '',
            'data': respuesta
        }, status=status.HTTP_200_OK)
        else:
            return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={'200': ArticulosXEvaluadorSerializer ,'400': 'Error.'})
@api_view(['GET'])
@authentication_classes([AuthenticationChairPrincipal])
def getArticulosParaEventos(request):

    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    idCongreso = payload['idCongreso']
    idSimposio = request.GET['idSimposio']
    # chairxsimposio = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso).filter(idUsuario=payload["id"]).first()
    try:
        simposioC = SimposiosxCongreso.objects.filter(idCongreso=idCongreso,idSimposio=idSimposio).first()
        articulos = Articulo.objects.filter(idCongreso=idCongreso, idSimposio=simposioC.id).all()
        # simposio = simposioC.idSimposio
        if len(articulos) > 0:
            respuesta = []
            for art in articulos:
                evento = Evento.objects.filter(idCongreso=idCongreso, idSimposio=idSimposio, idArticulo=art.id).first()
                if evento is not None:
                    continue
                vectorAutores = []
                autores = AutorXArticulo.objects.filter(idArticulo=art.id).all()
                for a in autores:
                    dataAutor = {
                        "id": a.idUsuario.id,
                        "nombre": a.idUsuario.nombre,
                        "apellido": a.idUsuario.apellido,
                        "email": a.idUsuario.email,
                        "idSede": a.idUsuario.sede.id,
                        "nombreSede": a.idUsuario.sede.nombre
                    }
                    vectorAutores.append(dataAutor)
                if art.url_camera_ready is not None:
                    autor = Usuario.objects.filter(email=art.responsable).first()
                    estado = art.idEstado
                    data = {
                    "idArticulo": art.id,
                    "idEstado": estado.id,
                    "estadoArticuloNombre": estado.nombre,
                    "estadoArticuloDescripcion": estado.descripcion,
                    "nombreArticulo": art.nombre,
                    "idSimposio": art.idSimposio.idSimposio.id,
                    "nombreSimposio": art.idSimposio.idSimposio.nombre,
                    "descSimposio": art.idSimposio.idSimposio.descripcion,
                    "idSimposio": autor.sede.id,
                    "sedeArticulo": autor.sede.nombre,
                    "urlCameraReady": art.url_camera_ready,
                    "autores": vectorAutores
                    }
                    respuesta.append(data)
            return Response({
            'status': '200',
            'error': '',
            'data': respuesta
        }, status=status.HTTP_200_OK)
        else:
            return Response({
            'status': '400',
            'error': 'No existen articulos en el simposio para este congreso.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([AuthenticationChairSecundario])
def asignarArticuloEvaluadorMasivo(request):
    """
    Permite asignar a distintos artículos sus evaluadores.
    """
    try:
        datos = request.data
        respuesta = []
        for i in datos:
            idEvaluadores = i['idEvaluadores']
            articulo = i['articulo']
            idCongreso = i['idCongreso']
            if not Congreso.objects.filter(id=idCongreso).exists():
                return Response({
                'status': '400',
                'error': 'El congreso no existe.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
            for idEvaluador in idEvaluadores:
                if not Evaluador.objects.filter(idUsuario=idEvaluador).exists():
                    return Response({
                        'status': '400',
                        'error': 'El usuario no es evaluador.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                #evaluador_buscado = Evaluador.objects.filter(id=idEvaluador).first()
                #usuario = evaluador_buscado.idUsuario

                if not Articulo.objects.filter(id=articulo).exists():
                    return Response({
                        'status': '400',
                        'error': 'El artículo no existe.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                if ArticulosXEvaluador.objects.filter(idCongreso=idCongreso).filter(idUsuario=idEvaluador).filter(idArticulo=articulo).exists():
                    return Response({
                        'status': '400',
                        'error': 'El artículo ya está asignado al evaluador.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                serializer = ArticulosXEvaluadorSerializer(
                    data={'idCongreso': idCongreso, 'idUsuario': idEvaluador, 'idArticulo': articulo, 'is_active':False})
                if serializer.is_valid():
                    serializer.save()
                # -------------------ENVIO DE MAIL--------------------------------##
                current_site = config('URL_FRONT_DEV')
                relative_link = 'cancelacionEvaluacionPaper/'
                aceptar_link = 'aceptacionEvaluacionPaper/'
                payload = {
                    'idEvaluador': idEvaluador,
                    'idArticulo': articulo,
                    'idCongreso': idCongreso,
                    'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
                    'iat': datetime.datetime.utcnow()
                }
                token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
                url_envio = current_site + relative_link + token
                url_aceptar = current_site + aceptar_link + token
                congre = Congreso.objects.filter(id=idCongreso).first()
                usuario = Usuario.objects.filter(id=idEvaluador).first()
                datosInvitacion = {
                    'año': str(congre.año),
                    'nombreCongreso': str(congre.nombre),
                    'email': usuario.email,
                    'linkRechazo': url_envio,
                    'linkAceptar': url_aceptar
                }
                send_mail_evaluador(datosInvitacion)
                respuesta.append(serializer.data)
        return Response({
            'status': '200',
            'error': '',
            'data': respuesta
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@authentication_classes([AuthenticationChairSecundario])
def asignarPoolEvaluadores(request):
    """
    Permite asignar un pool de evaluadores para un simposio de un congreso determinado.
    """
    try:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        chair = payload['id']
        idCongreso = payload['idCongreso']
        datos = request.data["evaluadores"]
        for evaluador in datos:
            if not EvaluadorXCongresoXChair.objects.filter(idCongreso=idCongreso,idEvaluador=evaluador,idChair=chair).exists():
                data_pool = {
                    "idCongreso":idCongreso,
                    "idEvaluador":evaluador,
                    "idChair":chair
                }
                serializer = EvaluadorXCongresoXChairSerializer(data=data_pool)
                if serializer.is_valid():
                    serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([AuthenticationChairSecundario])
def eliminarEvaluadorPoolEvaluadores(request):
    """
    Permite eliminar un evaluador de un pool de evaluadores
    """
    try:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        chair = payload['id']
        idCongreso = payload['idCongreso']
        evaluador = request.GET["idEvaluador"]
        if EvaluadorXCongresoXChair.objects.filter(idCongreso=idCongreso,idEvaluador=evaluador,idChair=chair).exists():
            ev_pool = EvaluadorXCongresoXChair.objects.filter(idCongreso=idCongreso,idEvaluador=evaluador,idChair=chair).first()
            ev_pool.delete()
            return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                        'status': '400',
                        'error': "No existe el evaluador en el pool de evaluadores del chair",
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getPoolEvaluadores(request):

    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    chair = payload['id']
    idCongreso = payload['idCongreso']
    data = []
    try:
        evaluadores = EvaluadorXCongresoXChair.objects.filter(idCongreso=idCongreso,idChair=chair).all()
        for evaluador in evaluadores:
            datos_eval = evaluador.idEvaluador
            usuario = Usuario.objects.filter(id=datos_eval.id).first()
            sede = Sede.objects.filter(id=usuario.sede.id).first()
            datos = {
                "idEvaluador":datos_eval.id,
                "nombreEv": datos_eval.nombre,
                "apellidoEv": datos_eval.apellido,
                "sedeEvaluador":sede.nombre
            }
            data.append(datos)
        return Response({
                'status': '200',
                'error': '',
                'data': data
            }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getEvaluadoresSimposio(request):

    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    chair = payload['id']
    idCongreso = payload['idCongreso']
    data = []
    try:
        simposioxcongreso = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso,idUsuario=chair).first()
        simposio = simposioxcongreso.idSimposio
        evaluadores = SimposiosXEvaluador.objects.filter(idSimposio=simposio.id).all()
        if len(evaluadores) > 0:
            for evaluador in evaluadores:
                datos_eval = evaluador.idUsuario
                datos = {
                    "idEvaluador":datos_eval.id,
                    "nombreEv": datos_eval.nombre,
                    "apellidoEv": datos_eval.apellido
                }
                data.append(datos)
            return Response({
                    'status': '200',
                    'error': '',
                    'data': data
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                    'status': '200',
                    'error': '',
                    'data': []
                }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getEvaluadoresFueraSimposio(request):

    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    chair = payload['id']
    idCongreso = payload['idCongreso']
    data = []
    try:
        simposioxcongreso = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso,idUsuario=chair).first()
        simposio = simposioxcongreso.idSimposio
        evaluadores_simposio = SimposiosXEvaluador.objects.filter(idSimposio=simposio.id).all()
        id_evitar = []
        if len(evaluadores_simposio) > 0:
            for evaluador in evaluadores_simposio:
                datos_eval = evaluador.idUsuario
                id_evitar.append(datos_eval.id)
            evaluadores = Evaluador.objects.filter(is_active=True).exclude(idUsuario__in=id_evitar).all()
        else:
            evaluadores = Evaluador.objects.filter().all()
        if len(evaluadores) > 0:
            for evaluador in evaluadores:
                print(evaluador.id)
                datos = {
                    "idEvaluador":evaluador.idUsuario.id,
                    "nombreEv": evaluador.idUsuario.nombre,
                    "apellidoEv": evaluador.idUsuario.apellido
                }
                data.append(datos)
            return Response({
                    'status': '200',
                    'error': '',
                    'data': data
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                    'status': '400',
                    'error': 'No existen evaluadores que no pertenezcan a este simposio',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([AuthenticationChairSecundario])
def getArticulosXChair(request):
    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    idChair = payload['id']
    idCongreso = payload['idCongreso']
    try:
        simposio = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso).filter(idUsuario=idChair).first()

        if simposio is not None:
            simposio = simposio.idSimposio
            simposioxcongreso = SimposiosxCongreso.objects.filter(idSimposio=simposio,idCongreso=idCongreso).first()
            print('filtros:',idCongreso,simposioxcongreso.id)
            articulos = Articulo.objects.filter(idCongreso=idCongreso).filter(idSimposio=simposioxcongreso.id).exclude(idEstado=1).exclude(idEstado=2).exclude(idEstado=3).all()
            print('ARTICULOS:',articulos)
            vectorArticulos = []
            for a in articulos:
                evaluaciones = ArticulosXEvaluador.objects.filter(idArticulo=a.id).all()
                vectorEvaluaciones = []
                for e in evaluaciones:
                    nombre = e.idUsuario.nombre + ' ' + e.idUsuario.apellido
                    if e.recomendacion is None:
                        recomendacion = None
                    else:
                        recomendacion = e.recomendacion.nombre

                    if e.observaciones is None:
                        observacion = None
                    else:
                        observacion = e.observaciones

                    evaluacion = {
                        'idEvaluacion': e.id,
                        'idEvaluador': e.idUsuario.id,
                        'evaluador': nombre,
                        'recomendacion': recomendacion,
                        'observacion': observacion,
                        'observacionInterna': e.observacionInterna
                    }
                    vectorEvaluaciones.append(evaluacion)

                articulo = {
                    'id': a.id,
                    'nombre': a.nombre,
                    'idSimposio': a.idSimposio.id,
                    'idCongreso': a.idCongreso.id,
                    'responsable': a.responsable,
                    'url': a.url,
                    'idEstado': a.idEstado.id,
                    'estado': a.idEstado.nombre,
                    'observacion': a.observacion,
                    'evaluaciones': vectorEvaluaciones
                }
                vectorArticulos.append(articulo)
            # serializer = ArticuloCompletoSerializer(articulos, many=True)

            datos = {
                'idSimposio': simposio.id,
                'simposio': simposio.nombre,
                'articulos': vectorArticulos
            }
            return Response({
                'status': '200',
                'error': '',
                'data': [datos]
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': '400',
                'error': "El simposio no existe en el congreso.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([Authentication])
def realizarEntregaFinal(request):
    """
    Permite subir un paper a un congreso a un simposio determinado.
    """
    idArticulo = request.data['idArticulo']
    archivo = request.FILES['articulo']
    autores = request.data['autores']
    autores = autores.split(',')
    try:
        aprobado = EstadoArticulo.objects.filter(id=6).get()
        reentrega = EstadoArticulo.objects.filter(id=8).get()
        articulo = Articulo.objects.get(id = idArticulo)

        if ((articulo.idEstado != aprobado) and (articulo.idEstado != reentrega)):
            return Response({
                'status': '400',
                'error': 'Error, el articulo no fue aprobado para subir la versión final',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        idUsuario = payload['id']        
        usuario = Usuario.objects.filter(id=idUsuario).first()
        if articulo.responsable != usuario.email:
            return Response({
                    'status': '400',
                    'error': 'Error, no es responsable del articulo',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST) 
        if archivo == None:
            return Response({
                'status': '400',
                'error': 'No se subió el archivo.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        extension_archivo = request.FILES['articulo'].name.split('.')[-1]
        if extension_archivo.upper() != 'PDF':
            return Response({
                'status': '400',
                'error': 'El archivo no tiene el formato PDF.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        filename =  'A_' + str(articulo.idCongreso.id) + '_' + str(articulo.idSimposio.id) + '_' + str(idArticulo) + '_' + 'VF' + ".pdf"
        fs = FileSystemStorage()
        if fs.exists(filename):
            return Response({
                'status': '400',
                'error': 'Error.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        file = fs.save(filename, archivo)
        file_url = filename
        articulo.url_camera_ready = filename
        articulo.save()

        for autor in autores:
            if Usuario.objects.filter(email=autor).exists():
                idAutor = Usuario.objects.get(email=autor).id
                if not AutorXArticulo.objects.filter(idUsuario=idAutor,idArticulo=idArticulo).exists():
                    datos = {
                    "idArticulo": idArticulo,
                    "idUsuario": idAutor,
                    }
                    serializer_autor = AutorxArticuloSerializer(data=datos)
                    if serializer_autor.is_valid():
                        serializer_autor.save()

        return Response({
                'status': '200',
                'error': '',
                'data': "Se guardo con éxito el camera ready"
            }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                'status': '500',
                'error': e.args,
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([Authentication])
def getArchivoArticuloCameraReady(request):
    idArticulo = request.GET['idArticulo']
    try:
        articulo = Articulo.objects.filter(id=idArticulo).first()
        if articulo == None:
            return Response({
            'status': '400',
            'error': 'No existe el artículo.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        url = articulo.url_camera_ready
        url_completa = settings.MEDIA_ROOT + url
        archivo = open(url_completa, 'rb')
        response = FileResponse(archivo)
        return response
    except:
        return Response({
            'status': '400',
            'error': 'Error.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def getSimposiosxEvaluador(request):
    idEvaluador = request.user.id
    simposios = SimposiosXEvaluador.objects.filter(idUsuario=idEvaluador).all()
    datos = []
    for s in simposios:
        nombreEvaluador = s.idUsuario.nombre + ' ' + s.idUsuario.apellido
        simposio = {
            'idEvaluador':s.idUsuario.id,
            'nombreEvaluador': nombreEvaluador,
            'idSimposio': s.idSimposio.id,
            'nombreSimposio': s.idSimposio.nombre,
            'descripcionSimposio': s.idSimposio.descripcion
        }
        datos.append(simposio)
    return Response({
        'status': '200',
        'error': '',
        'data': datos
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminarSimposioEvaluador(request):
    """
    Permite dar de baja una preferencia de simposio por parte de un evaluador.
    """
    usuario = request.user
    idSimposio = request.GET['idSimposio']

    simposio = SimposiosXEvaluador.objects.filter(idUsuario=usuario.id, idSimposio=idSimposio).first()
    
    if simposio is None:
        return Response({
            'status': '400',
            'error': 'El simposio no está en su lista de preferencias.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    evaluador = Evaluador.objects.filter(idUsuario=usuario.id).first()
    if evaluador != None:
        simposio.delete()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)

    return Response({
        'status': '400',
        'error': 'Error al dar de baja la preferencia de simposio.',
        'data': []
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def devolverEvaluadoresCongreso(request):
    """
    Devuelve una lista de los evaluadores actuales (recibe un parametro para saber si son todos o solo los activos).
    Devuelve la calificacion calculada, en ves de los dos atributos del model
    """
    idCongreso = request.GET['idCongreso']
    try:
        evaluadores = RolxUsuarioxCongreso.objects.filter(idCongreso=idCongreso, idRol=3)
        data = []
        if len(evaluadores) > 0:
            for ev in evaluadores:
                usuario = Usuario.objects.filter(id=ev.idUsuario.id).first()
                sede = Sede.objects.filter(id=usuario.sede.id).first()
                if sede is None:
                    nombreSede = None
                else:
                    nombreSede = sede.nombre
                evaluador = {
                    'nombre': str(usuario.nombre) + ' ' + str(usuario.apellido),
                    'sede': nombreSede
                }
                data.append(evaluador)

        return Response({
                'status': '200',
                'error': '',
                'data': data
        }, status=status.HTTP_200_OK)

    except Exception as e:
         return Response({
                'status': '400',
                'error': e.args,
                'data': []
         }, status=status.HTTP_400_BAD_REQUEST)

      
@api_view(['GET'])
@authentication_classes([Authentication])
def esEvaluador(request):
    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    idUusario = payload['id']
    evaluador = Evaluador.objects.filter(idUsuario=idUusario, is_active=True).first()
    if evaluador is None:
        return Response({
            'status': '200',
            'error': '',
            'data': False
        }, status=status.HTTP_200_OK)
    return Response({
        'status': '200',
        'error': '',
        'data': True
    }, status=status.HTTP_200_OK)


def registrarCancelacion(datos):
    serializer = EvaluacionCanceladaSerializer(data=datos)
    if serializer.is_valid():
            serializer.save()