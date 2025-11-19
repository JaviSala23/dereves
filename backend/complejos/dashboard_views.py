from django.views.decorators.http import require_POST
from django.urls import reverse

"""
Vistas del dashboard para dueños de complejos.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime, time
import json
from .models import Complejo, Cancha
from reservas.models import Reserva, ReservaFija
from cuentas.models import PerfilDueno
from reservas.models import ReservaFijaLiberacion
from django.db.models import Q
from django.http import JsonResponse


@login_required
def dashboard_principal(request):
    """
    Dashboard principal para dueños de complejos.
    Muestra estadísticas generales y resumen de actividad.
    """
    # Verificar que el usuario sea dueño
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Acceso denegado. Solo para dueños de complejos.')
        return redirect('home')
    
    perfil_dueno = PerfilDueno.objects.get(usuario=request.user)
    complejos = Complejo.objects.filter(dueno=perfil_dueno)
    
    # Rango de fechas para estadísticas (último mes)
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    hace_7_dias = hoy - timedelta(days=7)
    
    # Estadísticas generales
    total_complejos = complejos.count()
    total_canchas = Cancha.objects.filter(complejo__in=complejos).count()
    
    # Reservas del último mes
    reservas_mes = Reserva.objects.filter(
        cancha__complejo__in=complejos,
        fecha__gte=hace_30_dias,
        fecha__lte=hoy
    )
    
    total_reservas_mes = reservas_mes.count()
    reservas_confirmadas = reservas_mes.filter(estado='CONFIRMADA').count()
    reservas_pendientes = reservas_mes.filter(estado='PENDIENTE').count()
    reservas_canceladas = reservas_mes.filter(estado='CANCELADA').count()
    
    # Ingresos del mes (solo reservas confirmadas y pagadas)
    ingresos_mes = reservas_mes.filter(
        estado='CONFIRMADA',
        pagado=True
    ).aggregate(total=Sum('precio'))['total'] or 0
    
    # Reservas de la última semana
    reservas_semana = Reserva.objects.filter(
        cancha__complejo__in=complejos,
        fecha__gte=hace_7_dias,
        fecha__lte=hoy
    ).count()
    
    # Próximas reservas (hoy y mañana)
    manana = hoy + timedelta(days=1)
    proximas_reservas = Reserva.objects.filter(
        cancha__complejo__in=complejos,
        fecha__gte=hoy,
        fecha__lte=manana,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).select_related('cancha', 'jugador_principal', 'cancha__complejo').order_by('fecha', 'hora_inicio')[:10]
    
    # Tasa de ocupación (reservas confirmadas vs slots disponibles aproxido)
    if total_canchas > 0:
        slots_disponibles_mes = total_canchas * 30 * 15  # aprox 15 slots por día por cancha
        tasa_ocupacion = (reservas_confirmadas / slots_disponibles_mes * 100) if slots_disponibles_mes > 0 else 0
    else:
        tasa_ocupacion = 0
    
    # Canchas más reservadas
    canchas_populares = Cancha.objects.filter(
        complejo__in=complejos
    ).annotate(
        num_reservas=Count('reservas', filter=Q(reservas__fecha__gte=hace_30_dias))
    ).order_by('-num_reservas')[:5]
    
    # Datos para gráfico de reservas por día (últimos 7 días)
    reservas_por_dia = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        count = Reserva.objects.filter(
            cancha__complejo__in=complejos,
            fecha=dia
        ).count()
        reservas_por_dia.append({
            'fecha': dia.strftime('%d/%m'),
            'cantidad': count
        })
    
    context = {
        'perfil_dueno': perfil_dueno,
        'complejos': complejos,
        'total_complejos': total_complejos,
        'total_canchas': total_canchas,
        'total_reservas_mes': total_reservas_mes,
        'reservas_confirmadas': reservas_confirmadas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_canceladas': reservas_canceladas,
        'ingresos_mes': ingresos_mes,
        'reservas_semana': reservas_semana,
        'tasa_ocupacion': round(tasa_ocupacion, 1),
        'proximas_reservas': proximas_reservas,
        'canchas_populares': canchas_populares,
        'reservas_por_dia': json.dumps(reservas_por_dia),  # Convertir a JSON
    }
    
    return render(request, 'complejos/dashboard/principal.html', context)


@login_required
def mis_complejos_dashboard(request):
    """
    Vista de gestión de complejos del dueño.
    Lista todos los complejos con opciones de edición.
    """
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Acceso denegado. Solo para dueños de complejos.')
        return redirect('home')

    perfil_dueno = PerfilDueno.objects.get(usuario=request.user)
    complejos = Complejo.objects.filter(dueno=perfil_dueno).prefetch_related('canchas')

    # Agregar estadísticas a cada complejo
    for complejo in complejos:
        complejo.num_canchas = complejo.canchas.count()
        complejo.num_reservas_mes = Reserva.objects.filter(
            cancha__complejo=complejo,
            fecha__gte=timezone.now().date() - timedelta(days=30)
        ).count()

    context = {
        'complejos': complejos,
        'perfil_dueno': perfil_dueno,
    }

    return render(request, 'complejos/dashboard/mis_complejos.html', context)



# Vista: Gestionar todas las reservas de los complejos del dueño
@login_required
def gestionar_reservas(request):
    """
    Vista para gestionar todas las reservas de los complejos del dueño.
    Incluye filtros por estado, fecha, complejo, etc.
    También muestra las reservas fijas activas.
    """
    from datetime import timedelta, date
    fechas_disponibles = []
    if not (request.user.tipo_usuario == 'DUENIO' or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Acceso denegado.')
        return redirect('home')

    perfil_dueno = PerfilDueno.objects.get(usuario=request.user)
    complejos = Complejo.objects.filter(dueno=perfil_dueno)

    # Reservas fijas activas
    reservas_fijas_activas = ReservaFija.objects.filter(
        cancha__complejo__in=complejos,
        estado='ACTIVA'
    ).select_related(
        'cancha', 'cancha__complejo', 'jugador', 'jugador__usuario'
    ).order_by('cancha__complejo__nombre', 'cancha__nombre', 'dia_semana', 'hora_inicio')

    # Reservas de los complejos
    reservas = Reserva.objects.filter(
        cancha__complejo__in=complejos
    ).select_related(
        'cancha', 'cancha__complejo', 'jugador_principal', 'metodo_pago'
    ).order_by('-fecha', '-hora_inicio')

    # Filtros
    estado_filtro = request.GET.get('estado', '')
    complejo_filtro = request.GET.get('complejo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    pagado_filtro = request.GET.get('pagado', '')

    if estado_filtro:
        reservas = reservas.filter(estado=estado_filtro)
    if complejo_filtro:
        reservas = reservas.filter(cancha__complejo__id=complejo_filtro)
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            reservas = reservas.filter(fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            reservas = reservas.filter(fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    if pagado_filtro:
        reservas = reservas.filter(pagado=(pagado_filtro == 'true'))

    # Estadísticas
    total_reservas = reservas.count()
    reservas_pendientes = reservas.filter(estado='PENDIENTE').count()
    reservas_confirmadas = reservas.filter(estado='CONFIRMADA').count()
    total_ingresos = reservas.filter(estado='CONFIRMADA', pagado=True).aggregate(
        total=Sum('precio')
    )['total'] or 0

    # Jugadores para modal crear reserva fija
    from cuentas.models import PerfilJugador
    jugadores = PerfilJugador.objects.filter(usuario__is_active=True).select_related('usuario').order_by('usuario__first_name')

    # Canchas del dueño para el modal
    canchas_qs = Cancha.objects.filter(complejo__in=complejos, activo=True).select_related('complejo')
    canchas = [
        {
            'id': cancha.id,
            'nombre': cancha.nombre,
            'complejo': str(cancha.complejo),
            'horario_apertura': cancha.horario_apertura.strftime('%H:%M'),
            'horario_cierre': cancha.horario_cierre.strftime('%H:%M'),
            'duracion_turno_minutos': cancha.duracion_turno_minutos,
            'precio_base': float(cancha.precio_base) if hasattr(cancha, 'precio_base') else 0,
            'turnos': [
                f"{h:02d}:{m:02d}"
                for h in range(int(cancha.horario_apertura.hour), int(cancha.horario_cierre.hour) + 1)
                for m in range(0, 60, cancha.duracion_turno_minutos)
                if (h < cancha.horario_cierre.hour or (h == cancha.horario_cierre.hour and m <= cancha.horario_cierre.minute - cancha.duracion_turno_minutos))
            ]
        }
        for cancha in canchas_qs
    ]

    # Calcular fechas_disponibles y turnos_por_fecha (próximos 14 días, al menos una cancha activa y sin reservas fijas ni simples en ese día)
    from datetime import timedelta, date
    fechas_disponibles = []
    turnos_por_fecha = {}
    hoy = date.today()
    for i in range(0, 14):
        dia = hoy + timedelta(days=i)
        turnos_dia = set()
        for cancha in canchas_qs:
            dia_semana = dia.weekday()
            # Obtener reservas fijas activas para ese día y cancha
            reservas_fijas = ReservaFija.objects.filter(cancha=cancha, dia_semana=dia_semana, estado='ACTIVA')
            # Obtener reservas simples para ese día y cancha
            reservas_simples = Reserva.objects.filter(cancha=cancha, fecha=dia)
            # Generar turnos posibles para la cancha
            hora_apertura = cancha.horario_apertura
            hora_cierre = cancha.horario_cierre
            duracion = cancha.duracion_turno_minutos
            h = hora_apertura.hour
            m = hora_apertura.minute
            while True:
                hora_inicio = h * 60 + m
                hora_fin = hora_inicio + duracion
                if hora_fin > (hora_cierre.hour * 60 + hora_cierre.minute):
                    break
                turno_inicio = time(hour=h, minute=m)
                turno_fin = (datetime.combine(dia, turno_inicio) + timedelta(minutes=duracion)).time()
                ocupado = False
                # Verificar solapamiento con reservas fijas
                for rf in reservas_fijas:
                    if (rf.hora_inicio < turno_fin and rf.hora_fin > turno_inicio):
                        ocupado = True
                        break
                # Verificar solapamiento con reservas simples
                if not ocupado:
                    for rs in reservas_simples:
                        if (rs.hora_inicio < turno_fin and rs.hora_fin > turno_inicio):
                            ocupado = True
                            break
                if not ocupado:
                    turno_str = f"{h:02d}:{m:02d}"
                    turnos_dia.add(turno_str)
                m += duracion
                while m >= 60:
                    m -= 60
                    h += 1
                if (h > hora_cierre.hour) or (h == hora_cierre.hour and m > hora_cierre.minute - duracion):
                    break
        fechas_disponibles.append(dia)
        turnos_por_fecha[dia] = sorted(turnos_dia)

    # Agrupar fechas_disponibles en sublistas de hasta 4 para el carrusel
    fechas_disponibles_grouped = [fechas_disponibles[i:i+4] for i in range(0, len(fechas_disponibles), 4)]

    context = {
        'reservas': reservas,
        'reservas_fijas_activas': reservas_fijas_activas,
        'total_reservas': total_reservas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_confirmadas': reservas_confirmadas,
        'total_ingresos': total_ingresos,
        'jugadores': jugadores,
        'canchas': canchas,
        'complejos': complejos,
        'fechas_disponibles_grouped': fechas_disponibles_grouped,
        'turnos_por_fecha': turnos_por_fecha,
    }

    return render(request, 'complejos/dashboard/gestionar_reservas.html', context)

# Vista: Estadísticas por complejo (usando slug)
@login_required
def estadisticas_complejo(request, slug):
    """
    Vista de estadísticas por complejo, usando slug.
    """
    from datetime import timedelta
    if not (request.user.tipo_usuario == 'DUENIO' or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Acceso denegado.')
        return redirect('home')

    perfil_dueno = PerfilDueno.objects.get(usuario=request.user)
    complejo = Complejo.objects.filter(slug=slug, dueno=perfil_dueno).first()

    if not complejo:
        messages.error(request, 'Complejo no encontrado.')
        return redirect('complejos:dashboard_principal')

    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)

    canchas = complejo.canchas.all()
    reservas_mes = Reserva.objects.filter(
        cancha__complejo=complejo,
        fecha__gte=hace_30_dias
    )

    stats_canchas = []
    for cancha in canchas:
        reservas_cancha = reservas_mes.filter(cancha=cancha)
        stats_canchas.append({
            'cancha': cancha,
            'total_reservas': reservas_cancha.count(),
            'confirmadas': reservas_cancha.filter(estado='CONFIRMADA').count(),
            'ingresos': reservas_cancha.filter(estado='CONFIRMADA', pagado=True).aggregate(
                total=Sum('precio')
            )['total'] or 0,
        })

    ingresos_total = reservas_mes.filter(estado='CONFIRMADA', pagado=True).aggregate(
        total=Sum('precio')
    )['total'] or 0

    context = {
        'complejo': complejo,
        'canchas': canchas,
        'stats_canchas': stats_canchas,
        'ingresos_total': ingresos_total,
        'total_reservas': reservas_mes.count(),
    }

    return render(request, 'complejos/dashboard/estadisticas_complejo.html', context)


@login_required
def crear_reserva_fija_dashboard(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    try:
        data = json.loads(request.body.decode())
        perfil_dueno = request.user.perfil_dueno
        cancha = Cancha.objects.get(id=data['cancha_id'], complejo__dueno=perfil_dueno)
        from datetime import datetime, timedelta
        hora_inicio = data['hora_inicio']
        dia_semana = int(data['dia_semana'])
        nombre_cliente = data.get('nombre_cliente', '')
        telefono_cliente = data.get('telefono_cliente', '')
        precio = float(data['precio'])
        # Calcular hora_fin
        hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
        hora_fin_dt = datetime.combine(timezone.now().date(), hora_inicio_obj) + timedelta(minutes=cancha.duracion_turno_minutos)
        hora_fin = hora_fin_dt.time()
        # Verificar si ya existe una reserva fija activa para ese día, cancha y hora
        existe = ReservaFija.objects.filter(
            cancha=cancha,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            estado='ACTIVA'
        ).exists()
        if existe:
            return JsonResponse({'success': False, 'message': 'Ya existe un turno fijo para ese día y horario en esta cancha.'})
        reserva_fija = ReservaFija.objects.create(
            cancha=cancha,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            fecha_inicio=timezone.now().date(),
            nombre_cliente=nombre_cliente,
            telefono_cliente=telefono_cliente,
            precio=precio,
            creada_por=perfil_dueno,
            estado='ACTIVA'
        )
        return JsonResponse({'success': True, 'message': 'Turno fijo creado correctamente.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'})


@login_required
def crear_reserva_campeonato_dashboard(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    try:
        data = json.loads(request.body.decode())
        perfil_dueno = request.user.perfil_dueno
        cancha = Cancha.objects.get(id=data['cancha_id'], complejo__dueno=perfil_dueno)
        from datetime import datetime, timedelta
        fecha_dt = datetime.fromisoformat(data['fecha']).date()
        hora_inicio_dt = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        duracion_minutos = cancha.duracion_turno_minutos or 90
        hora_fin = (datetime.combine(fecha_dt, hora_inicio_dt) + timedelta(minutes=duracion_minutos)).time()
        from reservas.models import Turno, Reserva
        turno, created = Turno.objects.get_or_create(
            cancha=cancha,
            fecha=fecha_dt,
            hora_inicio=hora_inicio_dt,
            defaults={
                'hora_fin': hora_fin,
                'precio': data['precio'],
                'estado': 'RESERVADO'
            }
        )
        if hasattr(turno, 'reserva'):
            return JsonResponse({'success': False, 'message': 'Ya existe una reserva para este horario.'})
        Reserva.objects.create(
            turno=turno,
            tipo_reserva='BLOQUEADA',
            observaciones=f"Reserva de campeonato: {data['nombre_campeonato']}",
            precio=data['precio'],
            reservado_por_dueno=True,
            creado_por=request.user
        )
        return JsonResponse({'success': True, 'message': 'Reserva de campeonato creada correctamente.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'})


@login_required
def crear_reserva_simple_dashboard(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    try:
        data = json.loads(request.body.decode())
        perfil_dueno = request.user.perfil_dueno
        cancha = Cancha.objects.get(id=data['cancha_id'], complejo__dueno=perfil_dueno)
        from datetime import datetime, timedelta
        fecha_dt = datetime.fromisoformat(data['fecha']).date()
        hora_inicio_dt = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        duracion_minutos = cancha.duracion_turno_minutos or 90
        hora_fin = (datetime.combine(fecha_dt, hora_inicio_dt) + timedelta(minutes=duracion_minutos)).time()
        from reservas.models import Turno, Reserva
        # Verificar si ya existe una reserva simple para ese horario y cancha
        if Reserva.objects.filter(
            cancha=cancha,
            fecha=fecha_dt,
            hora_inicio=hora_inicio_dt
        ).exists():
            return JsonResponse({'success': False, 'message': 'Ya existe una reserva para este horario.'})
        # Verificar si hay una reserva fija activa y no liberada para ese turno
        from reservas.models import ReservaFija, ReservaFijaLiberacion
        dia_semana = fecha_dt.weekday()
        reservas_fijas = ReservaFija.objects.filter(
            cancha=cancha,
            dia_semana=dia_semana,
            estado='ACTIVA',
            hora_inicio=hora_inicio_dt
        )
        for rf in reservas_fijas:
            liberada = ReservaFijaLiberacion.objects.filter(reserva_fija=rf, fecha=fecha_dt).exists()
            if not liberada:
                return JsonResponse({'success': False, 'message': 'No se puede reservar: turno fijo activo no liberado.'})
        try:
            Reserva.objects.create(
                cancha=cancha,
                jugador_principal=None,  # O puedes mapear a un jugador si corresponde
                fecha=fecha_dt,
                hora_inicio=hora_inicio_dt,
                hora_fin=hora_fin,
                precio=data['precio'],
                estado='PENDIENTE',
                metodo_pago=None,
                pagado=False,
                observaciones='',
                nombre_cliente=data.get('nombre_cliente', ''),
            )
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error creando Reserva: {e}'})
        return JsonResponse({'success': True, 'message': 'Reserva simple creada correctamente.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'})


# Confirmar reserva desde dashboard: cambia estado a CONFIRMADA y marca como no pagada
@login_required
@require_POST
def confirmar(request, reserva_id):
    try:
        reserva = Reserva.objects.get(id=reserva_id)
    except Reserva.DoesNotExist:
        messages.error(request, 'Reserva no encontrada.')
        return redirect(reverse('complejos:gestionar_reservas'))

    # Verificar que el usuario sea dueño del complejo de la reserva
    try:
        if reserva.cancha.complejo.dueno != request.user.perfil_dueno:
            messages.error(request, 'No tienes permiso para confirmar esta reserva.')
            return redirect(reverse('complejos:gestionar_reservas'))
    except AttributeError:
        messages.error(request, 'Solo dueños pueden confirmar reservas.')
        return redirect(reverse('complejos:gestionar_reservas'))

    if reserva.estado == 'CONFIRMADA':
        messages.warning(request, 'La reserva ya estaba confirmada.')
    elif reserva.estado == 'CANCELADA':
        messages.error(request, 'No se puede confirmar una reserva cancelada.')
    else:
        reserva.estado = 'CONFIRMADA'
        reserva.pagado = False  # Confirmada pero no pagada
        reserva.save(update_fields=['estado', 'pagado'])
        messages.success(request, 'Reserva confirmada exitosamente. Ahora figura como pendiente de pago.')

    return redirect(reverse('complejos:gestionar_reservas'))