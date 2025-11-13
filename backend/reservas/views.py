
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, time
from .models import ReservaFijaLiberacion
from .models import (
    Turno, Reserva, MetodoPago, ReservaFija, 
    PartidoAbierto, JugadorPartido, Torneo, BloqueoTorneo
)
from django.db import models
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
    
    # Reservas comunes (a través del nuevo modelo Turno)
    reservas = Reserva.objects.filter(
        jugador=perfil_jugador
    ).select_related(
        'turno__cancha__complejo'
    ).order_by('-turno__fecha', '-turno__hora_inicio')
    
    # Reservas fijas
    reservas_fijas = ReservaFija.objects.filter(
        jugador=perfil_jugador
    ).select_related('cancha', 'cancha__complejo').order_by('dia_semana', 'hora_inicio')
    
    # Partidos abiertos donde participa
    partidos = JugadorPartido.objects.filter(
        jugador=perfil_jugador,
        confirmado=True
    ).select_related(
        'partido__turno__cancha__complejo'
    ).order_by('-partido__creado_en')
    
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
        'partidos': partidos,
    }
    return render(request, 'reservas/mis_reservas.html', context)


@login_required
def calendario_cancha(request, cancha_id):
    """Calendario de disponibilidad de una cancha con sistema de Turnos."""
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    # Verificar si el usuario es dueño del complejo
    es_dueno = False
    if request.user.is_authenticated and request.user.tipo_usuario == 'DUENIO':
        try:
            perfil_dueno = request.user.perfil_dueno
            es_dueno = cancha.complejo.dueno == perfil_dueno
        except AttributeError:
            pass
    
    # Obtener fecha desde parámetros o usar hoy
    fecha_str = request.GET.get('fecha', timezone.now().date().isoformat())
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except ValueError:
        fecha = timezone.now().date()
    
    # Verificar que la cancha tenga horarios configurados
    if not cancha.horario_apertura or not cancha.horario_cierre:
        messages.error(request, 'Esta cancha no tiene horarios configurados.')
        return redirect('complejos:detalle', slug=cancha.complejo.slug)
    
    # Obtener turnos de ese día
    turnos = Turno.objects.filter(
        cancha=cancha,
        fecha=fecha
    ).order_by('hora_inicio')
    
    # Crear dict de turnos existentes por hora
    turnos_dict = {
        turno.hora_inicio: turno
        for turno in turnos
    }
    
    # Crear lista de horarios con su estado
    horarios = []
    hora_actual = cancha.horario_apertura
    duracion = timedelta(minutes=cancha.duracion_turno_minutos or 90)  # Default 90 minutos
    
    while hora_actual < cancha.horario_cierre:
        hora_fin = (datetime.combine(fecha, hora_actual) + duracion).time()
        
        # No agregar si excede el horario de cierre
        if hora_fin > cancha.horario_cierre:
            break
        
        # Si es hoy, no mostrar horarios pasados
        es_hoy = fecha == timezone.now().date()
        hora_pasada = es_hoy and hora_actual < timezone.now().time()
        
        if not hora_pasada:
            turno = turnos_dict.get(hora_actual)
            
            if turno:
                # Turno existe, obtener su estado
                # El dueño puede seleccionar cualquier turno, jugadores solo DISPONIBLE
                disponible = turno.estado == 'DISPONIBLE' or es_dueno
                
                horarios.append({
                    'hora': hora_actual.strftime('%H:%M'),
                    'hora_fin': hora_fin.strftime('%H:%M'),
                    'estado': turno.estado,
                    'disponible': disponible,
                    'precio': turno.precio,
                    'turno_id': turno.id,
                })
            else:
                # Turno no existe, asumir disponible (tanto para dueño como jugador)
                horarios.append({
                    'hora': hora_actual.strftime('%H:%M'),
                    'hora_fin': hora_fin.strftime('%H:%M'),
                    'estado': 'DISPONIBLE',
                    'disponible': True,
                    'precio': cancha.precio_hora,
                    'turno_id': None,
                })
        
        # Avanzar según duración del turno
        hora_actual = (datetime.combine(fecha, hora_actual) + duracion).time()
        
        # Evitar loop infinito
        if hora_actual <= (datetime.combine(fecha, hora_actual) - duracion).time():
            break
    
    context = {
        'cancha': cancha,
        'fecha': fecha,
        'fecha_anterior': fecha - timedelta(days=1),
        'fecha_siguiente': fecha + timedelta(days=1),
        'horarios': horarios,
        'es_dueno': es_dueno,
    }
    return render(request, 'reservas/calendario.html', context)


@login_required
def crear_reserva(request, cancha_id):
    """Crear una nueva reserva usando el sistema de Turnos."""
    if request.method != 'POST':
        return redirect('reservas:calendario_cancha', cancha_id=cancha_id)
    
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    # Verificar permisos
    perfil_jugador = None
    es_dueno = False
    
    if request.user.tipo_usuario == 'JUGADOR':
        try:
            perfil_jugador = request.user.perfil_jugador
        except AttributeError:
            messages.error(request, 'No se encontró tu perfil de jugador.')
            return redirect('complejos:detalle', slug=cancha.complejo.slug)
    
    elif request.user.tipo_usuario == 'DUENIO':
        try:
            perfil_dueno = request.user.perfil_dueno
            es_dueno = cancha.complejo.dueno == perfil_dueno
            if not es_dueno:
                messages.error(request, 'Solo puedes crear reservas en tus propios complejos.')
                return redirect('complejos:lista')
        except AttributeError:
            messages.error(request, 'No se encontró tu perfil de dueño.')
            return redirect('home')
    else:
        messages.error(request, 'Necesitas ser jugador o dueño para hacer reservas.')
        return redirect('complejos:detalle', slug=cancha.complejo.slug)
    
    # Obtener datos del formulario
    fecha_str = request.POST.get('fecha')
    hora_str = request.POST.get('hora')
    metodo_pago_id = request.POST.get('metodo_pago')
    
    # Si es dueño, puede reservar para cliente sin cuenta
    reservado_por_dueno = es_dueno
    nombre_cliente = request.POST.get('nombre_cliente', '') if es_dueno else ''
    telefono_cliente = request.POST.get('telefono_cliente', '') if es_dueno else ''
    email_cliente = request.POST.get('email_cliente', '') if es_dueno else ''
    
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
    
    # Buscar o crear el Turno
    turno, created = Turno.objects.get_or_create(
        cancha=cancha,
        fecha=fecha,
        hora_inicio=hora_inicio,
        defaults={
            'hora_fin': hora_fin,
            'precio': cancha.precio_hora,
            'estado': 'DISPONIBLE'
        }
    )
    
    # Verificar que el turno esté disponible
    if not es_dueno:
        # Jugadores solo pueden reservar turnos disponibles
        if not turno.puede_ser_reservado_por_jugador():
            messages.error(request, f'Este turno no está disponible. Estado: {turno.get_estado_display()}')
            return redirect('reservas:calendario_cancha', cancha_id=cancha_id)
    else:
        # Dueños pueden reservar sobre turnos disponibles
        if turno.estado != 'DISPONIBLE':
            messages.error(request, f'Este turno ya está ocupado. Estado: {turno.get_estado_display()}')
            return redirect('reservas:calendario_cancha', cancha_id=cancha_id)
    
    # Crear la reserva
    reserva = Reserva.objects.create(
        turno=turno,
        tipo_reserva='CLIENTE',  # Reservas desde calendario de jugadores son siempre de cliente
        jugador=perfil_jugador if not es_dueno else None,
        reservado_por_dueno=reservado_por_dueno,
        nombre_cliente_sin_cuenta=nombre_cliente,
        telefono_cliente=telefono_cliente,
        email_cliente=email_cliente,
        precio=turno.precio,
        metodo_pago=metodo_pago,
        estado='CONFIRMADA' if es_dueno else 'PENDIENTE',
        creado_por=request.user
    )
    
    # Actualizar estado del turno
    turno.estado = 'RESERVADO'
    turno.save()
    
    if es_dueno:
        cliente_info = nombre_cliente or 'Cliente'
        messages.success(request, f'Reserva creada para {cliente_info}. Total: ${reserva.precio}')
    else:
        messages.success(request, f'Reserva creada exitosamente. Total: ${reserva.precio}')
    
    return redirect('reservas:mis_reservas') if not es_dueno else redirect('complejos:gestionar', slug=cancha.complejo.slug)


@login_required
def detalle_reserva(request, reserva_id):
    """Detalle de una reserva específica."""
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    from django.http import JsonResponse
    from django.utils import timezone
    from django.db.models import Q
    from datetime import datetime, timedelta, time
    from .models import ReservaFija, ReservaFijaLiberacion, Turno
    from .models import Reserva, MetodoPago, PartidoAbierto, JugadorPartido, Torneo, BloqueoTorneo
    from django.db import models
    from complejos.models import Cancha, Complejo
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que sea del usuario o del dueño del complejo
    es_dueno = False
    if request.user.tipo_usuario == 'DUENIO':
        try:
            es_dueno = reserva.cancha.complejo.dueno == request.user.perfil_dueno
        except AttributeError:
            pass
    
    es_propietario = (
        (reserva.jugador and reserva.jugador.usuario == request.user) or
        es_dueno or 
        request.user.is_staff
    )
    
    if not es_propietario:
        messages.error(request, 'No tienes permiso para ver esta reserva.')
        return redirect('home')
    
    context = {
        'reserva': reserva,
        'es_dueno': es_dueno,
    }
    return render(request, 'reservas/detalle_reserva.html', context)


@login_required
def cancelar_reserva(request, reserva_id):
    """Cancelar una reserva usando el nuevo sistema."""
    if request.method != 'POST':
        return redirect('reservas:mis_reservas')
    
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar permisos
    es_dueno = False
    if request.user.tipo_usuario == 'DUENIO':
        try:
            es_dueno = reserva.cancha.complejo.dueno == request.user.perfil_dueno
        except AttributeError:
            pass
    
    es_propietario = (getattr(reserva, 'jugador_principal', None) and reserva.jugador_principal.usuario == request.user) or es_dueno
    
    if not es_propietario:
        messages.error(request, 'No tienes permiso para cancelar esta reserva.')
        return redirect('reservas:mis_reservas')
    
    # Eliminar la reserva directamente
    reserva.delete()
    messages.success(request, 'Reserva eliminada exitosamente.')
    return redirect('reservas:gestionar_reservas')


@login_required
def cancelar_reserva_fija(request, reserva_fija_id):
    """Cancelar/pausar una reserva fija (jugador o dueño)."""
    if request.method != 'POST':
        return redirect('reservas:mis_reservas')
    
    reserva_fija = get_object_or_404(ReservaFija, id=reserva_fija_id)
    
    # Verificar que sea el jugador o el dueño del complejo
    es_jugador = reserva_fija.jugador and reserva_fija.jugador.usuario == request.user
    es_dueno = False
    
    if request.user.tipo_usuario == 'DUENIO':
        try:
            es_dueno = reserva_fija.cancha.complejo.dueno == request.user.perfil_dueno
        except AttributeError:
            pass
    
    if not es_jugador and not es_dueno:
        messages.error(request, 'No tienes permiso para cancelar esta reserva fija.')
        return redirect('reservas:mis_reservas')
    
    # Opción de pausar o cancelar definitivamente
    accion = request.POST.get('accion', 'PAUSADA')
    
    if accion == 'CANCELADA':
        reserva_fija.estado = 'CANCELADA'
        mensaje = 'cancelada'
    else:
        reserva_fija.estado = 'PAUSADA'
        mensaje = 'pausada'
    
    reserva_fija.save()
    
    actor = 'el dueño' if es_dueno else 'el jugador'
    messages.success(request, f'Reserva fija {mensaje} por {actor}.')
    
    if es_dueno:
        return redirect('complejos:gestionar', slug=reserva_fija.cancha.complejo.slug)
    else:
        return redirect('reservas:mis_reservas')


@login_required
def crear_reserva_fija(request, cancha_id):
    """Crear una reserva fija (solo dueños) con auto-bloqueo de turnos."""
    if request.method != 'POST':
        return redirect('complejos:gestionar', slug=request.POST.get('slug', ''))
    
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    # Verificar que sea el dueño del complejo
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Solo los dueños pueden crear reservas fijas.')
        return redirect('home')
    
    try:
        perfil_dueno = request.user.perfil_dueno
        if cancha.complejo.dueno != perfil_dueno:
            messages.error(request, 'No tienes permiso para crear reservas fijas en este complejo.')
            return redirect('complejos:gestionar', slug=cancha.complejo.slug)
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de dueño.')
        return redirect('home')
    
    # Obtener datos del formulario
    jugador_id = request.POST.get('jugador_id')
    nombre_cliente = request.POST.get('nombre_cliente', '')
    dia_semana = int(request.POST.get('dia_semana'))
    hora_inicio_str = request.POST.get('hora_inicio')
    fecha_inicio_str = request.POST.get('fecha_inicio')
    fecha_fin_str = request.POST.get('fecha_fin', '')
    observaciones = request.POST.get('observaciones', '')
    
    try:
        from cuentas.models import PerfilJugador
        
        jugador = None
        if jugador_id:
            jugador = PerfilJugador.objects.get(id=jugador_id)
        
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = (datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=cancha.duracion_turno_minutos)).time()
        fecha_inicio = datetime.fromisoformat(fecha_inicio_str).date()
        
        fecha_fin = None
        if fecha_fin_str:
            fecha_fin = datetime.fromisoformat(fecha_fin_str).date()
        
    except (ValueError, TypeError, PerfilJugador.DoesNotExist) as e:
        messages.error(request, f'Datos inválidos: {str(e)}')
        return redirect('complejos:gestionar', slug=cancha.complejo.slug)
    
    # Verificar si ya existe una reserva fija para ese horario
    existe_fija = ReservaFija.objects.filter(
        cancha=cancha,
        dia_semana=dia_semana,
        hora_inicio=hora_inicio,
        estado='ACTIVA'
    ).exists()
    
    if existe_fija:
        messages.error(request, 'Ya existe una reserva fija activa para este horario.')
        return redirect('complejos:gestionar', slug=cancha.complejo.slug)
    
    # Crear la reserva fija
    reserva_fija = ReservaFija.objects.create(
        cancha=cancha,
        jugador=jugador,
        nombre_cliente=nombre_cliente,
        dia_semana=dia_semana,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        precio=cancha.precio_hora,
        estado='ACTIVA',
        observaciones=observaciones,
        creada_por=perfil_dueno
    )
    
    # Bloquear turnos futuros automáticamente (próximos 3 meses)
    hasta_fecha = fecha_inicio + timedelta(days=90)
    if fecha_fin and fecha_fin < hasta_fecha:
        hasta_fecha = fecha_fin
    
    turnos_bloqueados = reserva_fija.bloquear_turnos_futuros(hasta_fecha)
    
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Determinar nombre para el mensaje
    if jugador:
        cliente_nombre = jugador.alias
    elif nombre_cliente:
        cliente_nombre = nombre_cliente
    else:
        cliente_nombre = "Reserva administrativa"
    
    messages.success(
        request, 
        f'Reserva fija creada: {dias[dia_semana]}s {hora_inicio_str} para {cliente_nombre}. Se bloquearon {len(turnos_bloqueados)} turnos.'
    )
    return redirect('complejos:gestionar', slug=cancha.complejo.slug)


@login_required
def editar_reserva_fija(request, reserva_fija_id):
    """Editar una reserva fija (solo dueños)."""
    if request.method != 'POST':
        return redirect('complejos:gestionar', slug=request.POST.get('slug', ''))
    
    reserva_fija = get_object_or_404(ReservaFija, id=reserva_fija_id)
    
    # Verificar que sea el dueño del complejo
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Solo los dueños pueden editar reservas fijas.')
        return redirect('home')
    
    try:
        perfil_dueno = request.user.perfil_dueno
        if reserva_fija.cancha.complejo.dueno != perfil_dueno:
            messages.error(request, 'No tienes permiso para editar esta reserva fija.')
            return redirect('complejos:gestionar', slug=reserva_fija.cancha.complejo.slug)
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de dueño.')
        return redirect('home')
    
    # Obtener nuevos datos
    jugador_id = request.POST.get('jugador_id')
    nombre_cliente = request.POST.get('nombre_cliente', '')
    observaciones = request.POST.get('observaciones', '')
    
    try:
        from cuentas.models import PerfilJugador
        
        if jugador_id:
            jugador = PerfilJugador.objects.get(id=jugador_id)
            reserva_fija.jugador = jugador
            reserva_fija.nombre_cliente = ''
        else:
            reserva_fija.jugador = None
            reserva_fija.nombre_cliente = nombre_cliente
        
        reserva_fija.observaciones = observaciones
        reserva_fija.save()
        
        messages.success(request, 'Reserva fija actualizada exitosamente.')
    except PerfilJugador.DoesNotExist:
        messages.error(request, 'Jugador no encontrado.')
    
    return redirect('complejos:gestionar', slug=reserva_fija.cancha.complejo.slug)


# ============= NUEVAS VISTAS PARA PARTIDOS ABIERTOS =============

@login_required
def crear_partido_abierto(request, turno_id):
    """Crear un partido abierto sobre un turno disponible."""
    if request.method != 'POST':
        return redirect('home')
    
    turno = get_object_or_404(Turno, id=turno_id)
    
    # Verificar que el turno esté disponible
    if turno.estado != 'DISPONIBLE':
        messages.error(request, f'Este turno no está disponible. Estado: {turno.get_estado_display()}')
        return redirect('reservas:calendario_cancha', cancha_id=turno.cancha.id)
    
    # Obtener datos
    cupo_jugadores = int(request.POST.get('cupo_jugadores', 4))
    nivel = request.POST.get('nivel', 'MIXTO')
    categoria = request.POST.get('categoria', '')
    descripcion = request.POST.get('descripcion', '')
    
    # Verificar si es dueño
    creado_por_dueno = False
    if request.user.tipo_usuario == 'DUENIO':
        try:
            creado_por_dueno = turno.cancha.complejo.dueno == request.user.perfil_dueno
        except AttributeError:
            messages.error(request, 'No tienes permiso para crear partidos aquí.')
            return redirect('home')
    elif request.user.tipo_usuario != 'JUGADOR':
        messages.error(request, 'Solo jugadores y dueños pueden crear partidos abiertos.')
        return redirect('home')
    
    # Crear el partido abierto
    partido = PartidoAbierto.objects.create(
        turno=turno,
        creador=request.user,
        creado_por_dueno=creado_por_dueno,
        cupo_jugadores=cupo_jugadores,
        nivel=nivel,
        categoria=categoria,
        descripcion=descripcion,
        precio_por_jugador=turno.precio / cupo_jugadores,
        estado='ABIERTO'
    )
    
    # Agregar al creador como primer jugador
    if request.user.tipo_usuario == 'JUGADOR':
        try:
            JugadorPartido.objects.create(
                partido=partido,
                jugador=request.user.perfil_jugador,
                confirmado=True,
                es_creador=True
            )
        except AttributeError:
            pass
    
    messages.success(request, f'Partido abierto creado! Link: {partido.get_link_invitacion()}')
    return redirect('reservas:detalle_partido', partido_id=partido.id)


@login_required
def detalle_partido(request, partido_id):
    """Ver detalle de un partido abierto."""
    partido = get_object_or_404(
        PartidoAbierto.objects.select_related(
            'turno__cancha__complejo',
            'creador'
        ).prefetch_related('jugadores__jugador__usuario'),
        id=partido_id
    )
    
    # Verificar si el usuario ya está en el partido
    ya_participa = False
    if request.user.tipo_usuario == 'JUGADOR':
        try:
            ya_participa = partido.jugadores.filter(
                jugador=request.user.perfil_jugador
            ).exists()
        except AttributeError:
            pass
    
    context = {
        'partido': partido,
        'ya_participa': ya_participa,
        'link_invitacion': partido.get_link_invitacion(),
    }
    return render(request, 'reservas/detalle_partido.html', context)


def unirse_partido(request, token):
    """Unirse a un partido abierto mediante link de invitación (público)."""
    partido = get_object_or_404(PartidoAbierto, token_invitacion=token)
    
    if not partido.puede_sumarse():
        messages.error(request, 'Este partido ya está completo o no está abierto.')
        return redirect('reservas:detalle_partido', partido_id=partido.id)
    
    if request.method == 'POST':
        # Usuario registrado
        if request.user.is_authenticated and request.user.tipo_usuario == 'JUGADOR':
            try:
                perfil = request.user.perfil_jugador
                
                # Verificar que no esté ya en el partido
                if partido.jugadores.filter(jugador=perfil).exists():
                    messages.warning(request, 'Ya estás en este partido.')
                    return redirect('reservas:detalle_partido', partido_id=partido.id)
                
                JugadorPartido.objects.create(
                    partido=partido,
                    jugador=perfil,
                    confirmado=True,
                    es_creador=False
                )
                
                messages.success(request, 'Te uniste al partido exitosamente!')
                return redirect('reservas:detalle_partido', partido_id=partido.id)
            
            except AttributeError:
                messages.error(request, 'No tienes perfil de jugador.')
                return redirect('reservas:detalle_partido', partido_id=partido.id)
        
        # Invitado sin cuenta
        else:
            nombre = request.POST.get('nombre_invitado')
            telefono = request.POST.get('telefono_invitado')
            email = request.POST.get('email_invitado', '')
            
            if not nombre or not telefono:
                messages.error(request, 'Debes proporcionar nombre y teléfono.')
                return redirect('reservas:unirse_partido', token=token)
            
            JugadorPartido.objects.create(
                partido=partido,
                jugador=None,
                es_invitado=True,
                nombre_invitado=nombre,
                telefono_invitado=telefono,
                email_invitado=email,
                confirmado=True,
                es_creador=False
            )
            
            messages.success(request, f'{nombre} se unió al partido exitosamente!')
            return redirect('reservas:detalle_partido', partido_id=partido.id)
    
    # GET: mostrar formulario
    context = {
        'partido': partido,
    }
    return render(request, 'reservas/unirse_partido.html', context)


@login_required
def confirmar_reserva(request, reserva_id):
    """Confirmar pago de una reserva (solo dueños)."""
    if request.method != 'POST':
        return redirect('reservas:detalle_reserva', reserva_id=reserva_id)
    
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que sea el dueño
    try:
        if reserva.cancha.complejo.dueno != request.user.perfil_dueno:
            messages.error(request, 'No tienes permiso para confirmar esta reserva.')
            return redirect('home')
    except AttributeError:
        messages.error(request, 'Solo dueños pueden confirmar reservas.')
        return redirect('home')
    
    resultado = reserva.confirmar()
    
    if resultado:
        messages.success(request, 'Reserva confirmada exitosamente.')
    else:
        messages.warning(request, 'La reserva ya estaba confirmada.')
    
    return redirect('reservas:detalle_reserva', reserva_id=reserva_id)


@login_required
def liberar_reserva_fija_fecha(request, reserva_fija_id):
    """
    Libera una ocurrencia específica de una reserva fija sin cancelar la recurrencia.
    Solo puede ser ejecutado por el dueño del complejo.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    reserva_fija = get_object_or_404(ReservaFija, id=reserva_fija_id)
    # Verificar que sea el dueño
    try:
        if reserva_fija.cancha.complejo.dueno != request.user.perfil_dueno:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para liberar esta reserva fija.'
            }, status=403)
    except AttributeError:
        return JsonResponse({
            'success': False,
            'message': 'Solo dueños pueden liberar reservas fijas.'
        }, status=403)
    # Obtener fecha desde el request
    import json
    try:
        data = json.loads(request.body)
        fecha_str = data.get('fecha')
        motivo = data.get('motivo', '')
        if not fecha_str:
            return JsonResponse({
                'success': False,
                'message': 'Fecha requerida.'
            }, status=400)
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        # Validar que la fecha corresponda al día de la semana de la reserva fija
        if fecha.weekday() != reserva_fija.dia_semana:
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            return JsonResponse({
                'success': False,
                'message': f'La fecha seleccionada no corresponde a un {dias[reserva_fija.dia_semana]}.'
            }, status=400)
        # Validar que la fecha esté dentro del rango de la reserva fija
        if fecha < reserva_fija.fecha_inicio:
            return JsonResponse({
                'success': False,
                'message': 'La fecha es anterior al inicio de la reserva fija.'
            }, status=400)
        if reserva_fija.fecha_fin and fecha > reserva_fija.fecha_fin:
            return JsonResponse({
                'success': False,
                'message': 'La fecha es posterior al fin de la reserva fija.'
            }, status=400)
        # Crear o actualizar la liberación
        liberacion, created = ReservaFijaLiberacion.objects.get_or_create(
            reserva_fija=reserva_fija,
            fecha=fecha,
            defaults={'motivo': motivo}
        )
        if not created:
            liberacion.motivo = motivo
            liberacion.save()
        # Liberar el turno si existe y está marcado como FIJO
        turno = Turno.objects.filter(
            cancha=reserva_fija.cancha,
            fecha=fecha,
            hora_inicio=reserva_fija.hora_inicio,
            estado='FIJO'
        ).first()
        if turno:
            turno.estado = 'DISPONIBLE'
            turno.save()
        action = 'liberada' if created else 'actualizada'
        return JsonResponse({
            'success': True,
            'message': f'Reserva fija {action} para el {fecha.strftime("%d/%m/%Y")}.',
            'liberacion_id': liberacion.id
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos inválidos.'
        }, status=400)
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Formato de fecha inválido.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al liberar reserva: {str(e)}'
        }, status=500)


@login_required
def cancelar_liberacion_reserva_fija(request, liberacion_id):
    """
    Cancela una liberación, volviendo a bloquear el turno.
    Solo puede ser ejecutado por el dueño del complejo.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    liberacion = get_object_or_404(ReservaFijaLiberacion, id=liberacion_id)
    reserva_fija = liberacion.reserva_fija
    # Verificar que sea el dueño
    try:
        if reserva_fija.cancha.complejo.dueno != request.user.perfil_dueno:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para cancelar esta liberación.'
            }, status=403)
    except AttributeError:
        return JsonResponse({
            'success': False,
            'message': 'Solo dueños pueden cancelar liberaciones.'
        }, status=403)
    fecha = liberacion.fecha
    liberacion.delete()
    turno = Turno.objects.filter(
        cancha=reserva_fija.cancha,
        fecha=fecha,
        hora_inicio=reserva_fija.hora_inicio
    ).first()
    if turno:
        if turno.estado == 'DISPONIBLE':
            turno.estado = 'FIJO'
            turno.save()
    else:
        Turno.objects.create(
            cancha=reserva_fija.cancha,
            fecha=fecha,
            hora_inicio=reserva_fija.hora_inicio,
            hora_fin=reserva_fija.hora_fin,
            precio=reserva_fija.precio,
            estado='FIJO'
        )
    return JsonResponse({
        'success': True,
        'message': f'Liberación cancelada. El turno volvió a bloquearse.'
    })


@login_required
def listar_liberaciones_reserva_fija(request, reserva_fija_id):
    """
    Lista todas las liberaciones de una reserva fija.
    """
    reserva_fija = get_object_or_404(ReservaFija, id=reserva_fija_id)
    # Verificar que sea el dueño
    try:
        if reserva_fija.cancha.complejo.dueno != request.user.perfil_dueno:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para ver estas liberaciones.'
            }, status=403)
    except AttributeError:
        return JsonResponse({
            'success': False,
            'message': 'Solo dueños pueden ver liberaciones.'
        }, status=403)
    liberaciones = ReservaFijaLiberacion.objects.filter(
        reserva_fija=reserva_fija
    ).order_by('fecha').values(
        'id',
        'fecha',
        'motivo',
        'creado_en'
    )
    return JsonResponse({
        'success': True,
        'liberaciones': list(liberaciones)
    })