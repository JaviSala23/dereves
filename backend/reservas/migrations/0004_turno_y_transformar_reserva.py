# Generated manually to transform Reserva model structure
# ADVERTENCIA: Esta migración elimina y recrea el modelo Reserva
# Se perderán las reservas existentes

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0003_remove_reservafija_aprobada_por_and_more'),
        ('complejos', '0006_complejo_pais_complejo_provincia'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cuentas', '0002_remove_perfildueno_nombre_comercial_and_more'),
    ]

    operations = [
        # Paso 1: Crear modelo Turno (solo si no existe)
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.CharField(
                    choices=[
                        ('DISPONIBLE', 'Disponible'),
                        ('RESERVADO', 'Reservado'),
                        ('FIJO', 'Turno Fijo'),
                        ('BLOQUEADO_TORNEO', 'Bloqueado por Torneo'),
                        ('PARTIDO_ABIERTO', 'Partido Abierto')
                    ],
                    default='DISPONIBLE',
                    max_length=20
                )),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('cancha', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='turnos',
                    to='complejos.cancha'
                )),
            ],
            options={
                'verbose_name': 'Turno',
                'verbose_name_plural': 'Turnos',
                'ordering': ['fecha', 'hora_inicio'],
                'unique_together': {('cancha', 'fecha', 'hora_inicio')},
                'indexes': [
                    models.Index(fields=['cancha', 'fecha']),
                    models.Index(fields=['fecha', 'estado']),
                ],
            },
        ),
        
        # Paso 2: Crear modelo Torneo
        migrations.CreateModel(
            name='Torneo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('estado', models.CharField(
                    choices=[
                        ('PROGRAMADO', 'Programado'),
                        ('EN_CURSO', 'En Curso'),
                        ('FINALIZADO', 'Finalizado'),
                        ('CANCELADO', 'Cancelado')
                    ],
                    default='PROGRAMADO',
                    max_length=20
                )),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('complejo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='torneos',
                    to='complejos.complejo'
                )),
            ],
            options={
                'verbose_name': 'Torneo',
                'verbose_name_plural': 'Torneos',
                'ordering': ['-creado_en'],
            },
        ),
        
        # Paso 3: Eliminar modelo Reserva antiguo si existe
        migrations.RunSQL(
            "DROP TABLE IF EXISTS `reservas_reserva`",
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Paso 4: Crear modelo PartidoAbierto
        migrations.CreateModel(
            name='PartidoAbierto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_invitacion', models.CharField(max_length=50, unique=True)),
                ('cupo_jugadores', models.IntegerField(default=4)),
                ('nivel', models.CharField(
                    choices=[
                        ('PRINCIPIANTE', 'Principiante'),
                        ('INTERMEDIO', 'Intermedio'),
                        ('AVANZADO', 'Avanzado'),
                        ('PROFESIONAL', 'Profesional')
                    ],
                    max_length=20
                )),
                ('categoria', models.CharField(blank=True, max_length=50)),
                ('descripcion', models.TextField(blank=True)),
                ('precio_por_jugador', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.CharField(
                    choices=[
                        ('ABIERTO', 'Abierto'),
                        ('COMPLETO', 'Completo'),
                        ('CANCELADO', 'Cancelado'),
                        ('FINALIZADO', 'Finalizado')
                    ],
                    default='ABIERTO',
                    max_length=20
                )),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('organizador', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='partidos_organizados',
                    to='cuentas.perfiljugador'
                )),
                ('turno', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='partido_abierto',
                    to='reservas.turno'
                )),
            ],
            options={
                'verbose_name': 'Partido Abierto',
                'verbose_name_plural': 'Partidos Abiertos',
                'ordering': ['-creado_en'],
            },
        ),
        
        # Paso 5: Recrear modelo Reserva con nueva estructura
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reservado_por_dueno', models.BooleanField(default=False)),
                ('nombre_cliente_sin_cuenta', models.CharField(blank=True, max_length=200)),
                ('telefono_cliente', models.CharField(blank=True, max_length=20)),
                ('email_cliente', models.EmailField(blank=True, max_length=254)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.CharField(
                    choices=[
                        ('PENDIENTE', 'Pendiente'),
                        ('CONFIRMADA', 'Confirmada'),
                        ('CANCELADA', 'Cancelada'),
                        ('NO_ASISTIO', 'No Asistió'),
                        ('COMPLETADA', 'Completada')
                    ],
                    default='PENDIENTE',
                    max_length=20
                )),
                ('pagado', models.BooleanField(default=False)),
                ('observaciones', models.TextField(blank=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('turno', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reserva',
                    to='reservas.turno'
                )),
                ('jugador', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reservas',
                    to='cuentas.perfiljugador'
                )),
                ('metodo_pago', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='reservas.metodopago'
                )),
                ('creado_por', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reservas_creadas',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'ordering': ['-creado_en'],
                'indexes': [
                    models.Index(fields=['jugador', 'estado']),
                    models.Index(fields=['estado', 'creado_en']),
                ],
            },
        ),
        
        # Paso 6: Crear modelo JugadorPartido
        migrations.CreateModel(
            name='JugadorPartido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_invitado', models.CharField(blank=True, max_length=200)),
                ('telefono_invitado', models.CharField(blank=True, max_length=20)),
                ('email_invitado', models.EmailField(blank=True, max_length=254)),
                ('es_invitado', models.BooleanField(default=False)),
                ('pagado', models.BooleanField(default=False)),
                ('fecha_union', models.DateTimeField(auto_now_add=True)),
                ('jugador', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='participaciones_partidos',
                    to='cuentas.perfiljugador'
                )),
                ('partido', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='jugadores',
                    to='reservas.partidoabierto'
                )),
            ],
            options={
                'verbose_name': 'Jugador en Partido',
                'verbose_name_plural': 'Jugadores en Partidos',
                'ordering': ['fecha_union'],
            },
        ),
        
        # Paso 7: Crear modelo BloqueoTorneo
        migrations.CreateModel(
            name='BloqueoTorneo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('torneo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bloqueos',
                    to='reservas.torneo'
                )),
                ('turno', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bloqueos_torneo',
                    to='reservas.turno'
                )),
            ],
            options={
                'verbose_name': 'Bloqueo de Torneo',
                'verbose_name_plural': 'Bloqueos de Torneos',
                'unique_together': {('torneo', 'turno')},
            },
        ),
    ]
