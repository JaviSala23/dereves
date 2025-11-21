from cuentas.models import Deporte
from django.db import transaction

# Definición de deportes y habilidades/categorías sugeridas
DEPORTES = [
    {
        'nombre': 'Pádel',
        'descripcion': 'Deporte de raqueta muy popular en Argentina.',
        'habilidades': ['Drive', 'Reves', 'Bandeja', 'Volea', 'Smash', 'Posición: Derecha', 'Posición: Revés'],
        'categorias': ['Sexta', 'Quinta', 'Cuarta', 'Tercera', 'Segunda', 'Primera', 'PRO']
    },
    {
        'nombre': 'Fútbol',
        'descripcion': 'Fútbol 5, 7 u 11.',
        'habilidades': ['Arquero', 'Defensor', 'Mediocampista', 'Delantero', 'Pie hábil: Derecho', 'Pie hábil: Izquierdo', 'Pie hábil: Ambos'],
        'categorias': ['Recreativo', 'Competitivo', 'Libre', 'Senior']
    },
    {
        'nombre': 'Tenis',
        'descripcion': 'Tenis tradicional.',
        'habilidades': ['Drive', 'Reves', 'Volea', 'Smash', 'Mano hábil: Derecha', 'Mano hábil: Izquierda', 'Mano hábil: Ambas'],
        'categorias': ['Intermedia', 'Avanzada', 'Primera', 'PRO']
    },
    {
        'nombre': 'Vóley',
        'descripcion': 'Vóley tradicional o de playa.',
        'habilidades': ['Armador', 'Opuesto', 'Central', 'Punta', 'Libero', 'Mano hábil: Derecha', 'Mano hábil: Izquierda'],
        'categorias': ['Recreativo', 'Competitivo']
    },
]

@transaction.atomic
def poblar_deportes():
    for dep in DEPORTES:
        deporte, created = Deporte.objects.get_or_create(nombre=dep['nombre'], defaults={'descripcion': dep['descripcion']})
        if created:
            print(f"Creado: {deporte.nombre}")
        else:
            print(f"Ya existe: {deporte.nombre}")
        # (Opcional) Aquí podrías guardar habilidades/categorías en otro modelo si lo implementas
        print(f"  Habilidades sugeridas: {', '.join(dep['habilidades'])}")
        print(f"  Categorías sugeridas: {', '.join(dep['categorias'])}")

if __name__ == "__main__":
    poblar_deportes()
