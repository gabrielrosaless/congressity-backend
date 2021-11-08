from django.utils import timezone
from django.shortcuts import render
from usuarios.authentication import *
from congresos.models import Congreso
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
import datetime as date_mails
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

# SDK de Mercado Pago
import mercadopago
from decouple import config

# Agrega credenciales
sdk = mercadopago.SDK("TEST-5758864551072877-091319-fa5f2207043cbd3d3ce7fc0dd6693686-348600704")

# Create your views here.

@api_view(['POST'])
@authentication_classes([AuthenticationChairPrincipal])
def crearTarifa(request):
    """ Metodo para crear la tarifa asociada a un congreso. """

    usuario = request.user
    
    serializer = TarifaSerializer(data=request.data)

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
            'error': serializer.errors,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([AuthenticationChairPrincipal])
def editarTarifa(request):
    """ Permite editar una tarifa. """

    id_tarifa = request.GET['id']

    try:
        tarifa = Tarifa.objects.get(pk=id_tarifa)
    except Tarifa.DoesNotExist:
        raise Http404("La tarifa no existe.")

    serializer = TarifaSerializer(instance=tarifa, data=request.data)

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


@api_view(['GET'])
@authentication_classes([Authentication])
def devolverTarifas(request):
    """ Devuelve la lista de tarifas por congreso. """

    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    id_congreso = payload['idCongreso']
    try:
        tarifas = Tarifa.objects.filter(idCongreso=id_congreso).all()
        datos = []
        for t in tarifas:
            tarifa = {
                'id': t.id,
                'idCongreso': t.idCongreso.id,
                'nombre': t.nombre,
                'precio': t.precio,
                'fechaDesde': t.fechaDesde,
                'fechaHasta': t.fechaHasta
            }
            datos.append(tarifa)
        return Response({
            'status': '200',
            'error': '',
            'data': datos
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver la lista de tarifas.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def devolverTarifasActivas(request):
    """ Devuelve la lista de tarifas activas - disponibles hoy. """

    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    id_congreso = payload['idCongreso']
    fechaHoy = timezone.now()
    try:
        tarifas = Tarifa.objects.filter(idCongreso=id_congreso).all()
        datos = []
        for t in tarifas:
            if t.fechaDesde <= fechaHoy <= t.fechaHasta:
                tarifa = {
                    'id': t.id,
                    'idCongreso': t.idCongreso.id,
                    'nombre': t.nombre,
                    'precio': t.precio,
                    'fechaDesde': t.fechaDesde,
                    'fechaHasta': t.fechaHasta
                }
                datos.append(tarifa)
        return Response({
            'status': '200',
            'error': '',
            'data': datos
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver la lista de tarifas.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([AuthenticationChairPrincipal])
def eliminarTarifa(request):
    """
    Permite dar de baja una tarifa.
    """
    usuario = request.user
    idTarifa = request.GET['id']

    try:
        tarifa = Tarifa.objects.filter(pk=idTarifa).first()
    except Tarifa.DoesNotExist:
        raise Http404("La tarifa no existe.")

    if usuario.is_authenticated:
        tarifa.delete()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)

    return Response({
        'status': '400',
        'error': 'Error al dar de baja la tarifa.',
        'data': []
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([Authentication])
def crearCuponDescuento(request):
    """
    Crea un nuevo cupon de descuento
    """
    usuario = request.user

    cupon = CuponDescuento.objects.filter(codigo=request.data['codigo']).first()
    if cupon is not None:
        return Response({
            'status': '400',
            'error': 'El cupón ya existe.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = CuponDescuentoSerializer(data=request.data)

    if serializer.is_valid() and usuario.is_authenticated:
        serializer.save()
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


@api_view(['PUT'])
@authentication_classes([Authentication])
def editarCuponDescuento(request):
    """ Permite editar un cupón de descuento. """
    usuario = request.user

    codigoCupon = request.GET['codigoCupon']

    try:
        cupon = CuponDescuento.objects.get(codigo=codigoCupon)
    except CuponDescuento.DoesNotExist:
        raise Http404("El cupón no existe.")

    serializer = CuponDescuentoSerializer(instance=cupon, data=request.data)

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
@authentication_classes([Authentication])
def eliminarCuponDescuento(request):
    """ Permite editar un cupón de descuento. """
    usuario = request.user

    codigoCupon = request.GET['codigoCupon']

    cupon = CuponDescuento.objects.filter(codigo=codigoCupon).first()
    if cupon is not None:
        cupon.delete()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': '400',
            'error': 'El cupón ya ha sido eliminado.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def getCuponesDescuento(request):
    """ Devuelve la lista de cupones de descuento de un congreso. """

    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    id_congreso = payload['idCongreso']
    try:
        cupones = CuponDescuento.objects.all()
        datos = []
        for c in cupones:
            tarifa = Tarifa.objects.filter(id=c.idTarifa.id).first()
            if tarifa.idCongreso.id == int(id_congreso):
                precioDescuento = float(tarifa.precio) - float(tarifa.precio) * float(c.porcentajeDesc) / 100
                cupon = {
                    'codigo': c.codigo,
                    'porcentajeDesc': c.porcentajeDesc,
                    'idTarifa': tarifa.id,
                    'nombreTarifa': tarifa.nombre,
                    'precioTarifa': tarifa.precio,
                    'precioDescuento': precioDescuento,
                    'usosRestantes': c.usosRestantes
                }
                datos.append(cupon)
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
def getCuponDescuento(request):
    """ Devuelve los datos de un cupón de descuento. """

    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    codigoCupon = request.GET['codigoCupon']
    try:
        cupon = CuponDescuento.objects.filter(codigo=codigoCupon).first()
        if cupon is None:
            return Response({
                'status': '400',
                'error': "El cupón no existe.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        tarifa = Tarifa.objects.filter(id=cupon.idTarifa.id).first()
        precioDescuento = float(tarifa.precio) - float(tarifa.precio) * float(cupon.porcentajeDesc) / 100
        cupon = {
            'codigo': cupon.codigo,
            'porcentajeDesc': cupon.porcentajeDesc,
            'idTarifa': tarifa.id,
            'nombreTarifa': tarifa.nombre,
            'precioTarifa': tarifa.precio,
            'precioDescuento': precioDescuento,
            'usosRestantes': cupon.usosRestantes
        }
        return Response({
            'status': '200',
            'error': '',
            'data': [cupon]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([Authentication])
def crearInscripcion(request):
    """
    Registra una nueva inscripción.
    """
    usuario = request.user
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    inscripcion = Inscripcion.objects.filter(idUsuario=usuario.id).first()
    hoy = datetime.now()
    if inscripcion is not None:
        fechaInscripcion = inscripcion.fechaPago
        if inscripcion.idCupon is None:
            cupon = None
        else:
            cupon = inscripcion.idCupon.id
        if fechaInscripcion != None:
            return Response({
                'status': '200',
                'error': 'Usted ya se encuentra inscripto.',
                'data': []
            }, status=status.HTTP_200_OK)
        else:

            datos = {
                'id':inscripcion.id,
                'idUsuario': usuario.id,
                'idTarifa': inscripcion.idTarifa.id,
                'idCongreso': payload['idCongreso'],
                'fechaPago': None,
                'fechaInscripcion': hoy,
                'idCupon': cupon,
                'precioFinal': inscripcion.precioFinal
            }
            serializer = InscripcionSerializer(data=datos)
            if serializer.is_valid():
                return Response({
                        'status': '200',
                        'error': '',
                        'data': serializer.data
                }, status=status.HTTP_200_OK)
    
    congreso = Congreso.objects.filter(id=payload['idCongreso']).first()
    tarifas = Tarifa.objects.filter(idCongreso=congreso.id).all()
    for tar in tarifas:
        if tar.fechaDesde.date() <= hoy.date() <= tar.fechaHasta.date():
            tarifa = tar
            break
    
    if tarifa is None:
        return Response({
            'status': '200',
            'error': 'Se han cerrado las inscripciones.',
            'data': []
        }, status=status.HTTP_200_OK)

    cupon = CuponDescuento.objects.filter(codigo=request.data['cuponDescuento']).first()
    if cupon is not None:
        tarifa = cupon.idTarifa
        if tarifa.fechaDesde.date() <= hoy.date() <= tarifa.fechaHasta.date():
            if cupon.usosRestantes > 0:
                restante = cupon.usosRestantes - 1
                cupon.usosRestantes = restante
                cupon.save()

                porcentaje = cupon.porcentajeDesc / 100
                descuento = tarifa.precio * porcentaje
                precioFinal = tarifa.precio - descuento
                cupon = cupon.id
            else:
                return Response({
                    'status': '200',
                    'error': 'El cupón ingresado es inválido.',
                    'data': []
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': '200',
                'error': 'El cupón ingresado es inválido.',
                'data': []
            }, status=status.HTTP_200_OK)
    else:
        precioFinal = tarifa.precio

    datos = {
        'idUsuario': usuario.id,
        'idTarifa': tarifa.id,
        'idCongreso': payload['idCongreso'],
        'fechaPago': None,
        'fechaInscripcion': hoy,
        'idCupon': cupon,
        'precioFinal': precioFinal
    }
    serializer = InscripcionSerializer(data=datos)

    if serializer.is_valid() and usuario.is_authenticated:
        serializer.save()
        return Response({
            'status': '200',
            'error': '',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': '200',
            'error': serializer.errors,
            'data': []
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([Authentication])
def verificarCuponDescuento(request):
    """
    Verifica si el cupón es válido y devuelve los datos correspondientes.
    """
    cupon = CuponDescuento.objects.filter(codigo=request.GET['cuponDescuento']).first()
    if cupon is not None:
        tarifa = cupon.idTarifa
        hoy = timezone.now()
        if tarifa.fechaDesde.date() <= hoy.date() <= tarifa.fechaHasta.date():
            if cupon.usosRestantes > 0:
                serializer = CuponDescuentoSerializer(instance=cupon)
                return Response({
                    'status': '200',
                    'error': '',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': '400',
                    'error': 'El cupón ingresado es inválido.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'status': '400',
                'error': 'El cupón ingresado es inválido.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'status': '400',
            'error': 'El cupón ingresado es inválido.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([Authentication])
def editarInscripcion(request):
    return None
    # usuario = request.user
    # token = request.headers['Authorization']
    # payload = jwt.decode(token, settings.SECRET_KEY)
    # inscripcion = Inscripcion.objects.filter(idUsuario=usuario.id).first()
    # congreso = Congreso.objects.filter(id=payload['idCongreso']).first()
    # tarifa = inscripcion.idTarifa
    # cupon = CuponDescuento.objects.filter(codigo=request.data['cuponDescuento']).first()
    # if cupon is not None:
    #     if cupon.usosRestantes > 0:
    #             restante = cupon.usosRestantes - 1
    #             cupon.usosRestantes = restante
    #             cupon.save()

    #             porcentaje = cupon.porcentajeDesc / 100
    #             descuento = tarifa.precio * porcentaje
    #             precioFinal = tarifa.precio - descuento
    #             cupon = cupon.id
    #     else:
    #         return Response({
    #             'status': '400',
    #             'error': 'El cupón ingresado es inválido.',
    #             'data': []
    #         }, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     precioFinal = tarifa.precio

    # datos = {
    #     'idUsuario': usuario.id,
    #     'idTarifa': inscripcion.idTarifa.id,
    #     'idCongreso': payload['idCongreso'],
    #     'fechaPago': inscripcion.fechaPago,
    #     'fechaInscripcion': inscripcion.fechaInscripcion,
    #     'idCupon': request.data['cuponDescuento'],
    #     'precioFinal': precioFinal
    # }
    # serializer = InscripcionSerializer(instance=inscripcion, data=datos)

    # if serializer.is_valid():
    #     serializer.save()
    #     return Response({
    #         'status': '200',
    #         'error': '',
    #         'data': [serializer.data]
    #     }, status=status.HTTP_200_OK)

    # return Response({
    #     'status': '400',
    #     'error': serializer.errors,
    #     'data': []
    # }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminarInscripcion(request):
    """ Permite eliminar una inscripción. """
    usuario = request.user

    idInscripcion = request.GET['idInscripcion']

    inscripcion = Inscripcion.objects.filter(id=idInscripcion).first()
    if inscripcion is not None:
        inscripcion.delete()
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': '400',
            'error': 'La inscripción no existe.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def getInscripciones(request):
    """ Devuelve la lista de inscripciones a un congreso. """

    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    id_congreso = payload['idCongreso']
    try:
        inscripciones = Inscripcion.objects.filter(idCongreso=id_congreso).all()
        serializer = InscripcionSerializer(inscripciones, many=True)
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver la lista de inscripciones.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def getInscripcion(request):
    """ Devuelve los datos de una inscripción. """

    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY)
    idInscripcion = request.GET['idInscripcion']
    try:
        inscripcion = Inscripcion.objects.filter(id=idInscripcion).first()
        if inscripcion is None:
            return Response({
                'status': '400',
                'error': "La inscripción no existe.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = InscripcionSerializer(instance=inscripcion)
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver la inscripción.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


# PRUEBA MERCADO PAGO

@api_view(['GET'])
def pruebaMercadoPago(request):
    return render(request, 'prueba_mercadopago.html')


@api_view(['POST'])
@authentication_classes([Authentication])
def create_preference(request):
    # cantidadEntradas = request.data['cantidadEntradas']
    idInscripcion = request.data['idInscripcion']
    token = request.headers['Authorization']
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    fechaHoy = timezone.now()
    congreso = Congreso.objects.filter(id=payload['idCongreso']).first()
    print(congreso)
    # Verifico que no haya pasado la fecha de inscripción.
    if (fechaHoy.date() > congreso.fechaFinInsTardia.date()):
        return Response({
            'status': '400',
            'error': "La fecha de inscripcion al congreso finalizo. No es posible realizar su inscripción.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    datosInscripcion = Inscripcion.objects.filter(id=idInscripcion).first()

    precioEntrada = datosInscripcion.precioFinal

    # Creo el token que lleva la informacion de la inscripcion
    payloadIns = {
        'idInscripcion': idInscripcion,
        'nombreCongreso': congreso.nombre,
        'exp': datetime.utcnow() + timedelta(days=30),
        'iat': datetime.utcnow()
    }
    tokenInscripcion = jwt.encode(payloadIns, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
    current_site = config('URL_FRONT_DEV')
    relative_link_success = 'pagoInscripcionSuccess'
    relative_link_failure = 'pagoInscripcionFailure'
    relate_link_pending = 'pagoInscripcionPending'
    url_success = 'http://' + current_site + relative_link_success + "/" + tokenInscripcion
    url_failure = 'http://' + current_site + relative_link_failure + "/" + tokenInscripcion
    url_pending = 'http://' + current_site + relate_link_pending + "/" + tokenInscripcion

    # Crea un ítem en la preferencia
    preference_data = {
        "items": [
            {
                "title": "Entrada Congressity",
                "quantity": 1,
                "unit_price": precioEntrada,
                "description": "Entrada para el congreso CoNaIISI-" + str(fechaHoy.year),
                "category_id": "tickets"
            }
        ],
        "back_urls": {
            "success": url_success,
            "failure": url_failure,
            "pending": url_pending
        },
        "auto_return": "approved"
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    return Response(preference)


@api_view(['GET'])
def pagoInscripcionSuccess(request):
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        inscripcion = Inscripcion.objects.get(id=payload['idInscripcion'])
        if inscripcion != None:
            send_mail_entrada(request,inscripcion.id)
            inscripcion.fechaPago = timezone.now()
            inscripcion.save()
        return Response({'email': 'Se genero correctamente el pago de la inscripción.'}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError as identifier:
        return Response({'error': 'El link expiró'}, status=status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
        return Response({'error': 'Token Inválido'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def devolverTarifaPorId(request):
    """ Devuelve la lista de tarifas por congreso. """

    usuario = request.user
    idTarifa = request.GET['id']
    if usuario.is_authenticated:
        token = request.headers['Authorization']
        if not token:
            raise AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Usuario no autenticado!')
        id_congreso = payload['idCongreso']
    try:
        tarifa = Tarifa.objects.filter(idCongreso=id_congreso).filter(id=idTarifa).first()
        datos = {
            'id': tarifa.id,
            'idCongreso': tarifa.idCongreso.id,
            'nombre': tarifa.nombre,
            'precio': tarifa.precio,
            'fechaDesde': tarifa.fechaDesde,
            'fechaHasta': tarifa.fechaHasta
        }
        return Response({
            'status': '200',
            'error': '',
            'data': [datos]
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver la tarifa.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([Authentication])
def verificarCodigoCupon(request):
    """
    Verifica si el cupón recibido ya existe.
    """
    cupon = CuponDescuento.objects.filter(codigo=request.GET['cuponDescuento']).first()
    if cupon is None:
        return Response({
            'status': '200',
            'error': '',
            'data': []
        }, status=status.HTTP_200_OK)
    else:
        return Response({
                    'status': '400',
                    'error': 'Ya existe un cupón con ese código.',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)


def send_mail_entrada(request, idInscripcion):
    try:
        insc = Inscripcion.objects.filter(id=idInscripcion).first()
        idUsuario = insc.idUsuario.id
        idCongreso = insc.idCongreso.id
        usuario = Usuario.objects.filter(id=idUsuario).first()
        payload = {
                'idUsuario': idUsuario,
                'idCongreso': idCongreso,
                'exp' : date_mails.datetime.utcnow() + date_mails.timedelta(days=360),
                'iat': date_mails.datetime.utcnow()
            }
        token = jwt.encode(payload, settings.SECRET_KEY , algorithm='HS256').decode('utf-8')
        current_site = get_current_site(request).domain
        relative_link = reverse('registrar-asistencia')
        url= 'http://' + current_site + relative_link 
        url = url + "?token=" + token
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_H,
            box_size = 10,
            border = 4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image()
        nombre_archivo = str(idCongreso) + str(idUsuario) + ".png"
        archivo = settings.INSCRIPCIONES_CARPETA + nombre_archivo
        img.save(archivo)
        context = {'data_imagen': nombre_archivo}
        template = get_template('entrada_congreso.html')
        content = template.render(context) 
        correo = EmailMultiAlternatives(
            'Entrada Al Congreso - CoNaIISI',
            '',
            settings.EMAIL_HOST_USER,
            [usuario.email]
        )
        correo.attach_alternative(content, 'text/html')
        with open(archivo, 'rb') as f:
            img_data = f.read()
        correo.attach("Entrada_Congreso.png", img_data, 'image/png')
        correo.send()
        return Response({
            'status': '200',
            'error': '',
            'data': ''
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def registrar_asistencia(request):
    """
    Permite activar una cuenta a traves de un link de activación (Enviado cuando se registró.).
    """
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        user = Usuario.objects.get(id=payload['idUsuario'])
        congreso = Congreso.objects.get(id=payload['idCongreso'])
        if not user.is_verified:
            user.is_verified = True
            user.save()
        return Response({'email': 'Se activó correctamente la cuenta'}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError as identifier:
        return Response({'error': 'El link expiró'}, status= status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
        return Response({'error': 'Token Inválido'}, status= status.HTTP_400_BAD_REQUEST)