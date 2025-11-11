# Sistema de Localidades Personalizadas

## Resumen
Se ha implementado un sistema completo para que los dueños de complejos puedan agregar sus propias localidades si no encuentran la suya en la lista predeterminada.

## Cambios Realizados

### 1. Nuevo Modelo: `Localidad`
**Archivo:** `backend/complejos/models.py`

- Almacena localidades personalizadas agregadas por usuarios
- Campos: nombre, provincia, país, agregada_por, aprobada
- Validación única por combinación de nombre + provincia + país

### 2. API Endpoints Nuevos

#### a) Obtener localidades (actualizado)
- **URL:** `/complejos/api/localidades/?provincia=NOMBRE_PROVINCIA`
- **Método:** GET
- **Descripción:** Ahora retorna localidades predeterminadas + localidades de BD

#### b) Agregar localidad (nuevo)
- **URL:** `/complejos/api/localidades/agregar/`
- **Método:** POST
- **Autenticación:** Requerida (login_required)
- **Body:**
```json
{
    "nombre": "Mi Localidad",
    "provincia": "Córdoba",
    "pais": "Argentina"
}
```

### 3. Interfaz de Usuario
**Archivo:** `backend/templates/complejos/crear.html`

- Botón "+" junto al selector de localidades
- Modal/prompt para ingresar nombre de nueva localidad
- Actualización automática de la lista tras agregar
- Selección automática de la localidad recién agregada

### 4. Panel de Administración
**Archivo:** `backend/complejos/admin.py`

- Vista de todas las localidades agregadas
- Filtros por provincia, país, estado de aprobación
- Acciones masivas: aprobar/desaprobar localidades
- Visualización de quién agregó cada localidad

## Instrucciones para Desplegar

### Paso 1: Crear Migraciones
```bash
cd backend
python manage.py makemigrations complejos
```

Deberías ver algo como:
```
Migrations for 'complejos':
  complejos/migrations/000X_localidad.py
    - Create model Localidad
```

### Paso 2: Aplicar Migraciones
```bash
python manage.py migrate complejos
```

### Paso 3: Verificar en Admin
1. Accede al panel de administración: `/admin/`
2. Verifica que aparezca la sección "Localidades" bajo "Complejos"

### Paso 4: Probar la Funcionalidad

#### Desde el Formulario de Crear Complejo:
1. Ve a `/complejos/crear/`
2. Selecciona un país (Argentina)
3. Selecciona una provincia
4. Si tu localidad no aparece, haz clic en el botón "+"
5. Ingresa el nombre de la localidad
6. La localidad se agregará automáticamente y aparecerá seleccionada

#### Desde el Admin:
1. Ve a `/admin/complejos/localidad/`
2. Verás todas las localidades agregadas por usuarios
3. Puedes aprobar/desaprobar localidades
4. Puedes editarlas o eliminarlas

## Características Implementadas

✅ **Almacenamiento persistente** - Las localidades se guardan en la base de datos
✅ **Auto-aprobación** - Por defecto, las localidades se aprueban automáticamente
✅ **Validación de duplicados** - No se permite agregar localidades duplicadas
✅ **Interfaz intuitiva** - Botón "+" visible y fácil de usar
✅ **Feedback visual** - Mensajes de éxito/error al agregar
✅ **Panel de moderación** - Admin puede gestionar todas las localidades
✅ **Auditoría** - Se registra quién agregó cada localidad y cuándo

## Flujo de Usuario

1. Usuario va a crear un complejo
2. Selecciona país (Argentina)
3. Selecciona provincia de la lista
4. Ve la lista de localidades disponibles
5. Si no encuentra su localidad:
   - Hace clic en el botón "+"
   - Ingresa el nombre en el prompt
   - El sistema valida y guarda
   - La localidad aparece seleccionada
6. Continúa llenando el resto del formulario

## Seguridad

- ✅ Solo usuarios autenticados pueden agregar localidades
- ✅ Se registra quién agregó cada localidad
- ✅ Los administradores pueden moderar (aprobar/desaprobar)
- ✅ Validación de datos en el backend
- ✅ Protección CSRF en las peticiones POST

## Mantenimiento Futuro

### Para agregar moderación manual (opcional):
En `views.py`, línea ~648, cambiar:
```python
aprobada=True  # Auto-aprobar por ahora
```
a:
```python
aprobada=False  # Requiere aprobación manual
```

### Para notificar al admin de nuevas localidades:
Agregar en la vista `agregar_localidad`:
```python
from django.core.mail import mail_admins
mail_admins(
    'Nueva localidad agregada',
    f'Usuario {request.user} agregó: {nombre}, {provincia}'
)
```

## Problemas Conocidos y Soluciones

### Si las localidades no aparecen:
1. Verificar que la migración se aplicó correctamente
2. Verificar en el admin que las localidades estén aprobadas
3. Revisar la consola del navegador por errores JavaScript

### Si hay error al agregar:
1. Verificar que el usuario esté autenticado
2. Verificar que la URL del endpoint sea correcta
3. Revisar los logs del servidor

## Extensiones Futuras (Opcionales)

- 📍 Geocodificación automática de localidades
- 🗺️ Integración con API de Google Places
- 📊 Estadísticas de localidades más usadas
- 🔍 Búsqueda predictiva en el selector
- 🌍 Soporte para múltiples países
- 📱 Sugerencias basadas en ubicación GPS

---

**Notas:**
- Las localidades predeterminadas (200+) se mantienen en el código
- Las localidades de BD se suman a las predeterminadas
- No hay duplicados en la lista final mostrada al usuario
