from django.db import models
from congresos.models import *
from usuarios.models import *
# Create your models here.

class Tarifa(models.Model):
    codigoTarifa = models.IntegerField(null=True)
    nombre = models.CharField(max_length=60)
    precio = models.FloatField()
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    fechaDesde = models.DateTimeField(null=True)
    fechaHasta = models.DateTimeField(null=True)
    
class CuponDescuento(models.Model):
    codigo = models.CharField(max_length=16, unique=True)
    porcentajeDesc = models.FloatField()
    usosRestantes = models.IntegerField()
    idTarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE, null=True)

class Inscripcion(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idTarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE)
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    fechaPago = models.DateTimeField(null=True)
    fechaInscripcion = models.DateTimeField()
    idCupon = models.ForeignKey(CuponDescuento, on_delete=models.CASCADE, null=True)
    precioFinal = models.FloatField()
