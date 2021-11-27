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

# Es la de mercado pago y inscripcion fisica para persona con cuenta.
class Inscripcion(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idTarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE)
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    fechaPago = models.DateTimeField(null=True)
    fechaInscripcion = models.DateTimeField()
    idCupon = models.ForeignKey(CuponDescuento, on_delete=models.CASCADE, null=True)
    precioFinal = models.FloatField()
    asistio = models.BooleanField(default=False)


# Inscripcion fisica para persona sin cuenta
class InscripcionSinCuenta(models.Model):
    email = models.EmailField()
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    dni = models.IntegerField()
    tipoDni = models.ForeignKey('usuarios.TipoDni',on_delete=models.CASCADE)
    fechaNacimiento = models.DateField()
    idTarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE)
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    fechaPago = models.DateTimeField()
    fechaInscripcion = models.DateTimeField()
    precioFinal = models.FloatField()
    asistio = models.BooleanField(default=False)

class Ayudante(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)