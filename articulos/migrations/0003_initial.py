# Generated by Django 3.2.4 on 2021-11-09 02:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('congresos', '0001_initial'),
        ('articulos', '0002_simposiosxevaluador_idsimposio'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='simposiosxevaluador',
            name='idUsuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='itemevaluacionxevaluador',
            name='idEvaluacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articulos.articulosxevaluador'),
        ),
        migrations.AddField(
            model_name='itemevaluacionxevaluador',
            name='idItem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articulos.itemevaluacion'),
        ),
        migrations.AddField(
            model_name='itemevaluacion',
            name='idCongreso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='congresos.congreso'),
        ),
        migrations.AddField(
            model_name='evaluadorxcongresoxchair',
            name='idChair',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='id_chair', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='evaluadorxcongresoxchair',
            name='idCongreso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='congresos.congreso'),
        ),
        migrations.AddField(
            model_name='evaluadorxcongresoxchair',
            name='idEvaluador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='id_evaluador', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='evaluadorxcongreso',
            name='idCongreso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='congresos.congreso'),
        ),
        migrations.AddField(
            model_name='evaluadorxcongreso',
            name='idUsuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='evaluador',
            name='idUsuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='evaluacionxevaluador',
            name='idArticulo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articulos.articulo'),
        ),
        migrations.AddField(
            model_name='evaluacionxevaluador',
            name='idCongreso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='congresos.congreso'),
        ),
        migrations.AddField(
            model_name='evaluacionxevaluador',
            name='idUsuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='evaluacionxevaluador',
            name='recomendacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articulos.estadoevaluacion'),
        ),
        migrations.AddField(
            model_name='chairxsimposioxcongreso',
            name='idCongreso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='congresos.congreso'),
        ),
        migrations.AddField(
            model_name='chairxsimposioxcongreso',
            name='idSimposio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='congresos.simposio'),
        ),
        migrations.AddField(
            model_name='chairxsimposioxcongreso',
            name='idUsuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='autorxarticulosinusuario',
            name='idArticulo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articulos.articulo'),
        ),
        migrations.AddField(
            model_name='autorxarticulo',
            name='idArticulo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articulos.articulo'),
        ),
        migrations.AddField(
            model_name='autorxarticulo',
            name='idUsuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='articulosxevaluador',
            name='estado',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='articulos.estadoevaluacion'),
        ),
        migrations.AddField(
            model_name='articulosxevaluador',
            name='idArticulo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articulos.articulo'),
        ),
        migrations.AddField(
            model_name='articulosxevaluador',
            name='idCongreso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='congresos.congreso'),
        ),
        migrations.AddField(
            model_name='articulosxevaluador',
            name='idUsuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='articulosxevaluador',
            name='recomendacion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='articulos.recomendacionevaluacion'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='idCongreso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='congresos.congreso'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='idEstado',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='articulos.estadoarticulo'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='idSimposio',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='congresos.simposiosxcongreso'),
        ),
    ]
