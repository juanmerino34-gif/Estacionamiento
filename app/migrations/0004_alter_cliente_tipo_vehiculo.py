

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_cliente_nombre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='tipo_vehiculo',
            field=models.CharField(blank=True, choices=[('Automovil', 'Automóvil'), ('Camioneta', 'Camioneta'), ('Moto', 'Motocicleta')], max_length=50, null=True),
        ),
    ]
