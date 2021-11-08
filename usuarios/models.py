
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
# Create your models here.

class Usuario(AbstractUser):
    dni = models.IntegerField()
    tipoDni = models.ForeignKey('usuarios.TipoDni',on_delete=models.CASCADE)  
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    fechaNacimiento = models.DateField()
    localidad = models.ForeignKey('congresos.Localidad',on_delete=models.CASCADE)  
    sede = models.ForeignKey('congresos.Sede',on_delete=models.CASCADE)  
    calle = models.CharField(max_length=128)
    numeroCalle = models.IntegerField()
    piso = models.CharField(max_length=2, null=True)
    dpto = models.CharField(max_length=1, null=True)
    telefono = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    first_name = None
    last_name = None
    username = None
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager() 

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    descripcion = models.CharField(max_length=60)

class TipoDni(models.Model):
    nombre = models.CharField(max_length=100)


class Permiso(models.Model):
    numeroProceso = models.IntegerField()

class RolxUsuarioxCongreso(models.Model):
    idCongreso = models.ForeignKey('congresos.Congreso', on_delete=models.CASCADE) # FK a congreso
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # FK a usuario
    idRol = models.ForeignKey(Rol, on_delete=models.CASCADE)      # FK a rol

# class PermisoxRol(models.Model):
#     idRol = models.IntegerField() # FK a rol
#     idPermiso = models.IntegerField() # FK a permiso




