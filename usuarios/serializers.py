
from rest_framework import serializers

from .models import *


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id','email','password','nombre','dni','tipoDni','apellido','fechaNacimiento',
        'localidad','calle','numeroCalle','piso','dpto','telefono','is_active','sede']
        #fields = '__all__'
        extra_kwargs = {
            'password':{'write_only': True}
        }

    #funcion para hashear la contraseña
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        
        instance.save()
        return instance

class UsuarioCompletoSerializer(serializers.ModelSerializer):
    # fechaNacimiento = serializers.DateField(required=False,allow_null=True)
    class Meta:
        model = Usuario
        fields = ['id','nombre','email','dni','tipoDni','apellido','fechaNacimiento',
        'localidad','calle','numeroCalle','piso','dpto','telefono','is_active']
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.dni = validated_data.get('dni', instance.dni)
        instance.tipoDni = validated_data.get('tipoDni', instance.tipoDni)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.fechaNacimiento = validated_data.get('fechaNacimiento', instance.fechaNacimiento)
        instance.localidad = validated_data.get('localidad', instance.localidad)
        instance.calle = validated_data.get('calle', instance.calle)
        instance.numeroCalle = validated_data.get('numeroCalle', instance.numeroCalle)
        instance.piso = validated_data.get('piso', instance.piso)
        instance.dpto = validated_data.get('dpto', instance.dpto)
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        
        instance.save()
        return instance


class RolxUsuarioxCongresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolxUsuarioxCongreso
        fields = ['idCongreso','idUsuario', 'idRol']

class TipoDniSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDni
        fields = ['id', 'nombre']