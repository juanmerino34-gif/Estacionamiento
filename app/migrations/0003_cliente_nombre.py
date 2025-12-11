

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='nombre',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
