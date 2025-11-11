from django.contrib import admin
from .models import MetodoPago, Reserva, ReservaFija


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['cancha', 'jugador_principal', 'fecha', 'hora_inicio', 'estado', 'pagado']
    list_filter = ['estado', 'pagado', 'fecha']
    search_fields = ['cancha__nombre', 'jugador_principal__alias']
    date_hierarchy = 'fecha'
    readonly_fields = ['creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Información de la reserva', {
            'fields': ('cancha', 'jugador_principal', 'fecha', 'hora_inicio', 'hora_fin')
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
    list_display = ['cancha', 'jugador', 'dia_semana', 'hora_inicio', 'estado', 'fecha_inicio']
    list_filter = ['estado', 'dia_semana']
    search_fields = ['cancha__nombre', 'jugador__alias']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Información de la reserva fija', {
            'fields': ('cancha', 'jugador', 'dia_semana', 'hora_inicio', 'hora_fin', 'fecha_inicio')
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
