
from django.urls import path
from .views import *


urlpatterns = [
    path('', apiOverView, name="api-overview"),
    path('lista-usuarios/', devolverUsuarios, name="lista-usuarios"),
    path('devolverUsuarioLogueado/', getUsuarioLogueado, name="devolverUsuarioLogueado"),
    path('registrar/', registrar,name="registrar"),
    path('login/', login, name="login"),
    path('verificarUsuario/', verificarUsuario, name="verificarUsuario"),
    path('logout/', logout, name="logout"),
    path('editar/', editar, name="editar"),
    path('eliminar/', eliminar, name="editar"),
    path('email-verify/', verify_email, name="email-verify"),
    path('reenviar-confirmacion/', reenviarmailactivacion, name="reenviar-confirmacion"),
    path('activar/', activar, name="activar"),
    path('asignar-chairPrincipal/', asignarRolChairPpal, name="asignar-chairPrincipal"),
    path('asignar-chairSecundario/', asignarRolChairSecundario, name="asignar-chairSecundario"),
    path('lista-tiposDni/', devolverTiposDNI, name="lista-tiposDni"),
    path('enviarMailRestablecerContrasenia/', enviarMailRestablecerContraseña, name="enviarMailRestablecerContrasenia"),
    path('restablecer-contrasenia/', restablecer_contraseña, name="restablecer-contrasenia"),
    path('cambiar-contrasenia/', cambiarContraseña, name="cambiar-contrasenia")
]

