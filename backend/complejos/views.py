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
    
    # Obtener fecha seleccionada o usar hoy
    fecha_str = request.GET.get('fecha', timezone.now().date().isoformat())
    try:
        from datetime import datetime
        fecha = datetime.fromisoformat(fecha_str).date()
    except ValueError:
        fecha = timezone.now().date()
    
    # No permitir fechas pasadas
    if fecha < timezone.now().date():
        fecha = timezone.now().date()
    
    # Preparar datos de complejos con sus canchas y disponibilidad
    complejos_data = []
    for complejo in complejos:
        canchas = complejo.canchas.filter(activo=True)
        
        if deporte:
            canchas = canchas.filter(deporte=deporte)
        
        if canchas.exists():
            complejos_data.append({
                'complejo': complejo,
                'canchas': canchas,
            })
    
    # Obtener deportes para filtro
    from complejos.models import Cancha
    deportes = Cancha.DEPORTE_CHOICES
    
    # Obtener listas únicas de provincias y países para los filtros
    provincias = Complejo.objects.filter(activo=True).values_list('provincia', flat=True).distinct().order_by('provincia')
    paises = Complejo.objects.filter(activo=True).values_list('pais', flat=True).distinct().order_by('pais')
    
    # Agrupar complejos por país y provincia
    complejos_agrupados = {}
    for item in complejos_data:
        complejo = item['complejo']
        pais_key = complejo.pais
        provincia_key = complejo.provincia
        
        if pais_key not in complejos_agrupados:
            complejos_agrupados[pais_key] = {}
        
        if provincia_key not in complejos_agrupados[pais_key]:
            complejos_agrupados[pais_key][provincia_key] = []
        
        complejos_agrupados[pais_key][provincia_key].append(item)
    
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
    
    context = {
        'complejo': complejo,
        'canchas': canchas,
        'servicios': servicios,
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
            return redirect('complejos:detalle', slug=complejo.slug)
    
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
    """
    API endpoint para obtener horarios disponibles de una cancha en una fecha.
    Actualizado para usar el sistema de Turnos.
    """
    from reservas.models import Turno
    
    cancha = get_object_or_404(Cancha, id=cancha_id, activo=True)
    fecha_str = request.GET.get('fecha', timezone.now().date().isoformat())
    
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)
    
    # No permitir fechas pasadas
    if fecha < timezone.now().date():
        return JsonResponse({'error': 'No se puede reservar en fechas pasadas'}, status=400)
    
    # Verificar que la cancha tenga horarios configurados
    if not cancha.horario_apertura or not cancha.horario_cierre:
        return JsonResponse({'error': 'Esta cancha no tiene horarios configurados'}, status=400)
    
    # Obtener turnos del día
    turnos = Turno.objects.filter(
        cancha=cancha,
        fecha=fecha
    ).order_by('hora_inicio')
    
    # Crear dict de turnos existentes por hora
    turnos_dict = {
        turno.hora_inicio: turno
        for turno in turnos
    }
    
    # Crear lista de horarios
    horarios = []
    hora_actual = cancha.horario_apertura
    duracion = timedelta(minutes=cancha.duracion_turno_minutos or 90)
    
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
                # Turno existe, verificar su estado
                ocupado = turno.estado != 'DISPONIBLE'
                precio = float(turno.precio)
            else:
                # Turno no existe, está disponible
                ocupado = False
                precio = float(cancha.precio_hora)
            
            horarios.append({
                'hora_inicio': hora_actual.strftime('%H:%M'),
                'hora_fin': hora_fin.strftime('%H:%M'),
                'ocupado': ocupado,
                'precio': precio,
            })
        
        # Avanzar según duración del turno
        hora_actual = (datetime.combine(fecha, hora_actual) + duracion).time()
        
        # Evitar loop infinito
        if hora_actual <= (datetime.combine(fecha, hora_actual) - duracion).time():
            break
    
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
