from rest_framework import authentication
from rest_framework import exceptions
from .models import Usuario,RolxUsuarioxCongreso
import jwt
from django.shortcuts import get_object_or_404
from django.conf import settings

class Authentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        token = request.headers['Authorization']

        if not token:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')

        user = get_object_or_404(Usuario, pk=payload['id'])
        return (user, None)

class AuthenticationChairPrincipal(authentication.BaseAuthentication):
    def authenticate(self, request):

        token = request.headers['Authorization']
        
        if not token:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')

        user = get_object_or_404(Usuario, pk=payload['id'])

        if user.is_superuser:
            return (user, None)

        if 1 not in payload['rol']: raise exceptions.AuthenticationFailed('Se necesitan permisos de Chair principal.')

        user = get_object_or_404(Usuario, pk=payload['id'])
        return (user, None)

class AuthenticationChairSecundario(authentication.BaseAuthentication):
    def authenticate(self, request):

        token = request.headers['Authorization']
        
        if not token:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')

        user = get_object_or_404(Usuario, pk=payload['id'])

        if user.is_superuser:
            return (user, None)

        if 2 not in payload['rol']: raise exceptions.AuthenticationFailed('Se necesitan permisos de chair secundario.')

        user = get_object_or_404(Usuario, pk=payload['id'])
        return (user, None)


class AuthenticationEvaluador(authentication.BaseAuthentication):
    def authenticate(self, request):

        token = request.headers['Authorization']
        
        if not token:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')

        if 3 not in payload['rol']: raise exceptions.AuthenticationFailed('Se necesitan permisos de evaluador.')

        user = get_object_or_404(Usuario, pk=payload['id'])
        return (user, None)

class AuthenticationAutor(authentication.BaseAuthentication):
    def authenticate(self, request):

        token = request.headers['Authorization']
        
        if not token:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')

        if 4 not in payload['rol']: raise exceptions.AuthenticationFailed('Se necesitan permisos de autor.')
        user = get_object_or_404(Usuario, pk=payload['id'])
        return (user, None)


class AuthenticationAyudante(authentication.BaseAuthentication):
    def authenticate(self, request):

        token = request.headers['Authorization']
        
        if not token:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Usuario no autenticado!')

        if 5 not in payload['rol']: raise exceptions.AuthenticationFailed('Se necesitan permisos de ayudante.')
        user = get_object_or_404(Usuario, pk=payload['id'])
        return (user, None)

 