# Guía de Despliegue en Cloud - DeRevés

## 🚀 Pasos para Desplegar las Nuevas Funcionalidades

### 1. Subir Cambios al Repositorio
```bash
# Desde tu máquina local (Windows PowerShell)
cd C:\Users\Javi\Desktop\coso\dereves
git add .
git commit -m "feat: sistema de finanzas completo y correcciones de enlaces"
git push origin main
```

### 2. Conectarse al Servidor Cloud
```bash
# Ejemplo con SSH (ajusta según tu proveedor)
ssh usuario@tu-servidor.com

# O si usas un servicio específico:
# - Railway: railway shell
# - Render: usa el web shell desde el dashboard
# - DigitalOcean: doctl compute ssh nombre-droplet
# - AWS: ssh -i tu-clave.pem ec2-user@tu-instancia.com
```

### 3. Actualizar el Código en el Servidor
```bash
# Navegar al directorio del proyecto
cd /ruta/al/proyecto/dereves

# Actualizar desde Git
git pull origin main

# Activar entorno virtual (si aplica)
source venv/bin/activate
# O en algunos casos: source env/bin/activate
```

### 4. Instalar/Actualizar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Crear y Aplicar Migraciones
```bash
cd backend

# Crear migraciones para las nuevas apps/modelos
python manage.py makemigrations complejos
python manage.py makemigrations finanzas

# Ver qué migraciones se van a aplicar
python manage.py showmigrations

# Aplicar las migraciones
python manage.py migrate

# Verificar que se aplicaron correctamente
python manage.py showmigrations
```

### 6. Recolectar Archivos Estáticos
```bash
python manage.py collectstatic --noinput
```

### 7. Verificar Permisos de Archivos
```bash
# Dar permisos a las carpetas de media y static (ajusta el usuario según tu servidor)
sudo chown -R www-data:www-data /ruta/al/proyecto/dereves/backend/media
sudo chown -R www-data:www-data /ruta/al/proyecto/dereves/backend/staticfiles

# O si usas otro usuario (ej: ubuntu, nginx, etc.)
# sudo chown -R ubuntu:ubuntu /ruta/al/proyecto/dereves/backend/media
```

### 8. Reiniciar el Servicio Web

#### Si usas Gunicorn con systemd:
```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

#### Si usas uWSGI:
```bash
sudo systemctl restart uwsgi
sudo systemctl status uwsgi
```

#### Si usas Docker/Docker Compose:
```bash
docker-compose down
docker-compose pull
docker-compose up -d
docker-compose logs -f web
```

#### Si usas Railway/Render (auto-deploy):
- Solo necesitas hacer `git push` y el servicio se redesplegará automáticamente
- Monitorea los logs desde el dashboard

### 9. Verificar la Base de Datos
```bash
# Entrar al shell de Django para verificar que los modelos funcionan
python manage.py shell
```

Dentro del shell de Python:
```python
from finanzas.models import Transaccion, ResumenMensual
from complejos.models import Complejo, Localidad, FotoComplejo
from django.contrib.auth import get_user_model

User = get_user_model()

# Verificar que hay usuarios DUENIO
duenios = User.objects.filter(tipo_usuario='DUENIO')
print(f"Total dueños: {duenios.count()}")

# Verificar complejos activos
complejos = Complejo.objects.filter(activo=True)
print(f"Total complejos activos: {complejos.count()}")

# Verificar tablas de finanzas (deben estar vacías si es primera vez)
print(f"Total transacciones: {Transaccion.objects.count()}")
print(f"Total resúmenes: {ResumenMensual.objects.count()}")

# Salir
exit()
```

---

## 🔍 Verificaciones Post-Despliegue

### 1. Verificar URLs Principales
```bash
# Desde el servidor o tu máquina
curl -I https://tu-dominio.com/
curl -I https://tu-dominio.com/accounts/login/
curl -I https://tu-dominio.com/complejos/
curl -I https://tu-dominio.com/finanzas/
```

### 2. Probar desde el Navegador

#### A) Login como Dueño:
1. Ve a `https://tu-dominio.com/accounts/login/`
2. Ingresa con un usuario tipo DUENIO
3. Ve a `https://tu-dominio.com/accounts/perfil/`
4. Verifica que aparece el menú lateral con:
   - ✅ Dashboard
   - ✅ Mis Complejos
   - ✅ Gestionar Reservas
   - ✅ **Finanzas** (nuevo)

#### B) Probar Mis Complejos:
1. Click en "Mis Complejos"
2. Verifica que cada tarjeta de complejo tenga:
   - Botón "Gestionar" (principal, azul)
   - Botón "Ver Complejo" (outline)
   - Botón "Estadísticas" (outline)
   - Footer con botones:
     - **"Editar"** → debe llevar a `/complejos/{slug}/editar/`
     - **"Configurar"** → debe llevar a `/complejos/{slug}/gestionar/`

#### C) Probar Finanzas:
1. Click en "Finanzas" del menú lateral
2. Deberías ver el dashboard con:
   - Tarjetas de resumen (Ingresos, Gastos, Balance)
   - Gráfico de Chart.js (últimos 6 meses)
   - Lista de transacciones
   - Botón "Nueva Transacción"
3. Hacer click en "Nueva Transacción":
   - Llenar el formulario
   - Guardar
   - Verificar que aparece en la lista
4. Probar el botón "Ver Reporte Completo"
5. Probar "Exportar CSV"

---

## 🐛 Solución de Problemas

### Problema 1: "No module named 'finanzas'"
**Causa:** La app no está en INSTALLED_APPS o no se reinició el servidor.

**Solución:**
```bash
# Verificar settings.py
grep -n "finanzas" backend/dereves_project/settings.py

# Debe aparecer en INSTALLED_APPS
# Si no está, agrégalo y reinicia el servidor
```

### Problema 2: Botones de Finanzas no aparecen
**Causa:** El usuario no es tipo DUENIO.

**Solución:**
```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Verificar tipo de usuario
u = User.objects.get(username='TU_USUARIO')
print(u.tipo_usuario)

# Si no es DUENIO, cambiarlo:
u.tipo_usuario = 'DUENIO'
u.save()
exit()
```

### Problema 3: Error 500 al entrar a /finanzas/
**Causa:** El usuario dueño no tiene complejos activos.

**Solución:**
La vista redirige automáticamente a crear complejo. Verificar:
```bash
python manage.py shell
```
```python
from complejos.models import Complejo
from django.contrib.auth import get_user_model
User = get_user_model()

u = User.objects.get(username='TU_USUARIO')
complejos = Complejo.objects.filter(dueno__usuario=u, activo=True)
print(f"Complejos activos: {complejos.count()}")

# Si no hay, crear uno o activar uno existente
if complejos.count() == 0:
    print("El usuario no tiene complejos. Debe crear uno primero.")
exit()
```

### Problema 4: Error con Chart.js
**Causa:** CDN no carga o problema con JavaScript.

**Solución:**
1. Abrir DevTools (F12) → Console
2. Verificar que no hay errores de "Chart is not defined"
3. Si hay error, verificar conexión a CDN o usar versión local

### Problema 5: CSV no descarga
**Causa:** Headers incorrectos o problema con el servidor.

**Solución:**
```bash
# Ver logs del servidor
sudo journalctl -u gunicorn -n 50 -f
# O
tail -f /var/log/nginx/error.log
```

### Problema 6: Imágenes no se ven (logo, fotos)
**Causa:** MEDIA_ROOT no está servido correctamente.

**Solución en Nginx:**
```nginx
# Agregar en tu configuración de nginx
location /media/ {
    alias /ruta/al/proyecto/dereves/backend/media/;
}
```

Luego:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📊 Verificar Logs

### Logs de Aplicación:
```bash
# Gunicorn con systemd
sudo journalctl -u gunicorn -f

# uWSGI
sudo journalctl -u uwsgi -f

# Docker
docker logs -f nombre-contenedor
```

### Logs de Nginx:
```bash
# Errores
sudo tail -f /var/log/nginx/error.log

# Accesos
sudo tail -f /var/log/nginx/access.log
```

### Logs de Django (si DEBUG=True):
- Los errores aparecen directamente en el navegador
- Si DEBUG=False, verificar archivos de log en `/var/log/` o donde los tengas configurados

---

## ✅ Checklist de Verificación Final

- [ ] Código actualizado con `git pull`
- [ ] Dependencias instaladas con `pip install -r requirements.txt`
- [ ] Migraciones creadas y aplicadas (`makemigrations` + `migrate`)
- [ ] Estáticos recolectados (`collectstatic`)
- [ ] Permisos correctos en `media/` y `staticfiles/`
- [ ] Servicio web reiniciado
- [ ] Login funciona correctamente
- [ ] Usuario DUENIO puede acceder a `/accounts/perfil/`
- [ ] Botón "Finanzas" aparece en el menú lateral
- [ ] Click en "Finanzas" navega a `/finanzas/` y carga el dashboard
- [ ] Botones "Editar" y "Configurar" en "Mis Complejos" funcionan correctamente
- [ ] Se puede crear una transacción en Finanzas
- [ ] El gráfico de Chart.js se renderiza correctamente
- [ ] Exportar CSV funciona
- [ ] Imágenes (logos, fotos) se visualizan correctamente

---

## 🔧 Configuración Opcional de Producción

### 1. Variables de Entorno Recomendadas
Crear archivo `.env` en el servidor:
```bash
DEBUG=False
SECRET_KEY=tu-clave-super-secreta-aqui
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=mysql://user:password@localhost/dereves
MEDIA_ROOT=/ruta/completa/al/media
STATIC_ROOT=/ruta/completa/al/staticfiles

# Google Maps API Key (OBLIGATORIO para crear/editar complejos)
GOOGLE_MAPS_API_KEY=AIzaSyC13c8_QIypeuZCt4dDZxlAUrBnpbap5Y0
```

**IMPORTANTE:** La API key de Google Maps es **obligatoria** para que funcionen los formularios de crear y editar complejos con el mapa interactivo.

### 2. Actualizar settings.py para usar .env
```python
import os
from pathlib import Path

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-por-defecto')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

### 3. Configurar HTTPS (Let's Encrypt con Certbot)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
sudo certbot renew --dry-run
```

---

## 📞 Soporte

Si encuentras algún error durante el despliegue:

1. **Revisa los logs** (sección de arriba)
2. **Copia el error completo** (traceback)
3. **Comparte**:
   - El comando que ejecutaste
   - El error completo
   - El archivo donde ocurrió (si aplica)
4. **Información del entorno**:
   - SO del servidor (Ubuntu, Debian, CentOS, etc.)
   - Versión de Python (`python --version`)
   - Versión de Django (`python manage.py version`)
   - Servidor web (nginx, apache, etc.)

---

## 🎉 ¡Listo!

Una vez completados todos los pasos, tu aplicación DeRevés estará corriendo con:
- ✅ Sistema de finanzas completo
- ✅ Gestión de localidades personalizadas
- ✅ Subida múltiple de fotos por complejo
- ✅ Edición de complejos
- ✅ Todos los botones y enlaces funcionando correctamente

**Fecha de última actualización:** Noviembre 11, 2025
