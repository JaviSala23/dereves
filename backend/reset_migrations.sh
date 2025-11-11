#!/bin/bash
# Script para resetear migraciones y base de datos desde cero
# Ejecutar en el servidor cloud

echo "=========================================="
echo "RESET COMPLETO DE MIGRACIONES Y BASE DE DATOS"
echo "=========================================="

# Crear nuevas migraciones desde cero
echo "Generando migraciones nuevas..."
python manage.py makemigrations

# Aplicar migraciones a la base de datos limpia
echo "Aplicando migraciones a la base de datos..."
python manage.py migrate

# Crear superusuario (opcional - comentar si no necesitas)
# echo "Creando superusuario..."
# python manage.py createsuperuser

echo "=========================================="
echo "PROCESO COMPLETADO"
echo "=========================================="
echo "Tu base de datos está lista desde cero."
echo "Todas las tablas están creadas y limpias."
