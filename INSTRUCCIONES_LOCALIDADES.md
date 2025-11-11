# Sistema de Localidades Personalizadas y Múltiples Fotos

## Resumen
Se han implementado dos funcionalidades principales:
1. **Sistema de localidades personalizadas** - Los dueños pueden agregar sus localidades
2. **Múltiples fotos por complejo** - Los complejos pueden tener una galería de fotos

## Cambios Realizados

### 1. Nuevos Modelos

#### a) `Localidad`
**Archivo:** `backend/complejos/models.py`
- Almacena localidades personalizadas agregadas por usuarios
- Campos: nombre, provincia, país, agregada_por, aprobada
- Validación única por combinación de nombre + provincia + país

#### b) `FotoComplejo`
**Archivo:** `backend/complejos/models.py`
- Almacena múltiples fotos por complejo
- Campos: complejo, imagen, descripcion, orden, es_principal
- Auto-gestión de foto principal (solo una puede ser principal)

### 2. Nuevos Templates

#### a) `crear.html` (actualizado)
- Soporte para subir logo (foto principal) - **REQUERIDO**
- Soporte para subir múltiples fotos adicionales - **OPCIONAL**
- Preview de fotos antes de subir
- Validación de tamaño (máx 5MB por foto)

#### b) `editar.html` (nuevo)
- Formulario completo para editar datos del complejo
- Gestión de país, provincia y localidad con selectores dinámicos
- Subir nuevo logo
- Agregar fotos a la galería existente
- Eliminar fotos de la galería con confirmación SweetAlert2
- Preview de fotos existentes

### 3. API Endpoints

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

#### c) Eliminar foto (nuevo)
- **URL:** `/complejos/<slug>/fotos/<foto_id>/eliminar/`
- **Método:** POST
- **Autenticación:** Requerida (debe ser dueño del complejo)
- **Respuesta:** `{"success": true, "mensaje": "..."}`

### 4. Vistas Actualizadas
#### a) `crear_complejo` (actualizada)
- Maneja subida de logo (foto principal)
- Maneja subida de múltiples fotos adicionales
- Crea registros de FotoComplejo para cada foto

#### b) `editar_complejo` (actualizada)
- Permite editar todos los campos del complejo
- Maneja actualización de logo
- Permite agregar más fotos a la galería

#### c) `eliminar_foto_complejo` (nueva)
- Permite eliminar fotos individuales de la galería
- Valida permisos del usuario

### 5. Panel de Administración
**Archivo:** `backend/complejos/admin.py`

#### Localidades
- Vista de todas las localidades agregadas
- Filtros por provincia, país, estado de aprobación
- Acciones masivas: aprobar/desaprobar localidades
- Visualización de quién agregó cada localidad

#### Fotos de Complejos
- Vista de todas las fotos por complejo
- Edición de orden y foto principal
- Filtros por complejo y fecha
- Gestión completa de la galería

## Instrucciones para Desplegar

### Paso 1: Crear Migraciones
```bash
cd backend
python manage.py makemigrations complejos
```

Deberías ver algo como:
```
Migrations for 'complejos':
  complejos/migrations/000X_localidad_fotocomplejo.py
    - Create model Localidad
    - Create model FotoComplejo
```

### Paso 2: Aplicar Migraciones
```bash
python manage.py migrate complejos
```

### Paso 3: Verificar en Admin
1. Accede al panel de administración: `/admin/`
2. Verifica que aparezcan las secciones:
   - "Localidades" bajo "Complejos"
   - "Fotos de Complejos" bajo "Complejos"

### Paso 4: Probar la Funcionalidad

#### A) Crear Complejo con Fotos:
1. Ve a `/complejos/crear/`
2. Llena el formulario
3. **Sube un logo (obligatorio)**
4. Opcionalmente, sube múltiples fotos adicionales
5. Ve el preview de las fotos antes de guardar
6. Guarda el complejo

#### B) Editar Complejo:
1. Ve a `/complejos/<slug>/editar/`
2. Edita cualquier campo del complejo
3. Cambia el logo si quieres
4. Agrega más fotos a la galería
5. Elimina fotos existentes con el botón "Eliminar"
6. Guarda los cambios

#### C) Agregar Localidades:
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
