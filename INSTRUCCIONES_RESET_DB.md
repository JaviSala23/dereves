# Instrucciones para Reset de Base de Datos en la Nube

## Estado Actual
✅ Todas las migraciones antiguas han sido eliminadas
✅ Solo quedan los archivos `__init__.py` en cada carpeta de migrations
✅ El código está listo para generar migraciones frescas

## Apps con migraciones limpiadas:
- complejos
- cuentas
- finanzas
- reservas

## Apps sin migraciones (solo __init__.py):
- partidos
- torneos
- social
- valoraciones
- publicidades
- sitio_publico

## Pasos a seguir EN LA NUBE:

### 1. Asegúrate de tener la base de datos limpia
Si ya limpiaste la base de datos en el cloud, estás listo. Si no:
```bash
# Esto borra TODAS las tablas de Django en tu BD
python manage.py flush --no-input
```

O bien, si prefieres borrar y recrear la base de datos completamente desde el panel de tu hosting.

### 2. Sube el código actualizado
Asegúrate de subir todo el código con las migraciones eliminadas.

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecuta el script de reset (OPCIÓN A)
```bash
chmod +x backend/reset_migrations.sh
cd backend
./reset_migrations.sh
```

### O ejecuta los comandos manualmente (OPCIÓN B)
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 5. Verifica que todo funcionó
```bash
python manage.py showmigrations
```

Deberías ver algo como:
```
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
 ...
complejos
 [X] 0001_initial
cuentas
 [X] 0001_initial
finanzas
 [X] 0001_initial
reservas
 [X] 0001_initial
...
```

### 6. Crea un superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 7. Puebla datos de prueba (opcional)
Si tienes el script de poblar datos:
```bash
python poblar_datos.py
```

## Notas Importantes

- ⚠️ **Esto borrará TODOS los datos existentes** en tu base de datos
- Las nuevas migraciones se generarán automáticamente basadas en tus modelos actuales
- Todas las tablas se crearán frescas y vacías
- No habrá conflictos de migraciones

## Solución de Problemas

### Si `makemigrations` no detecta cambios:
```bash
python manage.py makemigrations complejos cuentas finanzas reservas
```

### Si hay errores de dependencias entre apps:
Revisa el orden en `INSTALLED_APPS` en `settings.py`. El orden actual es:
1. cuentas
2. complejos
3. reservas
4. partidos
5. torneos
6. social
7. valoraciones
8. publicidades
9. finanzas
10. sitio_publico

### Si la migración falla:
1. Verifica que la base de datos esté realmente vacía
2. Revisa los logs de error
3. Asegúrate de que `mysqlclient` esté instalado correctamente

## Verificación Final

Después de migrar, verifica que las tablas existen:
```bash
python manage.py dbshell
```

Luego en MySQL:
```sql
SHOW TABLES;
```

Deberías ver todas las tablas de Django y tus apps creadas.
