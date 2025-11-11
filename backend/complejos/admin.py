from django.contrib import admin
from .models import Complejo, Cancha, ServicioComplejo, Localidad, FotoComplejo


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'provincia', 'pais', 'aprobada', 'agregada_por', 'creado_en']
    list_filter = ['provincia', 'pais', 'aprobada', 'creado_en']
    search_fields = ['nombre', 'provincia']
    readonly_fields = ['creado_en', 'actualizado_en', 'agregada_por']
    actions = ['aprobar_localidades', 'desaprobar_localidades']
    
    fieldsets = (
        ('Información', {
            'fields': ('nombre', 'provincia', 'pais')
        }),
        ('Estado', {
            'fields': ('aprobada', 'agregada_por')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )
    
    def aprobar_localidades(self, request, queryset):
        count = queryset.update(aprobada=True)
        self.message_user(request, f'{count} localidades aprobadas exitosamente.')
    aprobar_localidades.short_description = "Aprobar localidades seleccionadas"
    
    def desaprobar_localidades(self, request, queryset):
        count = queryset.update(aprobada=False)
        self.message_user(request, f'{count} localidades desaprobadas.')
    desaprobar_localidades.short_description = "Desaprobar localidades seleccionadas"


@admin.register(Complejo)
class ComplejoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'dueno', 'localidad', 'subdominio', 'activo']
    list_filter = ['activo', 'localidad']
    search_fields = ['nombre', 'descripcion', 'subdominio']
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ['creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('dueno', 'nombre', 'descripcion', 'logo', 'activo')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'localidad', 'latitud', 'longitud', 
                      'google_place_id', 'direccion_formateada', 'google_maps_url')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'sitio_web')
        }),
        ('Web', {
            'fields': ('slug', 'subdominio')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'complejo', 'deporte', 'precio_base', 'activo']
    list_filter = ['deporte', 'activo', 'techada', 'iluminacion']
    search_fields = ['nombre', 'complejo__nombre']
    readonly_fields = ['creado_en', 'actualizado_en']


@admin.register(ServicioComplejo)
class ServicioComplejoAdmin(admin.ModelAdmin):
    list_display = ['complejo', 'tipo_servicio']
    list_filter = ['tipo_servicio']
    search_fields = ['complejo__nombre']


@admin.register(FotoComplejo)
class FotoComplejoAdmin(admin.ModelAdmin):
    list_display = ['complejo', 'es_principal', 'orden', 'creado_en']
    list_filter = ['es_principal', 'creado_en']
    search_fields = ['complejo__nombre', 'descripcion']
    readonly_fields = ['creado_en', 'actualizado_en']
    list_editable = ['orden', 'es_principal']
    
    fieldsets = (
        ('Información', {
            'fields': ('complejo', 'imagen', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('orden', 'es_principal')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )
