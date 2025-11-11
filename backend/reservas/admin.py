from django.contrib import admin
from .models import (
    MetodoPago, Turno, Reserva, ReservaFija,
    PartidoAbierto, JugadorPartido, Torneo, BloqueoTorneo
)


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['cancha', 'fecha', 'hora_inicio', 'hora_fin', 'estado', 'precio']
    list_filter = ['estado', 'fecha', 'cancha']
    search_fields = ['cancha__nombre', 'cancha__complejo__nombre']
    date_hierarchy = 'fecha'
    readonly_fields = ['creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Información del turno', {
            'fields': ('cancha', 'fecha', 'hora_inicio', 'hora_fin', 'precio')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['turno', 'get_jugador_display', 'reservado_por_dueno', 'estado', 'pagado']
    list_filter = ['estado', 'pagado', 'reservado_por_dueno']
    search_fields = ['turno__cancha__nombre', 'jugador__alias', 'nombre_cliente_sin_cuenta']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    def get_jugador_display(self, obj):
        if obj.reservado_por_dueno:
            return obj.nombre_cliente_sin_cuenta or 'Cliente sin nombre'
        return obj.jugador.alias if obj.jugador else 'Sin jugador'
    get_jugador_display.short_description = 'Cliente/Jugador'
    
    fieldsets = (
        ('Información de la reserva', {
            'fields': ('turno', 'jugador', 'reservado_por_dueno')
        }),
        ('Cliente sin cuenta', {
            'fields': ('nombre_cliente_sin_cuenta', 'telefono_cliente', 'email_cliente'),
            'classes': ('collapse',)
        }),
        ('Pago', {
            'fields': ('precio', 'metodo_pago', 'pagado')
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )


@admin.register(ReservaFija)
class ReservaFijaAdmin(admin.ModelAdmin):
    list_display = ['cancha', 'get_cliente_display', 'dia_semana', 'hora_inicio', 'estado', 'fecha_inicio']
    list_filter = ['estado', 'dia_semana']
    search_fields = ['cancha__nombre', 'jugador__alias', 'nombre_cliente']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    def get_cliente_display(self, obj):
        return obj.jugador.alias if obj.jugador else obj.nombre_cliente
    get_cliente_display.short_description = 'Cliente'
    
    fieldsets = (
        ('Información de la reserva fija', {
            'fields': ('cancha', 'jugador', 'nombre_cliente', 'dia_semana', 'hora_inicio', 'hora_fin', 'fecha_inicio', 'fecha_fin')
        }),
        ('Pago', {
            'fields': ('precio',)
        }),
        ('Estado', {
            'fields': ('estado', 'creada_por', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )


@admin.register(PartidoAbierto)
class PartidoAbiertoAdmin(admin.ModelAdmin):
    list_display = ['turno', 'creador', 'estado', 'nivel', 'cupo_jugadores', 'jugadores_actuales']
    list_filter = ['estado', 'nivel', 'creado_por_dueno']
    search_fields = ['turno__cancha__nombre', 'creador__username', 'descripcion']
    readonly_fields = ['token_invitacion', 'creado_en', 'actualizado_en', 'get_link_invitacion']
    
    def get_link_invitacion(self, obj):
        return obj.get_link_invitacion()
    get_link_invitacion.short_description = 'Link de invitación'
    
    fieldsets = (
        ('Información del partido', {
            'fields': ('turno', 'creador', 'creado_por_dueno')
        }),
        ('Configuración', {
            'fields': ('cupo_jugadores', 'nivel', 'categoria', 'descripcion', 'precio_por_jugador')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Invitación', {
            'fields': ('token_invitacion', 'get_link_invitacion')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )


@admin.register(JugadorPartido)
class JugadorPartidoAdmin(admin.ModelAdmin):
    list_display = ['partido', 'get_jugador_display', 'es_creador', 'confirmado', 'pagado']
    list_filter = ['confirmado', 'pagado', 'es_creador', 'es_invitado']
    search_fields = ['jugador__alias', 'nombre_invitado', 'partido__turno__cancha__nombre']
    readonly_fields = ['unido_en', 'actualizado_en']
    
    def get_jugador_display(self, obj):
        if obj.es_invitado:
            return f"{obj.nombre_invitado} (Invitado)"
        return obj.jugador.alias if obj.jugador else 'Sin jugador'
    get_jugador_display.short_description = 'Jugador'
    
    fieldsets = (
        ('Partido', {
            'fields': ('partido', 'jugador', 'es_invitado')
        }),
        ('Datos invitado', {
            'fields': ('nombre_invitado', 'telefono_invitado', 'email_invitado'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('confirmado', 'es_creador', 'pagado')
        }),
        ('Auditoría', {
            'fields': ('unido_en', 'actualizado_en')
        }),
    )


@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'complejo', 'fecha_inicio', 'fecha_fin', 'estado']
    list_filter = ['estado', 'fecha_inicio']
    search_fields = ['nombre', 'complejo__nombre']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Información del torneo', {
            'fields': ('nombre', 'complejo', 'descripcion')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )


@admin.register(BloqueoTorneo)
class BloqueoTorneoAdmin(admin.ModelAdmin):
    list_display = ['torneo', 'cancha', 'fecha', 'hora_inicio', 'hora_fin']
    list_filter = ['fecha', 'torneo']
    search_fields = ['torneo__nombre', 'cancha__nombre']
    readonly_fields = ['creado_en']
    
    fieldsets = (
        ('Información del bloqueo', {
            'fields': ('torneo', 'cancha', 'fecha', 'hora_inicio', 'hora_fin')
        }),
        ('Auditoría', {
            'fields': ('creado_en',)
        }),
    )
