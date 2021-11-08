from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
from usuarios.authentication import *
from congresos.models import Congreso
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
        SELECT "idUsuario_id", COUNT("idUsuario_id") as "Cantidad" FROM public.articulos_evaluacionxevaluador
        GROUP BY "idUsuario_id" ORDER BY "Cantidad" desc limit ''' + cantidad)
            rows = cursor.fetchall()
            cursor.close()
        data = []
        for i in rows:
            usuario = Usuario.objects.filter(id=i[0]).first()
            datos = {
                "Nombre": usuario.nombre,
                "Apellido": usuario.apellido,
                "Id": usuario.id,
                "Cantidad de Evaluaciones": i[1]
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

