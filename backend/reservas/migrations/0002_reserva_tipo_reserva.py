# Generated manually for adding tipo_reserva field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='tipo_reserva',
            field=models.CharField(
                choices=[
                    ('CLIENTE', 'Reserva de Cliente'),
                    ('ADMINISTRATIVA', 'Reserva Administrativa'),
                    ('BLOQUEADA', 'Horario Bloqueado'),
                    ('MANTENIMIENTO', 'Mantenimiento')
                ],
                default='CLIENTE',
                help_text='Tipo de reserva: cliente normal, administrativa (dueño), bloqueada o mantenimiento',
                max_length=20
            ),
        ),
    ]
