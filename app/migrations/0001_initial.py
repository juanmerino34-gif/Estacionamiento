

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Espacio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identificador', models.CharField(max_length=10)),
                ('zona', models.CharField(choices=[('BALBUENA', 'Balbuena'), ('MOCTEZUMA', 'Moctezuma'), ('AEROPUERTO', 'Aeropuerto')], default='BALBUENA', max_length=20)),
                ('ocupado', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TipoEspacio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('tarifa_por_hora', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Registro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricula', models.CharField(max_length=20)),
                ('hora_entrada', models.DateTimeField(default=django.utils.timezone.now)),
                ('hora_salida', models.DateTimeField(blank=True, null=True)),
                ('monto_pagado', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('pagado', models.BooleanField(default=False)),
                ('espacio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.espacio')),
            ],
        ),
        migrations.AddField(
            model_name='espacio',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.tipoespacio'),
        ),
    ]
