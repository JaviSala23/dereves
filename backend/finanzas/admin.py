from django.contrib import admin
from .models import Transaccion, ResumenMensual


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['complejo', 'tipo', 'categoria', 'monto', 'fecha', 'registrado_por']
    list_filter = ['tipo', 'categoria', 'fecha', 'complejo']
    search_fields = ['descripcion', 'complejo__nombre']
    readonly_fields = ['creado_en', 'actualizado_en', 'registrado_por']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('complejo', 'tipo', 'categoria', 'monto', 'fecha')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'comprobante')
        }),
        ('Relaciones', {
            'fields': ('reserva', 'registrado_por')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(ResumenMensual)
class ResumenMensualAdmin(admin.ModelAdmin):
    list_display = ['complejo', 'mes_año', 'total_ingresos', 'total_gastos', 'balance', 'cantidad_reservas']
    list_filter = ['año', 'mes', 'complejo']
    search_fields = ['complejo__nombre']
    readonly_fields = [
        'total_ingresos', 'total_gastos', 'balance',
        'ingresos_reservas', 'ingresos_reservas_fijas', 'ingresos_otros',
        'cantidad_reservas', 'cantidad_transacciones', 'actualizado_en'
    ]
    actions = ['recalcular_resumenes']
    
    fieldsets = (
        ('Período', {
            'fields': ('complejo', 'año', 'mes')
        }),
        ('Totales', {
            'fields': ('total_ingresos', 'total_gastos', 'balance')
        }),
        ('Desglose de Ingresos', {
            'fields': ('ingresos_reservas', 'ingresos_reservas_fijas', 'ingresos_otros')
        }),
        ('Estadísticas', {
            'fields': ('cantidad_reservas', 'cantidad_transacciones')
        }),
        ('Auditoría', {
            'fields': ('actualizado_en',)
        }),
    )
    
    def mes_año(self, obj):
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{meses[obj.mes-1]} {obj.año}"
    mes_año.short_description = 'Período'
    
    def recalcular_resumenes(self, request, queryset):
        for resumen in queryset:
            resumen.calcular_resumen()
        self.message_user(request, f'{queryset.count()} resúmenes recalculados.')
    recalcular_resumenes.short_description = "Recalcular resúmenes seleccionados"

