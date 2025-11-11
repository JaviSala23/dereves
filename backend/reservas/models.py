from django.db import models
from django.conf import settings


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


class Reserva(models.Model):
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
        related_name='reservas'
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


class ReservaFija(models.Model):
    """
    Modelo para reservas recurrentes/fijas que se repiten automáticamente.
    Solo el dueño del complejo puede crearlas y asignarlas a jugadores.
    El turno queda reservado permanentemente hasta que se cancele.
    """
    
    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    cancha = models.ForeignKey(
        'complejos.Cancha',
        on_delete=models.CASCADE,
        related_name='reservas_fijas'
    )
    jugador = models.ForeignKey(
        'cuentas.PerfilJugador',
        on_delete=models.CASCADE,
        related_name='reservas_fijas'
    )
    
    # Día y horario del turno fijo
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
    
    # Fecha desde la cual aplica la reserva fija
    fecha_inicio = models.DateField(
        help_text='Primera fecha en que se aplicará esta reserva fija'
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVA'
    )
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
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reserva Fija'
        verbose_name_plural = 'Reservas Fijas'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['cancha', 'dia_semana', 'hora_inicio']
    
    def __str__(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return f"{self.cancha} - {dias[self.dia_semana]} {self.hora_inicio} ({self.get_estado_display()})"
    
    def get_proximas_fechas(self, cantidad=4):
        """
        Retorna las próximas N fechas en que aplica esta reserva fija.
        """
        from datetime import timedelta
        fechas = []
        fecha_actual = self.fecha_inicio
        
        while len(fechas) < cantidad:
            if fecha_actual.weekday() == self.dia_semana:
                fechas.append(fecha_actual)
            fecha_actual += timedelta(days=1)
        
        return fechas
