from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Reserva, MetodoPago, ReservaFija
from complejos.models import Cancha, Complejo


@login_required
def mis_reservas(request):
    """Vista de las reservas del usuario."""
    # Verificar que el usuario sea jugador
    if request.user.tipo_usuario != 'JUGADOR':
        messages.error(request, 'Necesitas un perfil de jugador para ver tus reservas.')
        return redirect('home')
    
    try:
        perfil_jugador = request.user.perfil_jugador
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de jugador.')
        return redirect('home')
    
    # Reservas comunes
    reservas = Reserva.objects.filter(
        jugador_principal=perfil_jugador
    ).select_related('cancha', 'cancha__complejo').order_by('-fecha', '-hora_inicio')
    
    # Reservas fijas
    reservas_fijas = ReservaFija.objects.filter(
        jugador=perfil_jugador
    ).select_related('cancha', 'cancha__complejo').order_by('dia_semana', 'hora_inicio')
    
    # Separar en activas y pasadas
    ahora = timezone.now()
    reservas_activas = []
    reservas_pasadas = []
    
    for reserva in reservas:
        # Combinar fecha y hora para comparar
        fecha_hora_reserva = datetime.combine(reserva.fecha, reserva.hora_inicio)
        if fecha_hora_reserva >= ahora.date() and reserva.estado != 'CANCELADA':
            reservas_activas.append(reserva)
        else:
            reservas_pasadas.append(reserva)
    
    context = {
        'reservas_activas': reservas_activas,
        'reservas_pasadas': reservas_pasadas,
        'reservas_fijas': reservas_fijas,
    }
    return render(request, 'reservas/mis_reservas.html', context)


@login_required
def calendario_cancha(request, cancha_id):
    """Calendario de disponibilidad de una cancha."""
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    # Obtener fecha desde parámetros o usar hoy
    fecha_str = request.GET.get('fecha', timezone.now().date().isoformat())
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except ValueError:
        fecha = timezone.now().date()
    
    # Obtener reservas de ese día
    reservas_dia = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).values_list('hora_inicio', 'hora_fin')
    
    # Convertir a lista para facilitar comparación
    reservas_list = list(reservas_dia)
    
    # Crear lista de horarios disponibles
    horarios = []
    hora_actual = cancha.horario_apertura
    duracion = timedelta(minutes=cancha.duracion_turno_minutos)
    
    while hora_actual < cancha.horario_cierre:
        hora_fin = (datetime.combine(fecha, hora_actual) + duracion).time()
        
        # No agregar si excede el horario de cierre
        if hora_fin > cancha.horario_cierre:
            break
        
        # Verificar si hay conflicto con alguna reserva existente
        ocupado = False
        for reserva_inicio, reserva_fin in reservas_list:
            # Hay solapamiento si el turno se cruza con una reserva
            if (hora_actual < reserva_fin and hora_fin > reserva_inicio):
                ocupado = True
                break
        
        # Si es hoy, no mostrar horarios pasados
        es_hoy = fecha == timezone.now().date()
        hora_pasada = es_hoy and hora_actual < timezone.now().time()
        
        if not hora_pasada:
            horarios.append({
                'hora': hora_actual.strftime('%H:%M'),
                'hora_fin': hora_fin.strftime('%H:%M'),
                'ocupado': ocupado,
                'precio': cancha.precio_hora,
            })
        
        # Avanzar según duración del turno
        hora_actual = (datetime.combine(fecha, hora_actual) + duracion).time()
        
        # Evitar loop infinito si hora_actual pasa horario_cierre
        if hora_actual <= (datetime.combine(fecha, hora_actual) - duracion).time():
            break
    
    context = {
        'cancha': cancha,
        'fecha': fecha,
        'fecha_anterior': fecha - timedelta(days=1),
        'fecha_siguiente': fecha + timedelta(days=1),
        'horarios': horarios,
    }
    return render(request, 'reservas/calendario.html', context)


@login_required
def crear_reserva(request, cancha_id):
    """Crear una nueva reserva común."""
    if request.method != 'POST':
        return redirect('reservas:calendario_cancha', cancha_id=cancha_id)
    
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    # Los dueños y jugadores pueden reservar
    perfil_jugador = None
    
    if request.user.tipo_usuario == 'JUGADOR':
        try:
            perfil_jugador = request.user.perfil_jugador
        except AttributeError:
            messages.error(request, 'No se encontró tu perfil de jugador.')
            return redirect('complejos:detalle', slug=cancha.complejo.slug)
    
    elif request.user.tipo_usuario == 'DUENIO':
        # Los dueños pueden reservar, pero deben tener un perfil de jugador también
        # Si no lo tienen, podemos crear la reserva a nombre del dueño como jugador
        try:
            perfil_jugador = request.user.perfil_jugador
        except AttributeError:
            # Si el dueño no tiene perfil de jugador, usamos el primero disponible o creamos uno
            from cuentas.models import PerfilJugador
            perfil_jugador, created = PerfilJugador.objects.get_or_create(
                usuario=request.user,
                defaults={
                    'alias': request.user.get_full_name() or request.user.email.split('@')[0],
                    'nivel': 'INTERMEDIO'
                }
            )
    
    else:
        messages.error(request, 'Necesitas ser jugador o dueño para hacer reservas.')
        return redirect('complejos:detalle', slug=cancha.complejo.slug)
    
    # Obtener datos del formulario
    fecha_str = request.POST.get('fecha')
    hora_str = request.POST.get('hora')
    metodo_pago_id = request.POST.get('metodo_pago')
    
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
        hora_inicio = datetime.strptime(hora_str, '%H:%M').time()
        hora_fin = (datetime.combine(fecha, hora_inicio) + timedelta(minutes=cancha.duracion_turno_minutos)).time()
    except (ValueError, TypeError):
        messages.error(request, 'Fecha u hora inválida.')
        return redirect('reservas:calendario_cancha', cancha_id=cancha_id)
    
    # Validar que no sea una fecha/hora pasada
    ahora = timezone.now()
    fecha_hora_reserva = timezone.make_aware(datetime.combine(fecha, hora_inicio))
    
    if fecha_hora_reserva <= ahora:
        messages.error(request, 'No puedes reservar en fechas u horas pasadas.')
        return redirect('reservas:calendario_cancha', cancha_id=cancha_id)
    
    # Obtener método de pago
    metodo_pago = None
    if metodo_pago_id:
        metodo_pago = MetodoPago.objects.filter(id=metodo_pago_id).first()
    
    # Verificar conflictos con reservas normales
    conflicto_reserva = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha,
        hora_inicio__lt=hora_fin,
        hora_fin__gt=hora_inicio,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).exists()
    
    # Verificar conflictos con reservas fijas activas
    dia_semana = fecha.weekday()
    conflicto_fija = ReservaFija.objects.filter(
        cancha=cancha,
        dia_semana=dia_semana,
        hora_inicio__lt=hora_fin,
        hora_fin__gt=hora_inicio,
        estado='ACTIVA',
        fecha_inicio__lte=fecha
    ).exists()
    
    if conflicto_reserva or conflicto_fija:
        messages.error(request, 'Este horario ya está reservado.')
        return redirect('complejos:lista')
    
    # Crear la reserva
    reserva = Reserva.objects.create(
        cancha=cancha,
        jugador_principal=perfil_jugador,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        precio=cancha.precio_hora,
        metodo_pago=metodo_pago,
        estado='PENDIENTE'
    )
    
    messages.success(request, f'Reserva creada exitosamente. Total: ${reserva.precio}')
    return redirect('complejos:lista')


@login_required
def detalle_reserva(request, reserva_id):
    """Detalle de una reserva específica."""
    reserva = get_object_or_404(
        Reserva.objects.select_related('cancha', 'cancha__complejo', 'jugador_principal__usuario'),
        id=reserva_id
    )
    
    # Verificar que sea del usuario o del dueño del complejo
    es_dueno = False
    if request.user.tipo_usuario == 'DUENIO':
        try:
            es_dueno = reserva.cancha.complejo.dueno == request.user.perfil_dueno
        except AttributeError:
            pass
    
    if reserva.jugador_principal.usuario != request.user and not es_dueno and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver esta reserva.')
        return redirect('home')
    
    context = {
        'reserva': reserva,
        'es_dueno': es_dueno,
    }
    return render(request, 'reservas/detalle_reserva.html', context)


@login_required
def cancelar_reserva(request, reserva_id):
    """Cancelar una reserva."""
    if request.method != 'POST':
        return redirect('reservas:mis_reservas')
    
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que sea el jugador que hizo la reserva
    if reserva.jugador_principal.usuario != request.user:
        messages.error(request, 'No tienes permiso para cancelar esta reserva.')
        return redirect('reservas:mis_reservas')
    
    # Verificar que pueda cancelarse
    if reserva.estado == 'CANCELADA':
        messages.warning(request, 'Esta reserva ya está cancelada.')
    elif reserva.estado == 'COMPLETADA':
        messages.error(request, 'No se puede cancelar una reserva completada.')
    else:
        reserva.estado = 'CANCELADA'
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente.')
    
    return redirect('reservas:mis_reservas')


@login_required
def cancelar_reserva_fija(request, reserva_fija_id):
    """Cancelar una reserva fija (jugador o dueño)."""
    if request.method != 'POST':
        return redirect('reservas:mis_reservas')
    
    reserva_fija = get_object_or_404(ReservaFija, id=reserva_fija_id)
    
    # Verificar que sea el jugador o el dueño del complejo
    es_jugador = reserva_fija.jugador.usuario == request.user
    es_dueno = False
    
    if request.user.tipo_usuario == 'DUENIO':
        try:
            es_dueno = reserva_fija.cancha.complejo.dueno == request.user.perfil_dueno
        except AttributeError:
            pass
    
    if not es_jugador and not es_dueno:
        messages.error(request, 'No tienes permiso para cancelar esta reserva fija.')
        return redirect('reservas:mis_reservas')
    
    # Cancelar la reserva fija
    reserva_fija.estado = 'CANCELADA'
    reserva_fija.save()
    
    actor = 'el dueño' if es_dueno else 'el jugador'
    messages.success(request, f'Reserva fija cancelada por {actor}.')
    
    if es_dueno:
        return redirect('complejos:gestionar_reservas')
    else:
        return redirect('reservas:mis_reservas')


@login_required
def crear_reserva_fija(request, cancha_id):
    """Crear una reserva fija (solo dueños)."""
    if request.method != 'POST':
        return redirect('complejos:gestionar_reservas')
    
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    # Verificar que sea el dueño del complejo
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Solo los dueños pueden crear reservas fijas.')
        return redirect('home')
    
    try:
        perfil_dueno = request.user.perfil_dueno
        if cancha.complejo.dueno != perfil_dueno:
            messages.error(request, 'No tienes permiso para crear reservas fijas en este complejo.')
            return redirect('complejos:gestionar_reservas')
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de dueño.')
        return redirect('home')
    
    # Obtener datos del formulario
    jugador_id = request.POST.get('jugador_id')
    dia_semana = int(request.POST.get('dia_semana'))
    hora_inicio_str = request.POST.get('hora_inicio')
    fecha_inicio_str = request.POST.get('fecha_inicio')
    observaciones = request.POST.get('observaciones', '')
    
    try:
        from cuentas.models import PerfilJugador
        jugador = PerfilJugador.objects.get(id=jugador_id)
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = (datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=cancha.duracion_turno_minutos)).time()
        fecha_inicio = datetime.fromisoformat(fecha_inicio_str).date()
    except (ValueError, TypeError, PerfilJugador.DoesNotExist) as e:
        messages.error(request, f'Datos inválidos: {str(e)}')
        return redirect('complejos:gestionar_reservas')
    
    # Verificar si ya existe una reserva fija para ese horario
    existe_fija = ReservaFija.objects.filter(
        cancha=cancha,
        dia_semana=dia_semana,
        hora_inicio=hora_inicio,
        estado='ACTIVA'
    ).exists()
    
    if existe_fija:
        messages.error(request, 'Ya existe una reserva fija activa para este horario.')
        return redirect('complejos:gestionar_reservas')
    
    # Crear la reserva fija
    reserva_fija = ReservaFija.objects.create(
        cancha=cancha,
        jugador=jugador,
        dia_semana=dia_semana,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        fecha_inicio=fecha_inicio,
        precio=cancha.precio_hora,
        estado='ACTIVA',
        observaciones=observaciones,
        creada_por=perfil_dueno
    )
    
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    messages.success(
        request, 
        f'Reserva fija creada: {dias[dia_semana]}s {hora_inicio_str} para {jugador.usuario.get_full_name()}'
    )
    return redirect('complejos:gestionar_reservas')


@login_required
def editar_reserva_fija(request, reserva_fija_id):
    """Editar una reserva fija (solo dueños)."""
    if request.method != 'POST':
        return redirect('complejos:gestionar_reservas')
    
    reserva_fija = get_object_or_404(ReservaFija, id=reserva_fija_id)
    
    # Verificar que sea el dueño del complejo
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Solo los dueños pueden editar reservas fijas.')
        return redirect('home')
    
    try:
        perfil_dueno = request.user.perfil_dueno
        if reserva_fija.cancha.complejo.dueno != perfil_dueno:
            messages.error(request, 'No tienes permiso para editar esta reserva fija.')
            return redirect('complejos:gestionar_reservas')
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de dueño.')
        return redirect('home')
    
    # Obtener nuevos datos
    jugador_id = request.POST.get('jugador_id')
    observaciones = request.POST.get('observaciones', '')
    
    try:
        from cuentas.models import PerfilJugador
        jugador = PerfilJugador.objects.get(id=jugador_id)
        
        reserva_fija.jugador = jugador
        reserva_fija.observaciones = observaciones
        reserva_fija.save()
        
        messages.success(request, 'Reserva fija actualizada exitosamente.')
    except PerfilJugador.DoesNotExist:
        messages.error(request, 'Jugador no encontrado.')
    
    return redirect('complejos:gestionar_reservas')


@login_required
def aprobar_reserva_fija(request, reserva_fija_id):
    """Esta vista ya no se usa - las reservas fijas se crean directamente activas."""
    return redirect('complejos:gestionar_reservas')


@login_required
def rechazar_reserva_fija(request, reserva_fija_id):
    """Esta vista ya no se usa - las reservas fijas se crean directamente activas."""
    return redirect('complejos:gestionar_reservas')


@login_required
def confirmar_reserva(request, reserva_id):
    """Confirmar pago de una reserva (solo dueños)."""
    if request.method != 'POST':
        return redirect('reservas:detalle_reserva', reserva_id=reserva_id)
    
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que sea el dueño
    if reserva.cancha.complejo.dueno != request.user:
        messages.error(request, 'No tienes permiso para confirmar esta reserva.')
        return redirect('home')
    
    if reserva.estado == 'PENDIENTE':
        reserva.estado = 'CONFIRMADA'
        reserva.save()
        messages.success(request, 'Reserva confirmada exitosamente.')
    
    return redirect('reservas:detalle_reserva', reserva_id=reserva_id)

