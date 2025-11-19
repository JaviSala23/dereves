from django.core.management.base import BaseCommand
from django.utils import timezone
from reservas.models import ReservaFija
from finanzas.models import Transaccion
from django.db import models
from datetime import date

class Command(BaseCommand):
    help = 'Registra ingresos de reservas fijas cumplidas (no liberadas) para el día actual.'

    def handle(self, *args, **options):
        hoy = date.today()
        count = 0
        reservas_fijas = ReservaFija.objects.filter(
            estado='ACTIVA',
            pagado=False,
            fecha_inicio__lte=hoy
        ).filter(
            models.Q(fecha_fin__gte=hoy) | models.Q(fecha_fin__isnull=True)
        )
        for rf in reservas_fijas:
            if hoy.weekday() != rf.dia_semana:
                continue
            if rf.liberaciones.filter(fecha=hoy).exists():
                continue
            if Transaccion.objects.filter(
                complejo=rf.cancha.complejo,
                tipo='INGRESO',
                categoria='RESERVA_FIJA',
                fecha=hoy,
                descripcion__icontains=f"Reserva fija {rf.id}"
            ).exists():
                continue
            Transaccion.objects.create(
                complejo=rf.cancha.complejo,
                tipo='INGRESO',
                categoria='RESERVA_FIJA',
                monto=rf.precio,
                descripcion=f'Pago automático reserva fija {rf.id} ({rf.nombre_cliente or rf.jugador})',
                fecha=hoy
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} ingresos de reservas fijas registrados para el día {hoy}'))
