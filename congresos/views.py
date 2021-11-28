#Agregar estas 2 lineas cuando exista el problema de los imports entre primos

# from backendTesis.usuarios.authentication import AuthenticationChairPrincipal

import sys
from django.http.response import HttpResponse
from .tasks import *
from django.core.exceptions import ObjectDoesNotExist
sys.path.append('..')
from datetime import date, datetime, timedelta
from django.db.models.query import FlatValuesListIterable
from django.utils.functional import partition
from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
#from ..usuarios.models import Usuario
from .models import *
from articulos.serializers import *
from articulos.models import *
#import jwt,datetime
from usuarios.authentication import *
from articulos.serializers import *
from usuarios.serializers import *
from rest_framework.decorators import api_view, authentication_classes
from usuarios.models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import jwt
# Create your views here.

@swagger_auto_schema(method='get', responses={200: openapi.Response('Successful operation')})
@api_view(['GET'])
def apiOverView(request):
    """
    Muestra la vista principal de la api, con todos sus endpoints.
    """
    api_urls = {
        'Lista de congresos':'/lista-congresos/',
        'Crear Congreso':'/crear/',
        'Editar Congreso':'/editar/',
        'Eliminar Congreso':'/eliminar/',
        'Activar Congreso':'/activar/',
    }
    return Response(api_urls)

@swagger_auto_schema(method='post', request_body= CongresoSerializer, 
                    responses={'200': openapi.Response('Congreso creado.', CongresoSerializer), '400': 'Error.'})                
@api_view(['POST'])
@authentication_classes([Authentication])
def crearCongreso(request):
    """
    Metodo para crear un Congreso
    """
    try:
        usuario = request.user
        if usuario.is_authenticated and usuario.is_superuser:
            
            serializer = CongresoSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                congres = Congreso.objects.filter(sede=serializer.validated_data["sede"], año=serializer.validated_data["año"])
                if congres.count() > 0:
                    return Response({
                        'status': '400',
                        'error': 'El congreso ya existe',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                email_chair = serializer.validated_data["chairPrincipal"]
                email_coord = serializer.validated_data["coordLocal"]
                usuario = Usuario.objects.filter(email=email_chair).first()
                if usuario is None:
                    return Response({
                        'status': '400',
                        'error': 'El correo del Chair no se encuentra registrado en el sitio.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not usuario.is_verified:
                    return Response({
                        'status': '400',
                        'error': 'La Cuenta del Chair no se encuentra activa.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
                usuario2 = Usuario.objects.filter(email=email_coord).first()
                if usuario2 is None:
                    return Response({
                        'status': '400',
                        'error': 'El correo del asistente no se encuentra registrado en el sitio.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not usuario2.is_verified:
                    return Response({
                        'status': '400',
                        'error': 'La Cuenta del asistente no se encuentra activa.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                #Asignar Roles a los dos administradores
                congreso = Congreso.objects.filter(sede=serializer.validated_data["sede"], año=serializer.validated_data["año"]).first()
                data = {
                    'idCongreso': congreso.id,
                    'idUsuario': usuario.id,
                    'idRol': 1
                }
                serializer = RolxUsuarioxCongresoSerializer(data = data)
                if serializer.is_valid():
                    serializer.save()
                data = {
                    'idCongreso': congreso.id,
                    'idUsuario': usuario2.id,
                    'idRol': 1
                }
                serializer = RolxUsuarioxCongresoSerializer(data = data)
                if serializer.is_valid():
                    serializer.save()
                return Response({
                    'status': '200',
                    'error': '',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                        'status': '400',
                        'error': 'Error.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                        'status': '400',
                        'error': 'No tiene permisos para realizar esta accion.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='post', request_body= CongresoEditarSerializer, 
                                    responses={'200': openapi.Response('Congreso editado.', CongresoEditarSerializer), '400': openapi.Response('Error')})
@api_view(['POST'])
@authentication_classes([Authentication])
def editar(request):
    """
    Permite editar un Congreso.
    """
    try:
        usuario = request.user
        if usuario.is_authenticated and usuario.is_superuser:
            serializer = CongresoEditarSerializer(data=request.data)
            if serializer.is_valid():
                congres = Congreso.objects.filter(sede=serializer.validated_data["sede"], año=serializer.validated_data["año"]).first()
                if  congres == None:
                    return Response({
                        'status': '400',
                        'error': 'El congreso no existe',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                if not congres.is_active:
                    return Response({
                        'status': '400',
                        'error': 'El congreso no esta Activo',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                email_chair = serializer.validated_data["chairPrincipal"]
                email_coord = serializer.validated_data["coordLocal"]
                usuario = Usuario.objects.filter(email=email_chair).first()
                if usuario is None:
                    return Response({
                        'status': '400',
                        'error': 'El correo del Chair no se encuentra registrado en el sitio.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not usuario.is_verified:
                    return Response({
                        'status': '400',
                        'error': 'La Cuenta del Chair no se encuentra activa.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
                usuario2 = Usuario.objects.filter(email=email_coord).first()
                if usuario2 is None:
                    return Response({
                        'status': '400',
                        'error': 'El correo del asistente no se encuentra registrado en el sitio.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not usuario2.is_verified:
                    return Response({
                        'status': '400',
                        'error': 'La Cuenta del asistente no se encuentra activa.',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

                congres.nombre = serializer.validated_data["nombre"]
                congres.sede = serializer.validated_data["sede"]
                congres.año = serializer.validated_data["año"]
                congres.chairPrincipal = serializer.validated_data["chairPrincipal"]
                congres.coordLocal = serializer.validated_data["coordLocal"]
                congres.save()
                return Response({
                    'status': '200',
                    'error': '',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                        'status': '400',
                        'error': serializer.errors,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                        'status': '400',
                        'error': "No tiene permisos para realizar esta accion",
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(method='delete', 
manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description="id", type=openapi.TYPE_INTEGER)], 
responses={200: CongresoCompletoSerializer })
@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminar(request):
    """
    Permite darse baja logica al Congreso.
    """
    try:
        usuario = request.user
        if usuario.is_authenticated and usuario.is_superuser:
            congreso_id = request.GET['id']
            congreso = Congreso.objects.filter(id=congreso_id)
            if congreso.count() == 0:
                return Response({
                    'status': '400',
                    'error': 'El congreso no existe',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                congreso = Congreso.objects.get(id=congreso_id)
            if not congreso.is_active:
                return Response({
                    'status': '400',
                    'error': 'El congreso ya esta en baja',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
            congreso.is_active = False
            congreso.save()
            return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                        'status': '400',
                        'error': 'No tiene permisos para realizar esta accion',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='post', request_body= SimposioSerializer, 
                    responses={'200': openapi.Response('Simposio creado.', SimposioSerializer), '400': 'Error.'})                
@api_view(['POST'])
@authentication_classes([Authentication])
def altaSimposio(request):
    """
    Permite dar de alta un simposio.
    """
    usuario = request.user
    if usuario.is_authenticated:
        if usuario.is_superuser:
            serializer = SimposioSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            simposio_data = serializer.data
            return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': '401',
                'error': 'No se pudo cargar el simposio: se necesitan permisos de administrador.',
                'data': []
        }, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(method='post', 
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'sede:':openapi.Schema(type=openapi.TYPE_INTEGER), 'año:':openapi.Schema(type=openapi.TYPE_INTEGER)}),
    responses={'200': openapi.Response('Congreso activado.'),'400': openapi.Response('Error')})
@api_view(['POST'])
@authentication_classes([Authentication])
def activar(request):
    usuario = request.user
    if usuario.is_authenticated and usuario.is_superuser:
        serializer = CongresoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            congreso = Congreso.objects.filter(sede=serializer.validated_data["sede"], año=serializer.validated_data["año"])
            if congreso.count() == 0:
                return Response({
                        'status': '400',
                        'error': 'El congreso no existe',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                congreso = Congreso.objects.get(sede=serializer.validated_data["sede"], año=serializer.validated_data["año"])
            if congreso.is_active:
                return Response({
                        'status': '400',
                        'error': 'El congreso no esta dado de baja',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)                
            congreso.is_active = True
            congreso.save()
            return Response({
                    'status': '200',
                    'error': '',
                    'data': []
                }, status=status.HTTP_200_OK)
    else:
        return Response({
                        'status': '400',
                        'error': 'No tiene permisos para realizar esta accion',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de congresos completa', CongresoCompletoSerializer)})
@api_view(['GET'])
@authentication_classes([Authentication])
def listaCongresos(request):
    """
    Permite consultar todos los Congresos.
    Permite consultar todos los Congresos.
    """
    try:
        usuario = request.user
        if usuario.is_authenticated:
            congres = Congreso.objects.all()
            data = []
            if len(congres) > 0:
                for cong in congres:
                    serializer = CongresoCompletoSerializer(cong)
                    sede_nombre = Sede.objects.get(id= cong.sede).nombre
                    data_con = serializer.data
                    data_con['nombre_sede'] = sede_nombre
                    data.append(data_con)
                return Response({
                    'status': '200',
                    'error': '',
                    'data': data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                        'status': '400',
                        'error': 'No existen congresos para este usuario',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                        'status': '400',
                        'error': 'No tiene permisos para realizar esta accion',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)            
    except:
        return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de congresos activos completa', CongresoCompletoSerializer)})
@api_view(['GET'])
def listaCongresosActivos(request):
    """
    Permite consultar todos los Congresos Activos.
    """
    try:        
        congres = Congreso.objects.filter(is_active=True).all()
        data = []
        if len(congres) > 0:
            for cong in congres:
                serializer = CongresoCompletoIdSerializer(cong)
                sede_nombre = Sede.objects.get(id= cong.sede).nombre
                data_con = serializer.data
                data_con['nombre_sede'] = sede_nombre
                data.append(data_con)
            return Response({
                'status': '200',
                'error': '',
                'data': data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                    'status': '400',
                    'error': 'No existen congresos para este usuario',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)         
    except:
        return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', 
manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description="id", type=openapi.TYPE_INTEGER) ], 
responses={200: CongresoCompletoSerializer })
@api_view(['GET'])
@authentication_classes([Authentication])
def consultaCongreso(request):
    """
    Permite consultar un congreso en especifico.
    """
    try:
        usuario = request.user
        if usuario.is_authenticated:
            congreso_id = request.GET['id']
            congres = Congreso.objects.filter(id=congreso_id).first()
            if congres != None:
                serializer = CongresoCompletoSerializer(congres)
                sede_nombre = Sede.objects.get(id= congres.sede).nombre
                data = serializer.data
                data['nombre_sede'] = sede_nombre
                return Response({
                    'status': '200',
                    'error': '',
                    'data': [data]
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                        'status': '400',
                        'error': 'No existe el congreso',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                        'status': '400',
                        'error': 'No tiene permisos para realizar esta accion',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get', 
    responses={200: CongresoCompletoSerializer })
@api_view(['GET'])
@authentication_classes([AuthenticationChairPrincipal])
def consultaCongresoXChair(request):
    """
    Permite consultar los congresos de un chair.
    """
    try:
        usuario = request.user
        if usuario.is_authenticated:
            token = request.headers['Authorization']
            if not token:
                raise AuthenticationFailed('Usuario no autenticado!')
            try:
                payload = jwt.decode(token, settings.SECRET_KEY)
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Usuario no autenticado!')
            usuario = Usuario.objects.filter(id=payload['id']).first()
            congres = Congreso.objects.filter(chairPrincipal=usuario.email)
            data = []
            
            if len(congres) > 0:
                for cong in congres:
                    serializer = CongresoCompletoSerializer(cong)
                    sede_nombre = Sede.objects.get(id= cong.sede).nombre
                    data_con = serializer.data
                    data_con['nombre_sede'] = sede_nombre
                    data.append(data_con)
                return Response({
                    'status': '200',
                    'error': '',
                    'data': data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                        'status': '400',
                        'error': 'No existen congresos para este usuario',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                        'status': '400',
                        'error': 'No tiene permisos para realizar esta accion',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
                        'status': '400',
                        'error': 'Error',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', request_body= CongresoFechasSerializer, 
                                     responses={'200': openapi.Response('Fechas designadas.', CongresoFechasSerializer),'400': openapi.Response('Error')})
@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def definirAgenda(request):
    """
    Permite modificar/asignar las fechas correspondientes a un congreso
    """
    
    usuario = request.user
    idCongreso = request.data['id']

    try:
        congreso = Congreso.objects.get(pk=idCongreso)
    except ObjectDoesNotExist:
        raise Http404("El congreso no existe")
    

    serializer = CongresoFechasSerializer(instance=congreso,data=request.data)
    
    if serializer.is_valid() and usuario.is_authenticated:
        serializer.save(raise_exception=True)

        # ------------ CELERY ----------------- #
        # if congreso.task_id != None:
        #     revoke_task_id.delay(congreso.task_id)
        #     revoke_task_id.delay(congreso.task_id_aviso_chair)
        
        # date_time_obj = datetime.strptime(request.data['fechaFinEvaluacion'], '%d/%m/%Y %H:%M:%S')
        # fechaAvisoChair = date_time_obj - timedelta(2)

        # r = send_mail_task.apply_async((congreso.id,),eta=date_time_obj)
        # r2 = send_mail_task_cs.apply_async((congreso.id,),eta=fechaAvisoChair)
        # congreso.task_id = r.task_id
        # congreso.task_id_aviso_chair = r2.task_id
        # congreso.save()
        # ------------------------------------- #
        return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
        
    return Response({
                'status': '401',
                'error': serializer.errors,
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get',manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description="Id del congreso", type=openapi.TYPE_INTEGER)],
                    responses={200: CongresoFechasSerializer})
@api_view(['GET'])
def devolverFechasCongreso(request):
    """
    Devuelve la agenda de un congreso especifico.
    """
    usuario = request.user
    idCongreso = request.GET['id']
    try:
        congreso = Congreso.objects.get(pk=idCongreso)
    except ObjectDoesNotExist:
        raise Http404("El congreso no existe") 

    serializer = CongresoFechasSerializer(congreso)
    return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)


@swagger_auto_schema(method='get',responses={200: CongresoFechasInscripcionSerializer})
@api_view(['GET'])
def devolverFechasInscripcion(request):
    """ Devuelve informacion publica de todos los congresos. """
    try:
        congresos = Congreso.objects.filter(is_active=True).all()
        
        data = []
        if len(congresos) > 0:
            for cong in congresos:
                serializer = CongresoFechasInscripcionSerializer(cong)
                sede_nombre = Sede.objects.get(id=cong.sede).nombre
                data_con = serializer.data
                data_con['nombre_sede'] = sede_nombre
                data.append(data_con)
            return Response({
                'status': '200',
                'error': '',
                'data': data
            }, status=status.HTTP_200_OK)
        return Response({
                'status': '200',
                'error': '',
                'data': []
        }, status=status.HTTP_200_OK)
    except:
        return Response({
                'status': '400',
                'error': 'Ocurrio un error al devolver los congresos.',
                'data': ''
        }, status=status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(method='post', request_body= AulaSerializer,
                    responses={'200': openapi.Response('Aula creada.', AulaSerializer), '400': 'Error.'})
@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def crearAula(request):
    """
    Metodo para crear un Aula
    """
    usuario = request.user
    serializer = AulaSerializer(data=request.data)

    if (serializer.is_valid() and usuario.is_authenticated):
        serializer.save()
        return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
    else:
        return Response({
                'status': '400',
                'error': "Error al crear el aula.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)





@swagger_auto_schema(method='put', request_body= AulaSerializer,
                    responses={'200': openapi.Response('Aula editada.', AulaSerializer), '400': 'Error.'})
@api_view(['PUT'])
@authentication_classes([AuthenticationChairPrincipal])
def editarAula(request):
    """
    Permite editar un Aula (enviar el ID en el body).
    """
    usuario = request.user
    id = request.data['id']

    try:
        aula = Aula.objects.get(pk=id)
    except ObjectDoesNotExist:
        raise Http404("El aula no existe")

    serializer = AulaSerializer(instance=aula,data=request.data)
    
    if serializer.is_valid() and usuario.is_authenticated:
        serializer.save()
        return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)

    return Response({
                'status': '400',
                'error': "Error al editar el aula.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('idSede', openapi.IN_QUERY, description="Id de sede", type=openapi.TYPE_INTEGER)],
                    responses={'200': openapi.Response('Lista de aulas en activo', AulaSerializer)})
@api_view(['GET'])
@authentication_classes([AuthenticationChairPrincipal])
def devolverAulas(request):
    """
    Devuelve la lista completa de aulas.
    """
    sede_id = request.GET['idSede']
    try:
        aulas = Aula.objects.filter(is_active=True).filter(sede=sede_id).all()
        serializer = AulaSerializer(aulas, many=True)
        return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
    except:
         return Response({
                'status': '400',
                'error': "Error al devolver la lista de aulas.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)




@swagger_auto_schema(method='post', 
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idCongreso:':openapi.Schema(type=openapi.TYPE_INTEGER), 'aulas:':openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))}),
        responses={'200': AulaXCongresoSerializer,'400': openapi.Response('Error')})
@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def asignarAulas(request):
    """
    Permite asignas las aulas que seran utilizadas el dia del congreso.
    """
    idCongreso = request.data['idCongreso']
    idAulas = request.data['idAulas']
    try:
        congreso = Congreso.objects.get(pk=idCongreso)
        aulas = Aula.objects.filter(id__in=idAulas).filter(is_active=True).filter(sede=congreso.sede)
        
        if len(aulas) > 0 and congreso != None:
            for aula in aulas:

                response = {
                    "idCongreso": idCongreso,
                    "idAula": aula.id,
                }

                serializer = AulaXCongresoSerializer(data=response)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
        else:
            raise Http404("El aula o el congreso no existe.")
    except:
        return Response({
                'status': '400',
                'error': 'No se pudo asignar el aula al congreso.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='delete', 
request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'id:':openapi.Schema(type=openapi.TYPE_INTEGER), 'sede:':openapi.Schema(type=openapi.TYPE_INTEGER)}),
responses={'200': openapi.Response('Aula eliminada.'),'400': openapi.Response('Error')})
@api_view(['DELETE'])
@authentication_classes([AuthenticationChairPrincipal])
def eliminarAula(request):
    """
    Permite dar de baja lógica un aula
    """
    usuario = request.user
    id = request.data['id']
    sede = request.data['sede']

    aula = Aula.objects.filter(pk=id).filter(sede=sede).first()
    if aula is None:
        return Response({
            'status': 400,
            'error': 'El aula no existe.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


    if usuario.is_authenticated:
        aula.is_active = False
        aula.save()
        return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)

    return Response({
                'status': '400',
                'error': 'Error al dar de baja el aula.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post',request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idSimposio:':openapi.Schema(type=openapi.TYPE_INTEGER), 'idCongreso:':openapi.Schema(type=openapi.TYPE_INTEGER), 'idChair:':openapi.Schema(type=openapi.TYPE_INTEGER)}),
                    responses={'200': openapi.Response('Simposio asignado al congreso.', SimposioXCongreso), '400': 'Error.'})
@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def altaSimposioxCongreso(request):
    """
    Permite asignar un simposio a un congreso.
    """
    usuario = request.user
    if usuario.is_authenticated:
        idCongreso = request.data['idCongreso']
        idSimposio = request.data['idSimposio']
        idChair = request.data['idChair']
        if Congreso.objects.filter(id=idCongreso).exists() is False:
            return Response({
                'status': '400',
                'error': 'El congreso no existe.',
                'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)
        if Simposio.objects.filter(id=idSimposio).exists() is False:
            return Response({
                'status': '400',
                'error': 'El simposio no existe.',
                'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)
        if RolxUsuarioxCongreso.objects.filter(idUsuario=idChair, idRol=1).exists() is False:
            return Response({
                'status': '400',
                'error': 'El usuario no es chair principal.',
                'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)
        if SimposiosxCongreso.objects.filter(idCongreso=idCongreso, idSimposio=idSimposio).exists():
            return Response({
                'status': '400',
                'error': 'El simposio ya está asignado al congreso.',
                'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = SimposioXCongreso(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)



@swagger_auto_schema(method='delete',
request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idCongreso:':openapi.Schema(type=openapi.TYPE_INTEGER), 'idSimposio:':openapi.Schema(type=openapi.TYPE_INTEGER), 'idChair:':openapi.Schema(type=openapi.TYPE_INTEGER)}),
responses={'200': openapi.Response('Simposio eliminado de congreso.'),'400': openapi.Response('Error')})
@api_view(['DELETE'])
@authentication_classes([AuthenticationChairPrincipal])
def eliminarSimposioXCongreso(request):
    """
    Permite dar de baja un simposio de un congreso.
    """
    usuario = request.user
    idSimposio = request.data['idSimposio']
    idCongreso = request.data['idCongreso']
    idChair = request.data['idChair']

    simposioxcongreso = SimposiosxCongreso.objects.filter(idCongreso=idCongreso, idSimposio=idSimposio, idChair=idChair).first()
    if simposioxcongreso is None:
        return Response({
                'status': '404',
                'error': 'El simposio no está asociado al congreso.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

    if usuario.is_authenticated:
        simposioxcongreso.delete()
        return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)

    return Response({
                'status': '400',
                'error': 'Error al dar de baja el simposio del congreso.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='put',request_body= SimposioSerializer,
                    responses={'200': openapi.Response('Simposio editado.', SimposioSerializer), '400': 'Error.'})
@api_view(['PUT'])
@authentication_classes([Authentication])
def editarSimposio(request):
    """
    Permite editar los datos de un simposio (ENVIAR ID EN EL BODY)
    """
    usuario = request.user
    id = request.data['idSimposio']
    try:
        simposio = Simposio.objects.get(pk=id)
    except ObjectDoesNotExist:
        return Response({
            'status': '400',
            'error': 'No existe el simposio.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
    serializer = SimposioSerializer(instance=simposio, data=request.data)
    if serializer.is_valid() and usuario.is_authenticated and usuario.is_superuser:
        serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    return Response({
        'status': '400',
        'error': 'No se pudo modificar el simposio: faltan datos.',
        'data': []
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de simposios completa', SimposioSerializer)})
@api_view(['GET'])
@authentication_classes([Authentication])
def getSimposios(request):
    """
    Muestra una lista de todos los simposios.
    """
    simposios = Simposio.objects.filter(is_active = True).all()
    data = []
    if len(simposios) > 0:
        for simp in simposios:
            serializer = SimposioSerializer(simp)
            data_con = serializer.data
            data_con['id'] = simp.id
            data.append(data_con)
    return Response({
        'status': '200',
        'error': '',
        'data': data
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(method='get',manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description="id", type=openapi.TYPE_INTEGER) ],
                    responses={'200': openapi.Response('Simposio', SimposioSerializer)})
@api_view(['GET'])
@authentication_classes([Authentication])
def getSimposio(request):
    """
    Permite obtener los datos de un simposio.
    """
    idSimposio = request.data['idSimposio']
    try:
        simposio = Simposio.objects.get(pk=idSimposio)
    except ObjectDoesNotExist:
        return Response({
            'status': '400',
            'error': 'No existe el simposio.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
    serializer = SimposioSerializer(instance=simposio, data=request.data)
    return Response({
        'status': '200',
        'error': '',
        'data': [serializer.data]
    }, status=status.HTTP_200_OK)



@swagger_auto_schema(method='get',manual_parameters=[openapi.Parameter('idCongreso', openapi.IN_QUERY, description="id del congreso", type=openapi.TYPE_INTEGER) ],
                    responses={'200': openapi.Response('Simposio', SimposioSerializer)})
@api_view(['GET'])
def getSimposiosXCongreso(request):
    """
    Muestra una lista de todos los simposios de x congreso.
    """
    idCongreso = request.GET['idCongreso']
    simposios = SimposiosxCongreso.objects.filter(idCongreso=idCongreso).all()
    data = []
    for simp in simposios:
        simposio = simp.idSimposio
        serializer = SimposioSerializer(simposio)
        data_con = serializer.data
        data_con['id'] = simposio.id
        data.append(data_con)

    return Response({
        'status': '200',
        'error': '',
        'data': data
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(method='delete',
request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'idSimposio:':openapi.Schema(type=openapi.TYPE_INTEGER)}),
responses={'200': openapi.Response('Simposio eliminado.'),'400': openapi.Response('Error')})
@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminarSimposio(request):
    """
    Permite dar de baja lógica un simposio
    """
    usuario = request.user
    id = request.data['idSimposio']


    simposio = Simposio.objects.filter(pk=id).first()
    if simposio is None:
        return Response({
            'status': '400',
            'error': 'El simposio no existe.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    if usuario.is_authenticated:
        simposio.is_active = False
        simposio.save()
        return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)

    return Response({
                'status': '400',
                'error': 'Error al dar de baja el simposio.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de sedes', SedeSerializer)})
@api_view(['GET'])
def devolverSedes(request):
    """
    Devuelve la lista de sedes completa. 
    """
    data = []
    try:
        sedes = Sede.objects.all()
        for s in sedes:
            sede = {
                'id': s.id,
                'nombre': s.nombre,
                'direccion': str(s.calle),
                'numero': str(s.numero),
                'nombreLocalidad': s.localidad.nombre,
                'idLocalidad': s.localidad.id,
                'nombreProvincia': s.localidad.provincia.nombre,
                'idProvincia': s.localidad.provincia.id
            }
            data.append(sede)
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


@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de localidades por provincia', LocalidadSerializer)})
@api_view(['GET'])
def devolverLocalidadesXProvincia(request):
    """ Devuelve la lista localidades por provincia."""
    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    idProvincia = request.GET['idProvincia']
    localidades = Localidad.objects.filter(provincia=idProvincia).all()
    data = []
    for l in localidades:
            localidad = {
                'id': l.id,
                'nombre': l.nombre
            }
            data.append(localidad)
    return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)


@swagger_auto_schema(method='get', 
                    manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description="id congreso", type=openapi.TYPE_INTEGER)],
                    responses={'200': openapi.Response('Sede asociada al congreso del que forma parte el chair local', SedeSerializer)})
@api_view(['GET'])
@authentication_classes([Authentication])
def devolverSedesXChairLocal(request, id):
    """
    Devuelve la sede especifica que esta coordinando el chair local. Debes estar logueado al sistema, 
    y tener asignado el rol de administrador local (2) o administrador supremo (1).
    """
    usuario = request.user
    
    try:
        congreso = Congreso.objects.get(pk=id)
        rolxUsuario = RolxUsuarioxCongreso.objects.filter(idUsuario=usuario.id).filter(idCongreso=congreso.id).first()

        if usuario.is_authenticated and (rolxUsuario != None) and (rolxUsuario.idRol.id == 2 or rolxUsuario.idRol.id == 1):
            
            sede = Sede.objects.filter(pk=congreso.sede).first()
            serializer = SedeSerializer(sede)
            return Response(serializer.data)

        else:
            return Response({
                'status': 401,
                'error': 'No tiene permisos para realizar esta acción.',
                'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)
    except ObjectDoesNotExist:
        raise Http404("El congreso no existe") 


@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de localidades', LocalidadSerializer)})
@api_view(['GET'])
def devolverLocalidades(request):
    """ Devuelve la lista localidades."""
    localidades = Localidad.objects.all()
    serializer = LocalidadSerializer(localidades, many=True)
    return Response({
        'status': 200,
        'error': '',                        
        'data': serializer.data
    })



@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de provincias', ProvinciaSerializer)})
@api_view(['GET'])
def devolverProvincias(request):
    """ Devuelve la lista provincias. """
    provincias = Provincia.objects.all()
    serializer = ProvinciaSerializer(provincias, many=True)
    return Response({
        'status': 200,
        'error': '',                        
        'data': serializer.data
    })

@swagger_auto_schema(method='get', 
    responses={'200': openapi.Response('Lista de paises', PaisSerializer)})
@api_view(['GET'])
def devolverPaises(request):
    """ Devuelve la lista de paises."""
    paises = Pais.objects.all()
    serializer = PaisSerializer(paises, many=True)
    return Response({
        'status': 200,
        'error': '',                        
        'data': serializer.data
    })

@swagger_auto_schema(method='get',
                    responses={'200': openapi.Response('Lista de chairs por simposios.', ProvinciaSerializer)})
@api_view(['GET'])
@authentication_classes([AuthenticationChairPrincipal])
def devolverChairsSimposios(request):
    """
    Devuelve los chairs secundarios junto con sus simposios
    """
    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    idCongreso = payload['idCongreso']
    try:
        # idCongreso = request.GET['idCongreso']
        congreso = Congreso.objects.get(id=idCongreso)
        chairs = ChairXSimposioXCongreso.objects.filter(idCongreso=congreso).all()
        data = []
        for chair in chairs:
            chair = {
                'nombreChair': chair.idUsuario.nombre,
                'apellidoChair':chair.idUsuario.apellido,
                'idChair': chair.idUsuario.id,
                'idSimposio': chair.idSimposio.id,
                'nombreSimposio': chair.idSimposio.descripcion
            }
            data.append(chair)
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': 'Ocurrió un error',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def asignarChairASimposio(request):
    """
    Asigna un chair a un simposio
    """    
    try:
        idCongreso = request.data['idCongreso']
        idChair = request.data['idChair']
        idSimposioData = request.data['idSimposio']
        simposio_lista = Simposio.objects.filter(id=idSimposioData).first()
        simposio = SimposiosxCongreso.objects.filter(idSimposio=simposio_lista).first()
        data = {
            'idCongreso': idCongreso,
            'idUsuario' : idChair,
            'idSimposio' : simposio.id
        }
        chair = ChairXSimposioXCongreso.objects.filter(idUsuario=idChair, idSimposio=idSimposioData, idCongreso=idCongreso).first()
        if chair is None:
            serializer = ChairXSimposioXCongresoSerializer(data=data)
            if serializer.is_valid():
                serializer.save()

        chair = RolxUsuarioxCongreso.objects.filter(idUsuario=idChair, idRol=2, idCongreso=idCongreso).first()
        if chair is None:
            data = {
                'idCongreso': idCongreso,
                'idUsuario': idChair,
                'idRol': 2
            }
            serializer = RolxUsuarioxCongresoSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        
        chair = Usuario.objects.filter(id=idChair).first()
        datos_enviar = {
            'nombreChair':chair.nombre,
            'apellidoChair':chair.apellido,
            'idChair':chair.id,
            'idSimposio': simposio_lista.id,
            'nombreSimposio':simposio_lista.nombre
        }

        return Response({
            'status': '200',
            'error': '',
            'data': datos_enviar
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['DELETE'])
@authentication_classes([AuthenticationChairPrincipal])
def eliminarChairSecundario(request):
    """Elimina un chair secundario"""
   
    try:
        idChair = request.data['idChair']
        idSimposio = request.data['idSimposio']
        simposio_lista = Simposio.objects.filter(id=idSimposio).first()
        simposio =  SimposiosxCongreso.objects.filter(idSimposio=simposio_lista).first()
        usuario = Usuario.objects.filter(id=idChair).first()
        chair = ChairXSimposioXCongreso.objects.filter(idSimposio=simposio.id,idUsuario=usuario.id).first()
        if chair != None:
            chair.delete()
            return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)
        return Response({
            'status': '200',
            'error': 'No existe el chair secundario.',
            'data': []
        }, status=status.HTTP_200_OK) 
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def notificarResultadosEvaluacion(request):
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    usuario = request.user

    idCongreso = payload['idCongreso']
    simposio = SimposiosxCongreso.objects.filter(idCongreso=idCongreso, idChair=usuario.id).first()
    articulos = Articulo.objects.filter(idCongreso=idCongreso, idSimposio=simposio.idSimposio.id).all()
    destinatariosAprobados = []
    destinatariosRechazados = []
    destinatariosReentrega = []
    try:
        for art in articulos:
            if art.responsable != "":
                if (art.idEstado_id == 5):  # Reentregados
                    destinatariosReentrega.append(art.responsable)
                elif (art.idEstado_id == 6):  # Aprobados
                    destinatariosAprobados.append(art.responsable)
                elif (art.idEstado_id == 7):  # Rechazados
                    destinatariosRechazados.append(art.responsable)

        if (len(destinatariosReentrega) > 0):
            template = get_template('evaluacion_reentrega.html')
            content = template.render({})
            correo = EmailMultiAlternatives(
                'Resultado de Evaluación - CoNaIISI', '', settings.EMAIL_HOST_USER, destinatariosReentrega)
            correo.attach_alternative(content, 'text/html')
            correo.send()

        if (len(destinatariosAprobados) > 0):
            template = get_template('evaluacion_aprobada.html')
            content = template.render({})
            correo = EmailMultiAlternatives(
                'Resultado de Evaluación - CoNaIISI', '', settings.EMAIL_HOST_USER, destinatariosAprobados)
            correo.attach_alternative(content, 'text/html')
            correo.send()
        if (len(destinatariosRechazados) > 0):
            template = get_template('evaluacion_rechazada.html')
            content = template.render({})
            correo = EmailMultiAlternatives(
                'Resultado de Evaluación - CoNaIISI', '', settings.EMAIL_HOST_USER, destinatariosRechazados)
            correo.attach_alternative(content, 'text/html')
            correo.send()
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'status': '200',
        'error': '',
        'data': []
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def devolverInfoPublicaChairs(request):
    """
    Devuelve los chairs secundarios junto con sus simposios para info pública
    """
    idCongreso = request.GET['idCongreso']
    try:
        congreso = Congreso.objects.filter(id=idCongreso).first()
        if congreso is None:
            return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)
        usuario = Usuario.objects.filter(email=congreso.chairPrincipal).first()
        chairs = ChairXSimposioXCongreso.objects.filter(idCongreso=congreso).all()
        data = []
        for chair in chairs:
            chair = {
                'nombreChair': chair.idUsuario.nombre,
                'apellidoChair':chair.idUsuario.apellido,
                'idChair': chair.idUsuario.id,
                'idSimposio': chair.idSimposio.id,
                'nombreSimposio': chair.idSimposio.descripcion
            }
            data.append(chair)

        resp = { 
            "chairPrincipal":usuario.nombre + ' '+ usuario.apellido, 
            "chairsSecundarios":data 
        }
        
        return Response({
            'status': '200',
            'error': '',
            'data': resp
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': 'Ocurrió un error',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', request_body= SedeSerializer,
                    responses={'200': openapi.Response('Sede creada.', SedeSerializer), '400': 'Error.'})
@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def crearSede(request):
    """
    Metodo para crear una sede
    """

    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    usuario = request.user
    serializer = SedeSerializer(data=request.data)

    if (serializer.is_valid() and usuario.is_authenticated):
        serializer.save()
        return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
    else:
        return Response({
                'status': '400',
                'error': "Error al crear la sede.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)





@swagger_auto_schema(method='put', request_body= SedeSerializer,
                    responses={'200': openapi.Response('Aula editada.', SedeSerializer), '400': 'Error.'})
@api_view(['PUT'])
@authentication_classes([AuthenticationChairPrincipal])
def editarSede(request):
    """
    Permite editar una sede (enviar el ID en el body).
    """
    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    usuario = request.user
    id = request.GET['id']

    try:
        sede = Sede.objects.get(pk=id)
    except ObjectDoesNotExist:
        raise Http404("La sede no existe")

    serializer = SedeSerializer(instance=sede,data=request.data)
    
    if serializer.is_valid() and usuario.is_authenticated:
        serializer.save()
        return Response({
                'status': '200',
                'error': '',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)

    return Response({
                'status': '400',
                'error': "Error al editar la sede.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('idSede', openapi.IN_QUERY, description="Id de sede", type=openapi.TYPE_INTEGER)],
                    responses={'200': openapi.Response('Sede', SedeSerializer)})
@api_view(['GET'])
@authentication_classes([AuthenticationChairPrincipal])
def getSede(request):
    """
    Devuelve los datos de una sede.
    """
    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    sede_id = request.GET['idSede']
    try:
        s = Sede.objects.filter(id=sede_id).first()
        sede = {
                'id': s.id,
                'nombre': s.nombre,
                'direccion': str(s.calle),
                'numero':  str(s.numero),
                'nombreLocalidad': s.localidad.nombre,
                'idLocalidad': s.localidad.id,
                'nombreProvincia': s.localidad.provincia.nombre,
                'idProvincia': s.localidad.provincia.id
            }
        return Response({
                'status': '200',
                'error': '',
                'data': [sede]
            }, status=status.HTTP_200_OK)
    except:
         return Response({
                'status': '400',
                'error': "Error al devolver la sede.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='delete', 
request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'id:':openapi.Schema(type=openapi.TYPE_INTEGER), 'sede:':openapi.Schema(type=openapi.TYPE_INTEGER)}),
responses={'200': openapi.Response('Sede eliminada.'),'400': openapi.Response('Error')})
@api_view(['DELETE'])
@authentication_classes([AuthenticationChairPrincipal])
def eliminarSede(request):
    """
    Permite eliminar una sede
    """
    token = request.headers['Authorization']
    if not token:
        raise AuthenticationFailed('Usuario no autenticado!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Usuario no autenticado!')
    usuario = request.user
    id = request.GET['id']

    sede = Sede.objects.filter(pk=id).first()
    if sede is None:
        return Response({
            'status': 400,
            'error': 'La sede no existe.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
    
    congresos = Congreso.objects.filter(sede=id).all()
    print(congresos)
    if congresos.count() > 0:
        return Response({
            'status': 400,
            'error': 'La sede está siendo utilizada en al menos un congreso.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


    if usuario.is_authenticated and usuario.is_superuser:
        sede.delete()
        return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)

    return Response({
                'status': '400',
                'error': 'Error al eliminar la sede.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
