
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets

# Permitir liberar una ocurrencia específica de una reserva fija (sin cancelar la recurrencia)
class ReservaFijaLiberacion(models.Model):
    reserva_fija = models.ForeignKey('ReservaFija', on_delete=models.CASCADE, related_name='liberaciones')
    fecha = models.DateField()
    motivo = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['reserva_fija', 'fecha']
        verbose_name = 'Liberación de Reserva Fija'
        verbose_name_plural = 'Liberaciones de Reservas Fijas'

    def __str__(self):
        return f"Liberación {self.reserva_fija} en {self.fecha}"


class MetodoPago(models.Model):
    """
    Métodos de pago disponibles.
    """
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
    
    def __str__(self):
        return self.nombre


class Turno(models.Model):
    """
    Representa un slot de tiempo disponible en una cancha.
    Este modelo gestiona la disponibilidad y el estado de cada turno.
    """
    
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('RESERVADO', 'Reservado'),
        ('FIJO', 'Turno Fijo'),
        ('BLOQUEADO_TORNEO', 'Bloqueado por Torneo'),
        ('PARTIDO_ABIERTO', 'Partido Abierto'),
    ]
    
    cancha = models.ForeignKey(
        'complejos.Cancha',
        on_delete=models.CASCADE,
        related_name='turnos'
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='DISPONIBLE'
    )
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['fecha', 'hora_inicio']
        unique_together = ['cancha', 'fecha', 'hora_inicio']
        indexes = [
            models.Index(fields=['cancha', 'fecha', 'estado']),
            models.Index(fields=['fecha', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.cancha} - {self.fecha} {self.hora_inicio} ({self.get_estado_display()})"
    
    def esta_disponible(self):
        """Verifica si el turno está disponible para reservar."""
        return self.estado == 'DISPONIBLE'
    
    def puede_ser_reservado_por_jugador(self):
        """Verifica si un jugador común puede reservar este turno."""
        return self.estado in ['DISPONIBLE', 'PARTIDO_ABIERTO']


class Reserva(models.Model):
        def cancelar(self):
            """
            Cancela la reserva si está pendiente o confirmada y no está pagada.
            Cambia el estado a CANCELADA y guarda.
            Devuelve True si se modificó, False si ya estaba cancelada o pagada.
            """
            if self.estado in ['PENDIENTE', 'CONFIRMADA'] and not self.pagado:
                self.estado = 'CANCELADA'
                self.save(update_fields=['estado', 'actualizado_en'])
                return True
            return False
    """
    Modelo para reservas de canchas.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('NO_ASISTIO', 'No Asistió'),
        ('COMPLETADA', 'Completada'),
    ]
    
    cancha = models.ForeignKey(
        'complejos.Cancha',
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    jugador_principal = models.ForeignKey(
        'cuentas.PerfilJugador',
        on_delete=models.CASCADE,
        related_name='reservas',
        null=True,
        blank=True
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pagado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    # Permitir nombre de cliente no registrado (para reservas simples)
    nombre_cliente = models.CharField(max_length=200, blank=True, help_text='Nombre del cliente si no es jugador registrado')
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha', '-hora_inicio']
        unique_together = ['cancha', 'fecha', 'hora_inicio']
    

    def __str__(self):
        return f"{self.cancha} - {self.fecha} {self.hora_inicio}"

    def confirmar(self):
        """
        Marca la reserva como pagada y confirmada (solo dueños).
        Si ya está pagada, no hace nada.
        Devuelve True si se modificó, False si ya estaba pagada.
        """
        modificado = False
        if not self.pagado:
            self.pagado = True
            modificado = True
        if self.estado != 'CONFIRMADA':
            self.estado = 'CONFIRMADA'
            modificado = True
        if modificado:
            self.save(update_fields=['pagado', 'estado', 'actualizado_en'])
        return modificado


class ReservaFija(models.Model):
    """
    Modelo para reservas recurrentes/fijas que se repiten automáticamente.
    Solo el dueño del complejo puede crearlas y asignarlas a jugadores.
    Los turnos fijos quedan bloqueados automáticamente y no pueden ser reservados por otros.
    """
    
    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('CANCELADA', 'Cancelada'),
        ('PAUSADA', 'Pausada'),
    ]
    
    cancha = models.ForeignKey(
        'complejos.Cancha',
        on_delete=models.CASCADE,
        related_name='reservas_fijas'
    )
    
    # Jugador asignado al turno fijo (puede ser null si es reserva del dueño para cliente sin cuenta)
    jugador = models.ForeignKey(
        'cuentas.PerfilJugador',
        on_delete=models.CASCADE,
        related_name='reservas_fijas',
        null=True,
        blank=True
    )
    
    # Campos para turnos fijos de clientes sin cuenta
    nombre_cliente = models.CharField(
        max_length=200,
        blank=True,
        help_text='Nombre del cliente que tiene el turno fijo'
    )
    telefono_cliente = models.CharField(max_length=20, blank=True)
    
    # Configuración del turno fijo
    dia_semana = models.IntegerField(
        choices=[
            (0, 'Lunes'),
            (1, 'Martes'),
            (2, 'Miércoles'),
            (3, 'Jueves'),
            (4, 'Viernes'),
            (5, 'Sábado'),
            (6, 'Domingo'),
        ],
        help_text='0=Lunes, 6=Domingo'
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    # Vigencia del turno fijo
    fecha_inicio = models.DateField(
        help_text='Primera fecha en que se aplicará esta reserva fija'
    )
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha final del turno fijo (opcional, si es null es indefinido)'
    )
    
    # Estado, pagado y precio
    ESTADO_RESERVA_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('NO_ASISTIO', 'No Asistió'),
        ('COMPLETADA', 'Completada'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_RESERVA_CHOICES,
        default='PENDIENTE'
    )
    pagado = models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Observaciones
    observaciones = models.TextField(blank=True)
    
    # Quién creó la reserva fija (el dueño)
    creada_por = models.ForeignKey(
        'cuentas.PerfilDueno',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_fijas_creadas'
    )
    
    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reserva Fija'
        verbose_name_plural = 'Reservas Fijas'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['cancha', 'dia_semana', 'hora_inicio']
        indexes = [
            models.Index(fields=['cancha', 'estado']),
            models.Index(fields=['estado', 'fecha_inicio']),
        ]
    
    def __str__(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        nombre = self.jugador.alias if self.jugador else self.nombre_cliente
        return f"{self.cancha} - {dias[self.dia_semana]} {self.hora_inicio} - {nombre} ({self.get_estado_display()})"
    
    def get_proximas_fechas(self, cantidad=4):
        """
        Retorna las próximas N fechas en que aplica esta reserva fija.
        """
        from datetime import timedelta
        fechas = []
        fecha_actual = max(self.fecha_inicio, timezone.now().date())
        limite = 365  # Evitar bucles infinitos
        dias_evaluados = 0
        
        while len(fechas) < cantidad and dias_evaluados < limite:
            if fecha_actual.weekday() == self.dia_semana:
                if self.fecha_fin is None or fecha_actual <= self.fecha_fin:
                    fechas.append(fecha_actual)
            fecha_actual += timedelta(days=1)
            dias_evaluados += 1
        
        return fechas
    
    def bloquear_turnos_futuros(self, hasta_fecha=None):
        """
        Crea/actualiza turnos FIJO para las próximas ocurrencias de esta reserva fija.
        hasta_fecha: hasta qué fecha bloquear (por defecto 30 días a futuro)
        """
        if self.estado != 'ACTIVA':
            return []
        
        if hasta_fecha is None:
            hasta_fecha = timezone.now().date() + timedelta(days=30)
        
        fecha_actual = max(self.fecha_inicio, timezone.now().date())
        turnos_bloqueados = []
        
        while fecha_actual <= hasta_fecha:
            if fecha_actual.weekday() == self.dia_semana:
                if self.fecha_fin is None or fecha_actual <= self.fecha_fin:
                    # Buscar o crear turno
                    turno, created = Turno.objects.get_or_create(
                        cancha=self.cancha,
                        fecha=fecha_actual,
                        hora_inicio=self.hora_inicio,
                        defaults={
                            'hora_fin': self.hora_fin,
                            'precio': self.precio,
                            'estado': 'FIJO'
                        }
                    )
                    if not created and turno.estado != 'FIJO':
                        turno.estado = 'FIJO'
                        turno.precio = self.precio
                        turno.save()
                    turnos_bloqueados.append(turno)
            
            fecha_actual += timedelta(days=1)
        
        return turnos_bloqueados


class Torneo(models.Model):
    """
    Modelo para gestionar torneos que bloquean turnos en rangos de fechas.
    Solo el dueño del complejo puede crear y gestionar torneos.
    """
    ESTADO_CHOICES = [
        ('PROGRAMADO', 'Programado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    complejo = models.ForeignKey(
        'complejos.Complejo',
        on_delete=models.CASCADE,
        related_name='torneos'
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PROGRAMADO'
    )
    
    # Configuración del torneo
    categoria = models.CharField(
        max_length=100,
        blank=True,
        help_text='Ej: Principiantes, Intermedio, Avanzado'
    )
    cupo_equipos = models.IntegerField(
        null=True,
        blank=True,
        help_text='Cantidad máxima de equipos'
    )
    
    # Auditoría
    creado_por = models.ForeignKey(
        'cuentas.PerfilDueno',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='torneos_creados'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Torneo'
        verbose_name_plural = 'Torneos'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['complejo', 'estado']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.complejo.nombre} ({self.get_estado_display()})"
    
    def bloquear_turnos(self, canchas=None, horarios=None):
        """
        Bloquea turnos para el torneo en las canchas y horarios especificados.
        canchas: lista de canchas a bloquear (si es None, bloquea todas del complejo)
        horarios: lista de tuplas (hora_inicio, hora_fin) (si es None, bloquea todo el día)
        """
        if self.estado == 'CANCELADO':
            return []
        
        if canchas is None:
            canchas = self.complejo.canchas.filter(activo=True)
        
        fecha_actual = self.fecha_inicio
        turnos_bloqueados = []
        
        while fecha_actual <= self.fecha_fin:
            for cancha in canchas:
                if horarios:
                    # Bloquear solo horarios específicos
                    for hora_inicio, hora_fin in horarios:
                        bloqueo, created = BloqueoTorneo.objects.get_or_create(
                            torneo=self,
                            cancha=cancha,
                            fecha=fecha_actual,
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin
                        )
                        turnos_bloqueados.append(bloqueo)
                        
                        # Actualizar o crear turno con estado BLOQUEADO_TORNEO
                        turno, t_created = Turno.objects.get_or_create(
                            cancha=cancha,
                            fecha=fecha_actual,
                            hora_inicio=hora_inicio,
                            defaults={
                                'hora_fin': hora_fin,
                                'precio': cancha.precio_base,
                                'estado': 'BLOQUEADO_TORNEO'
                            }
                        )
                        if not t_created:
                            turno.estado = 'BLOQUEADO_TORNEO'
                            turno.save()
                else:
                    # Bloquear todo el día
                    from datetime import time
                    bloqueo, created = BloqueoTorneo.objects.get_or_create(
                        torneo=self,
                        cancha=cancha,
                        fecha=fecha_actual,
                        hora_inicio=cancha.horario_apertura,
                        hora_fin=cancha.horario_cierre
                    )
                    turnos_bloqueados.append(bloqueo)
            
            fecha_actual += timedelta(days=1)
        
        return turnos_bloqueados
    
    def liberar_turnos(self):
        """Libera todos los turnos bloqueados por este torneo."""
        bloqueos = BloqueoTorneo.objects.filter(torneo=self)
        
        for bloqueo in bloqueos:
            # Buscar turnos bloqueados y liberarlos si no hay reserva activa
            turnos = Turno.objects.filter(
                cancha=bloqueo.cancha,
                fecha=bloqueo.fecha,
                hora_inicio=bloqueo.hora_inicio,
                estado='BLOQUEADO_TORNEO'
            )
            for turno in turnos:
                turno.estado = 'DISPONIBLE'
                turno.save()
        
        bloqueos.delete()


class BloqueoTorneo(models.Model):
    """
    Registra qué turnos específicos están bloqueados por un torneo.
    """
    torneo = models.ForeignKey(
        Torneo,
        on_delete=models.CASCADE,
        related_name='bloqueos'
    )
    cancha = models.ForeignKey(
        'complejos.Cancha',
        on_delete=models.CASCADE,
        related_name='bloqueos_torneo'
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Bloqueo de Torneo'
        verbose_name_plural = 'Bloqueos de Torneo'
        ordering = ['fecha', 'hora_inicio']
        unique_together = ['torneo', 'cancha', 'fecha', 'hora_inicio']
        indexes = [
            models.Index(fields=['torneo', 'fecha']),
            models.Index(fields=['cancha', 'fecha']),
        ]
    
    def __str__(self):
        return f"{self.torneo.nombre} - {self.cancha} - {self.fecha} {self.hora_inicio}"


class PartidoAbierto(models.Model):
    """
    Modelo para gestionar partidos donde jugadores pueden sumarse.
    Puede ser creado por un jugador o por el dueño del complejo.
    """
    ESTADO_CHOICES = [
        ('ABIERTO', 'Abierto'),
        ('COMPLETO', 'Completo'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    NIVEL_CHOICES = [
        ('PRINCIPIANTE', 'Principiante'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado'),
        ('PROFESIONAL', 'Profesional'),
        ('MIXTO', 'Mixto'),
    ]
    
    turno = models.OneToOneField(
        Turno,
        on_delete=models.CASCADE,
        related_name='partido_abierto'
    )
    
    # Creador del partido
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='partidos_creados',
        help_text='Usuario que creó el partido (puede ser jugador o dueño)'
    )
    creado_por_dueno = models.BooleanField(
        default=False,
        help_text='Indica si fue creado por un dueño del complejo'
    )
    
    # Configuración del partido
    cupo_jugadores = models.IntegerField(
        default=4,
        help_text='Cantidad total de jugadores para el partido (generalmente 4 para pádel)'
    )
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='MIXTO',
        help_text='Nivel de juego requerido/esperado'
    )
    categoria = models.CharField(
        max_length=100,
        blank=True,
        help_text='Categoría adicional: Masculino, Femenino, Mixto, etc.'
    )
    descripcion = models.TextField(
        blank=True,
        help_text='Descripción adicional del partido'
    )
    
    # Estado del partido
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ABIERTO'
    )
    
    # Link de invitación único
    token_invitacion = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text='Token único para el link de invitación'
    )
    
    # Precio por jugador (puede diferir del precio del turno si se divide entre jugadores)
    precio_por_jugador = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio que paga cada jugador'
    )
    
    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Partido Abierto'
        verbose_name_plural = 'Partidos Abiertos'
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['estado', 'creado_en']),
            models.Index(fields=['token_invitacion']),
        ]
    
    def __str__(self):
        return f"Partido {self.get_nivel_display()} - {self.turno} ({self.get_estado_display()})"
    
    def save(self, *args, **kwargs):
        # Generar token de invitación si no existe
        if not self.token_invitacion:
            self.token_invitacion = secrets.token_urlsafe(32)
        
        # Calcular precio por jugador si no está definido
        if not self.precio_por_jugador:
            self.precio_por_jugador = self.turno.precio / self.cupo_jugadores
        
        super().save(*args, **kwargs)
        
        # Actualizar estado del turno
        if self.estado == 'ABIERTO':
            self.turno.estado = 'PARTIDO_ABIERTO'
            self.turno.save()
    
    def get_link_invitacion(self, base_url='https://dereves.com'):
        """Retorna el link completo de invitación."""
        return f"{base_url}/partidos/{self.token_invitacion}/unirse"
    
    def jugadores_actuales(self):
        """Retorna la cantidad de jugadores ya anotados."""
        return self.jugadores.filter(confirmado=True).count()
    
    def cupos_disponibles(self):
        """Retorna cuántos cupos quedan disponibles."""
        return self.cupo_jugadores - self.jugadores_actuales()
    
    def esta_completo(self):
        """Verifica si el partido ya está completo."""
        return self.jugadores_actuales() >= self.cupo_jugadores
    
    def puede_sumarse(self):
        """Verifica si hay cupo para que se sume otro jugador."""
        return self.estado == 'ABIERTO' and not self.esta_completo()
    
    def actualizar_estado(self):
        """Actualiza el estado del partido según los cupos."""
        if self.esta_completo() and self.estado == 'ABIERTO':
            self.estado = 'COMPLETO'
            self.save()
        elif not self.esta_completo() and self.estado == 'COMPLETO':
            self.estado = 'ABIERTO'
            self.save()
    
    @property
    def cancha(self):
        return self.turno.cancha
    
    @property
    def fecha(self):
        return self.turno.fecha
    
    @property
    def hora_inicio(self):
        return self.turno.hora_inicio
    
    @property
    def hora_fin(self):
        return self.turno.hora_fin


class JugadorPartido(models.Model):
    """
    Relación entre un partido abierto y los jugadores que participan.
    Permite jugadores registrados y jugadores invitados sin cuenta.
    """
    partido = models.ForeignKey(
        PartidoAbierto,
        on_delete=models.CASCADE,
        related_name='jugadores'
    )
    
    # Jugador registrado (puede ser null si es invitado sin cuenta)
    jugador = models.ForeignKey(
        'cuentas.PerfilJugador',
        on_delete=models.CASCADE,
        related_name='participaciones_partidos',
        null=True,
        blank=True
    )
    
    # Datos para jugadores invitados sin cuenta
    es_invitado = models.BooleanField(
        default=False,
        help_text='Indica si es un jugador invitado sin cuenta'
    )
    nombre_invitado = models.CharField(
        max_length=200,
        blank=True,
        help_text='Nombre del jugador invitado'
    )
    telefono_invitado = models.CharField(
        max_length=20,
        blank=True,
        help_text='Teléfono de contacto del invitado'
    )
    email_invitado = models.EmailField(
        blank=True,
        help_text='Email opcional del invitado'
    )
    
    # Estado de la participación
    confirmado = models.BooleanField(
        default=True,
        help_text='Indica si el jugador confirmó su participación'
    )
    es_creador = models.BooleanField(
        default=False,
        help_text='Indica si este jugador es el creador del partido'
    )
    pagado = models.BooleanField(
        default=False,
        help_text='Indica si el jugador pagó su parte'
    )
    
    # Auditoría
    unido_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Jugador en Partido'
        verbose_name_plural = 'Jugadores en Partidos'
        ordering = ['-es_creador', 'unido_en']
        unique_together = ['partido', 'jugador']  # Un jugador no puede estar dos veces en el mismo partido
        indexes = [
            models.Index(fields=['partido', 'confirmado']),
            models.Index(fields=['jugador', 'confirmado']),
        ]
    
    def __str__(self):
        if self.jugador:
            nombre = self.jugador.alias
        else:
            nombre = self.nombre_invitado
        
        tipo = "Creador" if self.es_creador else "Invitado"
        return f"{nombre} ({tipo}) - {self.partido}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar estado del partido después de agregar/quitar jugador
        self.partido.actualizar_estado()
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Actualizar estado del partido después de eliminar jugador
        self.partido.actualizar_estado()



