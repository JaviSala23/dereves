# Sistema de Finanzas Completo - DeRevés

## Resumen
Se ha implementado un sistema completo de gestión financiera para que los dueños de complejos puedan:
- Registrar ingresos y gastos
- Ver dashboard con estadísticas y gráficos
- Generar reportes detallados
- Exportar datos a CSV
- Calcular resúmenes mensuales automáticos

## Archivos Creados/Modificados

### 1. Modelos (`finanzas/models.py`)

#### **Transaccion**
Registra todas las transacciones financieras:
- Tipo: Ingreso o Gasto
- Categorías personalizadas por tipo
- Monto, descripción, fecha
- Comprobante opcional (foto/PDF)
- Relación con reservas
- Auditoría automática

#### **ResumenMensual**
Calcula automáticamente resúmenes mensuales:
- Total ingresos/gastos/balance
- Desglose de ingresos por tipo
- Estadísticas (cantidad de reservas y transacciones)
- Método `calcular_resumen()` para recalcular

### 2. Vistas (`finanzas/views.py`)

#### **dashboard_finanzas**
- URL: `/finanzas/`
- Dashboard principal con:
  - Tarjetas de resumen (ingresos, gastos, balance)
  - Gráfico de últimos 6 meses (Chart.js)
  - Top 5 categorías de gastos
  - Últimas 20 transacciones
  - Modal para registrar nueva transacción

#### **registrar_transaccion**
- URL: `/finanzas/registrar/`
- API POST para registrar transacciones
- Actualiza automáticamente el resumen mensual
- Maneja subida de comprobantes

#### **eliminar_transaccion**
- URL: `/finanzas/transaccion/<id>/eliminar/`
- Elimina transacción y recalcula resumen

#### **reporte_finanzas**
- URL: `/finanzas/reporte/`
- Reporte detallado con filtros:
  - Por complejo
  - Por rango de fechas
  - Por tipo (ingreso/gasto)
  - Por categoría
- Muestra totales calculados

#### **exportar_reporte**
- URL: `/finanzas/exportar/`
- Exporta transacciones filtradas a CSV
- Compatible con Excel (BOM UTF-8)

### 3. Templates

#### **dashboard.html**
- Diseño moderno con tarjetas de estadísticas
- Gráfico interactivo (Chart.js)
- Lista de transacciones con opción de eliminar
- Modal para agregar transacciones
- Selector dinámico de complejo
- Categorías dinámicas según tipo
- SweetAlert2 para confirmaciones

#### **reporte.html**
- Filtros avanzados
- Tabla de transacciones
- Resumen con totales
- Botón de exportar a CSV

### 4. URLs (`finanzas/urls.py`)
```python
/finanzas/                              # Dashboard
/finanzas/registrar/                    # API: Registrar transacción
/finanzas/transaccion/<id>/eliminar/    # API: Eliminar transacción
/finanzas/reporte/                      # Reporte detallado
/finanzas/exportar/                     # Exportar CSV
```

### 5. Admin (`finanzas/admin.py`)
- **TransaccionAdmin**: Gestión completa de transacciones
- **ResumenMensualAdmin**: Ver y recalcular resúmenes
- Acciones masivas para recalcular resúmenes
- Filtros y búsquedas avanzadas

## Categorías Implementadas

### Ingresos
- Reserva de Cancha
- Reserva Fija
- Seña/Adelanto
- Otro Ingreso

### Gastos
- Mantenimiento
- Servicios (Luz, Agua, Gas)
- Sueldos
- Equipamiento
- Limpieza
- Impuestos
- Publicidad
- Otro Gasto

## Instrucciones de Instalación

### Paso 1: Ejecutar Migraciones
```bash
cd backend
python manage.py makemigrations finanzas
python manage.py migrate
```

### Paso 2: Acceder al Sistema
1. **Dashboard**: Ve a `/finanzas/`
2. **Reporte**: Ve a `/finanzas/reporte/`

### Paso 3: Vincular desde el Perfil
Busca el botón "Finanzas" en `/accounts/perfil/` y actualiza el enlace:
```html
<a href="{% url 'finanzas:dashboard' %}" class="btn btn-primary">
    <span class="material-symbols-rounded">account_balance</span>
    Finanzas
</a>
```

## Funcionalidades Principales

### ✅ Dashboard Financiero
- **Tarjetas de resumen**: Ingresos, Gastos, Balance del mes
- **Gráfico histórico**: Últimos 6 meses con Chart.js
- **Top gastos**: Las 5 categorías con más gastos
- **Transacciones recientes**: Últimas 20 con opción de eliminar
- **Selector de complejo**: Para dueños con múltiples complejos
- **Modal de registro**: Formulario completo para nuevas transacciones

### ✅ Registro de Transacciones
- Tipo: Ingreso o Gasto
- Categorías dinámicas según el tipo
- Monto con decimales
- Descripción detallada
- Fecha personalizable
- Comprobante opcional (foto/PDF)
- Actualización automática de resúmenes

### ✅ Gestión de Transacciones
- Visualización clara con colores (verde=ingreso, rojo=gasto)
- Eliminar con confirmación (SweetAlert2)
- Filtros por período y tipo
- Búsqueda en admin

### ✅ Reportes
- Filtros avanzados:
  - Por complejo
  - Rango de fechas
  - Tipo de transacción
  - Categoría específica
- Cálculo automático de totales
- Vista en tabla responsive
- Exportación a CSV

### ✅ Exportación
- Formato CSV compatible con Excel
- BOM UTF-8 para caracteres especiales
- Incluye todos los campos principales
- Respeta filtros aplicados

### ✅ Resúmenes Automáticos
- Cálculo automático al registrar/eliminar transacciones
- Desglose detallado de ingresos
- Estadísticas de reservas
- Recalculable manualmente desde el admin

## Características de Seguridad

✅ **Control de acceso**: Solo dueños de complejos
✅ **Validación de permisos**: Solo pueden ver/editar sus propios complejos
✅ **Auditoría**: Se registra quién creó cada transacción
✅ **Protección CSRF**: En todos los formularios
✅ **SweetAlert2**: Confirmaciones antes de eliminar

## Características de UX

✅ **Diseño moderno**: Tarjetas con gradientes
✅ **Colores semánticos**: Verde=ingresos, Rojo=gastos, Azul=balance
✅ **Gráficos interactivos**: Chart.js con tooltips
✅ **Responsive**: Funciona en móviles
✅ **Feedback visual**: Mensajes de éxito/error
✅ **Carga dinámica**: Categorías según tipo
✅ **Preview de datos**: Antes de guardar

## Flujo de Uso

1. **Dueño accede al dashboard** (`/finanzas/`)
2. Ve resumen del mes actual de su complejo
3. Puede cambiar de complejo si tiene varios
4. **Registrar nueva transacción**:
   - Click en "Nueva Transacción"
   - Selecciona tipo (ingreso/gasto)
   - Elige categoría (se cargan según el tipo)
   - Ingresa monto y descripción
   - Opcional: fecha y comprobante
   - Guarda
5. **El sistema automáticamente**:
   - Registra la transacción
   - Actualiza el resumen mensual
   - Recalcula totales
   - Actualiza gráficos
6. **Ver reportes detallados**:
   - Click en "Ver Reporte Completo"
   - Aplica filtros según necesidad
   - Exporta a CSV si necesita

## Integración con Reservas

El sistema está preparado para:
- Crear transacciones automáticas al confirmar reservas
- Vincular transacciones con reservas específicas
- Diferenciar entre reservas puntuales y fijas

### Para activar (opcional):
En el modelo de Reserva, agregar signal:
```python
from django.db.models.signals import post_save
from finanzas.models import Transaccion

@receiver(post_save, sender=Reserva)
def crear_transaccion_reserva(sender, instance, created, **kwargs):
    if instance.estado == 'CONFIRMADA' and not instance.transacciones.exists():
        Transaccion.objects.create(
            complejo=instance.cancha.complejo,
            tipo='INGRESO',
            categoria='RESERVA',
            monto=instance.precio,
            descripcion=f'Reserva de {instance.cancha.nombre}',
            fecha=instance.fecha,
            reserva=instance
        )
```

## Próximas Mejoras (Opcional)

- 📊 Más gráficos (torta, líneas)
- 📅 Proyecciones futuras
- 💰 Metas financieras
- 🔔 Alertas de gastos excesivos
- 📱 Notificaciones por email
- 🏦 Integración con pasarelas de pago
- 📈 Análisis de rentabilidad por cancha
- 🎯 Presupuestos mensuales

## Notas Técnicas

- **Chart.js**: Para gráficos interactivos
- **Bootstrap 5**: Para estilos
- **SweetAlert2**: Para modales y alertas
- **Material Symbols**: Para iconos
- **Ajax**: Para operaciones sin recargar página
- **CSV**: Con BOM para Excel

## Soporte

Si hay errores:
1. Verificar que las migraciones se aplicaron correctamente
2. Verificar que el usuario sea tipo "DUENIO"
3. Verificar que tenga al menos un complejo activo
4. Revisar la consola del navegador por errores JavaScript
5. Revisar los logs del servidor

---

**¡Sistema de Finanzas Completo y Listo para Usar!** 🎉💰📊
