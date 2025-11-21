# Habilidades asociadas a cada deporte
class HabilidadDeporte(models.Model):
    deporte = models.ForeignKey('Deporte', on_delete=models.CASCADE, related_name='habilidades')
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = ('deporte', 'nombre')
        verbose_name = 'Habilidad de Deporte'
        verbose_name_plural = 'Habilidades de Deporte'

    def __str__(self):
        return f"{self.deporte.nombre} - {self.nombre}"

# Categorías asociadas a cada deporte
class CategoriaDeporte(models.Model):
    deporte = models.ForeignKey('Deporte', on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = ('deporte', 'nombre')
        verbose_name = 'Categoría de Deporte'
        verbose_name_plural = 'Categorías de Deporte'

    def __str__(self):
        return f"{self.deporte.nombre} - {self.nombre}"
from django.db import models
class Deporte(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Deporte'
        verbose_name_plural = 'Deportes'

    def __str__(self):
        return self.nombre


# Relación intermedia para habilidades/categoría por deporte
class JugadorDeporte(models.Model):
    perfil = models.ForeignKey('PerfilJugador', on_delete=models.CASCADE, related_name='deportes_jugador')
    deporte = models.ForeignKey(Deporte, on_delete=models.CASCADE)
    # Categoría/nivel por deporte (ej: "Intermedio", "Avanzado", "Primera", etc)
    categoria = models.CharField(max_length=50, blank=True)
    # Posición favorita (opcional, depende del deporte)
    posicion_favorita = models.CharField(max_length=100, blank=True)
    # Pie o brazo hábil (opcional, depende del deporte)
    lado_habil = models.CharField(max_length=20, blank=True, help_text='Pie o brazo hábil según el deporte')

    class Meta:
        unique_together = ('perfil', 'deporte')
        verbose_name = 'Deporte del Jugador'
        verbose_name_plural = 'Deportes del Jugador'

    def __str__(self):
        return f"{self.perfil.alias} - {self.deporte.nombre}"
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para DeRevés.
    Extiende AbstractUser con campos adicionales para identificación y OAuth.
    """
    TIPO_USUARIO_CHOICES = [
        ('JUGADOR', 'Jugador'),
        ('DUENIO', 'Dueño de Complejo'),
        ('ORGANIZADOR', 'Organizador de Torneos'),
        ('ADMIN_SISTEMA', 'Administrador del Sistema'),
    ]
    
    PROVIDER_CHOICES = [
        ('local', 'Local'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='JUGADOR'
    )
    telefono = models.CharField(max_length=20, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    
    # Campos de identificación
    dni = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Documento nacional de identidad (dato sensible)"
    )
    nombre_real = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nombre completo real del usuario"
    )
    
    # Campos OAuth
    google_oauth2_id = models.CharField(max_length=200, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='local'
    )
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.username or self.email


class PerfilJugador(models.Model):
    """
    Perfil extendido para usuarios tipo JUGADOR.
    """
    ESTADO_JUEGO_CHOICES = [
        ('RECREATIVO', 'Recreativo'),
        ('COMPETITIVO', 'Competitivo'),
    ]
    
    PIE_HABIL_CHOICES = [
        ('DERECHO', 'Derecho'),
        ('IZQUIERDO', 'Izquierdo'),
        ('AMBOS', 'Ambos'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_jugador')
    alias = models.CharField(max_length=100)
    localidad = models.CharField(max_length=200, blank=True)
    # Ahora las habilidades y categoría van por deporte
    # posicion_favorita y pie_habil/lado_habil se gestionan en JugadorDeporte
    deportes = models.ManyToManyField(Deporte, through='JugadorDeporte', related_name='jugadores')
    estado_juego = models.CharField(
        max_length=20,
        choices=ESTADO_JUEGO_CHOICES,
        default='RECREATIVO'
    )
    fecha_nacimiento = models.DateField(blank=True, null=True)
    biografia = models.TextField(blank=True)
    perfil_publico = models.BooleanField(default=True)
    
    # Estadísticas (denormalizadas para performance)
    partidos_jugados = models.IntegerField(default=0)
    torneos_ganados = models.IntegerField(default=0)
    rating = models.IntegerField(default=1000)
    pelotitas = models.IntegerField(default=0)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Jugador'
        verbose_name_plural = 'Perfiles de Jugadores'
    
    def __str__(self):
        return f"{self.alias} ({self.usuario.email})"


class PerfilDueno(models.Model):
    """
    Perfil extendido para usuarios tipo DUENIO (dueños de complejos).
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_dueno')
    nombre_negocio = models.CharField(max_length=200, blank=True)
    telefono_contacto = models.CharField(max_length=20, blank=True)
    cuit_cuil = models.CharField(max_length=15, blank=True)
    es_organizador_torneos = models.BooleanField(default=False)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Dueño'
        verbose_name_plural = 'Perfiles de Dueños'
    
    def __str__(self):
        return f"{self.usuario.email} - {self.nombre_comercial or 'Sin nombre comercial'}"
