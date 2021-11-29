from django.urls import path
# from .views import RegisterView, LoginView, UsuarioView, LogoutView, hello_world


from .views import *


urlpatterns = [
    path('apicongresos', apiOverView, name="api-overview"),
    path('crear-congreso/', crearCongreso, name="crear"),
    path('editar-congreso/', editar, name="editar"),
    path('eliminar-congreso/', eliminar, name="eliminar"),
    path('definir-agenda/',definirAgenda, name="definir-agenda"),
    path('devolver-agenda/',devolverFechasCongreso, name="devolver-agenda"),
    path('crear-aula/', crearAula, name="crear-aula"),
    path('lista-aulas/', devolverAulas, name="lista-aulas"),
    path('lista-aulasxcongreso/', devolverAulasxCongreso, name="lista-aulasxcongreso"),
    path('editar-aula/', editarAula, name="editar-aula"),
    path('asignar-aulas/', asignarAulas, name="asignar-aulas"),
    path('eliminar-aula/', eliminarAula, name="eliminar-aula"),
    path('activar-congreso/', activar, name="activar"),
    path('lista-congresos/', listaCongresos, name="lista-congresos"),
    path('consultaCongreso/', consultaCongreso, name="consultaCongreso"),
    path('crear-simposio/', altaSimposio, name="alta-simposio"),
    path('lista-simposios/', getSimposios, name="get-simposios"),
    path('lista-simposiosxcongreso/',getSimposiosXCongreso , name="lista-simposiosxcongreso"),
    path('consultar-simposio/', getSimposio, name="get-simposio"),
    path('editar-simposio/', editarSimposio, name="editar-simposio"),
    path('eliminar-simposio/', eliminarSimposio, name="eliminar-simposio"),
    path('asignar-simposioxcongreso/', altaSimposioxCongreso, name="alta-simposioxcongreso"),
    path('lista-sedes/', devolverSedes, name="lista-sedes"),
    path('sede-x-chair/<int:id>', devolverSedesXChairLocal, name="sede-x-chair"),
    path('consultaCongresoXChair/', consultaCongresoXChair, name="consultaCongresoXChair"),
    path('listaCongresosActivos/', listaCongresosActivos, name="listaCongresosActivos"),
    path('eliminar-simposioxcongreso/', eliminarSimposioXCongreso, name="eliminar-simposioxcongreso"),
    path('lista-localidades/', devolverLocalidades, name="lista-localidades"),
    path('lista-provincia/', devolverProvincias, name="lista-provincia"),
    path('lista-paises/', devolverPaises, name="lista-paises"),
    path('devolverChairsSimposios/', devolverChairsSimposios, name="devolverChairsSimposios"),
    path('asignarChairASimposio/', asignarChairASimposio, name="asignarChairASimposio"),
    path('eliminarChairSecundario/', eliminarChairSecundario, name="eliminarChairSecundario"),
    path('lista-congresos-publico/', devolverFechasInscripcion, name="lista-congresos-publico"),
    path('notificarResultadosEvaluacion/', notificarResultadosEvaluacion, name='notificarResultadosEvaluacion'),
    path('lista-chairs/', devolverInfoPublicaChairs, name='lista-chairs'),
    path('crear-sede/', crearSede, name='crear-sede'),
    path('editar-sede/', editarSede, name='editar-sede'),
    path('eliminar-sede/', eliminarSede, name='eliminar-sede'),
    path('consultar-sede/', getSede, name='consultar-sede'),
    path('lista-localidadesProvincia/', devolverLocalidadesXProvincia, name="lista-localidadesProvincia")

]

