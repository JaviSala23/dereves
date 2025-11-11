from django.contrib import admin
from .models import Complejo, Cancha, ServicioComplejo


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
