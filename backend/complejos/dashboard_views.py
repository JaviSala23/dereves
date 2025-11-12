"""
Vistas del dashboard para dueños de complejos.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
import json
from .models import Complejo, Cancha
from reservas.models import Reserva, ReservaFija
from cuentas.models import PerfilDueno
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
        messages.error(request, 'Acceso denegado.')
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


@login_required
def gestionar_reservas(request):
    """
    Vista para gestionar todas las reservas de los complejos del dueño.
    Incluye filtros por estado, fecha, complejo, etc.
    También muestra las reservas fijas activas.
    """
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Acceso denegado.')
        return redirect('home')
    
    perfil_dueno = PerfilDueno.objects.get(usuario=request.user)
    complejos = Complejo.objects.filter(dueno=perfil_dueno)
    
    # Obtener todas las reservas fijas activas
    reservas_fijas_activas = ReservaFija.objects.filter(
        cancha__complejo__in=complejos,
        estado='ACTIVA'
    ).select_related(
        'cancha', 'cancha__complejo', 'jugador', 'jugador__usuario'
    ).order_by('cancha__complejo__nombre', 'cancha__nombre', 'dia_semana', 'hora_inicio')
    
    # Obtener todas las reservas de los complejos del dueño
    reservas = Reserva.objects.filter(
        cancha__complejo__in=complejos
    ).select_related(
        'cancha', 'cancha__complejo', 'jugador_principal', 'metodo_pago'
    ).order_by('-fecha', '-hora_inicio')
    
    # Aplicar filtros
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
    
    # Estadísticas de las reservas filtradas
    total_reservas = reservas.count()
    reservas_pendientes = reservas.filter(estado='PENDIENTE').count()
    reservas_confirmadas = reservas.filter(estado='CONFIRMADA').count()
    total_ingresos = reservas.filter(estado='CONFIRMADA', pagado=True).aggregate(
        total=Sum('precio')
    )['total'] or 0
    
    # Obtener jugadores para el modal de crear reserva fija
    from cuentas.models import PerfilJugador
    jugadores = PerfilJugador.objects.filter(usuario__is_active=True).select_related('usuario').order_by('usuario__first_name')
    
    # Obtener canchas del dueño para el modal
    canchas = Cancha.objects.filter(complejo__in=complejos, activo=True).select_related('complejo')
    
    context = {
        'reservas': reservas[:100],  # Limitar a 100 para performance
        'complejos': complejos,
        'reservas_fijas_activas': reservas_fijas_activas,
        'jugadores': jugadores,
        'canchas': canchas,
        'total_reservas': total_reservas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_confirmadas': reservas_confirmadas,
        'total_ingresos': total_ingresos,
        # Filtros actuales
        'estado_filtro': estado_filtro,
        'complejo_filtro': complejo_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'pagado_filtro': pagado_filtro,
        'estados': Reserva.ESTADO_CHOICES,
    }
    
    return render(request, 'complejos/dashboard/gestionar_reservas.html', context)


@login_required
def estadisticas_complejo(request, slug):
    """
    Estadísticas detalladas de un complejo específico.
    """
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Acceso denegado.')
        return redirect('home')
    
    perfil_dueno = PerfilDueno.objects.get(usuario=request.user)
    complejo = Complejo.objects.filter(slug=slug, dueno=perfil_dueno).first()
    
    if not complejo:
        messages.error(request, 'Complejo no encontrado.')
        return redirect('complejos:dashboard_principal')
    
    # Rango de fechas
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    
    # Canchas del complejo
    canchas = complejo.canchas.all()
    
    # Reservas del mes
    reservas_mes = Reserva.objects.filter(
        cancha__complejo=complejo,
        fecha__gte=hace_30_dias
    )
    
    # Estadísticas por cancha
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
    
    # Ingresos totales
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
        reserva_fija = ReservaFija.objects.create(
            cancha=cancha,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            fecha_inicio=timezone.now().date(),
            nombre_cliente=nombre_cliente,
            telefono_cliente=telefono_cliente,
            precio=precio,
            creada_por=perfil_dueno
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
            tipo_reserva='ADMINISTRATIVA',
            nombre_cliente_sin_cuenta=data.get('nombre_cliente', ''),
            telefono_cliente=data.get('telefono_cliente', ''),
            precio=data['precio'],
            reservado_por_dueno=True,
            creado_por=request.user
        )
        return JsonResponse({'success': True, 'message': 'Reserva simple creada correctamente.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'})
