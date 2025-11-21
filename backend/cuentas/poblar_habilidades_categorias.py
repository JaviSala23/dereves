from cuentas.models import Deporte, HabilidadDeporte, CategoriaDeporte
from django.db import transaction

# Definición de habilidades y categorías por deporte
DEPORTES = [
    {
        'nombre': 'Pádel',
        'habilidades': ['Drive', 'Reves', 'Bandeja', 'Volea', 'Smash', 'Posición: Derecha', 'Posición: Revés'],
        'categorias': ['Sexta', 'Quinta', 'Cuarta', 'Tercera', 'Segunda', 'Primera', 'PRO']
    },
    {
        'nombre': 'Fútbol',
        'habilidades': ['Arquero', 'Defensor', 'Mediocampista', 'Delantero', 'Pie hábil: Derecho', 'Pie hábil: Izquierdo', 'Pie hábil: Ambos'],
        'categorias': ['Recreativo', 'Competitivo', 'Libre', 'Senior']
    },
    {
        'nombre': 'Tenis',
        'habilidades': ['Drive', 'Reves', 'Volea', 'Smash', 'Mano hábil: Derecha', 'Mano hábil: Izquierda', 'Mano hábil: Ambas'],
        'categorias': ['Intermedia', 'Avanzada', 'Primera', 'PRO']
    },
    {
        'nombre': 'Vóley',
        'habilidades': ['Armador', 'Opuesto', 'Central', 'Punta', 'Libero', 'Mano hábil: Derecha', 'Mano hábil: Izquierda'],
        'categorias': ['Recreativo', 'Competitivo']
    },
]

@transaction.atomic
def poblar_habilidades_categorias():
    for dep in DEPORTES:
        try:
            deporte = Deporte.objects.get(nombre=dep['nombre'])
        except Deporte.DoesNotExist:
            print(f"Deporte no encontrado: {dep['nombre']}")
            continue
        for hab in dep['habilidades']:
            obj, created = HabilidadDeporte.objects.get_or_create(deporte=deporte, nombre=hab)
            if created:
                print(f"Habilidad creada: {deporte.nombre} - {hab}")
        for cat in dep['categorias']:
            obj, created = CategoriaDeporte.objects.get_or_create(deporte=deporte, nombre=cat)
            if created:
                print(f"Categoría creada: {deporte.nombre} - {cat}")

if __name__ == "__main__":
    poblar_habilidades_categorias()
