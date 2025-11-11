"""
Context processors para agregar variables globales a los templates
"""
from django.conf import settings


def google_maps_api_key(request):
    """
    Agrega la API key de Google Maps a todos los templates
    """
    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
