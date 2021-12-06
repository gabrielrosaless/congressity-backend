from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
from usuarios.authentication import *
from usuarios.serializers import *
from articulos.models import *
from articulos.serializers import *
from congresos.models import *
from inscripciones.models import *
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
from django.forms.models import model_to_dict
from django.http import FileResponse
from tempfile import TemporaryFile

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
        datos = request.data["datos"] # id - valor
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
    myfile = request.FILES['archivo']
    fs = FileSystemStorage()
    filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
    url = fs.url(filename)
    datos = {
        "template": myfile.name,
        "nombre": request.data["nombre"],
        "descripcion": request.data["descripcion"]
    }
    serializer = CertificadoSerializer(data=datos)
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
@authentication_classes([Authentication])
def editarCertificado(request):
    usuario = request.user
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
        certificados = Certificado.objects.filter().all()
        serializer = CertificadoSerializer(certificados, many=True)
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


@api_view(['DELETE'])
@authentication_classes([Authentication])
def eliminarCertificado(request):
    usuario = request.user
    idCertificado = request.GET['idCertificado']
    try:
        certificado = Certificado.objects.filter(pk=idCertificado).first()
    except Certificado.DoesNotExist:
        raise Http404("El Certificado no existe.")

    if usuario.is_authenticated:
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
    serializer = DetalleCertificadoSerializer(data=request.data)
    print(serializer)
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
@authentication_classes([Authentication])
def editarDetalleCertificado(request):
    usuario = request.user

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
        certificados = DetalleCertificado.objects.filter(idCerificado=idCertificado).filter().all()
        serializer = DetalleCertificadoSerializer(certificados, many=True)
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
        certificado = Certificado.objects.filter(id=idCertificado).first()
        template = os.path.join(settings.BASE_DIR , "articulos/papers/" +certificado.template)
        img = Image.open(template)
        datos = request.data["datos"]
        if len(datos) > 0:
            for detalles in datos:
                font = ImageFont.truetype(font = os.path.join(settings.BASE_DIR , "certificados/fonts/" + str(detalles["tipoLetra"])), size=detalles["tamañoLetra"])
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


@api_view(['GET'])
@authentication_classes([Authentication])
def getArchivoTemplate(request):
    idCertificado = request.GET['idCertificado']
    try:
        certificado = Certificado.objects.filter(id=idCertificado).first()
        if certificado == None:
            return Response({
            'status': '400',
            'error': 'No existe el certificado.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        url = certificado.template
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
        
        
@api_view(['POST'])
@authentication_classes([Authentication])
def crearCertificadoMasivo(request):
    mensaje = ""
    try:
        idCongreso = request.data["idCongreso"]
        idCertificadoAsistentes = request.data["idCertificadoAsistentes"]
        idCertificadoAutores = request.data["idCertificadoAutores"]
        idCertificadoEvaluadores = request.data["idCertificadoEvaluadores"]
        idCertificadoChairPpal = request.data["idCertificadoChairPpal"]
        idCertificadoCharSec = request.data["idCertificadoCharSec"]
        idCertificadoExpositores = request.data["idCertificadoExpositores"]
        
        ##########################  ASISTENTES ################################
        mensaje = "Asistentes"
        certificado_asistentes = Certificado.objects.filter(id=idCertificadoAsistentes).first()
        template_asistentes = os.path.join(settings.BASE_DIR , "articulos/papers/" + certificado_asistentes.template)
        asistentes = Inscripcion.objects.filter(idCongreso=idCongreso,asistio=True).all()
        if len(asistentes) > 0:
            for asistente in asistentes:
                usuario = Usuario.objects.filter(id=asistente.idUsuario.id).first()
                datos_usuario = model_to_dict(usuario)
                img = Image.open(template_asistentes)
                nombre = "Certificado_Asistente_"  + str(usuario.id) + "_" + str(idCongreso) + ".png"
                # archivo = settings.CERTIFICADOS_CARPETA + nombre
                detalles = DetalleCertificado.objects.filter(idCerificado=idCertificadoAsistentes).all()
                if len(detalles) > 0:
                    for detalle in detalles:
                        font = ImageFont.truetype(font = os.path.join(settings.BASE_DIR , "certificados/fonts/" + str(detalle.tipoLetra)), size=detalle.tamañoLetra)
                        draw = ImageDraw.Draw(img)
                        draw.text(xy=(detalle.posX,detalle.posY),text='{}'.format(datos_usuario[detalle.atributo_usuario]),fill=(0,0,0),font=font)
                    fp = TemporaryFile()
                    img.save(fp, "PNG")
                    fs = FileSystemStorage()
                    if not fs.exists(nombre):
                        file = fs.save(nombre, fp)
                    res = send_mail_certificado(str(nombre) ,str(nombre),'Asistente',usuario.id)
                    
        ##########################  ASISTENTES SIN CUENTA ################################
        mensaje = "Asistentes sin cuenta"
        certificado_asistentes = Certificado.objects.filter(id=idCertificadoAsistentes).first()
        template_asistentes_sin_cuenta = os.path.join(settings.BASE_DIR , "articulos/papers/" + certificado_asistentes.template)
        asistentes_sin_cuenta = InscripcionSinCuenta.objects.filter(idCongreso=idCongreso,asistio=True).all()
        if len(asistentes_sin_cuenta) > 0:
            for asistente in asistentes_sin_cuenta:
                datos_usuario = model_to_dict(asistente)
                img = Image.open(template_asistentes_sin_cuenta)
                nombre = "Certificado_Asistente_" + str(asistente.dni) + "_" + str(idCongreso) + ".png"
                # archivo = settings.CERTIFICADOS_CARPETA + nombre
                detalles = DetalleCertificado.objects.filter(idCerificado=idCertificadoAsistentes).all()
                if len(detalles) > 0:
                    for detalle in detalles:
                        font = ImageFont.truetype(font = os.path.join(settings.BASE_DIR , "certificados/fonts/" + str(detalle.tipoLetra)), size=detalle.tamañoLetra)
                        draw = ImageDraw.Draw(img)
                        draw.text(xy=(detalle.posX,detalle.posY),text='{}'.format(datos_usuario[detalle.atributo_usuario]),fill=(0,0,0),font=font)
                    fp = TemporaryFile()
                    img.save(fp, "PNG")
                    fs = FileSystemStorage()
                    if not fs.exists(nombre):
                        file = fs.save(nombre, fp)
                    res = send_mail_certificado_sin_cuenta(str(nombre) ,str(nombre),'Asistente',asistente.email)

        ##########################  AUTORES ################################
        mensaje = "Autores"
        certificado_autores = Certificado.objects.filter(id=idCertificadoAutores).first()
        template_autores = os.path.join(settings.BASE_DIR , "articulos/papers/" +certificado_autores.template)
        autores = AutorXArticulo.objects.filter(idArticulo__idCongreso=idCongreso).all()
        if len(autores) > 0:
            for autor in autores:
                usuario = Usuario.objects.filter(id=autor.idUsuario.id).first()
                datos_usuario = model_to_dict(usuario)
                img = Image.open(template_autores)
                nombre = "Certificado_Autor"  + str(usuario.id) + "_" + str(idCongreso) + ".png"
                # archivo = settings.CERTIFICADOS_CARPETA + nombre
                detalles = DetalleCertificado.objects.filter(idCerificado=idCertificadoAutores).all()
                if len(detalles) > 0:
                    for detalle in detalles:
                        font = ImageFont.truetype(font = os.path.join(settings.BASE_DIR , "certificados/fonts/" + str(detalle.tipoLetra)), size=detalle.tamañoLetra)
                        draw = ImageDraw.Draw(img)
                        draw.text(xy=(detalle.posX,detalle.posY),text='{}'.format(datos_usuario[detalle.atributo_usuario]),fill=(0,0,0),font=font)
                    fp = TemporaryFile()
                    img.save(fp, "PNG")
                    fs = FileSystemStorage()
                    if not fs.exists(nombre):
                        file = fs.save(nombre, fp)
                    res = send_mail_certificado(str(nombre) ,str(nombre),'Autor',usuario.id)
        
        ##########################  CHAIR PPAL ################################
        mensaje = "CP"
        certificado_chairppal = Certificado.objects.filter(id=idCertificadoChairPpal).first()
        template_chairppal = os.path.join(settings.BASE_DIR , "articulos/papers/" +certificado_chairppal.template)
        congreso = Congreso.objects.filter(id=idCongreso).first()
        chair = congreso.chairPrincipal
        usuario = Usuario.objects.filter(email=chair).first()
        datos_usuario = model_to_dict(usuario)
        img = Image.open(template_chairppal)
        nombre = "Certificado_Chair_Ppal_" + str(usuario.id) + "_" + str(idCongreso) + ".png"
        # archivo = settings.CERTIFICADOS_CARPETA + nombre
        detalles = DetalleCertificado.objects.filter(idCerificado=idCertificadoChairPpal).all()
        if len(detalles) > 0:
            for detalle in detalles:
                font = ImageFont.truetype(font = os.path.join(settings.BASE_DIR , "certificados/fonts/" + str(detalle.tipoLetra)), size=detalle.tamañoLetra)
                draw = ImageDraw.Draw(img)
                draw.text(xy=(detalle.posX,detalle.posY),text='{}'.format(datos_usuario[detalle.atributo_usuario]),fill=(0,0,0),font=font)
            fp = TemporaryFile()
            img.save(fp, "PNG")
            fs = FileSystemStorage()
            if not fs.exists(nombre):
                file = fs.save(nombre, fp)
            res = send_mail_certificado(str(nombre) ,str(nombre),'Chair Principal',usuario.id)

        ##########################  CHAIR SECUNDARIO ################################
        mensaje = "CS"
        certificado_chairsecundario = Certificado.objects.filter(id=idCertificadoCharSec).first()
        template_chairsecundario = os.path.join(settings.BASE_DIR , "articulos/papers/" +certificado_chairsecundario.template)
        chairSecundarios = ChairXSimposioXCongreso.objects.filter(idCongreso=idCongreso).all()
        data = []
        if len(chairSecundarios) > 0:
            for chair in chairSecundarios:
                usuario = Usuario.objects.filter(id=chair.idUsuario.id).first()
                datos_usuario = model_to_dict(usuario)
                img = Image.open(template_chairsecundario)
                nombre = "Certificado_Chair_Secun_"  + str(usuario.id) + "_" + str(idCongreso) + ".png"
                # archivo = settings.CERTIFICADOS_CARPETA + nombre
                detalles = DetalleCertificado.objects.filter(idCerificado=idCertificadoCharSec).all()
                if len(detalles) > 0:
                    for detalle in detalles:
                        font = ImageFont.truetype(font = os.path.join(settings.BASE_DIR , "certificados/fonts/" + str(detalle.tipoLetra)), size=detalle.tamañoLetra)
                        draw = ImageDraw.Draw(img)
                        draw.text(xy=(detalle.posX,detalle.posY),text='{}'.format(datos_usuario[detalle.atributo_usuario]),fill=(0,0,0),font=font)
                    fp = TemporaryFile()
                    img.save(fp, "PNG")
                    fs = FileSystemStorage()
                    if not fs.exists(nombre):
                        file = fs.save(nombre, fp)
                    res = send_mail_certificado(str(nombre) ,str(nombre) ,'Chair Secundario',usuario.id)
        
        ##########################  EVALUADORES ################################
        mensaje = "Ev"
        certificado_evaluador = Certificado.objects.filter(id=idCertificadoEvaluadores).first()
        template_evaluador = os.path.join(settings.BASE_DIR , "articulos/papers/" +certificado_evaluador.template)
        evaluadores = EvaluadorXCongreso.objects.filter(idCongreso=idCongreso).all()
        data = []
        if len(evaluadores) > 0:
            for evaluador in evaluadores:
                usuario = Usuario.objects.filter(id=evaluador.idUsuario.id).first()
                datos_usuario = model_to_dict(usuario)
                img = Image.open(template_evaluador)
                nombre = "Certificado_Evaluador_"  + str(usuario.id) + "_" + str(idCongreso) + ".png"
                # archivo = settings.CERTIFICADOS_CARPETA + nombre
                detalles = DetalleCertificado.objects.filter(idCerificado=idCertificadoEvaluadores).all()
                if len(detalles) > 0:
                    for detalle in detalles:
                        font = ImageFont.truetype(font = os.path.join(settings.BASE_DIR , "certificados/fonts/" + str(detalle.tipoLetra)), size=detalle.tamañoLetra)
                        draw = ImageDraw.Draw(img)
                        draw.text(xy=(detalle.posX,detalle.posY),text='{}'.format(datos_usuario[detalle.atributo_usuario]),fill=(0,0,0),font=font)
                    fp = TemporaryFile()
                    img.save(fp, "PNG")
                    fs = FileSystemStorage()
                    if not fs.exists(nombre):
                        file = fs.save(nombre, fp)
                    res = send_mail_certificado(str(nombre) ,str(nombre) ,'Evaluador',usuario.id)
        
        ##########################  EXPOSITOR ################################
        mensaje = "Ex"
        certificado_expositores = Certificado.objects.filter(id=idCertificadoExpositores).first()
        template_expositores = os.path.join(settings.BASE_DIR , "articulos/papers/" +certificado_expositores.template)
        autores = AutorXArticulo.objects.filter(idUsuario__id__in=Inscripcion.objects.values_list('idUsuario', flat=True),idArticulo__idCongreso=idCongreso, idArticulo__idEstado__in=[5,6]).all()
        data = []
        if len(autores) > 0:
            for autor in autores:
                usuario = Usuario.objects.filter(id=autor.id).first()
                datos_usuario = model_to_dict(usuario)
                img = Image.open(template_expositores)
                nombre = "Certificado_Expositor_"  + str(usuario.id) + "_" + str(idCongreso) + ".png"
                # archivo = settings.CERTIFICADOS_CARPETA + nombre
                detalles = DetalleCertificado.objects.filter(idCerificado=idCertificadoAutores).all()
                if len(detalles) > 0:
                    for detalle in detalles:
                        font = ImageFont.truetype(font = os.path.join(settings.BASE_DIR , "certificados/fonts/" + str(detalle.tipoLetra)), size=detalle.tamañoLetra)
                        draw = ImageDraw.Draw(img)
                        draw.text(xy=(detalle.posX,detalle.posY),text='{}'.format(datos_usuario[detalle.atributo_usuario]),fill=(0,0,0),font=font)
                    fp = TemporaryFile()
                    img.save(fp, "PNG")
                    fs = FileSystemStorage()
                    if not fs.exists(nombre):
                        file = fs.save(nombre, fp)
                    res = send_mail_certificado(str(nombre),str(nombre) ,'Expositor',usuario.id)
        
        return Response({
            'status': '200',
            'error': '',
            'data': "Ok"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': str(e.args) + "|| " + mensaje ,
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

def send_mail_certificado(archivo,nombre_archivo, tipo, idUsuario):
    try:
        archivo = settings.MEDIA_ROOT + archivo
        usuario = Usuario.objects.filter(id=idUsuario).first()
        context = {'data_imagen': nombre_archivo, 'rol':tipo}
        template = get_template('certificado_congreso.html')
        content = template.render(context) 
        correo = EmailMultiAlternatives(
            'Certificado Congreso ' + str(tipo) + '- CoNaIISI',
            '',
            settings.EMAIL_HOST_USER,
            [usuario.email]
        )
        correo.attach_alternative(content, 'text/html')
        with open(archivo, 'rb') as f:
            img_data = f.read()
        correo.attach("Certificado_Congreso.png", img_data, 'image/png')
        correo.send()
        return True
    except Exception as e:
        return e.args
    
def send_mail_certificado_sin_cuenta(archivo,nombre_archivo, tipo, correo_usuario):
    try:
        archivo = settings.MEDIA_ROOT + archivo
        context = {'data_imagen': nombre_archivo, 'rol':tipo}
        template = get_template('certificado_congreso.html')
        content = template.render(context) 
        correo = EmailMultiAlternatives(
            'Certificado Congreso ' + str(tipo) + '- CoNaIISI',
            '',
            settings.EMAIL_HOST_USER,
            [correo_usuario]
        )
        correo.attach_alternative(content, 'text/html')
        with open(archivo, 'rb') as f:
            img_data = f.read()
        correo.attach("Certificado_Congreso.png", img_data, 'image/png')
        correo.send()
        return True
    except Exception as e:
        return e.args