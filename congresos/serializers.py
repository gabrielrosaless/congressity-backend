from rest_framework import serializers
from rest_framework.views import exception_handler
from .models import Congreso, Localidad, Pais, Provincia, Simposio, SimposiosxCongreso, AulaXCongreso, Aula, Sede
from datetime import datetime


class CongresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Congreso
        fields = ['nombre','sede','año','chairPrincipal','coordLocal']

class CongresoEditarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Congreso
        fields = ['nombre','sede','año','chairPrincipal','coordLocal']

    def update(self, instance, validated_data):
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.sede = validated_data.get('sede', instance.sede)
        instance.año = validated_data.get('año', instance.año)
        instance.chairPrincipal = validated_data.get('chairPrincipal', instance.chairPrincipal)
        instance.coordLocal = validated_data.get('coordLocal', instance.coordLocal)
        instance.save()
        return instance

class CongresoCompletoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Congreso
        fields = ['nombre','sede','año', 'chairPrincipal','coordLocal','fechaInCongreso','fechaFinCongreso','fechaLimPapers','fechaProrrogaPapers','fechaFinEvaluacion','fechaFinReEv','fechaFinInsTemprana','fechaFinInsTardia', 'fechaCierreCongreso', 'modalidad','is_active']
    

    def update(self, instance, validated_data):
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.sede = validated_data.get('sede', instance.sede)
        instance.año = validated_data.get('año', instance.año)
        instance.chairPrincipal = validated_data.get('chairPrincipal', instance.chairPrincipal)
        instance.coordLocal = validated_data.get('coordLocal', instance.coordLocal)
        instance.fechaInCongreso = validated_data.get('fechaInCongreso', instance.fechaInCongreso)
        instance.fechaFinCongreso = validated_data.get('fechaFinCongreso', instance.fechaFinCongreso)
        instance.fechaLimPapers = validated_data.get('fechaLimPapers', instance.fechaLimPapers)
        instance.fechaProrrogaPapers = validated_data.get('fechaProrrogaPapers', instance.fechaProrrogaPapers)
        instance.fechaFinEvaluacion = validated_data.get('fechaFinEvaluacion', instance.fechaFinEvaluacion)
        instance.fechaFinReEv = validated_data.get('fechaFinReEv', instance.fechaFinReEv)
        instance.fechaFinInsTemprana = validated_data.get('fechaFinInsTemprana', instance.fechaFinInsTemprana)
        instance.fechaFinInsTardia = validated_data.get('fechaFinInsTardia', instance.fechaFinInsTardia)
        
        instance.modalidad = validated_data.get('modalidad', instance.modalidad)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()
        return instance

class CongresoFechasInscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Congreso
        fields = ['id','nombre','sede','año', 'fechaFinInsTemprana','fechaFinInsTardia']

class CongresoCompletoIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Congreso
        fields = ['id','nombre','sede','año', 'chairPrincipal','coordLocal','fechaInCongreso','fechaFinCongreso','fechaLimPapers','fechaProrrogaPapers','fechaFinEvaluacion','fechaFinReEv','fechaFinInsTemprana','fechaFinInsTardia', 'fechaCierreCongreso','modalidad','is_active']
    

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.sede = validated_data.get('sede', instance.sede)
        instance.año = validated_data.get('año', instance.año)
        instance.chairPrincipal = validated_data.get('chairPrincipal', instance.chairPrincipal)
        instance.coordLocal = validated_data.get('coordLocal', instance.coordLocal)
        instance.fechaInCongreso = validated_data.get('fechaInCongreso', instance.fechaInCongreso)
        instance.fechaFinCongreso = validated_data.get('fechaFinCongreso', instance.fechaFinCongreso)
        instance.fechaLimPapers = validated_data.get('fechaLimPapers', instance.fechaLimPapers)
        instance.fechaProrrogaPapers = validated_data.get('fechaProrrogaPapers', instance.fechaProrrogaPapers)
        instance.fechaFinEvaluacion = validated_data.get('fechaFinEvaluacion', instance.fechaFinEvaluacion)
        instance.fechaFinReEv = validated_data.get('fechaFinReEv', instance.fechaFinReEv)
        instance.fechaFinInsTemprana = validated_data.get('fechaFinInsTemprana', instance.fechaFinInsTemprana)
        instance.fechaFinInsTardia = validated_data.get('fechaFinInsTardia', instance.fechaFinInsTardia)
        instance.modalidad = validated_data.get('modalidad', instance.modalidad)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()
        return instance

class SimposioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simposio
        fields = ['id','nombre', 'descripcion']

        def update(self, instance, validated_data):
            instance.nombre = validated_data.get('nombre', instance.nombre)
            instance.descripcion = validated_data.get('sede', instance.descripcion)
            instance.save()
            return instance

class SimposioNombre(serializers.ModelSerializer):
    class Meta:
        model = Simposio
        fields = ['nombre']

class SimposioXCongreso(serializers.ModelSerializer):
    class Meta:
        model = SimposiosxCongreso
        fields = ['idSimposio', 'idCongreso', 'idChair']

class CongresoFechasSerializer(serializers.ModelSerializer):
    
    fechaInCongreso = serializers.DateTimeField(required=False,allow_null=True)
    fechaFinCongreso = serializers.DateTimeField(required=False,allow_null=True)
    fechaLimPapers = serializers.DateTimeField(required=False,allow_null=True)
    fechaProrrogaPapers = serializers.DateTimeField(required=False,allow_null=True)
    fechaFinEvaluacion = serializers.DateTimeField(required=False,allow_null=True)
    fechaFinInsTemprana = serializers.DateTimeField(required=False,allow_null=True)
    fechaFinInsTardia = serializers.DateTimeField(required=False,allow_null=True)
    fechaCierreCongreso = serializers.DateTimeField(required=False,allow_null=True)

    class Meta:
        model = Congreso
        #fields = ['id','fechaInCongreso']
        fields = ['id','fechaInCongreso','fechaFinCongreso','fechaLimPapers','fechaProrrogaPapers','fechaFinEvaluacion',
        'fechaFinReEv','fechaFinInsTemprana','fechaFinInsTardia','fechaCierreCongreso']
    
    def update(self, instance, validated_data):
        instance.fechaInCongreso = validated_data.get('fechaInCongreso', instance.fechaInCongreso)
        instance.fechaFinCongreso = validated_data.get('fechaFinCongreso', instance.fechaFinCongreso)
        instance.fechaLimPapers = validated_data.get('fechaLimPapers', instance.fechaLimPapers)
        instance.fechaProrrogaPapers = validated_data.get('fechaProrrogaPapers', instance.fechaProrrogaPapers)
        instance.fechaFinEvaluacion = validated_data.get('fechaFinEvaluacion', instance.fechaFinEvaluacion)
        instance.fechaFinReEv = validated_data.get('fechaFinReEv', instance.fechaFinReEv)     
        instance.fechaFinInsTemprana = validated_data.get('fechaFinInsTemprana', instance.fechaFinReEv)     
        instance.fechaFinInsTardia = validated_data.get('fechaFinInsTardia', instance.fechaFinReEv)        
        instance.fechaCierreCongreso = validated_data.get('fechaCierreCongreso', instance.fechaCierreCongreso)        
        instance.save()
        return instance

    # 
    # Metodo para validar las fechas
    def validate(self, data):
        _fechaInCongreso = data['fechaInCongreso']
        _fechaFinCongreso = data['fechaFinCongreso']
        _fechaLimPapers = data['fechaLimPapers']
        _fechaProrrogaPapers = data['fechaProrrogaPapers']
        _fechaFinEvaluacion = data['fechaFinEvaluacion']
        _fechaFinInsTemprana = data['fechaFinInsTemprana'] 
        _fechaFinInsTardia = data['fechaFinInsTardia']
        _fechaCierreCongreso = data['fechaCierreCongreso']
        _fechaFinReEv = data['fechaFinReEv']
        
        if ( _fechaInCongreso == None or _fechaFinCongreso == None 
            or _fechaLimPapers == None or _fechaProrrogaPapers == None
            or _fechaFinEvaluacion == None or _fechaFinInsTemprana == None 
            or _fechaFinInsTardia == None or _fechaCierreCongreso == None
            or _fechaFinReEv == None):
            raise serializers.ValidationError("Debe completar todas las fechas del congreso.")
        
        if _fechaInCongreso > _fechaFinCongreso:
            raise serializers.ValidationError("La fecha de inicio de congreso no puede ser mayor a la fecha de fin del congreso.")
        
        if _fechaFinEvaluacion >= _fechaFinCongreso:
            raise serializers.ValidationError("La fecha de fin de congreso debe ser mayor a la fecha de fin de las evaluaciones.")

        if _fechaFinEvaluacion <= _fechaInCongreso:
            raise serializers.ValidationError("La fecha fin de las evaluaciones debe ser mayor a la fecha de inicio del congreso .")
         
        if _fechaFinEvaluacion <= _fechaLimPapers:
            raise serializers.ValidationError("La fecha fin de las evaluaciones debe ser mayor a la fecha limite de entrega de los articulos.")
        
        if _fechaFinEvaluacion <= _fechaProrrogaPapers:
            raise serializers.ValidationError("La fecha fin de las evaluaciones debe ser mayor a la fecha de prórroga.")
        
        if _fechaLimPapers >= _fechaProrrogaPapers:
            raise serializers.ValidationError("La fecha de prorroga debe ser mayor a la fecha limite de entrega de papers.")
    
        if _fechaFinCongreso <= _fechaFinInsTemprana:
            raise serializers.ValidationError("La fecha fin del congreso debe ser mayor a la fecha de inscripción temprana.")

        if _fechaFinCongreso <= _fechaFinInsTardia:
            raise serializers.ValidationError("La fecha fin del congreso debe ser mayor a la fecha de inscripción tardía.")

        if _fechaFinInsTardia <= _fechaFinInsTemprana:
            raise serializers.ValidationError("La fecha fecha fin de inscripción tardía debe ser mayor a la fecha fin  de inscripcion temprana.")

        if _fechaFinCongreso <= _fechaProrrogaPapers:
            raise serializers.ValidationError("La fecha fin del congreso debe ser mayor a la fecha de prórroga.")

        if _fechaFinCongreso <= _fechaLimPapers:
            raise serializers.ValidationError("La fecha fin del congreso debe ser mayor a la fecha límite de entrega de artículos.")

        if (_fechaCierreCongreso <= _fechaInCongreso or 
            _fechaCierreCongreso <= _fechaFinCongreso or
            _fechaCierreCongreso <= _fechaLimPapers or 
            _fechaCierreCongreso <= _fechaProrrogaPapers or 
            _fechaCierreCongreso <= _fechaFinEvaluacion or 
            _fechaCierreCongreso <= _fechaFinInsTemprana or
            _fechaCierreCongreso <= _fechaFinInsTardia or 
            _fechaCierreCongreso <= _fechaFinReEv):
            raise serializers.ValidationError("La fecha de cierre debe ser mayor a todas las demas fechas.")

        return data

class AulaSerializer(serializers.ModelSerializer):
    sede = serializers.PrimaryKeyRelatedField(queryset=Sede.objects.all())
    class Meta:
        model = Aula
        fields = ['id','nombre','descripcion','capacidad','sede','ubicacion']

    def update(self, instance, validated_data):
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.capacidad = validated_data.get('capacidad', instance.capacidad)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.sede = validated_data.get('sede', instance.sede)
        instance.ubicacion = validated_data.get('ubicacion', instance.ubicacion)
        instance.save()
        return instance

class AulaXCongresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AulaXCongreso
        fields = ['idCongreso','idAula']

class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ['nombre', 'calle', 'numero', 'localidad']

class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = ['id', 'nombre']

class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = ['id', 'nombre']
        

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ['id', 'nombre']
