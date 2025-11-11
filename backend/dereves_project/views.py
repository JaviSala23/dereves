from django.shortcuts import render
from complejos.models import Complejo


def home(request):
    """Vista principal del sitio."""
    complejos_destacados = Complejo.objects.filter(activo=True)[:6]
    context = {
        'complejos_destacados': complejos_destacados,
    }
    return render(request, 'home.html', context)
