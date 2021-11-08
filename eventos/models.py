from django.db import models
from congresos.models import *
from articulos.models import *

# Create your models here.
class Evento(models.Model):
    title = models.CharField(max_length=256)
    content = models.CharField(max_length=512)
    start = models.DateTimeField()
    end = models.DateTimeField()
    idCongreso = models.ForeignKey(Congreso, on_delete=models.CASCADE)
    idAula = models.ForeignKey(Aula, on_delete=models.CASCADE, null=True)
    idSimposio = models.ForeignKey(Simposio, on_delete=models.CASCADE, null=True)
    idArticulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, null=True)