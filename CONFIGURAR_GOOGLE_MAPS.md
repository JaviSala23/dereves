# Configurar Google Maps API Key

## Error Actual
```
Google Maps JavaScript API error: RefererNotAllowedMapError
Your site URL to be authorized: http://habitatonline.ar:9000/complejos/crear/
```

## Solución: Autorizar tu dominio en Google Cloud Console

### Paso 1: Acceder a Google Cloud Console
1. Ve a: https://console.cloud.google.com/
2. Inicia sesión con tu cuenta de Google
3. Selecciona tu proyecto (o crea uno si no tienes)

### Paso 2: Ir a la sección de Credenciales
1. En el menú lateral, ve a: **APIs y servicios** → **Credenciales**
2. O directamente: https://console.cloud.google.com/apis/credentials

### Paso 3: Editar la API Key
1. Busca tu API Key: `AIzaSyAaKSwBOBhRshTQpxjuYQsNiw1Ex1PI3lA`
2. Haz clic en el ícono de editar (lápiz) al lado de la key
3. En la sección **Restricciones de aplicación**, selecciona: **Referentes HTTP (sitios web)**

### Paso 4: Agregar tus URLs autorizadas
En el campo **Restricciones de referentes de sitio web**, agrega las siguientes URLs:

```
http://habitatonline.ar:9000/*
http://habitatonline.ar/*
https://habitatonline.ar/*
http://localhost:8000/*
http://127.0.0.1:8000/*
http://localhost:9000/*
http://127.0.0.1:9000/*
```

**Nota:** El asterisco `*` al final permite todas las rutas dentro del dominio.

### Paso 5: Verificar APIs habilitadas
Asegúrate de que las siguientes APIs estén habilitadas en tu proyecto:

1. Ve a: **APIs y servicios** → **Biblioteca**
2. Busca y habilita (si no están habilitadas):
   - ✅ **Maps JavaScript API**
   - ✅ **Geocoding API** (para buscar direcciones automáticamente)
   - ✅ **Places API** (opcional, para autocompletar direcciones)

### Paso 6: Guardar cambios
1. Haz clic en **Guardar** en la página de edición de la API Key
2. Espera unos segundos (puede tardar hasta 5 minutos en propagarse)
3. Recarga tu página web

---

## Configuración Recomendada para Producción

### Restricciones de Referente (más seguras)
```
# Producción
https://habitatonline.ar/*
https://www.habitatonline.ar/*
http://habitatonline.ar/*

# Desarrollo (opcional, para testing local)
http://localhost:8000/*
http://127.0.0.1:8000/*
```

### Restricciones de API
En la sección **Restricciones de API**, limita el uso solo a las APIs que necesitas:
- Maps JavaScript API
- Geocoding API
- Places API (si usas autocompletar)

---

## Verificación Post-Configuración

### 1. Verificar en el navegador
1. Abre: http://habitatonline.ar:9000/complejos/crear/
2. Abre la consola del navegador (F12)
3. Deberías ver el mapa sin errores
4. Haz clic en el mapa para verificar que coloca el marcador

### 2. Verificar coordenadas
- Al hacer clic en el mapa, los campos de latitud y longitud deben rellenarse automáticamente
- Puedes arrastrar el marcador para ajustar la ubicación

### 3. Verificar geocodificación
- Completa la dirección y localidad
- El mapa debería centrarse automáticamente en esa ubicación

---

## Si persiste el error

### Opción 1: Usar una API Key sin restricciones (SOLO PARA TESTING)
⚠️ **NO RECOMENDADO PARA PRODUCCIÓN**

1. Crea una nueva API Key
2. En **Restricciones de aplicación**, selecciona: **Ninguna**
3. Usa esta key temporalmente para verificar que el código funciona
4. Luego configura las restricciones correctamente

### Opción 2: Verificar la configuración actual
```bash
# En la consola del navegador (F12), ejecuta:
console.log('API Key cargada:', document.querySelector('script[src*="maps.googleapis.com"]')?.src);
```

### Opción 3: Limpiar caché
1. Limpia la caché del navegador
2. Recarga la página con Ctrl+F5
3. Espera unos minutos (la propagación puede tardar)

---

## URLs a Autorizar según tu Entorno

### Desarrollo Local
```
http://localhost:8000/*
http://127.0.0.1:8000/*
```

### Servidor de Staging/Testing
```
http://habitatonline.ar:9000/*
http://habitatonline.ar/*
```

### Producción
```
https://habitatonline.ar/*
https://www.habitatonline.ar/*
http://habitatonline.ar/*
```

**Importante:** Siempre incluye el puerto si estás usando uno no estándar (como `:9000`)

---

## Límites de Uso Gratuito de Google Maps

- **Cargas de mapa**: $200 USD de crédito mensual gratuito
- **Equivale a**: ~28,000 cargas de mapa por mes gratis
- **Geocodificación**: 40,000 solicitudes gratuitas por mes

Si superas estos límites, Google te cobrará. Para evitar cargos inesperados:

1. Configura un **presupuesto y alertas** en Google Cloud Console
2. Ve a: **Facturación** → **Presupuestos y alertas**
3. Establece un límite (ej: $10 USD/mes)
4. Recibirás emails cuando te acerques al límite

---

## Checklist de Configuración

- [ ] Acceder a Google Cloud Console
- [ ] Editar la API Key existente
- [ ] Seleccionar "Referentes HTTP (sitios web)"
- [ ] Agregar todas las URLs necesarias con `/*`
- [ ] Habilitar Maps JavaScript API
- [ ] Habilitar Geocoding API
- [ ] Guardar cambios
- [ ] Esperar 2-5 minutos
- [ ] Limpiar caché del navegador
- [ ] Recargar la página y verificar
- [ ] Confirmar que el mapa se muestra sin errores
- [ ] Verificar que al hacer clic se coloca el marcador
- [ ] Configurar presupuesto y alertas (opcional pero recomendado)

---

## Soporte

Si después de seguir estos pasos aún tienes problemas:

1. Verifica que la API Key sea la correcta: `AIzaSyAaKSwBOBhRshTQpxjuYQsNiw1Ex1PI3lA`
2. Comprueba que el proyecto de Google Cloud tenga facturación habilitada (aunque uses el tier gratuito)
3. Revisa los logs en Google Cloud Console → **APIs y servicios** → **Credenciales** → **Métricas**
4. Verifica en la consola del navegador si hay otros errores de JavaScript

**Última actualización:** Noviembre 11, 2025
