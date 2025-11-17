from django.views.decorators.http import require_GET
# API: buscar jugador por nombre, usuario o DNI
@require_GET
def buscar_jugador(request):
    from cuentas.models import PerfilJugador
    from django.db.models import Q
    q = request.GET.get('q', '').strip()
    resultados = []
    if q:
        if q.isdigit():
            jugadores = PerfilJugador.objects.filter(
                usuario__dni=q
            ).select_related('usuario')[:10]
        elif q.startswith('@'):
            jugadores = PerfilJugador.objects.filter(
                Q(usuario__username__icontains=q[1:])
            ).select_related('usuario')[:10]
        else:
            jugadores = PerfilJugador.objects.filter(
                Q(usuario__first_name__icontains=q) |
                Q(usuario__last_name__icontains=q)
            ).select_related('usuario')[:10]
        for j in jugadores:
            resultados.append({
                'id': j.id,
                'nombre': f"{j.usuario.first_name} {j.usuario.last_name}",
                'usuario': j.usuario.username,
                'dni': j.usuario.dni or '',
                'nombre_real': j.usuario.nombre_real or ''
            })
    return JsonResponse(resultados, safe=False)
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
@require_GET
@login_required
def turnos_fijos_ocupados(request):
    """
    Devuelve los horarios ocupados por reservas fijas para un día de semana específico.
    Excluye los horarios que tienen una liberación registrada.
    """
    from reservas.models import ReservaFija, ReservaFijaLiberacion
    from .models import Cancha
    from datetime import datetime
    cancha_id = request.GET.get('cancha_id')
    dia_semana = request.GET.get('dia_semana')
    fecha = request.GET.get('fecha')  # Nueva: fecha específica para verificar liberaciones
    if not cancha_id or dia_semana is None:
        return JsonResponse([], safe=False)
    try:
        dia_semana = int(dia_semana)
        cancha = Cancha.objects.get(id=cancha_id)
    except (ValueError, Cancha.DoesNotExist):
        return JsonResponse([], safe=False)
    # Obtener reservas fijas activas para ese día
    reservas_fijas = ReservaFija.objects.filter(
        cancha=cancha,
        dia_semana=dia_semana,
        estado='ACTIVA'
    )
    horarios_ocupados = []
    for reserva_fija in reservas_fijas:
        # Si se proporciona una fecha específica, verificar si está liberada
        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                liberacion_existe = ReservaFijaLiberacion.objects.filter(
                    reserva_fija=reserva_fija,
                    fecha=fecha_obj
                ).exists()
                if liberacion_existe:
                    continue
            except ValueError:
                pass
        horarios_ocupados.append({
            'hora_inicio': reserva_fija.hora_inicio.strftime('%H:%M'),
            'hora_fin': reserva_fija.hora_fin.strftime('%H:%M'),
            'tipo': 'reserva_fija',
            'id': reserva_fija.id
        })
    return JsonResponse(horarios_ocupados, safe=False)
@require_GET
@login_required
def horarios_cancha(request, cancha_id):
    """
    Devuelve los horarios de una cancha para una fecha específica,
    incluyendo estado de ocupación por reservas simples y fijas.
    """
    from .models import Cancha
    from reservas.models import Turno, Reserva, ReservaFija, ReservaFijaLiberacion
    from django.db import models
    from datetime import datetime, timedelta
    fecha_str = request.GET.get('fecha')
    if not fecha_str:
        return JsonResponse({'error': 'Fecha requerida'}, status=400)
    try:
        cancha = Cancha.objects.get(id=cancha_id)
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except (Cancha.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Cancha o fecha inválida'}, status=400)
    dia_semana = fecha.weekday()
    turnos_existentes = Turno.objects.filter(
        cancha=cancha,
        fecha=fecha
    ).values('hora_inicio', 'estado')
    turnos_dict = {
        t['hora_inicio'].strftime('%H:%M'): t['estado']
        for t in turnos_existentes
    }
    reservas_fijas = ReservaFija.objects.filter(
        cancha=cancha,
        dia_semana=dia_semana,
        estado='ACTIVA',
        fecha_inicio__lte=fecha
    ).filter(
        models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=fecha)
    )
    liberaciones = set(
        ReservaFijaLiberacion.objects.filter(
            reserva_fija__cancha=cancha,
            fecha=fecha
        ).values_list('reserva_fija_id', flat=True)
    )
    reservas_simples = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    )
    # Guardar los rangos de cada reserva simple (asegurando tipo datetime.time)
    reservas_simples_rangos = []
    from datetime import time
    for r in reservas_simples:
        hora_inicio = r.hora_inicio
        hora_fin = r.hora_fin
        # Convertir a time si es string
        if isinstance(hora_inicio, str):
            h, m = map(int, hora_inicio.split(':'))
            hora_inicio = time(h, m)
        if isinstance(hora_fin, str):
            h, m = map(int, hora_fin.split(':'))
            hora_fin = time(h, m)
        reservas_simples_rangos.append((hora_inicio, hora_fin))
    horarios = []
    if cancha.horario_apertura and cancha.horario_cierre:
        hora_actual = datetime.combine(fecha, cancha.horario_apertura)
        hora_cierre = datetime.combine(fecha, cancha.horario_cierre)
        duracion = timedelta(minutes=cancha.duracion_turno_minutos or 90)
        while hora_actual + duracion <= hora_cierre:
            hora_str = hora_actual.time().strftime('%H:%M')
            hora_fin_time = (hora_actual + duracion).time()
            hora_fin_str = hora_fin_time.strftime('%H:%M')
            ocupado = False
            tipo_ocupacion = None
            # 1. Si existe un turno y no está disponible
            if hora_str in turnos_dict:
                estado_turno = turnos_dict[hora_str]
                if estado_turno != 'DISPONIBLE':
                    ocupado = True
                    tipo_ocupacion = estado_turno
            # 2. Si hay una reserva simple que solape (robusto)
            if not ocupado:
                inicio_turno = datetime.combine(fecha, hora_actual.time())
                fin_turno = datetime.combine(fecha, hora_fin_time)
                for r_inicio, r_fin in reservas_simples_rangos:
                    if not (hasattr(r_inicio, 'hour') and hasattr(r_fin, 'hour')):
                        continue
                    inicio_res = datetime.combine(fecha, r_inicio)
                    fin_res = datetime.combine(fecha, r_fin)
                    # Solapamiento: inicio_turno < fin_res y fin_turno > inicio_res
                    if (
                        (inicio_turno < fin_res and fin_turno > inicio_res)
                        or (inicio_turno == inicio_res and fin_turno == fin_res)
                    ):
                        ocupado = True
                        tipo_ocupacion = 'RESERVA_SIMPLE'
                        break
            # 3. Si hay una reserva fija activa y no liberada que solape
            if not ocupado:
                for reserva_fija in reservas_fijas:
                    if reserva_fija.id in liberaciones:
                        continue
                    rf_inicio = reserva_fija.hora_inicio
                    rf_fin = reserva_fija.hora_fin
                    inicio_fijo = datetime.combine(fecha, rf_inicio)
                    fin_fijo = datetime.combine(fecha, rf_fin)
                    if (inicio_turno < fin_fijo and fin_turno > inicio_fijo):
                        ocupado = True
                        tipo_ocupacion = 'RESERVA_FIJA'
                        break
            horarios.append({
                'hora_inicio': hora_str,
                'hora_fin': hora_fin_str,
                'ocupado': ocupado,
                'tipo_ocupacion': tipo_ocupacion
            })
            hora_actual += duracion
    return JsonResponse({
        'horarios': horarios,
        'fecha': fecha_str,
        'dia_semana': dia_semana
    })
@require_GET
@login_required
def validar_reserva_fija(request):
    """
    Valida si ya existe una reserva fija para el horario especificado.
    """
    from reservas.models import ReservaFija
    from datetime import datetime
    cancha_id = request.GET.get('cancha_id')
    dia_semana = request.GET.get('dia_semana')
    hora_inicio = request.GET.get('hora_inicio')
    if not all([cancha_id, dia_semana, hora_inicio]):
        return JsonResponse({'yafijo': False})
    try:
        dia_semana = int(dia_semana)
        hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
        existe = ReservaFija.objects.filter(
            cancha_id=cancha_id,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio_obj,
            estado='ACTIVA'
        ).exists()
        return JsonResponse({'yafijo': existe})
    except (ValueError, Exception):
        return JsonResponse({'yafijo': False})
from django.views.decorators.http import require_GET
# API para validar si ya existe un turno fijo para ese día, cancha y hora
@require_GET
def validar_reserva_fija(request):
    from reservas.models import ReservaFija
    cancha_id = request.GET.get('cancha_id')
    dia_semana = request.GET.get('dia_semana')
    hora_inicio = request.GET.get('hora_inicio')
    existe = False
    if cancha_id and dia_semana is not None and hora_inicio:
        existe = ReservaFija.objects.filter(
            cancha_id=cancha_id,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            estado='ACTIVA'
        ).exists()
    return JsonResponse({'yafijo': existe})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Complejo, Cancha, ServicioComplejo, Localidad
from cuentas.models import PerfilDueno
from reservas.models import Reserva, ReservaFija


def lista_complejos(request):
    """Lista todos los complejos activos con posibilidad de reservar directamente."""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q
    
    complejos = Complejo.objects.filter(activo=True).select_related('dueno').prefetch_related('canchas')
    localidad = request.GET.get('localidad', '')
    provincia = request.GET.get('provincia', '')
    pais = request.GET.get('pais', '')
    deporte = request.GET.get('deporte', '')
    
    # Filtros
    if localidad:
        complejos = complejos.filter(localidad__icontains=localidad)
    if provincia:
        complejos = complejos.filter(provincia__icontains=provincia)
    if pais:
        complejos = complejos.filter(pais__icontains=pais)
    
    context = {
        'complejos_data': complejos_data,
        'complejos_agrupados': complejos_agrupados,
        'localidad': localidad,
        'provincia': provincia,
        'pais': pais,
        'provincias': provincias,
        'paises': paises,
        'deporte': deporte,
        'deportes': deportes,
        'fecha': fecha,
        'fecha_anterior': fecha - timedelta(days=1) if fecha > timezone.now().date() else None,
        'fecha_siguiente': fecha + timedelta(days=1),
    }
    return render(request, 'complejos/lista.html', context)


def detalle_complejo(request, slug):
    """Muestra el detalle de un complejo."""
    complejo = get_object_or_404(Complejo, slug=slug, activo=True)
    canchas = complejo.canchas.filter(activo=True)
    servicios = complejo.servicios.all()
    
    # Validar coordenadas para evitar errores en el mapa
    tiene_coordenadas_validas = False
    if complejo.latitud and complejo.longitud:
        try:
            lat = float(complejo.latitud)
            lng = float(complejo.longitud)
            # Validar que estén en rangos válidos
            if -90 <= lat <= 90 and -180 <= lng <= 180 and (lat != 0 or lng != 0):
                tiene_coordenadas_validas = True
        except (ValueError, TypeError):
            pass
    
    context = {
        'complejo': complejo,
        'canchas': canchas,
        'servicios': servicios,
        'tiene_coordenadas_validas': tiene_coordenadas_validas,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'complejos/detalle.html', context)


@login_required
def crear_complejo(request):
    """Permite a un dueño crear un complejo."""
    # Verificar que el usuario sea dueño o crear perfil
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Debes ser dueño de complejo para crear uno.')
        return redirect('home')
    
    perfil_dueno, created = PerfilDueno.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        direccion = request.POST.get('direccion')
        localidad = request.POST.get('localidad')
        provincia = request.POST.get('provincia', 'Córdoba')
        pais = request.POST.get('pais', 'Argentina')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        telefono = request.POST.get('telefono', '')
        email = request.POST.get('email', '')
        
        # Crear slug del nombre
        slug = slugify(nombre)
        # Generar subdominio automáticamente basado en el slug
        subdominio = slug
        
        # Verificar que no exista
        if Complejo.objects.filter(slug=slug).exists():
            messages.error(request, 'Ya existe un complejo con ese nombre.')
        else:
            complejo = Complejo.objects.create(
                dueno=perfil_dueno,
                nombre=nombre,
                descripcion=descripcion,
                direccion=direccion,
                localidad=localidad,
                provincia=provincia,
                pais=pais,
                latitud=float(latitud) if latitud else 0,
                longitud=float(longitud) if longitud else 0,
                telefono=telefono,
                email=email,
                slug=slug,
                subdominio=subdominio,
            )
            
            # Manejar logo/foto principal
            if 'logo' in request.FILES:
                complejo.logo = request.FILES['logo']
                complejo.save()
            
            messages.success(request, f'¡Complejo {nombre} creado exitosamente!')
            print('DEBUG: Redirigiendo a gestionar', complejo.slug)
            return redirect('complejos:gestionar', slug=complejo.slug)
    
    return render(request, 'complejos/crear.html')


@login_required
def editar_complejo(request, slug):
    """Permite al dueño editar su complejo."""
    complejo = get_object_or_404(Complejo, slug=slug)
    
    # Verificar que sea el dueño
    if complejo.dueno.usuario != request.user:
        messages.error(request, 'No tienes permiso para editar este complejo.')
        return redirect('complejos:detalle', slug=slug)
    
    if request.method == 'POST':
        complejo.nombre = request.POST.get('nombre', complejo.nombre)
        complejo.descripcion = request.POST.get('descripcion', complejo.descripcion)
        complejo.direccion = request.POST.get('direccion', complejo.direccion)
        complejo.localidad = request.POST.get('localidad', complejo.localidad)
        complejo.provincia = request.POST.get('provincia', complejo.provincia)
        complejo.pais = request.POST.get('pais', complejo.pais)
        
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        if latitud and longitud:
            complejo.latitud = float(latitud)
            complejo.longitud = float(longitud)
        
        complejo.telefono = request.POST.get('telefono', complejo.telefono)
        complejo.email = request.POST.get('email', complejo.email)
        
        # Manejar logo/foto principal
        if 'logo' in request.FILES:
            complejo.logo = request.FILES['logo']
        
        complejo.save()
        
        messages.success(request, 'Complejo actualizado correctamente.')
        return redirect('complejos:detalle', slug=complejo.slug)
    
    context = {
        'complejo': complejo,
    }
    return render(request, 'complejos/editar.html', context)


@login_required
def gestionar_complejo(request, slug):
    """
    Vista principal para gestionar un complejo (canchas y servicios).
    """
    complejo = get_object_or_404(Complejo, slug=slug)
    
    # Verificar que sea el dueño
    if complejo.dueno.usuario != request.user:
        messages.error(request, 'No tienes permiso para gestionar este complejo.')
        return redirect('complejos:detalle', slug=slug)
    
    canchas = complejo.canchas.all().order_by('-activo', 'nombre')
    servicios = complejo.servicios.all()
    servicios_disponibles = ServicioComplejo.TIPO_SERVICIO_CHOICES
    
    # Manejar foto del complejo
    if request.method == 'POST' and 'subir_logo' in request.POST:
        if 'logo' in request.FILES:
            complejo.logo = request.FILES['logo']
            complejo.save()
            messages.success(request, 'Logo actualizado correctamente.')
        return redirect('complejos:gestionar', slug=slug)
    
    # Manejar servicios
    if request.method == 'POST' and 'gestionar_servicios' in request.POST:
        # Eliminar servicios existentes y crear los nuevos seleccionados
        servicios_seleccionados = request.POST.getlist('servicios')
        complejo.servicios.all().delete()
        for tipo_servicio in servicios_seleccionados:
            ServicioComplejo.objects.create(
                complejo=complejo,
                tipo_servicio=tipo_servicio
            )
        messages.success(request, 'Servicios actualizados correctamente.')
        return redirect('complejos:gestionar', slug=slug)
    
    context = {
        'complejo': complejo,
        'canchas': canchas,
        'servicios': servicios,
        'servicios_disponibles': servicios_disponibles,
        'servicios_actuales': [s.tipo_servicio for s in servicios],
    }
    return render(request, 'complejos/gestionar.html', context)


@login_required
def agregar_cancha(request, slug):
    """
    Permite agregar una nueva cancha a un complejo.
    """
    complejo = get_object_or_404(Complejo, slug=slug)
    
    # Verificar que sea el dueño
    if complejo.dueno.usuario != request.user:
        messages.error(request, 'No tienes permiso para agregar canchas a este complejo.')
        return redirect('complejos:detalle', slug=slug)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        deporte = request.POST.get('deporte')
        tipo_superficie = request.POST.get('tipo_superficie', '')
        tipo_pared = request.POST.get('tipo_pared', '')
        techada = 'techada' in request.POST
        iluminacion = 'iluminacion' in request.POST
        precio_hora = request.POST.get('precio_hora')
        horario_apertura = request.POST.get('horario_apertura', '08:00')
        horario_cierre = request.POST.get('horario_cierre', '23:00')
        duracion_turno = request.POST.get('duracion_turno_minutos', 60)
        
        # Crear cancha
        cancha = Cancha.objects.create(
            complejo=complejo,
            nombre=nombre,
            deporte=deporte,
            tipo_superficie=tipo_superficie,
            tipo_pared=tipo_pared,
            techada=techada,
            iluminacion=iluminacion,
            precio_base=precio_hora,
            precio_hora=precio_hora,
            horario_apertura=horario_apertura,
            horario_cierre=horario_cierre,
            duracion_turno_minutos=duracion_turno,
        )
        
        # Manejar foto si se subió
        if 'foto' in request.FILES:
            cancha.foto = request.FILES['foto']
            cancha.save()
        
        messages.success(request, f'Cancha "{nombre}" agregada exitosamente.')
        return redirect('complejos:gestionar', slug=slug)
    
    context = {
        'complejo': complejo,
        'deportes': Cancha.DEPORTE_CHOICES,
        'tipos_pared': Cancha.TIPO_PARED_CHOICES,
    }
    return render(request, 'complejos/agregar_cancha.html', context)


@login_required
def editar_cancha(request, slug, cancha_id):
    """
    Permite editar una cancha existente.
    """
    complejo = get_object_or_404(Complejo, slug=slug)
    cancha = get_object_or_404(Cancha, id=cancha_id, complejo=complejo)
    
    # Verificar que sea el dueño
    if complejo.dueno.usuario != request.user:
        messages.error(request, 'No tienes permiso para editar esta cancha.')
        return redirect('complejos:detalle', slug=slug)
    
    if request.method == 'POST':
        cancha.nombre = request.POST.get('nombre', cancha.nombre)
        cancha.deporte = request.POST.get('deporte', cancha.deporte)
        cancha.tipo_superficie = request.POST.get('tipo_superficie', '')
        cancha.tipo_pared = request.POST.get('tipo_pared', '')
        cancha.techada = 'techada' in request.POST
        cancha.iluminacion = 'iluminacion' in request.POST
        
        precio_hora = request.POST.get('precio_hora')
        if precio_hora:
            cancha.precio_hora = precio_hora
            cancha.precio_base = precio_hora
        
        cancha.horario_apertura = request.POST.get('horario_apertura', cancha.horario_apertura)
        cancha.horario_cierre = request.POST.get('horario_cierre', cancha.horario_cierre)
        cancha.duracion_turno_minutos = request.POST.get('duracion_turno_minutos', cancha.duracion_turno_minutos)
        
        # Manejar foto si se subió una nueva
        if 'foto' in request.FILES:
            cancha.foto = request.FILES['foto']
        
        cancha.save()
        messages.success(request, f'Cancha "{cancha.nombre}" actualizada correctamente.')
        return redirect('complejos:gestionar', slug=slug)
    
    context = {
        'complejo': complejo,
        'cancha': cancha,
        'deportes': Cancha.DEPORTE_CHOICES,
        'tipos_pared': Cancha.TIPO_PARED_CHOICES,
    }
    return render(request, 'complejos/editar_cancha.html', context)


@login_required
def toggle_cancha(request, slug, cancha_id):
    """
    Activa o desactiva una cancha.
    """
    complejo = get_object_or_404(Complejo, slug=slug)
    cancha = get_object_or_404(Cancha, id=cancha_id, complejo=complejo)
    
    # Verificar que sea el dueño
    if complejo.dueno.usuario != request.user:
        messages.error(request, 'No tienes permiso.')
        return redirect('complejos:detalle', slug=slug)
    
    cancha.activo = not cancha.activo
    cancha.save()
    
    estado = "activada" if cancha.activo else "desactivada"
    messages.success(request, f'Cancha "{cancha.nombre}" {estado} correctamente.')
    return redirect('complejos:gestionar', slug=slug)


def obtener_horarios_disponibles(request, cancha_id):
    from reservas.models import ReservaFija, ReservaFijaLiberacion, Reserva, Turno
    from django.db import models

    cancha = get_object_or_404(Cancha, id=cancha_id, activo=True)
    fecha_str = request.GET.get('fecha', timezone.now().date().isoformat())

    # Parseo de fecha
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)

    # No permitir fechas pasadas
    if fecha < timezone.now().date():
        return JsonResponse({'error': 'No se puede reservar en fechas pasadas'}, status=400)

    # Debe tener horarios configurados
    if not cancha.horario_apertura or not cancha.horario_cierre:
        return JsonResponse({'error': 'Esta cancha no tiene horarios configurados'}, status=400)

    # Unificación de lógica robusta de ocupación
    from datetime import time
    dia_semana = fecha.weekday()
    turnos_existentes = Turno.objects.filter(
        cancha=cancha,
        fecha=fecha
    ).values('hora_inicio', 'estado', 'precio')
    turnos_dict = {
        t['hora_inicio'].strftime('%H:%M'): t for t in turnos_existentes
    }
    reservas_fijas = ReservaFija.objects.filter(
        cancha=cancha,
        dia_semana=dia_semana,
        estado='ACTIVA',
        fecha_inicio__lte=fecha
    ).filter(
        models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=fecha)
    )
    liberaciones = set(
        ReservaFijaLiberacion.objects.filter(
            reserva_fija__cancha=cancha,
            fecha=fecha
        ).values_list('reserva_fija_id', flat=True)
    )
    reservas_simples = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    )
    reservas_simples_rangos = []
    for r in reservas_simples:
        hora_inicio = r.hora_inicio
        hora_fin = r.hora_fin
        if isinstance(hora_inicio, str):
            h, m = map(int, hora_inicio.split(':'))
            hora_inicio = time(h, m)
        if isinstance(hora_fin, str):
            h, m = map(int, hora_fin.split(':'))
            hora_fin = time(h, m)
        reservas_simples_rangos.append((hora_inicio, hora_fin))
    horarios = []
    if cancha.horario_apertura and cancha.horario_cierre:
        hora_actual = datetime.combine(fecha, cancha.horario_apertura)
        hora_cierre = datetime.combine(fecha, cancha.horario_cierre)
        duracion = timedelta(minutes=cancha.duracion_turno_minutos or 90)
        while hora_actual + duracion <= hora_cierre:
            hora_str = hora_actual.time().strftime('%H:%M')
            hora_fin_time = (hora_actual + duracion).time()
            hora_fin_str = hora_fin_time.strftime('%H:%M')
            ocupado = False
            # 1. Si existe un turno y no está disponible
            if hora_str in turnos_dict:
                estado_turno = turnos_dict[hora_str]['estado']
                if estado_turno != 'DISPONIBLE':
                    ocupado = True
                    precio = float(turnos_dict[hora_str]['precio'])
                else:
                    precio = float(cancha.precio_hora)
            else:
                precio = float(cancha.precio_hora)
            # 2. Si hay una reserva simple que solape (robusto)
            if not ocupado:
                inicio_turno = hora_actual
                fin_turno = hora_actual + duracion
                for r_inicio, r_fin in reservas_simples_rangos:
                    if not (hasattr(r_inicio, 'hour') and hasattr(r_fin, 'hour')):
                        continue
                    inicio_res = datetime.combine(fecha, r_inicio)
                    fin_res = datetime.combine(fecha, r_fin)
                    # Solapamiento real: inicio_turno < fin_res y fin_turno > inicio_res
                    # Pero NO si fin_turno == inicio_res (no se solapan, solo se tocan)
                    if (
                        (inicio_turno < fin_res and fin_turno > inicio_res)
                        and not (fin_turno == inicio_res or inicio_turno == fin_res)
                    ):
                        ocupado = True
                        break
            # 3. Si hay una reserva fija activa y no liberada que solape
            if not ocupado:
                for reserva_fija in reservas_fijas:
                    if reserva_fija.id in liberaciones:
                        continue
                    rf_inicio = reserva_fija.hora_inicio
                    rf_fin = reserva_fija.hora_fin
                    inicio_fijo = datetime.combine(fecha, rf_inicio)
                    fin_fijo = datetime.combine(fecha, rf_fin)
                    # Igual que arriba: no marcar ocupado si solo se tocan los bordes
                    if (inicio_turno < fin_fijo and fin_turno > inicio_fijo and not (fin_turno == inicio_fijo or inicio_turno == fin_fijo)):
                        ocupado = True
                        break
            horarios.append({
                'hora_inicio': hora_str,
                'hora_fin': hora_fin_str,
                'ocupado': ocupado,
                'precio': precio
            })
            hora_actual += duracion
    return JsonResponse({
        'cancha': {
            'id': cancha.id,
            'nombre': cancha.nombre,
            'deporte': cancha.get_deporte_display(),
            'precio_hora': float(cancha.precio_hora),
            'duracion_turno': cancha.duracion_turno_minutos or 90,
        },
        'fecha': fecha.isoformat(),
        'horarios': horarios,
    })


def obtener_provincias(request):
    """
    API endpoint para obtener las provincias de Argentina.
    """
    provincias = [
        'Buenos Aires',
        'Ciudad Autónoma de Buenos Aires',
        'Catamarca',
        'Chaco',
        'Chubut',
        'Córdoba',
        'Corrientes',
        'Entre Ríos',
        'Formosa',
        'Jujuy',
        'La Pampa',
        'La Rioja',
        'Mendoza',
        'Misiones',
        'Neuquén',
        'Río Negro',
        'Salta',
        'San Juan',
        'San Luis',
        'Santa Cruz',
        'Santa Fe',
        'Santiago del Estero',
        'Tierra del Fuego',
        'Tucumán',
    ]
    
    return JsonResponse({'provincias': provincias})


def obtener_localidades(request):
    """
    API endpoint para obtener localidades por provincia de Argentina.
    Incluye localidades predeterminadas + localidades agregadas por usuarios.
    """
    provincia = request.GET.get('provincia', '')
    
    # Diccionario de localidades principales por provincia
    localidades_por_provincia = {
        'Buenos Aires': [
            'La Plata', 'Mar del Plata', 'Bahía Blanca', 'San Nicolás', 'Tandil',
            'Olavarría', 'Pergamino', 'Azul', 'Junín', 'Necochea', 'Quilmes',
            'Lanús', 'Lomas de Zamora', 'Avellaneda', 'San Isidro', 'Vicente López',
            'Morón', 'San Miguel', 'Tigre', 'Pilar', 'Escobar', 'La Matanza',
        ],
        'Ciudad Autónoma de Buenos Aires': [
            'Palermo', 'Belgrano', 'Recoleta', 'San Telmo', 'Caballito',
            'Villa Urquiza', 'Núñez', 'Flores', 'Almagro', 'Villa Crespo',
        ],
        'Catamarca': [
            'San Fernando del Valle de Catamarca', 'Andalgalá', 'Santa María',
            'Belén', 'Tinogasta', 'Recreo', 'Valle Viejo',
        ],
        'Chaco': [
            'Resistencia', 'Presidencia Roque Sáenz Peña', 'Villa Ángela',
            'Barranqueras', 'Fontana', 'Charata', 'General San Martín',
        ],
        'Chubut': [
            'Rawson', 'Comodoro Rivadavia', 'Trelew', 'Puerto Madryn',
            'Esquel', 'Sarmiento', 'Puerto Deseado',
        ],
        'Córdoba': [
            'Córdoba', 'Villa María', 'Río Cuarto', 'San Francisco', 'Villa Carlos Paz',
            'Alta Gracia', 'Bell Ville', 'Jesús María', 'La Calera', 'Río Tercero',
            'Cruz Alta', 'Marcos Juárez', 'Villa Dolores', 'Deán Funes', 'Cosquín',
            'Laboulaye', 'Villa Allende', 'Arroyito', 'Las Varillas', 'Morteros',
        ],
        'Corrientes': [
            'Corrientes', 'Goya', 'Paso de los Libres', 'Mercedes', 'Curuzú Cuatiá',
            'Esquina', 'Santo Tomé', 'Bella Vista',
        ],
        'Entre Ríos': [
            'Paraná', 'Concordia', 'Gualeguaychú', 'Concepción del Uruguay',
            'Victoria', 'Gualeguay', 'Chajarí', 'La Paz', 'Villaguay',
        ],
        'Formosa': [
            'Formosa', 'Clorinda', 'Pirané', 'El Colorado', 'Ibarreta',
            'Las Lomitas', 'Ingeniero Juárez',
        ],
        'Jujuy': [
            'San Salvador de Jujuy', 'Palpalá', 'San Pedro', 'Libertador General San Martín',
            'Perico', 'La Quiaca', 'Humahuaca', 'Tilcara',
        ],
        'La Pampa': [
            'Santa Rosa', 'General Pico', 'General Acha', 'Eduardo Castex',
            'Realicó', 'Victorica', 'Ingeniero Luiggi',
        ],
        'La Rioja': [
            'La Rioja', 'Chilecito', 'Aimogasta', 'Chamical', 'Chepes',
            'Villa Unión', 'Arauco',
        ],
        'Mendoza': [
            'Mendoza', 'Godoy Cruz', 'Guaymallén', 'Las Heras', 'Maipú',
            'San Rafael', 'San Martín', 'Tunuyán', 'Tupungato', 'Malargüe',
            'Luján de Cuyo', 'Rivadavia', 'Lavalle',
        ],
        'Misiones': [
            'Posadas', 'Oberá', 'Eldorado', 'Puerto Iguazú', 'Apóstoles',
            'Leandro N. Alem', 'San Vicente', 'Montecarlo', 'Jardín América',
        ],
        'Neuquén': [
            'Neuquén', 'Centenario', 'Plottier', 'San Martín de los Andes',
            'Zapala', 'Cutral Có', 'Plaza Huincul', 'Junín de los Andes', 'Villa La Angostura',
        ],
        'Río Negro': [
            'Viedma', 'San Carlos de Bariloche', 'General Roca', 'Cipolletti',
            'El Bolsón', 'Cinco Saltos', 'Villa Regina', 'Catriel',
        ],
        'Salta': [
            'Salta', 'San Ramón de la Nueva Orán', 'Tartagal', 'General Güemes',
            'Metán', 'Rosario de la Frontera', 'Cafayate', 'Joaquín V. González',
        ],
        'San Juan': [
            'San Juan', 'Rawson', 'Chimbas', 'Rivadavia', 'Santa Lucía',
            'Pocito', 'Caucete', 'Albardón', 'San Martín',
        ],
        'San Luis': [
            'San Luis', 'Villa Mercedes', 'La Punta', 'Merlo', 'Justo Daract',
            'Tilisarao', 'Concarán', 'Villa de la Quebrada',
        ],
        'Santa Cruz': [
            'Río Gallegos', 'Caleta Olivia', 'Pico Truncado', 'Puerto Deseado',
            'Puerto San Julián', 'El Calafate', 'Río Turbio', 'Las Heras',
        ],
        'Santa Fe': [
            'Santa Fe', 'Rosario', 'Rafaela', 'Reconquista', 'Venado Tuerto',
            'Villa Gobernador Gálvez', 'Casilda', 'San Lorenzo', 'Esperanza',
            'Santo Tomé', 'Cañada de Gómez', 'Firmat', 'Vera', 'Funes',
        ],
        'Santiago del Estero': [
            'Santiago del Estero', 'La Banda', 'Termas de Río Hondo', 'Frías',
            'Añatuya', 'Fernández', 'Monte Quemado', 'Suncho Corral',
        ],
        'Tierra del Fuego': [
            'Ushuaia', 'Río Grande', 'Tolhuin',
        ],
        'Tucumán': [
            'San Miguel de Tucumán', 'Yerba Buena', 'Tafí Viejo', 'Concepción',
            'Banda del Río Salí', 'Aguilares', 'Monteros', 'Famaillá', 'Simoca',
        ],
    }
    
    # Obtener localidades predeterminadas
    localidades = localidades_por_provincia.get(provincia, [])
    
    # Agregar localidades personalizadas de la base de datos (solo aprobadas)
    localidades_custom = Localidad.objects.filter(
        provincia=provincia,
        aprobada=True
    ).values_list('nombre', flat=True)
    
    # Combinar y eliminar duplicados
    todas_localidades = list(set(localidades + list(localidades_custom)))
    todas_localidades.sort()
    
    return JsonResponse({'localidades': todas_localidades})


@login_required
def agregar_localidad(request):
    """
    API endpoint para agregar una nueva localidad.
    Solo usuarios autenticados pueden agregar localidades.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    import json
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        provincia = data.get('provincia', '').strip()
        pais = data.get('pais', 'Argentina')
        
        if not nombre or not provincia:
            return JsonResponse({
                'error': 'Nombre y provincia son requeridos'
            }, status=400)
        
        # Verificar si ya existe
        localidad_existente = Localidad.objects.filter(
            nombre__iexact=nombre,
            provincia=provincia,
            pais=pais
        ).first()
        
        if localidad_existente:
            return JsonResponse({
                'success': True,
                'mensaje': 'La localidad ya existe',
                'localidad': {
                    'nombre': localidad_existente.nombre,
                    'provincia': localidad_existente.provincia,
                    'aprobada': localidad_existente.aprobada,
                }
            })
        
        # Crear nueva localidad
        localidad = Localidad.objects.create(
            nombre=nombre,
            provincia=provincia,
            pais=pais,
            agregada_por=request.user,
            aprobada=True  # Auto-aprobar por ahora
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Localidad agregada exitosamente',
            'localidad': {
                'nombre': localidad.nombre,
                'provincia': localidad.provincia,
                'aprobada': localidad.aprobada,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error al agregar localidad: {str(e)}'
        }, status=500)


# ========== VISTAS DE RESERVAS PARA DUEÑOS ==========

@login_required
def calendario_reservas_dueno(request, complejo_slug):
    """
    Vista del calendario de reservas desde el panel del dueño.
    Permite ver todas las canchas y crear reservas administrativas/bloqueos.
    """
    complejo = get_object_or_404(Complejo, slug=complejo_slug)
    
    # Verificar que sea el dueño
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Solo los dueños pueden acceder al panel de reservas.')
        return redirect('complejos:detalle', slug=complejo_slug)
    
    try:
        perfil_dueno = request.user.perfil_dueno
        if complejo.dueno != perfil_dueno:
            messages.error(request, 'No tienes permiso para gestionar este complejo.')
            return redirect('complejos:dashboard_principal')
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de dueño.')
        return redirect('home')
    
    # Obtener fecha desde parámetros o usar hoy
    fecha_str = request.GET.get('fecha', timezone.now().date().isoformat())
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except ValueError:
        fecha = timezone.now().date()
    
    # Obtener canchas del complejo
    canchas = complejo.canchas.filter(activo=True).order_by('nombre')
    
    # Importar modelos de reservas
    from reservas.models import Turno, Reserva
    
    # Obtener turnos y reservas del día
    turnos_por_cancha = {}
    for cancha in canchas:
        # Como Reserva tiene OneToOneField con related_name='reserva', 
        # no podemos hacer select_related desde Turno. 
        # En su lugar, obtenemos los turnos y Django cargará la reserva si existe
        turnos = Turno.objects.filter(
            cancha=cancha,
            fecha=fecha
        ).order_by('hora_inicio')
        
        turnos_por_cancha[cancha.id] = {
            'cancha': cancha,
            'turnos': turnos
        }
    
    context = {
        'complejo': complejo,
        'fecha': fecha,
        'fecha_anterior': fecha - timedelta(days=1),
        'fecha_siguiente': fecha + timedelta(days=1),
        'canchas': canchas,
        'turnos_por_cancha': turnos_por_cancha,
    }
    return render(request, 'complejos/calendario_reservas_dueno.html', context)


@login_required
def crear_reserva_dueno(request, complejo_slug):
    """
    Crear reserva desde el panel del dueño.
    Puede ser para cliente, administrativa o bloqueo.
    """
    if request.method != 'POST':
        return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)
    
    complejo = get_object_or_404(Complejo, slug=complejo_slug)
    
    # Verificar que sea el dueño
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Solo los dueños pueden crear reservas administrativas.')
        return redirect('complejos:detalle', slug=complejo_slug)
    
    try:
        perfil_dueno = request.user.perfil_dueno
        if complejo.dueno != perfil_dueno:
            messages.error(request, 'No tienes permiso para gestionar este complejo.')
            return redirect('complejos:dashboard_principal')
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de dueño.')
        return redirect('home')
    
    # Obtener datos del formulario
    cancha_id = request.POST.get('cancha_id')
    fecha_str = request.POST.get('fecha')
    hora_inicio_str = request.POST.get('hora_inicio')
    tipo_reserva = request.POST.get('tipo_reserva')
    nombre_cliente = request.POST.get('nombre_cliente')
    telefono_cliente = request.POST.get('telefono_cliente')
    precio_str = request.POST.get('precio')
    observaciones = request.POST.get('observaciones')

    from .models import Cancha
    from datetime import datetime, timedelta
    try:
        cancha = get_object_or_404(Cancha, id=cancha_id, complejo=complejo)
        fecha = datetime.fromisoformat(fecha_str).date()
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        # Calcular hora fin
        duracion_minutos = cancha.duracion_turno_minutos or 90
        hora_fin = (datetime.combine(fecha, hora_inicio) + timedelta(minutes=duracion_minutos)).time()
        # Precio
        if precio_str:
            precio = float(precio_str)
        else:
            precio = float(cancha.precio_hora) if tipo_reserva == 'CLIENTE' else 0
        hora_inicio_str = hora_inicio.strftime('%H:%M')
    except (ValueError, TypeError, Cancha.DoesNotExist) as e:
        messages.error(request, f'Datos inválidos: {str(e)}')
        return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)
    
    # Importar modelos de reservas
    from reservas.models import Turno, Reserva
    
    # Buscar o crear el turno
    turno, created = Turno.objects.get_or_create(
        cancha=cancha,
        fecha=fecha,
        hora_inicio=hora_inicio,
        defaults={
            'hora_fin': hora_fin,
            'precio': precio,
            'estado': 'DISPONIBLE'
        }
    )
    
    # Verificar si el turno ya tiene reserva
    if hasattr(turno, 'reserva'):
        messages.error(request, f'Ya existe una reserva para este horario.')
        return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)
    
    # Crear la reserva
    reserva = Reserva.objects.create(
        turno=turno,
        tipo_reserva=tipo_reserva,
        jugador=None,
        reservado_por_dueno=True,
        nombre_cliente_sin_cuenta=nombre_cliente,
        telefono_cliente=telefono_cliente,
        precio=precio,
        estado='CONFIRMADA',
        observaciones=observaciones,
        creado_por=request.user,
        pagado=(tipo_reserva != 'CLIENTE')  # Bloqueos y administrativas se marcan como pagadas
    )
    
    # Actualizar estado del turno
    if tipo_reserva == 'BLOQUEADA' or tipo_reserva == 'MANTENIMIENTO':
        turno.estado = 'BLOQUEADO_TORNEO'  # Reutilizamos este estado
    else:
        turno.estado = 'RESERVADO'
    turno.save()
    
    # Mensaje de éxito personalizado
    tipo_texto = dict(Reserva.TIPO_RESERVA_CHOICES).get(tipo_reserva, 'Reserva')
    
    if tipo_reserva == 'CLIENTE' and nombre_cliente:
        mensaje = f'{tipo_texto} creada para {nombre_cliente} - {hora_inicio_str}'
    elif tipo_reserva == 'CLIENTE':
        mensaje = f'{tipo_texto} creada - {hora_inicio_str}'
    elif tipo_reserva == 'BLOQUEADA':
        razon = f" ({observaciones[:30]}...)" if observaciones else ""
        mensaje = f'Horario bloqueado: {hora_inicio_str}{razon}'
    elif tipo_reserva == 'MANTENIMIENTO':
        mensaje = f'Mantenimiento programado: {hora_inicio_str}'
    else:  # ADMINISTRATIVA
        mensaje = f'{tipo_texto}: {hora_inicio_str}'
    
    messages.success(request, mensaje)
    
    return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)


@login_required
def cancelar_reserva_dueno(request, complejo_slug, reserva_id):
    """
    Cancelar una reserva desde el panel del dueño.
    """
    if request.method != 'POST':
        return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)
    
    complejo = get_object_or_404(Complejo, slug=complejo_slug)
    
    # Verificar que sea el dueño
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Solo los dueños pueden cancelar reservas.')
        return redirect('complejos:detalle', slug=complejo_slug)
    
    try:
        perfil_dueno = request.user.perfil_dueno
        if complejo.dueno != perfil_dueno:
            messages.error(request, 'No tienes permiso para gestionar este complejo.')
            return redirect('complejos:dashboard_principal')
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de dueño.')
        return redirect('home')
    
    # Importar modelo
    from reservas.models import Reserva
    
    # Obtener reserva
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que la reserva sea de una cancha del complejo
    if reserva.turno.cancha.complejo != complejo:
        messages.error(request, 'Esta reserva no pertenece a tu complejo.')
        return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)
    
    # Cancelar
    reserva.cancelar()
    
    messages.success(request, 'Reserva cancelada exitosamente.')
    return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)


@login_required
def crear_reserva_fija_dueno(request, complejo_slug):
    """
    Crear una reserva fija (turno fijo) desde el panel del dueño.
    """
    if request.method != 'POST':
        return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)
    
    complejo = get_object_or_404(Complejo, slug=complejo_slug)
    
    # Verificar que sea el dueño
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'Solo los dueños pueden crear turnos fijos.')
        return redirect('complejos:detalle', slug=complejo_slug)
    
    try:
        perfil_dueno = request.user.perfil_dueno
        if complejo.dueno != perfil_dueno:
            messages.error(request, 'No tienes permiso para gestionar este complejo.')
            return redirect('complejos:dashboard_principal')
    except AttributeError:
        messages.error(request, 'No se encontró tu perfil de dueño.')
        return redirect('home')
    
    # Obtener datos del formulario
    cancha_id = request.POST.get('cancha_id')
    dia_semana = request.POST.get('dia_semana')
    hora_inicio = request.POST.get('hora_inicio')
    nombre_cliente = request.POST.get('nombre_cliente')
    telefono_cliente = request.POST.get('telefono_cliente')
    precio = request.POST.get('precio')
    
    # Validar que la cancha pertenzca al complejo
    cancha = get_object_or_404(Cancha, id=cancha_id, complejo=complejo)
    
    try:
        from datetime import datetime, timedelta
        
        # Calcular hora_fin basado en la duración del turno
        hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
        hora_inicio_dt = datetime.combine(timezone.now().date(), hora_inicio_obj)
        hora_fin_dt = hora_inicio_dt + timedelta(minutes=cancha.duracion_turno_minutos)
        hora_fin = hora_fin_dt.time()
        
        # Crear reserva fija
        reserva_fija = ReservaFija.objects.create(
            cancha=cancha,
            dia_semana=int(dia_semana),
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            fecha_inicio=timezone.now().date(),
            nombre_cliente=nombre_cliente,
            telefono_cliente=telefono_cliente,
            precio=float(precio),
            creada_por=perfil_dueno
        )
        
        # Mapear día de semana a nombre
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dia_nombre = dias_semana[int(dia_semana)]
        
        messages.success(
            request, 
            f'¡Turno fijo creado! {cancha.nombre} - {dia_nombre}s a las {hora_inicio} para {nombre_cliente}'
        )
    except Exception as e:
        messages.error(request, f'Error al crear turno fijo: {str(e)}')
    
    return redirect('complejos:calendario_reservas_dueno', complejo_slug=complejo_slug)


# API: buscar jugador por cancha, fecha y hora (reserva simple)
from django.http import JsonResponse
from reservas.models import Reserva
@require_GET
def buscar_jugador_turno(request):
    from cuentas.models import PerfilJugador
    from django.db.models import Q
    cancha_id = request.GET.get('cancha_id')
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora_inicio')
    q = request.GET.get('q', '').strip()
    resultados = []
    if cancha_id and fecha and hora and q:
        reservas = Reserva.objects.filter(
            cancha_id=cancha_id,
            fecha=fecha,
            hora_inicio=hora
        ).select_related('jugador_principal__usuario')
        if q.isdigit():
            reservas = reservas.filter(jugador_principal__usuario__dni=q)
        elif q.startswith('@'):
            reservas = reservas.filter(jugador_principal__usuario__username__icontains=q[1:])
        else:
            reservas = reservas.filter(
                Q(jugador_principal__usuario__first_name__icontains=q) |
                Q(jugador_principal__usuario__last_name__icontains=q)
            )
        for r in reservas:
            j = r.jugador_principal
            if j:
                resultados.append({
                    'id': j.id,
                    'nombre': f"{j.usuario.first_name} {j.usuario.last_name}",
                    'usuario': j.usuario.username,
                    'dni': j.usuario.dni or '',
                    'nombre_real': j.usuario.nombre_real or ''
                })
    return JsonResponse(resultados, safe=False)
from django.http import JsonResponse



@login_required
def fechas_ocupadas_cancha(request, cancha_id):
    """
    Devuelve un array de fechas (YYYY-MM-DD) en las que la cancha está completamente ocupada:
    - TODOS los horarios de la fecha están ocupados (por reserva simple, fija no liberada, o turno bloqueado/no disponible)
    La lógica es equivalente a obtener_horarios_disponibles.
    """
    from reservas.models import Turno, Reserva, ReservaFija, ReservaFijaLiberacion
    from django.db.models import Q
    from datetime import timedelta, datetime
    from django.utils import timezone
    from .models import Cancha

    hoy = timezone.now().date()
    cancha = Cancha.objects.get(id=cancha_id)
    dias_a_buscar = 31  # Buscar hasta 1 mes adelante
    fechas_ocupadas = set()

    for i in range(dias_a_buscar):
        fecha = hoy + timedelta(days=i)
        dia_semana = fecha.weekday()
        # Generar todos los horarios posibles para la cancha en ese día
        if not cancha.horario_apertura or not cancha.horario_cierre:
            continue
        hora_actual = datetime.combine(fecha, cancha.horario_apertura)
        hora_cierre = datetime.combine(fecha, cancha.horario_cierre)
        duracion = timedelta(minutes=cancha.duracion_turno_minutos or 90)
        todos_ocupados = True
        while hora_actual + duracion <= hora_cierre:
            hora_str = hora_actual.time().strftime('%H:%M')
            hora_fin = (hora_actual + duracion).time().strftime('%H:%M')
            ocupado = False
            # 1. ¿Hay un turno para ese horario y está ocupado?
            turno = Turno.objects.filter(cancha=cancha, fecha=fecha, hora_inicio=hora_actual.time()).first()
            if turno:
                if turno.estado != 'DISPONIBLE':
                    ocupado = True
            # 2. ¿Hay una reserva simple para ese horario?
            if not ocupado:
                if Reserva.objects.filter(cancha=cancha, fecha=fecha, hora_inicio=hora_actual.time(), estado__in=['PENDIENTE', 'CONFIRMADA']).exists():
                    ocupado = True
            # 3. ¿Hay una reserva fija activa y no liberada que INICIA en este horario?
            if not ocupado:
                reservas_fijas = ReservaFija.objects.filter(
                    cancha=cancha,
                    dia_semana=dia_semana,
                    estado='ACTIVA',
                    fecha_inicio__lte=fecha
                ).filter(
                    Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha)
                )
                ocupado_fijo = False
                for rf in reservas_fijas:
                    # Si está liberada, no bloquear
                    if ReservaFijaLiberacion.objects.filter(reserva_fija=rf, fecha=fecha).exists():
                        continue
                    # Solo bloquear si el inicio del slot coincide con el inicio de la reserva fija
                    if hora_actual.time() == rf.hora_inicio:
                        ocupado_fijo = True
                        break
                if ocupado_fijo:
                    ocupado = True
            if not ocupado:
                todos_ocupados = False
                break
            hora_actual += duracion
        if todos_ocupados:
            fechas_ocupadas.add(fecha.isoformat())

    return JsonResponse(list(fechas_ocupadas), safe=False)

@login_required
def eliminar_complejo(request, slug):
    """
    Elimina un complejo y todo lo relacionado (canchas, reservas, etc) en cascada.
    Solo el dueño puede eliminarlo.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    complejo = get_object_or_404(Complejo, slug=slug)
    if complejo.dueno.usuario != request.user:
        return JsonResponse({'error': 'No tienes permiso para eliminar este complejo.'}, status=403)
    nombre = complejo.nombre
    complejo.delete()
    return JsonResponse({'success': True, 'message': f'Complejo "{nombre}" eliminado correctamente.'})


