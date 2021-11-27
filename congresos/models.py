from django.db import models
from usuarios.models import Usuario
from rest_framework.settings import api_settings
# Create your models here.

class Pais(models.Model):
    nombre = models.CharField(max_length=60)

class Provincia(models.Model):
    nombre = models.CharField(max_length=60)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, null=True)

class Localidad(models.Model):
    nombre = models.CharField(max_length=60)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

class Sede(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    calle = models.CharField(max_length=240)
    numero = models.IntegerField(null=True)
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE)

class Congreso(models.Model):
    nombre = models.CharField(max_length=255, null=True)
    sede = models.IntegerField(null=False) # models.ForeignKey(Sede, on_delete=models.CASCADE)  # apunta a tabla sedes
    año = models.IntegerField(null=False)
    # tematicas = models.ListField(null=True) # lista de integers que apunta a la tabla temáticas
    chairPrincipal = models.CharField(max_length=255,null=True) #Apunta la mail del chair ppal
    coordLocal = models.CharField(max_length=255,null=True) #Apunta al mail del coord Local
    fechaInCongreso = models.DateTimeField(null=True)
    fechaFinCongreso = models.DateTimeField(null=True)
    fechaLimPapers = models.DateTimeField(null=True)
    fechaProrrogaPapers = models.DateTimeField(null=True)
    fechaFinEvaluacion = models.DateTimeField(null=True)
    fechaFinReEv = models.DateTimeField(null=True)
    fechaFinInsTemprana = models.DateTimeField(null=True)
    fechaFinInsTardia = models.DateTimeField(null=True)
    fechaCierreCongreso = models.DateTimeField(null=True)
    fechaInicioExposiciones = models.DateTimeField(null=True)
    fechaFinExposiciones = models.DateTimeField(null=True)
    # aulas = models.ListField(null=True)  # lista de integers que apunta a la tabla aulas
    modalidad = models.CharField(null=True, max_length=240)  # Si es presencial o virtual
    is_active = models.BooleanField(default=True)
    task_id = models.CharField(null=True,max_length=255)
    task_id_aviso_chair = models.CharField(null=True,max_length=255)

    REQUIRED_FIELDS = [sede, año]

    def __str__(self):
        return str(self.sede) + "-" + str(self.año)

class Simposio(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=128)
    descripcion = models.CharField(max_length=512)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class SimposiosxCongreso(models.Model):

    idSimposio = models.ForeignKey(Simposio, on_delete=models.CASCADE)
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    idChair = models.ForeignKey(Usuario, on_delete=models.CASCADE)




class Aula(models.Model):
    nombre = models.CharField(max_length=60)
    descripcion = models.CharField(max_length=240, null=True)
    capacidad = models.IntegerField()
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(null=True,default=True)
    ubicacion = models.CharField(max_length=240,null=True)

class AulaXCongreso(models.Model):
    idCongreso =  models.ForeignKey(Congreso, on_delete=models.CASCADE)
    idAula =  models.ForeignKey(Aula, on_delete=models.CASCADE)
