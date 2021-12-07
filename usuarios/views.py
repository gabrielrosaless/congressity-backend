
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from random import SystemRandom
from .models import *
from .serializers import *
from congresos.models import *
import jwt,datetime
from rest_framework.decorators import api_view, authentication_classes
from .authentication import *
from congresos.models import *
from articulos.models import ChairXSimposioXCongreso
from articulos.serializers import ChairXSimposioXCongresoSerializer, EvaluadorSerializer, EvaludorXCongresoSerializer
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from decouple import config
import base64
# Create your views here.


@swagger_auto_schema(method='get', responses={200: openapi.Response('Successful operation')})
@api_view(['GET'])
def apiOverView(request):
    """
    Muestra la vista principal de la api, con todos sus endpoints.
    """
    api_urls = {
        'Lista de usuarios':'/lista-usuarios/',
        'Registrar usuario':'/registrar/',
        'Editar usuario':'/editar/',
        'Eliminar usuario':'/eliminar/',
        'Iniciar sesion:': '/login/',
        'Cerrar sesion': '/logout/',
        'Usuario en sesion':'/usuario/',
    }
    return Response(api_urls)


@swagger_auto_schema(method='post', request_body= UsuarioSerializer, 
                    responses={200: UsuarioSerializer})
@api_view(['POST'])
def registrar(request):
    """
    Metodo para registrar un usuario, con email y contraseña.
    """
    serializer = UsuarioSerializer(data=request.data)
    #serializer.is_valid(raise_exception=True)
     
    if serializer.is_valid():
        serializer.save()
        usuario_data = serializer.data
        usuario = Usuario.objects.filter(email=usuario_data['email']).first()
        payload = {
            'id': usuario.id,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
        mail = usuario.email
        relative_link= 'cuentaConfirmada/'
        current_site= config('URL_FRONT_DEV')
        url_envio = current_site + relative_link + token
        data = {'email': mail, 'link': url_envio}
        res = send_mail(data)

        response = {
            "status": status.HTTP_200_OK,
            "error": None,
            "data": serializer.data
        }
    else:
        response = {
            "status": status.HTTP_400_BAD_REQUEST,
            "error": serializer.errors,
            "data": []
        }
    return Response(response)


@swagger_auto_schema(method='post', request_body= UsuarioSerializer, 
                    responses={200: openapi.Response('Devuelve el token de inicio de sesion en base HS256 - { jwt: "token-ejemplo" }  ')})
@api_view(['POST'])
def login(request):
    """
    Permite iniciar sesión
    """
    email = request.data['email']
    password = request.data['password']
    idCongreso = request.data['idCongreso']
    usuario = Usuario.objects.filter(email=email).first()
    sede = Congreso.objects.filter(id=idCongreso).first().sede # Debería ser sede.id >>> primero se tiene que cambiar el models de congreso para sede = foreign key
    if usuario is None:
        raise AuthenticationFailed('Usuario no encontrado.')

    if not usuario.check_password(password):
        raise AuthenticationFailed('Contraseña incorrecta.')

    if not usuario.is_verified:
        raise AuthenticationFailed('Cuenta no activada.')

    rolesUsuario = RolxUsuarioxCongreso.objects.filter(idCongreso = idCongreso, idUsuario = usuario.id ).all()
    roles = []
    for rol in rolesUsuario:
        roles.append(rol.idRol.id)
    
    payload = {
        'id': usuario.id,
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=500),
        'iat': datetime.datetime.utcnow(),
        'idCongreso':idCongreso,
        'rol': roles,
        'sede': sede,
        'is_superuser':usuario.is_superuser
    }
    token = jwt.encode(payload,  settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
    response = Response()
    response.set_cookie(key='jwt',value=token,httponly=True)

    response.data = {
        'jwt': token
    }
    return response


@swagger_auto_schema(method='get',
manual_parameters=[openapi.Parameter('email', openapi.IN_QUERY, description="email", type=openapi.TYPE_INTEGER)],
responses={ 200: openapi.Response('True: Existe el usuario, False: no existe')})
@api_view(['GET'])
@authentication_classes([Authentication])
def verificarUsuario(request):
    
    emailUsuario = request.GET['email']

    if Usuario.objects.filter(email= emailUsuario).exists():
        return Response( {
            "status": status.HTTP_200_OK,
            "error": False,
            "data": True
        })
    return Response( {
            "status": status.HTTP_200_OK,
            "error": True,
            "data": False
    })



@swagger_auto_schema(method='post', responses={200: openapi.Response('Sesion terminada.')})
@api_view(['POST'])
@authentication_classes([Authentication])
def logout(request):
    """
    Permite cerrar sesión. La sesion debe estar iniciada.
    """
    usuario = request.user
    if usuario.is_authenticated:
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Sesion terminada.'
        }
        return response


@swagger_auto_schema(method='post', request_body= UsuarioCompletoSerializer, 
                                    responses={'200': openapi.Response('Usuario editado.', UsuarioCompletoSerializer)})
@api_view(['POST'])
@authentication_classes([Authentication])
def editar(request):
    """
    Permite editar un usuario.
    """
    usuario = request.user
    serializer = UsuarioCompletoSerializer(instance=usuario,data=request.data)
    
    if serializer.is_valid():
        serializer.save(raise_exception=True)
        response = {
            "status": 200,
            "error": None,
            "data": serializer.data
        }
    else:
        response = {
            "status": status.HTTP_400_BAD_REQUEST,
            "error": serializer.errors,
            "data": []
        }
    return Response(response)
    

@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de usuarios completa', UsuarioCompletoSerializer)})
@api_view(['GET'])
@authentication_classes([AuthenticationChairPrincipal])
def devolverUsuarios(request):
    """
    Devuelve la lista completa de usuarios.
    """
    usuarios = Usuario.objects.all()
    serializer = UsuarioCompletoSerializer(usuarios, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method='get',
                    responses={'200': openapi.Response('Datos del usuario logueado', UsuarioCompletoSerializer)})
@api_view(['GET'])
def getUsuarioLogueado(request):
    """
    Devuelve los datos del usuario logueado.
    """
    print(request.user)
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    usuario = Usuario.objects.filter(id=payload['id']).first()
    serializer = UsuarioCompletoSerializer(usuario)
    return Response(serializer.data)


@swagger_auto_schema(method='delete', responses={'200': openapi.Response('Usuario eliminado.')})
@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminar(request):
    """
    Permite darse baja logica al usuario.
    """
    usuario = request.user
    if usuario.is_authenticated:
        usuario.is_active = False
        usuario.save()
        return Response('Usuario eliminado!')



@swagger_auto_schema(method='post', 
                    request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'email:':openapi.Schema(type=openapi.TYPE_STRING)}), 
                    responses={'400': 'Usuario no autorizado.','200': 'Usuario activado!'})
@api_view(['POST'])
@authentication_classes([Authentication])
def activar(request):
    """
    Permite al administrador principal activar un usuario desactivado. 
    """
    usuario = request.user
    if usuario.is_authenticated and usuario.is_superuser:
        email = request.data['email']
        usuario = Usuario.objects.filter(email=email).first()
        usuario.is_active = True
        usuario.save()
        return Response('Usuario activado!')
    return Response('Usuario no autorizado.')

   
    

def send_mail(data):
    link = data['link']
    mail = data['email']
    context = {'linkActivacion': link}
    template = get_template('plantilla_confirmar_mail.html')
    content = template.render(context)
    correo = EmailMultiAlternatives(
        'Correo de Activacion de Cuenta',
        'Por favor Activa Tu Cuenta',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    correo.attach_alternative(content, 'text/html')
    correo.send()
    return True


@swagger_auto_schema(method='get', responses={'200': 'Se activó correctamente la cuenta.','400': 'Token Inválido o El link expiró .'})
@api_view(['GET'])
def verify_email(request):
    """
    Permite activar una cuenta a traves de un link de activación (Enviado cuando se registró.).
    """
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        user = Usuario.objects.get(id=payload['id'])
        if not user.is_verified:
            user.is_verified = True
            user.save()
        return Response({'email': 'Se activó correctamente la cuenta'}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError as identifier:
        return Response({'error': 'El link expiró'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
        return Response({'error': 'Token Inválido'}, status= status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(method='post', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'email:':openapi.Schema(type=openapi.TYPE_STRING)}), 
                    responses={'200': 'Se envió el correo de activacion.','400': 'El correo no se encuentra registrado en el sitio o La Cuenta ya se encuentra activa.'})
@api_view(['POST'])
def reenviarmailactivacion(request):
    mail = request.data['email']
    usuario = Usuario.objects.filter(email=mail).first()
    if usuario is None:
        return Response({'error': 'El correo no se encuentra registrado en el sitio'}, status= status.HTTP_400_BAD_REQUEST)
    if usuario.is_verified:
        return Response({'error': 'La Cuenta ya se encuentra activa'}, status= status.HTTP_400_BAD_REQUEST)
    payload = {
        'id': usuario.id,
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
    current_site = get_current_site(request).domain
    mail = usuario.email
    relative_link = reverse('email-verify')
    url_envio = current_site + relative_link + "?token=" + token
    data = {'email': mail, 'link': url_envio}
    res = send_mail(data)
    return Response({'OK': 'Se envió el correo de activacion'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([Authentication])
def asignarRolChairPpal(request):
    """
    Permite asignar el rol de Chair Principal a un Usuario
    """
    try:
        idUsuario = request.data['idUsuario']
        idCongreso = request.data['idCongreso']
        token = request.headers['Authorization']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        idUsuario = payload['id']
        usuario = Usuario.objects.filter(id=idUsuario).first()
        if usuario.is_superuser != True:
            return Response({
            'status': '400',
            'error': 'No posee los permisos para realizar esta tarea',
            'data': []
        }, status=status.HTTP_200_OK)
        congreso = Congreso.objects.filter(id = idCongreso).first()
        if congreso == None:
            return Response({
            'status': '400',
            'error': 'No existe el congreso',
            'data': []
        }, status=status.HTTP_200_OK)
        if usuario != None:
            data = {
                'idCongreso': idCongreso,
                'idUsuario': idUsuario,
                'idRol': 1
            }
            serializer = RolxUsuarioxCongresoSerializer(data = data)
            if serializer.is_valid():
                serializer.save()
        else:
            return Response({
            'status': '400',
            'error': 'No existe el usuario',
            'data': []
        }, status=status.HTTP_200_OK)
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    except:
        return Response({
                'status': '400',
                'error': "Error al asignar el Rol.",
                'data': []
         }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def asignarRolChairSecundario(request):
    """
    Permite asignar el rol de Chair Secundario a un Usuario
    """
    try:
        idUsuario = request.data['idUsuario']
        idCongreso = request.data['idCongreso']
        idSimposio = request.data['idSimposio']
        if ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso,idUsuario=idUsuario,idSimposio=idSimposio).count() != 0:
            return Response({
            'status': '400',
            'error': 'Ya es ChairSecundario del simposio',
            'data': []
        }, status=status.HTTP_200_OK)
        congreso = Congreso.objects.filter(id = idCongreso).first()
        if congreso == None:
            return Response({
            'status': '400',
            'error': 'No existe el congreso',
            'data': []
        }, status=status.HTTP_200_OK)
        usuario = Usuario.objects.filter(id=idUsuario).first()
        if usuario != None:
            rol = Rol.objects.filter(id=2).first()
            if RolxUsuarioxCongreso.objects.filter(idCongreso=congreso,idUsuario=usuario,idRol=rol).count() == 0:
                data = {
                    'idCongreso': idCongreso,
                    'idUsuario': idUsuario,
                    'idRol': 2
                }
                serializer = RolxUsuarioxCongresoSerializer(data = data)
                if serializer.is_valid():
                    serializer.save()
        else:
            return Response({
            'status': '400',
            'error': 'No existe el usuario',
            'data': []
        }, status=status.HTTP_200_OK)
        data = {
            'idCongreso': idCongreso,
            'idUsuario': idUsuario,
            'idSimposio': idSimposio
        }
        serializer = ChairXSimposioXCongresoSerializer(data=data)
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

@swagger_auto_schema(method='get', 
                    responses={'200': openapi.Response('Lista de tipos DNI', TipoDniSerializer)})
@api_view(['GET'])
def devolverTiposDNI(request):
    """
    Devuelve la lista provincias. 
    """
    tiposDNI = TipoDni.objects.all()
    serializer = TipoDniSerializer(tiposDNI, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def enviarMailRestablecerContraseña(request):
    """
    Permite mandar un mail a un usuario para reestablecer su contraseña
    """
    try:
        email = request.data['email']
        existe_usuario = Usuario.objects.filter(email=email).exists()
        if existe_usuario:
            usuario = Usuario.objects.filter(email=email).first()
            payload = {
                'id': usuario.id,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
            mail = usuario.email            
            relative_link = 'reestablecerContraseña/'
            current_site= config('URL_FRONT_DEV')
            url_envio = current_site + relative_link + token
            data = {'email': mail, 'link': url_envio}
            res = send_mail_restablecer_contraseña(data)
            return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': '400',
                'error': 'No existe el usuario',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
                        'status': '400',
                        'error': e.args,
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get', responses={'200': 'Se cambió la contraseña.','400': 'Token Inválido o El link expiró .'})
@api_view(['GET'])
def restablecer_contraseña(request):
    """
    Permite restablecer la contraseña de una cuenta
    """
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        user = Usuario.objects.get(id=payload['id'])
        if user != None:
            nueva_contraseña = generarContraseña()
            print(nueva_contraseña)
            user.set_password(nueva_contraseña)
            user.save()
            send_mail_nueva_contraseña(nueva_contraseña,user.email)
            return Response({'email': 'Se cambió la contraseña. Controle su casilla de email para consultar la nueva contraseña'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Ocurrió un error'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.ExpiredSignatureError as identifier:
        return Response({'error': 'El link expiró'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
        return Response({'error': 'Token Inválido'}, status= status.HTTP_400_BAD_REQUEST)

def generarContraseña():
    longitud = 18
    valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
    cryptogen = SystemRandom()
    contraseña = ""
    while longitud > 0:
        contraseña = contraseña + cryptogen.choice(valores)
        longitud = longitud - 1
    encoded = base64.b64encode(bytes(contraseña, 'utf-8'))
    return encoded

def send_mail_restablecer_contraseña(data):
    link = data['link']
    mail = data['email']
    context = {'linkRestablecer': link}
    template = get_template('plantilla_reestablecer_contraseña.html')
    content = template.render(context)
    correo = EmailMultiAlternatives(
        'Solicitud de Reestablecimiento de Contraseña',
        'Por favor si usted realizó la solicitud, haga click en Reestablecer Contraseña',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    correo.attach_alternative(content, 'text/html')
    correo.send()
    return True

def send_mail_nueva_contraseña(contraseña,mail):
    context = {'contraseña': contraseña}
    template = get_template('plantilla_nueva_contraseña.html')
    content = template.render(context)
    correo = EmailMultiAlternatives(
        'Nueva Contraseña',
        'Aquí se encuentra su nueva contraseña, si desea cambiarla puede acceder a la página de Congresity para cambiarla',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    correo.attach_alternative(content, 'text/html')
    correo.send()
    return True


@api_view(['POST'])
@authentication_classes([Authentication])
def cambiarContraseña(request):
    """
    Permite cambiar la contraseña
    """
    try:
        token = request.headers['Authorization']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        idUsuario = payload['id']
        usuario = Usuario.objects.filter(id=idUsuario).first()
        token_contraseñas = request.data['passwords']
        passwords = jwt.decode(token_contraseñas, 'encriptadofront', algorithms=['HS256'])
        pass_ant = passwords["pass_antigua"]
        pass_nueva = passwords['pass_nueva']
        if not usuario.check_password(pass_ant):
            return Response({
                        'status': '400',
                        'error': "La contraseña antigua no es correcta",
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
        usuario.set_password(pass_nueva)
        usuario.save()
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

