from django.db import models
from django.conf import settings
from django.utils import timezone


class Transaccion(models.Model):
    """
    Modelo para registrar todas las transacciones financieras.
    """
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    ]
    
    CATEGORIA_INGRESO_CHOICES = [
        ('RESERVA', 'Reserva de Cancha'),
        ('RESERVA_FIJA', 'Reserva Fija'),
        ('SEÑA', 'Seña/Adelanto'),
        ('OTRO', 'Otro Ingreso'),
    ]
    
    CATEGORIA_GASTO_CHOICES = [
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('SERVICIOS', 'Servicios (Luz, Agua, Gas)'),
        ('SUELDOS', 'Sueldos'),
        ('EQUIPAMIENTO', 'Equipamiento'),
        ('LIMPIEZA', 'Limpieza'),
        ('IMPUESTOS', 'Impuestos'),
        ('PUBLICIDAD', 'Publicidad'),
        ('OTRO', 'Otro Gasto'),
    ]
    
    complejo = models.ForeignKey(
        'complejos.Complejo',
        on_delete=models.CASCADE,
        related_name='transacciones'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=20)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    fecha = models.DateField(default=timezone.now)
    
    # Relación opcional con reserva
    reserva = models.ForeignKey(
        'reservas.Reserva',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones'
    )
    
    # Usuario que registró la transacción
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transacciones_registradas'
    )
    
    # Comprobante
    comprobante = models.FileField(
        upload_to='finanzas/comprobantes/',
        blank=True,
        null=True,
        help_text="Foto o PDF del comprobante"
    )
    
    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha', '-creado_en']
    
    def __str__(self):
        signo = '+' if self.tipo == 'INGRESO' else '-'
        return f"{self.complejo.nombre} - {signo}${self.monto} - {self.get_categoria_display()}"
    
    def get_categoria_display(self):
        """Retorna el display de la categoría según el tipo."""
        if self.tipo == 'INGRESO':
            choices_dict = dict(self.CATEGORIA_INGRESO_CHOICES)
        else:
            choices_dict = dict(self.CATEGORIA_GASTO_CHOICES)
        return choices_dict.get(self.categoria, self.categoria)


class ResumenMensual(models.Model):
    """
    Resumen financiero mensual por complejo.
    Se calcula automáticamente.
    """
    complejo = models.ForeignKey(
        'complejos.Complejo',
        on_delete=models.CASCADE,
        related_name='resumenes_mensuales'
    )
    año = models.IntegerField()
    mes = models.IntegerField()  # 1-12
    
    # Totales
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_gastos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Desglose de ingresos
    ingresos_reservas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ingresos_reservas_fijas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ingresos_otros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Estadísticas
    cantidad_reservas = models.IntegerField(default=0)
    cantidad_transacciones = models.IntegerField(default=0)
    
    # Auditoría
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Resumen Mensual'
        verbose_name_plural = 'Resúmenes Mensuales'
        unique_together = ['complejo', 'año', 'mes']
        ordering = ['-año', '-mes']
    
    def __str__(self):
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{self.complejo.nombre} - {meses[self.mes-1]} {self.año}"
    
    def calcular_resumen(self):
        """Recalcula los totales basándose en las transacciones del mes."""
        from datetime import date
        inicio_mes = date(self.año, self.mes, 1)
        if self.mes == 12:
            fin_mes = date(self.año + 1, 1, 1)
        else:
            fin_mes = date(self.año, self.mes + 1, 1)
        
        transacciones = self.complejo.transacciones.filter(
            fecha__gte=inicio_mes,
            fecha__lt=fin_mes
        )
        
        # Calcular totales
        ingresos = transacciones.filter(tipo='INGRESO')
        gastos = transacciones.filter(tipo='GASTO')
        
        self.total_ingresos = sum(t.monto for t in ingresos)
        self.total_gastos = sum(t.monto for t in gastos)
        self.balance = self.total_ingresos - self.total_gastos
        
        # Desglose de ingresos
        self.ingresos_reservas = sum(
            t.monto for t in ingresos.filter(categoria='RESERVA')
        )
        self.ingresos_reservas_fijas = sum(
            t.monto for t in ingresos.filter(categoria='RESERVA_FIJA')
        )
        self.ingresos_otros = sum(
            t.monto for t in ingresos.exclude(categoria__in=['RESERVA', 'RESERVA_FIJA'])
        )
        
        # Estadísticas
        self.cantidad_reservas = ingresos.filter(
            categoria__in=['RESERVA', 'RESERVA_FIJA']
        ).count()
        self.cantidad_transacciones = transacciones.count()
        
        self.save()

