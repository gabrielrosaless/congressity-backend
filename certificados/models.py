from django.db import models
from rest_framework.settings import api_settings

class Certificado(models.Model):
    template = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

class DetalleCertificado(models.Model):
    idCerificado = models.ForeignKey(Certificado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    tipoLetra = models.CharField(max_length=50)
    tamañoLetra = models.IntegerField()
    posX = models.IntegerField()
    posY = models.IntegerField()
