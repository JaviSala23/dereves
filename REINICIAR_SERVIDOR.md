# Instrucciones para Reiniciar el Servidor

El error `Cannot find 'reservas' on Turno object` ocurre porque el servidor tiene código en caché.

## Solución en servidor de producción (habitatonline.ar:9000)

```bash
# Conectarse al servidor
ssh usuario@habitatonline.ar

# Ir al directorio del proyecto
cd /ruta/al/proyecto/dereves/backend

# Reiniciar el servicio (el comando exacto depende de cómo esté configurado)
# Opciones comunes:

# Si usa systemd:
sudo systemctl restart dereves

# O si usa supervisor:
sudo supervisorctl restart dereves

# O si usa gunicorn directamente:
pkill -HUP gunicorn

# O si está en desarrollo:
# Detener el proceso (Ctrl+C) y volver a ejecutar:
python manage.py runserver 0.0.0.0:9000
```

## Verificar que los cambios se aplicaron

Una vez reiniciado, intenta acceder de nuevo a:
`http://habitatonline.ar:9000/complejos/mantis-sport/reservas/`

El error debería desaparecer porque el código ya no tiene referencias a `prefetch_related('reservas')`.
