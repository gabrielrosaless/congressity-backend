from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
from usuarios.authentication import *
from congresos.models import *
from inscripciones.models import *
from rest_framework.decorators import api_view, authentication_classes
from .models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.http import Http404
import jwt
from articulos.models import *
from django.db.models.expressions import RawSQL
from django.db import connection


@api_view(['GET'])
def devolverTopEvaluadores(request):
    try:
        cantidad = request.GET['cantidad']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT "idUsuario_id", COUNT("idUsuario_id") as "Cantidad" FROM public.articulos_articulosxevaluador
        GROUP BY "idUsuario_id" ORDER BY "Cantidad" desc limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            usuario = Usuario.objects.filter(id=i[0]).first()
            datos = {
                "name": usuario.nombre + " " + usuario.apellido,
                "value": i[1]
            }
            data.append(datos)
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def devolverTopEvaluadoresCongreso(request):
    try:
        cantidad = request.GET['cantidad']
        idCongreso = request.GET['idCongreso']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT "idUsuario_id", COUNT("idUsuario_id") as "Cantidad" FROM public.articulos_articulosxevaluador
        WHERE "idCongreso_id" = ''' + idCongreso + '''
        GROUP BY "idUsuario_id" ORDER BY "Cantidad" desc limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            usuario = Usuario.objects.filter(id=i[0]).first()
            datos = {
                "name": usuario.nombre + " " + usuario.apellido,
                "value": i[1]
            }
            data.append(datos)
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def devolverTopSimposiosXCongreso(request):
    try:
        cantidad = request.GET['cantidad']
        idCongreso = request.GET['idCongreso']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT "idSimposio_id", COUNT("idSimposio_id") as "Cantidad" FROM public.articulos_articulo
        WHERE "idCongreso_id" = ''' + idCongreso + '''
        GROUP BY "idSimposio_id" ORDER BY "Cantidad" desc limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            simposio = SimposiosxCongreso.objects.filter(id=i[0]).first()
            simposio_gral = Simposio.objects.filter(id=simposio.idSimposio.id).first()
            datos = {
                "name": simposio_gral.nombre,
                "value": i[1]
            }
            data.append(datos)
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def devolverTopSimposiosGeneral(request):
    try:
        cantidad = request.GET['cantidad']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT co.id, COUNT(co.id) as "Cantidad" FROM public.articulos_articulo a
        INNER JOIN public.congresos_simposiosxcongreso c on  (a."idSimposio_id" = c.id)
        INNER JOIN public.congresos_simposio co on (c."idSimposio_id" = co.id)
        GROUP BY co.id ORDER BY "Cantidad" desc limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            simposio_gral = Simposio.objects.filter(id=i[0]).first()
            datos = {
                "name": simposio_gral.nombre,
                "value": i[1]
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
def devolverTopSimposiosXEvaluadores(request):
    try:
        cantidad = request.GET['cantidad']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT "idSimposio_id", COUNT("idSimposio_id") as "Cantidad" FROM public.articulos_simposiosxevaluador 
        GROUP BY "idSimposio_id" ORDER BY "Cantidad" desc limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            simposio = Simposio.objects.filter(id=i[0]).first()
            datos = {
                "name": simposio.nombre,
                "value": i[1]
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
def devolverEdadesXCongreso(request):
    try:
        idCongreso = request.GET['idCongreso']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT SUM(CASE WHEN EXTRACT(YEAR FROM age(cast("fechaNacimiento" as date))) < 18 THEN 1 ELSE 0 END) AS "[Menor a 18]",
        SUM(CASE WHEN EXTRACT(YEAR FROM age(cast("fechaNacimiento" as date))) BETWEEN 18 AND 24 THEN 1 ELSE 0 END) AS "[18-24]",
        SUM(CASE WHEN EXTRACT(YEAR FROM age(cast("fechaNacimiento" as date))) BETWEEN 25 AND 40 THEN 1 ELSE 0 END) AS "[25-40]",
		SUM(CASE WHEN EXTRACT(YEAR FROM age(cast("fechaNacimiento" as date))) > 41 THEN 1 ELSE 0 END) AS "[Mayor a 40]"
        FROM public.usuarios_usuario
        WHERE id IN (select "idUsuario_id" from public.inscripciones_inscripcion where "idCongreso_id" = ''' +idCongreso + ")")
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            datos = {
                "menor-18": i[0],
                "entre-18-24": i[1],
                "entre-25-40": i[2],
                "mayor-40": i[3],
            }
            data.append(datos)
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def devolverParticipantesXSede(request):
    try:
        idCongreso = request.GET['idCongreso']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT public.congresos_sede.nombre , COUNT("sede_id") as "Cantidad" 
        FROM public.usuarios_usuario
        INNER JOIN public.congresos_sede ON public.congresos_sede.id = public.usuarios_usuario.sede_id
        WHERE public.usuarios_usuario.id IN (select "idUsuario_id" from public.inscripciones_inscripcion where "idCongreso_id" = ''' + idCongreso + ''' )
        GROUP BY public.congresos_sede.nombre ORDER BY "Cantidad"''')
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            datos = {
                "name": i[0],
                "value": i[1],
            }
            data.append(datos)
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': '400',
            'error': "Error.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@api_view(['GET'])
def devolverReporteEvaluadores(request):
    try:
        idCongreso = request.GET['idCongreso']
        
        evaluadores = EvaluadorXCongresoXChair.objects.filter(idCongreso=idCongreso).all().distinct('idEvaluador')
        data = []
        for evaluador in evaluadores:
            usuario = Usuario.objects.filter(id=evaluador.idEvaluador.id).first()
            cantidad_evaluaciones = ArticulosXEvaluador.objects.filter(idUsuario=usuario.id).count()
            cantidad_canceladas = EvaluacionCancelada.objects.filter(idUsuario=usuario.id,idCongreso=idCongreso).count()
            sede = Sede.objects.filter(id=usuario.sede.id).first()
            datos = {
                "nombre":usuario.nombre,
                "apellido":usuario.apellido,
                "dni": usuario.dni,
                "sede": sede.nombre,
                "evaluacionesRealizadas": cantidad_evaluaciones,
                "evaluacionesRechazadas": cantidad_canceladas
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
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def devolverReporteExpositores(request):
    try:
        idCongreso = request.GET['idCongreso']
        expositores = AutorXArticulo.objects.filter(idUsuario__id__in=Inscripcion.objects.values_list('idUsuario', flat=True),idArticulo__idCongreso=idCongreso, idArticulo__idEstado__in=[5,6]).all()
        data = []
        for expositor in expositores:
            usuario = Usuario.objects.filter(id=expositor.idUsuario.id).first()
            sede = Sede.objects.filter(id=usuario.sede.id).first()
            datos = {
                "nombre":usuario.nombre,
                "apellido":usuario.apellido,
                "dni": usuario.dni,
                "sede": sede.nombre
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
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@api_view(['GET'])
def devolverReporteArticulos(request):
    try:
        idCongreso = request.GET['idCongreso']
        articulos = Articulo.objects.filter(idCongreso=idCongreso).all()
        data = []
        for articulo in articulos:
            simposio = Simposio.objects.filter(id=articulo.idSimposio.idSimposio.id).first()
            estado = EstadoArticulo.objects.filter(id=articulo.idEstado.id).first()
            responsable = Usuario.objects.filter(email=articulo.responsable).first()
            cantidad_autores = AutorXArticulo.objects.filter(idArticulo=articulo.id).count()
            datos = {
                "nombreArticulo":articulo.nombre,
                "simposio":simposio.nombre,
                "estado": estado.nombre,
                "responsable": str(responsable.nombre) + " " + str(responsable.apellido),
                "cantidadAutores": cantidad_autores
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
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def devolverReporteAsistentes(request):
    try:
        idCongreso = request.GET['idCongreso']
        
        asistentes_cta = Inscripcion.objects.filter(idCongreso=idCongreso).all()
        asistentes_sin_cta = InscripcionSinCuenta.objects.filter(idCongreso=idCongreso).all()
        data = []
        for asistente in asistentes_cta:
            fechadepago = str(asistente.fechaPago).split(' ')[0]
            fechadeinscripcion = str(asistente.fechaInscripcion).split(' ')[0]
            tarifa =  Tarifa.objects.filter(id=asistente.idTarifa.id).first()
            usuario = Usuario.objects.filter(id=asistente.idUsuario.id).first()
            datos = {
                "fechaPago": fechadepago,
                "fechaInscripcion": fechadeinscripcion,
                "precioFinal": asistente.precioFinal,
                "tarifa": tarifa.nombre,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "dni": usuario.dni
            }
            if asistente.idCupon != None:
                cupon = CuponDescuento.objects.filter(id=asistente.idCupon.id).first()
                datos["Cupon"] = cupon.codigo
                datos["Descuento Cupon"] = cupon.porcentajeDesc
            else:
                datos["Cupon"] = None
                datos["Descuento Cupon"] = None
            if asistente.asistio ==  True:
                datos["Asistio"] = "Si"
            else:
                datos["Asistio"] = "No"
            data.append(datos)
        for asistente in asistentes_sin_cta:
            fechadepago = str(asistente.fechaPago).split(' ')[0]
            fechadeinscripcion = str(asistente.fechaInscripcion).split(' ')[0]
            tarifa =  Tarifa.objects.filter(id=asistente.idTarifa.id).first()
            datos = {
                "fechaPago":fechadepago,
                "fechaInscripcion": fechadeinscripcion,
                "precioFinal": asistente.precioFinal,
                "tarifa": tarifa.nombre,
                "nombre": asistente.nombre,
                "apellido": asistente.apellido,
                "dni": asistente.dni,
                "cupon": None,
                "descuentoCupon": None
            }
            if asistente.asistio ==  True:
                datos["Asistio"] = "Si"
            else:
                datos["Asistio"] = "No"
            data.append(datos)
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def devolverEvaluadoresCancelacionesGeneral(request):
    try:
        cantidad = request.GET['cantidad']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT "idUsuario_id", COUNT("idUsuario_id") as "Cantidad" FROM public.articulos_evaluacioncancelada
        GROUP BY "idUsuario_id" ORDER BY "Cantidad" desc limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            usuario = Usuario.objects.filter(id=i[0]).first()
            datos = {
                "name": usuario.nombre + " " + usuario.apellido,
                "value": i[1]
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
def devolverEvaluadoresCancelacionesCongreso(request):
    try:
        idCongreso = request.GET['idCongreso']
        cantidad = request.GET['cantidad']
        with connection.cursor() as cursor:
            cursor.execute('''
        SELECT "idUsuario_id", COUNT("idUsuario_id") as "Cantidad" FROM public.articulos_evaluacioncancelada
        WHERE "idCongreso_id" = ''' +idCongreso + '''
        GROUP BY "idUsuario_id" ORDER BY "Cantidad" desc limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            usuario = Usuario.objects.filter(id=i[0]).first()
            datos = {
                "Evaluador": usuario.nombre + " " + usuario.apellido,
                "Cantidad de Evaluaciones Canceladas": i[1]
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
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def devolverEstadosArticulos(request):
    try:
        idCongreso = request.GET['idCongreso']
        cantidad_aprobados = Articulo.objects.filter(idCongreso=idCongreso,idEstado=6).count()
        cantidad_reetrega = Articulo.objects.filter(idCongreso=idCongreso,idEstado=5).count()
        cantidad_rechazados = Articulo.objects.filter(idCongreso=idCongreso,idEstado=7).count()
        data = {
                "aprobados": cantidad_aprobados,
                "reentrega": cantidad_reetrega,
                "rechazados": cantidad_rechazados,
            }
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def devolverPromedioItemsEvaluacion(request):
    try:
        idCongreso = request.GET['idCongreso']
        cantidad_aprobados = Articulo.objects.filter(idCongreso=idCongreso,idEstado=5).count()
        cantidad_reetrega = Articulo.objects.filter(idCongreso=idCongreso,idEstado=6).count()
        cantidad_rechazados = Articulo.objects.filter(idCongreso=idCongreso,idEstado=7).count()
        data = {
                "aprobados": cantidad_aprobados,
                "reentrega": cantidad_reetrega,
                "rechazados": cantidad_rechazados,
            }
        return Response({
            'status': '200',
            'error': '',
            'data': data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': '400',
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def devolverTopEventos(request):
    try:
        cantidad = request.GET['cantidad']
        idCongreso = request.GET['idCongreso']
        data = []
        with connection.cursor() as cursor:
            cursor.execute('''
        select e.title,(sum(c.puntuacion) / count(c."idEvento_id")) as "Promedio" from public.eventos_calificacionevento c
        inner join public.eventos_evento e on (e.id = c."idEvento_id")
        where e."idCongreso_id" = ''' + idCongreso + '''
        group by c."idEvento_id",e.title
        order by "Promedio" desc
        limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            datos = {
                "name": i[0],
                "value": i[1]
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
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@api_view(['GET'])
def devolverReporteEventos(request):
    try:
        idCongreso = request.GET['idCongreso']
        data = []
        with connection.cursor() as cursor:
            cursor.execute('''
        select e.content,au.nombre,e.start,e.end,a.nombre,s.nombre,e.title,(sum(c.puntuacion) / count(c."idEvento_id")) as "Promedio" 
        from public.eventos_evento e
            left join public.eventos_calificacionevento c on (e.id = c."idEvento_id")
            left join public.articulos_articulo a on (a.id = e."idArticulo_id")
            left join public.congresos_simposio s on (s.id = e."idSimposio_id")
            left join public.congresos_aula au on (au.id = e."idAula_id")
            where e."idCongreso_id" = ''' + idCongreso + '''
            group by c."idEvento_id",s.nombre,e.title,a.nombre,e.start,e.end,au.nombre,e.content
            order by "Promedio" desc ''' )
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            datosinicio = str(i[2]).split(' ')[0]
            datosfin = str(i[3]).split(' ')[0]
            datos = {
                "evento": i[6],
                "descripcionEvento": i[0],
                "calificacionPromedio": i[7],
                "inicio":datosinicio,
                "fin": datosfin,
                "articulo": i[4],
                "aula": i[1],
                "simposio": i[5]
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
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def devolverSimposiosCalificaciones(request):
    try:
        idCongreso = request.GET['idCongreso']
        data = []
        with connection.cursor() as cursor:
            cursor.execute('''
        select s.nombre,(sum(c.puntuacion) / count(c."idEvento_id")) as "Promedio" 
        from public.eventos_calificacionevento c
        left join public.eventos_evento e on (e.id = c."idEvento_id")
        left join public.congresos_simposio s on (s.id = e."idSimposio_id")
        where e."idCongreso_id" = ''' + idCongreso + '''
        group by s.nombre
        order by "Promedio" desc ''' )
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            if i[0] != None:
                datos = {
                    "name": i[0],
                    "value": i[1]
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
            'error': "Error.",
            'data': [e.args]
        }, status=status.HTTP_400_BAD_REQUEST)