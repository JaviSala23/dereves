from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilJugador, PerfilDueno


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'tipo_usuario', 'nombre_real', 'provider', 'is_active']
    list_filter = ['tipo_usuario', 'provider', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'nombre_real', 'dni']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información DeRevés', {
            'fields': ('tipo_usuario', 'telefono', 'foto_perfil', 'dni', 'nombre_real')
        }),
        ('OAuth', {
            'fields': ('google_oauth2_id', 'email_verified', 'provider')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )
    readonly_fields = ['creado_en', 'actualizado_en']


@admin.register(PerfilJugador)
class PerfilJugadorAdmin(admin.ModelAdmin):
    list_display = ['alias', 'usuario', 'estado_juego', 'rating', 'pelotitas']
    list_filter = ['estado_juego', 'perfil_publico']
    search_fields = ['alias', 'usuario__email', 'usuario__username']
    readonly_fields = ['creado_en', 'actualizado_en']


@admin.register(PerfilDueno)
class PerfilDuenoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'nombre_negocio', 'telefono_contacto', 'es_organizador_torneos']
    list_filter = ['es_organizador_torneos']
    search_fields = ['usuario__email', 'nombre_negocio']
    readonly_fields = ['creado_en', 'actualizado_en']
