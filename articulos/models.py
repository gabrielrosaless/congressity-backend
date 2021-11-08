from django.db import models


# Create your models here.

from usuarios.models import Usuario
from congresos.models import SimposiosxCongreso,  Congreso, Simposio
from rest_framework.settings import api_settings

# Create your models here.

class EstadoArticulo(models.Model):
    nombre = models.CharField(max_length=128)
    descripcion = models.CharField(max_length=512)


class Articulo(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=250,null=True)
    idSimposio = models.ForeignKey(SimposiosxCongreso, on_delete=models.CASCADE,null=True)
    responsable = models.CharField(max_length=250,null=True)
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE,null=True)
    url = models.CharField(max_length=250,null=True)
    url_camera_ready = models.CharField(max_length=250,null=True)
    idEstado = models.ForeignKey(EstadoArticulo, on_delete=models.CASCADE, default=1)
    observacion = models.CharField(max_length=512, null=True)
    esta_correcto = models.BooleanField(default=False,null=True)
    enviado_corregir = models.BooleanField(default=False,null=True)

    def __str__(self):
        return self.nombre

class AutorXArticulo(models.Model):
    idArticulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

class AutorXArticuloSinUsuario(models.Model):
    idArticulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    mailUsuario = models.CharField(max_length=128)


class Evaluador(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    # califAcumulada = models.IntegerField(default=1)
    # califContador = models.IntegerField(default=1)

    # @property 
    # def calificacion(self):
    #     return self.califAcumulada / self.califContador

class EvaluadorXCongreso(models.Model):
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

class ChairXSimposioXCongreso(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idSimposio = models.ForeignKey(Simposio, on_delete=models.CASCADE)
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)

class SimposiosXEvaluador(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idSimposio = models.ForeignKey(Simposio, on_delete=models.CASCADE)

class ItemEvaluacion(models.Model):
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=512)
    descripcion = models.CharField(max_length=512, null=True)
    is_active = models.BooleanField(default=True)
    
class EstadoEvaluacion(models.Model):
    nombre = models.CharField(max_length=128)
    descripcion = models.CharField(max_length=512)

class RecomendacionEvaluacion(models.Model):
    nombre = models.CharField(max_length=128)
    descripcion = models.CharField(max_length=512)

class ArticulosXEvaluador(models.Model):
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idArticulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoEvaluacion, on_delete=models.CASCADE, default=1)
    recomendacion = models.ForeignKey(RecomendacionEvaluacion, on_delete=models.CASCADE, null=True)
    observaciones = models.CharField(max_length=512, null=True)
    observacionInterna = models.CharField(max_length=512, null=True)
    is_active = models.BooleanField()
    
class EvaluacionXEvaluador(models.Model):
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idArticulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    recomendacion = models.ForeignKey(EstadoEvaluacion, on_delete=models.CASCADE)
    observaciones = models.CharField(max_length=512, null=True)

class ItemEvaluacionXEvaluador(models.Model):
    idEvaluacion = models.ForeignKey(ArticulosXEvaluador, on_delete=models.CASCADE)
    idItem = models.ForeignKey(ItemEvaluacion, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(default=0, null=True)

class EvaluadorXCongresoXChair(models.Model):
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    idEvaluador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='id_evaluador')
    idChair = models.ForeignKey(Usuario, on_delete=models.CASCADE,related_name='id_chair')