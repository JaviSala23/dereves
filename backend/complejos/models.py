from django.db import models
from django.conf import settings


class Localidad(models.Model):
    """
    Modelo para localidades personalizadas agregadas por usuarios.
    """
    nombre = models.CharField(max_length=200)
    provincia = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, default='Argentina')
    
    # Usuario que agregó la localidad
    agregada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='localidades_agregadas'
    )
    
    # Validación y moderación
    aprobada = models.BooleanField(
        default=True,
        help_text="Si está aprobada para uso público"
    )
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Localidad'
        verbose_name_plural = 'Localidades'
        ordering = ['provincia', 'nombre']
        unique_together = ['nombre', 'provincia', 'pais']
    
    def __str__(self):
        return f"{self.nombre}, {self.provincia}"


class Complejo(models.Model):
    """
    Modelo para complejos deportivos.
    Incluye geolocalización con coordenadas de Google Maps.
    """
    dueno = models.ForeignKey(
        'cuentas.PerfilDueno',
        on_delete=models.CASCADE,
        related_name='complejos'
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    direccion = models.CharField(max_length=300)
    localidad = models.CharField(max_length=200)
    provincia = models.CharField(max_length=100, default='Córdoba')
    pais = models.CharField(max_length=100, default='Argentina')
    
    # Geolocalización (Google Maps)
    latitud = models.FloatField(
        help_text="Coordenada latitud WGS84 para búsquedas y mapas"
    )
    longitud = models.FloatField(
        help_text="Coordenada longitud WGS84 para búsquedas y mapas"
    )
    google_place_id = models.CharField(max_length=200, blank=True)
    direccion_formateada = models.CharField(
        max_length=400,
        blank=True,
        help_text="Dirección tal como la devuelve Google Places API"
    )
    google_maps_url = models.URLField(blank=True)
    
    # Contacto
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    sitio_web = models.URLField(blank=True)
    
    # URL y subdominio
    slug = models.SlugField(unique=True)
    subdominio = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Se genera automáticamente. Ej: puntoyreves para puntoyreves.dereves.ar"
    )
    
    logo = models.ImageField(upload_to='complejos/logos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Genera automáticamente el subdominio si está vacío."""
        if not self.subdominio:
            self.subdominio = self.slug
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Complejo'
        verbose_name_plural = 'Complejos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Cancha(models.Model):
    """
    Modelo para canchas dentro de un complejo.
    """
    DEPORTE_CHOICES = [
        ('PADEL', 'Pádel'),
        ('FUTBOL5', 'Fútbol 5'),
        ('FUTBOL7', 'Fútbol 7'),
        ('FUTBOL11', 'Fútbol 11'),
        ('TENIS', 'Tenis'),
        ('FUTBOL_TENIS', 'Fútbol-Tenis'),
        ('BASQUET', 'Básquet'),
        ('VOLEY', 'Voley'),
    ]
    
    TIPO_PARED_CHOICES = [
        ('VIDRIO', 'Vidrio'),
        ('CEMENTO', 'Cemento'),
        ('LADRILLO', 'Ladrillo'),
        ('MALLA', 'Malla Metálica'),
        ('MIXTA', 'Mixta (Vidrio y Cemento)'),
        ('PANORAMICA', 'Panorámica (Todo Vidrio)'),
        ('ALAMBRADO', 'Alambrado'),
        ('SIN_PARED', 'Sin Paredes / Cancha Abierta'),
    ]
    
    complejo = models.ForeignKey(
        Complejo,
        on_delete=models.CASCADE,
        related_name='canchas'
    )
    nombre = models.CharField(max_length=100)
    deporte = models.CharField(max_length=20, choices=DEPORTE_CHOICES)
    tipo_superficie = models.CharField(max_length=100, blank=True)
    tipo_pared = models.CharField(
        max_length=20,
        choices=TIPO_PARED_CHOICES,
        blank=True,
        help_text="Tipo de pared/cerramiento de la cancha"
    )
    techada = models.BooleanField(default=False)
    iluminacion = models.BooleanField(default=False)
    foto = models.ImageField(upload_to='canchas/', blank=True, null=True)
    
    # Precios y horarios
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio base por turno"
    )
    precio_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio por hora",
        null=True,
        blank=True
    )
    horario_apertura = models.TimeField(default='08:00')
    horario_cierre = models.TimeField(default='23:00')
    
    duracion_turno_minutos = models.IntegerField(default=60)
    activo = models.BooleanField(default=True)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Si no se especifica precio_hora, usar precio_base
        if not self.precio_hora:
            self.precio_hora = self.precio_base
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'
        ordering = ['complejo', 'nombre']
    
    def __str__(self):
        return f"{self.complejo.nombre} - {self.nombre}"


class ServicioComplejo(models.Model):
    """
    Servicios adicionales que ofrece un complejo.
    """
    TIPO_SERVICIO_CHOICES = [
        ('BUFET', 'Bufet'),
        ('PARRILLA', 'Parrilla'),
        ('AGUA_CALIENTE', 'Agua Caliente'),
        ('WIFI', 'Wi-Fi'),
        ('SALON', 'Salón'),
        ('ESTACIONAMIENTO', 'Estacionamiento'),
        ('VESTUARIOS', 'Vestuarios'),
        ('QUINCHO', 'Quincho'),
    ]
    
    complejo = models.ForeignKey(
        Complejo,
        on_delete=models.CASCADE,
        related_name='servicios'
    )
    tipo_servicio = models.CharField(max_length=30, choices=TIPO_SERVICIO_CHOICES)
    descripcion = models.TextField(blank=True)
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Servicio de Complejo'
        verbose_name_plural = 'Servicios de Complejos'
        unique_together = ['complejo', 'tipo_servicio']
    
    def __str__(self):
        return f"{self.complejo.nombre} - {self.get_tipo_servicio_display()}"
