from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from backendTesis.celery import app
from articulos.models import *
from .models import SimposiosxCongreso
from usuarios.models import Usuario
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives


#Permite eliminar el id de una tarea para que no se siga ejecutando.
@shared_task
def revoke_task_id(task_id):
    app.control.revoke(task_id, terminate=True)


# Envia una notificacion a todos los autores
# indicando el resultado de la evaluacion de su articulo.
@shared_task
def send_mail_task(idCongreso):
    articulos = Articulo.objects.filter(idCongreso=idCongreso)
    destinatariosAprobados = []
    destinatariosRechazados = []
    destinatariosReentrega = []

    for art in articulos:
        if art.responsable != "":
            if (art.idEstado_id == 5):   # Reentregados
                destinatariosReentrega.append(art.responsable)
            elif (art.idEstado_id == 6): # Aprobados
                destinatariosAprobados.append(art.responsable)
            elif (art.idEstado_id == 7): # Rechazados
                destinatariosRechazados.append(art.responsable)

    if (len(destinatariosReentrega) > 0):
        template = get_template('evaluacion_reentrega.html')
        content = template.render({}) 
        correo = EmailMultiAlternatives(
            'Resultado de Evaluación - CoNaIISI','',settings.EMAIL_HOST_USER,destinatariosReentrega)
        correo.attach_alternative(content,'text/html')
        correo.send()
        
    if (len(destinatariosAprobados) > 0):
        template = get_template('evaluacion_aprobada.html')
        content = template.render({}) 
        correo = EmailMultiAlternatives(
            'Resultado de Evaluación - CoNaIISI','',settings.EMAIL_HOST_USER,destinatariosAprobados)
        correo.attach_alternative(content,'text/html')
        correo.send()
    if (len(destinatariosRechazados) > 0):
        template = get_template('evaluacion_rechazada.html')
        content = template.render({})
        correo = EmailMultiAlternatives(
            'Resultado de Evaluación - CoNaIISI','',settings.EMAIL_HOST_USER,destinatariosRechazados)
        correo.attach_alternative(content,'text/html')
        correo.send()

    return None
    

# Envia una notificacion a todos los chairs secundarios 
# que posean simposios con articulos sin evaluar.
@shared_task
def send_mail_task_cs(idCongreso):

    articulos = Articulo.objects.filter(idCongreso=idCongreso).exclude(idEstado=6).exclude(idEstado=7).exclude(idEstado=8).exclude(idEstado=9)
    articulosSimposio = {}
    for art in articulos:
        if art.idSimposio in articulosSimposio:
            articulosSimposio[art.idSimposio.idSimposio_id].append(art.nombre)
        else:
            articulosSimposio[art.idSimposio.idSimposio_id] = []
            articulosSimposio[art.idSimposio.idSimposio_id].append(art.nombre)

    for simp in articulosSimposio:
        chairs_x_simposio = SimposiosxCongreso.objects.filter(idSimposio_id=simp).filter(idCongreso_id=idCongreso).values_list('idChair_id', flat=True)
        simposio = Simposio.objects.filter(id=simp).values_list('nombre', flat=True)
        nombreSimposio = simposio[0]  
        usuariosChair = Usuario.objects.filter(id__in=chairs_x_simposio)
        articulos = articulosSimposio[simp]
        
        for us in usuariosChair:
            template = get_template('evaluaciones_pendientes.html')
            content = template.render({'simposio':nombreSimposio, 'articulos': articulos}) 
            correo = EmailMultiAlternatives(
                'Aviso de articulos sin evaluar - CoNaIISI','',settings.EMAIL_HOST_USER,[us.email])
            correo.attach_alternative(content,'text/html')
            correo.send()
            

       
        
        
