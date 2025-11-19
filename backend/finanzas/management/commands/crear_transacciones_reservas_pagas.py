from django.core.management.base import BaseCommand
from reservas.models import Reserva
from finanzas.models import Transaccion

class Command(BaseCommand):
    help = 'Crea transacciones de ingreso para todas las reservas simples pagadas que no tienen transacción.'

    def handle(self, *args, **options):
        count = 0
        reservas = Reserva.objects.filter(pagado=True)
        for r in reservas:
            if not Transaccion.objects.filter(reserva=r, tipo='INGRESO', categoria='RESERVA').exists():
                Transaccion.objects.create(
                    complejo=r.cancha.complejo,
                    tipo='INGRESO',
                    categoria='RESERVA',
                    monto=r.precio,
                    descripcion=f'Pago de reserva {r.id}',
                    fecha=r.fecha,
                    reserva=r
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} transacciones creadas para reservas pagadas.'))
