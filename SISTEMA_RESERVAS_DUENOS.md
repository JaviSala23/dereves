# Sistema de Reservas para Dueños - DeRevés

## Cambios Implementados

### 1. ✅ Timezone Configurado
- **Archivo**: `backend/dereves_project/settings.py`
- **Configuración**: 
  - `TIME_ZONE = 'America/Argentina/Buenos_Aires'`
  - `USE_TZ = True`
- El sistema ahora usa correctamente el horario argentino.

### 2. ✅ Modelo de Reserva Actualizado
- **Archivo**: `backend/reservas/models.py`
- **Nuevo campo**: `tipo_reserva` con opciones:
  - `CLIENTE`: Reserva de Cliente (default)
  - `ADMINISTRATIVA`: Reserva Administrativa del dueño
  - `BLOQUEADA`: Horario bloqueado (no disponible)
  - `MANTENIMIENTO`: Mantenimiento de la cancha

### 3. ✅ Vistas para Dueños
- **Archivo**: `backend/complejos/views.py`
- **Nuevas vistas**:
  - `calendario_reservas_dueno`: Calendario completo de todas las canchas del complejo
  - `crear_reserva_dueno`: Crear reservas, bloqueos o mantenimiento
  - `cancelar_reserva_dueno`: Cancelar cualquier reserva del complejo

### 4. ✅ Template de Calendario para Dueños
- **Archivo**: `backend/templates/complejos/calendario_reservas_dueno.html`
- **Características**:
  - Vista completa de todas las canchas del complejo
  - Código de colores para diferentes tipos de reserva
  - Modal para crear nuevas reservas/bloqueos
  - Navegación por fechas (anterior/siguiente/selector)
  - Cancelación de reservas con confirmación

### 5. ✅ URLs Actualizadas
- **Archivo**: `backend/complejos/urls.py`
- **Nuevas rutas**:
  ```python
  /<slug>/reservas/                           # Calendario del dueño
  /<slug>/reservas/crear/                     # Crear reserva/bloqueo
  /<slug>/reservas/<id>/cancelar/            # Cancelar reserva
  ```

### 6. ✅ Template Gestionar Actualizado
- **Archivo**: `backend/templates/complejos/gestionar.html`
- Botón "Gestionar Reservas" agregado en el header para acceso rápido al calendario

### 7. ✅ Migración de Base de Datos
- **Archivo**: `backend/reservas/migrations/0002_reserva_tipo_reserva.py`
- Migración creada para agregar el campo `tipo_reserva`

## Cómo Usar el Sistema

### Para Dueños de Complejos

1. **Acceder al Panel**:
   - Dashboard → Mis Complejos → [Seleccionar Complejo] → "Gestionar Reservas"
   - O directamente: `/complejos/<slug>/reservas/`

2. **Crear Reserva para Cliente**:
   - Click en "Nueva Reserva/Bloqueo"
   - Seleccionar: Tipo = "Reserva de Cliente"
   - **Nombre y teléfono son OPCIONALES** (si el cliente no tiene cuenta)
   - Ingresar precio (o dejar vacío para usar precio default)
   - Agregar observaciones si es necesario

3. **Bloquear Horario**:
   - Click en "Nueva Reserva/Bloqueo"
   - Seleccionar: Tipo = "Bloqueo de Horario"
   - **NO requiere datos de cliente**
   - Agregar observaciones (ej: "Torneo interno", "Evento privado")
   - El horario quedará bloqueado y no disponible para jugadores

4. **Reserva Administrativa**:
   - Para eventos especiales, entrenamientos, etc.
   - **NO requiere datos de cliente**
   - Ideal para uso interno del complejo

5. **Mantenimiento**:
   - Para marcar horarios de mantenimiento de cancha
   - **NO requiere datos de cliente**
   - Visible con color especial en el calendario

### Reservas Fijas (Turnos Recurrentes)

- Se crean desde "Gestionar Complejo"
- **Cliente es OPCIONAL**: puede ser para un jugador específico o administrativa
- Si es para un jugador registrado: seleccionar de la lista
- Si es para cliente sin cuenta: ingresar nombre
- Si es administrativa: dejar ambos vacíos
- Se bloquean automáticamente todos los turnos futuros

### Para Jugadores

- Los jugadores **NO** tienen acceso al calendario de dueños
- Continúan reservando desde: `/reservas/cancha/<id>/calendario/`
- Solo ven turnos DISPONIBLES
- No pueden reservar en horarios bloqueados o administrativos

## Características del Sistema

### ✅ Separación de Roles
- Dueños: Panel administrativo completo con todas las canchas
- Jugadores: Vista pública de disponibilidad

### ✅ Tipos de Reserva
- **Cliente**: Reservas normales (jugadores o clientes del dueño)
- **Administrativa**: Reservas internas del complejo
- **Bloqueada**: Horarios no disponibles
- **Mantenimiento**: Mantenimiento programado

### ✅ Código de Colores
- 🟢 Verde: Disponible
- 🟡 Amarillo: Reservado por cliente
- 🔴 Rojo: Bloqueado
- 🔵 Azul: Turno fijo
- ⚫ Gris: Administrativa

### ✅ Timezone Argentino
- Todas las fechas y horas se manejan en horario de Argentina
- `USE_TZ=True` para manejo correcto de zonas horarias

## Próximos Pasos (Opcional)

1. **Estadísticas**: Agregar dashboard con estadísticas de ocupación
2. **Reportes**: Reportes de ingresos por fecha/cancha
3. **Notificaciones**: SMS/Email automáticos para recordatorios
4. **API**: Endpoints para integración con apps móviles
5. **Pagos Online**: Integración con Mercado Pago/PayPal

## Notas Importantes

- ⚠️ **Migración pendiente**: Ejecutar `python manage.py migrate` en el servidor
- ⚠️ La migración agregará el campo con valor default 'CLIENTE' para reservas existentes
- ✅ El sistema es compatible con las reservas fijas y partidos abiertos existentes
- ✅ No afecta el flujo normal de reservas de jugadores

## Acceso Rápido

**Dueños**:
- Panel principal: `/complejos/dashboard/`
- Mis complejos: `/complejos/dashboard/complejos/`
- Gestionar complejo: `/complejos/<slug>/gestionar/`
- **Calendario reservas**: `/complejos/<slug>/reservas/` ⭐ NUEVO

**Jugadores** (sin cambios):
- Ver complejo: `/complejos/<slug>/`
- Calendario cancha: `/reservas/cancha/<id>/calendario/`
- Mis reservas: `/reservas/mis-reservas/`
