"""
Script para poblar la base de datos con datos de ejemplo.
Ejecutar con: python manage.py shell < poblar_datos.py
"""
from django.contrib.auth import get_user_model
from cuentas.models import PerfilJugador, PerfilDueno
from complejos.models import Complejo, Cancha, ServicioComplejo
from reservas.models import MetodoPago
from decimal import Decimal

Usuario = get_user_model()

print("🌱 Poblando base de datos con datos de ejemplo...")

# Crear usuarios de ejemplo
print("\n👥 Creando usuarios...")

# Jugador 1
if not Usuario.objects.filter(username='juan_perez').exists():
    jugador1 = Usuario.objects.create_user(
        username='juan_perez',
        email='juan@example.com',
        password='password123',
        nombre_real='Juan Pérez',
        tipo_usuario='JUGADOR'
    )
    perfil1 = PerfilJugador.objects.create(
        usuario=jugador1,
        alias='Juanchi',
        posicion_favorita='Delantero',
        pie_habil='DERECHO',
        localidad='Villa Urquiza',
        biografia='Jugador recreativo, me gusta jugar con amigos los fines de semana'
    )
    print(f"✅ Creado jugador: {jugador1.username}")

# Jugador 2
if not Usuario.objects.filter(username='maria_gomez').exists():
    jugador2 = Usuario.objects.create_user(
        username='maria_gomez',
        email='maria@example.com',
        password='password123',
        nombre_real='María Gómez',
        tipo_usuario='JUGADOR'
    )
    perfil2 = PerfilJugador.objects.create(
        usuario=jugador2,
        alias='Mary',
        posicion_favorita='Mediocampista',
        pie_habil='AMBOS',
        localidad='Belgrano',
        biografia='Me encanta el fútbol 5!'
    )
    print(f"✅ Creado jugador: {jugador2.username}")

# Dueño 1
if not Usuario.objects.filter(username='complejo_norte').exists():
    dueno1 = Usuario.objects.create_user(
        username='complejo_norte',
        email='contacto@complejor norte.com',
        password='password123',
        nombre_real='Carlos Rodríguez',
        tipo_usuario='DUENIO'
    )
    perfil_dueno1 = PerfilDueno.objects.create(
        usuario=dueno1,
        nombre_negocio='Complejo Norte',
        telefono_contacto='+54 9 11 1234-5678',
        cuit_cuil='20-12345678-9'
    )
    print(f"✅ Creado dueño: {dueno1.username}")
    
    # Crear complejo
    complejo1 = Complejo.objects.create(
        dueno=perfil_dueno1,
        nombre='Complejo Deportivo Norte',
        descripcion='Moderno complejo deportivo con canchas de última generación',
        direccion='Av. Congreso 4500',
        localidad='Villa Urquiza',
        latitud=-34.5771,
        longitud=-58.4850,
        telefono='+54 9 11 1234-5678',
        email='info@complejonorte.com',
        slug='complejo-norte',
        subdominio='complejonorte'
    )
    print(f"✅ Creado complejo: {complejo1.nombre}")
    
    # Crear canchas
    cancha1 = Cancha.objects.create(
        complejo=complejo1,
        nombre='Cancha 1',
        deporte='FUTBOL5',
        tipo_superficie='Césped sintético',
        techada=True,
        iluminacion=True,
        precio_base=Decimal('8000.00'),
        precio_hora=Decimal('8000.00'),
        horario_apertura='08:00',
        horario_cierre='23:00'
    )
    print(f"✅ Creada cancha: {cancha1.nombre}")
    
    cancha2 = Cancha.objects.create(
        complejo=complejo1,
        nombre='Cancha 2',
        deporte='FUTBOL5',
        tipo_superficie='Césped sintético',
        techada=False,
        iluminacion=True,
        precio_base=Decimal('7000.00'),
        precio_hora=Decimal('7000.00'),
        horario_apertura='08:00',
        horario_cierre='23:00'
    )
    print(f"✅ Creada cancha: {cancha2.nombre}")
    
    cancha3 = Cancha.objects.create(
        complejo=complejo1,
        nombre='Cancha Pádel 1',
        deporte='PADEL',
        tipo_superficie='Cemento',
        techada=False,
        iluminacion=True,
        precio_base=Decimal('6000.00'),
        precio_hora=Decimal('6000.00'),
        horario_apertura='08:00',
        horario_cierre='22:00'
    )
    print(f"✅ Creada cancha: {cancha3.nombre}")
    
    # Servicios
    ServicioComplejo.objects.create(complejo=complejo1, tipo_servicio='VESTUARIOS', descripcion='Vestuarios completos')
    ServicioComplejo.objects.create(complejo=complejo1, tipo_servicio='ESTACIONAMIENTO', descripcion='Estacionamiento gratuito')
    ServicioComplejo.objects.create(complejo=complejo1, tipo_servicio='BUFET', descripcion='Cantina con comidas y bebidas')
    ServicioComplejo.objects.create(complejo=complejo1, tipo_servicio='WIFI', descripcion='WiFi gratis')
    print(f"✅ Creados servicios para {complejo1.nombre}")

# Dueño 2
if not Usuario.objects.filter(username='punto_reves').exists():
    dueno2 = Usuario.objects.create_user(
        username='punto_reves',
        email='info@puntoreves.com',
        password='password123',
        nombre_real='Ana Martínez',
        tipo_usuario='DUENIO'
    )
    perfil_dueno2 = PerfilDueno.objects.create(
        usuario=dueno2,
        nombre_negocio='Punto & Revés',
        telefono_contacto='+54 9 11 9876-5432',
        cuit_cuil='27-98765432-1'
    )
    print(f"✅ Creado dueño: {dueno2.username}")
    
    # Crear complejo
    complejo2 = Complejo.objects.create(
        dueno=perfil_dueno2,
        nombre='Punto & Revés - Palermo',
        descripcion='Club de pádel y tenis en el corazón de Palermo',
        direccion='Thames 1950',
        localidad='Palermo',
        latitud=-34.5835,
        longitud=-58.4304,
        telefono='+54 9 11 9876-5432',
        email='contacto@puntoreves.com',
        slug='punto-y-reves',
        subdominio='puntoreves'
    )
    print(f"✅ Creado complejo: {complejo2.nombre}")
    
    # Crear canchas
    cancha4 = Cancha.objects.create(
        complejo=complejo2,
        nombre='Pádel Court 1',
        deporte='PADEL',
        tipo_superficie='Cemento premium',
        techada=True,
        iluminacion=True,
        precio_base=Decimal('9000.00'),
        precio_hora=Decimal('9000.00'),
        horario_apertura='07:00',
        horario_cierre='23:00'
    )
    print(f"✅ Creada cancha: {cancha4.nombre}")
    
    cancha5 = Cancha.objects.create(
        complejo=complejo2,
        nombre='Pádel Court 2',
        deporte='PADEL',
        tipo_superficie='Cemento premium',
        techada=True,
        iluminacion=True,
        precio_base=Decimal('9000.00'),
        precio_hora=Decimal('9000.00'),
        horario_apertura='07:00',
        horario_cierre='23:00'
    )
    print(f"✅ Creada cancha: {cancha5.nombre}")
    
    cancha6 = Cancha.objects.create(
        complejo=complejo2,
        nombre='Cancha Tenis',
        deporte='TENIS',
        tipo_superficie='Polvo de ladrillo',
        techada=False,
        iluminacion=True,
        precio_base=Decimal('10000.00'),
        precio_hora=Decimal('10000.00'),
        horario_apertura='07:00',
        horario_cierre='21:00'
    )
    print(f"✅ Creada cancha: {cancha6.nombre}")
    
    # Servicios
    ServicioComplejo.objects.create(complejo=complejo2, tipo_servicio='VESTUARIOS', descripcion='Vestuarios premium')
    ServicioComplejo.objects.create(complejo=complejo2, tipo_servicio='PARRILLA', descripcion='Parrilla y quincho')
    ServicioComplejo.objects.create(complejo=complejo2, tipo_servicio='BUFET', descripcion='Bar y restaurante')
    ServicioComplejo.objects.create(complejo=complejo2, tipo_servicio='ESTACIONAMIENTO', descripcion='Estacionamiento techado')
    print(f"✅ Creados servicios para {complejo2.nombre}")

# Métodos de pago
print("\n💳 Creando métodos de pago...")
if not MetodoPago.objects.filter(nombre='Efectivo').exists():
    MetodoPago.objects.create(
        nombre='Efectivo',
        activo=True
    )
    print("✅ Creado método: Efectivo")

if not MetodoPago.objects.filter(nombre='Transferencia Bancaria').exists():
    MetodoPago.objects.create(
        nombre='Transferencia Bancaria',
        activo=True
    )
    print("✅ Creado método: Transferencia")

if not MetodoPago.objects.filter(nombre='MercadoPago').exists():
    MetodoPago.objects.create(
        nombre='MercadoPago',
        activo=True
    )
    print("✅ Creado método: MercadoPago")

print("\n✨ ¡Base de datos poblada exitosamente!")
print("\n📝 Usuarios de prueba:")
print("   - Jugador 1: juan_perez / password123")
print("   - Jugador 2: maria_gomez / password123")
print("   - Dueño 1: complejo_norte / password123")
print("   - Dueño 2: punto_reves / password123")
print("   - Admin: admin / (contraseña configurada previamente)")
