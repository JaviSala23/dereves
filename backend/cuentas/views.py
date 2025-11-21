from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Usuario, PerfilJugador, PerfilDueno, Deporte, JugadorDeporte, HabilidadDeporte, CategoriaDeporte


@login_required
def mi_perfil(request):
    """Vista del perfil del usuario logueado."""
    usuario = request.user
    
    # Obtener o crear perfil según tipo de usuario
    perfil = None
    
    if usuario.tipo_usuario == 'JUGADOR':
        perfil, created = PerfilJugador.objects.get_or_create(
            usuario=usuario,
            defaults={'alias': usuario.username}
        )
    elif usuario.tipo_usuario == 'DUENIO':
        perfil, created = PerfilDueno.objects.get_or_create(usuario=usuario)
    
    context = {
        'perfil': perfil,
    }
    return render(request, 'cuentas/mi_perfil.html', context)


@login_required
def editar_perfil(request):
    """Permite al usuario editar su perfil."""
    usuario = request.user
    
    # Obtener o crear perfil
    perfil = None
    
    if usuario.tipo_usuario == 'JUGADOR':
        perfil, _ = PerfilJugador.objects.get_or_create(
            usuario=usuario,
            defaults={'alias': usuario.username}
        )
    elif usuario.tipo_usuario == 'DUENIO':
        perfil, _ = PerfilDueno.objects.get_or_create(usuario=usuario)
    
    if request.method == 'POST':
        # Actualizar datos básicos del usuario
        usuario.username = request.POST.get('username', usuario.username)
        usuario.email = request.POST.get('email', usuario.email)
        usuario.nombre_real = request.POST.get('nombre_real', '')
        # Actualizar foto de perfil si se subió una nueva
        if 'foto_perfil' in request.FILES:
            usuario.foto_perfil = request.FILES['foto_perfil']
        usuario.save()
        # Actualizar perfil según tipo
        if usuario.tipo_usuario == 'JUGADOR' and perfil:
            perfil.biografia = request.POST.get('biografia', '')
            perfil.localidad = request.POST.get('localidad', '')
            fecha_nac = request.POST.get('fecha_nacimiento', '')
            if fecha_nac:
                perfil.fecha_nacimiento = fecha_nac
            perfil.perfil_publico = 'perfil_publico' in request.POST
            perfil.save()
            # --- Manejo de deportes y habilidades ---
            deportes_ids = request.POST.getlist('deportes')
            deportes_objs = Deporte.objects.filter(id__in=deportes_ids)
            # Eliminar los deportes que ya no están
            JugadorDeporte.objects.filter(perfil=perfil).exclude(deporte__in=deportes_objs).delete()
            for deporte in deportes_objs:
                jd, _ = JugadorDeporte.objects.get_or_create(perfil=perfil, deporte=deporte)
                jd.categoria = request.POST.get(f'categoria_{deporte.id}', '')
                jd.posicion_favorita = request.POST.get(f'posicion_{deporte.id}', '')
                jd.lado_habil = request.POST.get(f'lado_{deporte.id}', '')
                jd.save()
        elif usuario.tipo_usuario == 'DUENIO' and perfil:
            perfil.nombre_negocio = request.POST.get('nombre_negocio', '')
            perfil.telefono_contacto = request.POST.get('telefono_contacto', '')
            perfil.cuit_cuil = request.POST.get('cuit_cuil', '')
            perfil.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('cuentas:mi_perfil')
    
    # --- Contexto para template ---
    deportes_disponibles = Deporte.objects.filter(activo=True).order_by('nombre')
    deportes_seleccionados = []
    jugador_deportes = []
    habilidades_por_deporte = {}
    categorias_por_deporte = {}
    if usuario.tipo_usuario == 'JUGADOR' and perfil:
        jugador_deportes_db = list(JugadorDeporte.objects.filter(perfil=perfil).select_related('deporte'))
        deportes_seleccionados = [jd.deporte.id for jd in jugador_deportes_db]
        # Para cada deporte seleccionado, asegurar que haya un objeto JugadorDeporte (real o virtual)
        jugador_deportes = []
        for deporte in deportes_disponibles:
            if deporte.id in deportes_seleccionados:
                # Buscar si ya existe en la DB
                jd = next((j for j in jugador_deportes_db if j.deporte.id == deporte.id), None)
                if jd:
                    jugador_deportes.append(jd)
                else:
                    jugador_deportes.append(JugadorDeporte(perfil=perfil, deporte=deporte))
        # Poblar habilidades y categorías por deporte
        for deporte in deportes_disponibles:
            habilidades_por_deporte[deporte.id] = list(HabilidadDeporte.objects.filter(deporte=deporte, activa=True).order_by('nombre'))
            categorias_por_deporte[deporte.id] = list(CategoriaDeporte.objects.filter(deporte=deporte, activa=True).order_by('nombre'))
    context = {
        'perfil': perfil,
        'deportes_disponibles': deportes_disponibles,
        'deportes_seleccionados': deportes_seleccionados,
        'jugador_deportes': jugador_deportes,
        'habilidades_por_deporte': habilidades_por_deporte,
        'categorias_por_deporte': categorias_por_deporte,
    }
    return render(request, 'cuentas/editar_perfil.html', context)


def perfil_publico_jugador(request, id):
    """Vista pública del perfil de un jugador."""
    perfil_jugador = get_object_or_404(PerfilJugador, id=id)
    jugador = perfil_jugador.usuario
    
    context = {
        'jugador': jugador,
        'perfil_jugador': perfil_jugador,
    }
    return render(request, 'cuentas/perfil_publico.html', context)


def registro(request):
    """Registro de nuevo usuario."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        tipo_usuario = request.POST.get('tipo_usuario', 'JUGADOR')
        nombre_real = request.POST.get('nombre_real', '')
        
        # Validaciones
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
        elif Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
        else:
            # Crear usuario
            with transaction.atomic():
                usuario = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    tipo_usuario=tipo_usuario,
                    nombre_real=nombre_real
                )
                
                # Crear perfil correspondiente
                if tipo_usuario == 'JUGADOR':
                    PerfilJugador.objects.create(
                        usuario=usuario,
                        alias=username
                    )
                elif tipo_usuario == 'DUENIO':
                    PerfilDueno.objects.create(usuario=usuario)
                
                # Loguear automáticamente con backend específico
                login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'¡Bienvenido a DeRevés, {username}!')
                return redirect('home')
    
    return render(request, 'cuentas/registro.html')


def login_view(request):
    """Vista de login personalizada."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        usuario = authenticate(request, username=username, password=password)
        
        if usuario is not None:
            login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'¡Bienvenido de nuevo, {usuario.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'cuentas/login.html')


def logout_view(request):
    """Cierra la sesión del usuario."""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('home')
