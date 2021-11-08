from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
from usuarios.authentication import *
from congresos.models import Congreso
from rest_framework.decorators import api_view, authentication_classes
from .serializers import *
from .models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.http import Http404
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.template.loader import get_template
import jwt
from django.core.mail import EmailMultiAlternatives
from django.core.files.storage import default_storage, FileSystemStorage
import base64
from io import BytesIO


@api_view(['POST'])
def crearCertificado(request):
    try:
        nombre = request.data["nombre"]
        font = ImageFont.truetype('arial.ttf',60)
        template = os.path.join(settings.BASE_DIR , 'certificados\\templates\\certificate.jpg')
        img = Image.open(template)
        draw = ImageDraw.Draw(img)
        archivo = settings.CERTIFICADOS_CARPETA + nombre 
        draw.text(xy=(725,760),text='{}'.format(nombre),fill=(0,0,0),font=font)
        img.save('{}.jpg'.format(archivo))
        return Response({
            'status': '200',
            'error': '',
            'data': "Ok"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([Authentication])
def crearCertificadoParametrizado(request):
    try:
        idCertificado = request.data["idCertificado"]
        idUsuario = request.data["idUsuario"]
        idCongreso = request.data["idCongreso"]
        certificado = Certificado.objects.filter(id=idCertificado).first()
        template = os.path.join(settings.BASE_DIR , "certificados\\templates\\" +certificado.template)
        img = Image.open(template)
        nombre = "Certificado_" + certificado.nombre + "_" + str(idUsuario) + "_" + str(idCongreso)
        archivo = settings.CERTIFICADOS_CARPETA + nombre 
        datos = request.data["datos"]
        for detalles in datos:
            detalle = DetalleCertificado.objects.filter(id=detalles["id"]).first()
            font = ImageFont.truetype(detalle.tipoLetra,detalle.tamañoLetra)
            draw = ImageDraw.Draw(img)
            draw.text(xy=(detalle.posX,detalle.posY),text='{}'.format(detalles["valor"]),fill=(0,0,0),font=font)
        img.save('{}.jpg'.format(archivo))
        return Response({
            'status': '200',
            'error': '',
            'data': "Ok"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([Authentication])
def altaCertificado(request):
    usuario = request.user
    if not usuario.is_superuser:
        raise AuthenticationFailed('El usuario no posee los permisos necesarios.')
    myfile = request.FILES['archivo']
    fs = FileSystemStorage(settings.CERTIFICADOS_TEMPLATES)
    filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
    url = fs.url(filename)
    datos = {
        "template": myfile.name,
        "nombre": request.data["nombre"],
        "descripcion": request.data["descripcion"]
    }
    serializer = CertificadoSerializer(data=datos)
    if (serializer.is_valid() and usuario.is_authenticated and usuario.is_superuser):
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
def editarCertificado(request):
    usuario = request.user
    if not usuario.is_superuser:
        raise AuthenticationFailed('El usuario no posee los permisos necesarios.')

    id_certificado = request.GET['idCertificado']

    try:
        certificado = Certificado.objects.get(id=id_certificado)
    except Certificado.DoesNotExist:
        raise Http404("El Certificado no existe.")

    serializer = CertificadoSerializer(instance=certificado, data=request.data)

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
def devolverCertificados(request):
    try:
        certificados = Certificado.objects.filter(is_active=True).filter().all()
        serializer = CertificadoSerializer(certificados, many=True)
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver la lista de certificados.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminarCertificado(request):
    usuario = request.user
    idCertificado = request.GET['idCertificado']
    try:
        certificado = Certificado.objects.filter(pk=idCertificado).first()
    except Certificado.DoesNotExist:
        raise Http404("El Certificado no existe.")

    if usuario.is_authenticated and usuario.is_superuser:
        certificado.delete()
        return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)

    return Response({
                'status': '400',
                'error': 'Error al dar de baja el certificado.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([Authentication])
def altaDetalleCertificado(request):
    usuario = request.user
    if not usuario.is_superuser:
        raise AuthenticationFailed('El usuario no posee los permisos necesarios.')

    serializer = DetalleCertificadoSerializer(data=request.data)
    print(serializer)
    if (serializer.is_valid() and usuario.is_authenticated and usuario.is_superuser):
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
def editarDetalleCertificado(request):
    usuario = request.user
    if not usuario.is_superuser:
        raise AuthenticationFailed('El usuario no posee los permisos necesarios.')

    id_certificado = request.GET['idDetalleCertificado']

    try:
        certificado = DetalleCertificado.objects.get(id=id_certificado)
    except Certificado.DoesNotExist:
        raise Http404("El Certificado no existe.")

    serializer = DetalleCertificadoSerializer(instance=certificado, data=request.data)

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
def devolverDetallesCertificados(request):
    try:
        idCertificado = request.GET['idCertificado']
        certificados = DetalleCertificado.objects.filter(idCertificado=idCertificado).filter().all()
        serializer = DetalleCertificadoSerializer(certificados, many=True)
        return Response({
            'status': '200',
            'error': '',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error al devolver la lista de certificados.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminarDetalleCertificado(request):
    usuario = request.user
    idCertificado = request.GET['idDetalleCertificado']
    try:
        certificado = DetalleCertificado.objects.filter(id=idCertificado).first()
    except DetalleCertificado.DoesNotExist:
        raise Http404("El Certificado no existe.")

    if usuario.is_authenticated and usuario.is_superuser:
        certificado.delete()
        return Response({
                'status': '200',
                'error': '',
                'data': []
            }, status=status.HTTP_200_OK)

    return Response({
                'status': '400',
                'error': 'Error al dar de baja el certificado.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([Authentication])
def PruebaCertificadoParametrizado(request):
    try:
        idCertificado = request.data["idCertificado"]
        idUsuario = request.data["idUsuario"]
        idCongreso = request.data["idCongreso"]
        certificado = Certificado.objects.filter(id=idCertificado).first()
        template = os.path.join(settings.BASE_DIR , "certificados\\templates\\" +certificado.template)
        img = Image.open(template)
        datos = request.data["datos"]
        for detalles in datos:
            font = ImageFont.truetype(detalles["tipoLetra"],detalles["tamañoLetra"])
            draw = ImageDraw.Draw(img)
            draw.text(xy=(detalles["posX"],detalles["posY"]),text='{}'.format(detalles["valor"]),fill=(0,0,0),font=font)
        
        #byte_io = BytesIO()
        #img.save(byte_io, 'PNG')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=75)
        b64_string = base64.b64encode(buffer.getbuffer())
        return Response({
            'status': '200',
            'error': '',
            'data': [b64_string]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': e.args,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)