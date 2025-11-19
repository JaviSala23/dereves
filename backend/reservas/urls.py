from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    # Reservas comunes
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('canchas/<int:cancha_id>/calendario/', views.calendario_cancha, name='calendario_cancha'),
    path('canchas/<int:cancha_id>/crear/', views.crear_reserva, name='crear_reserva'),
    path('<int:reserva_id>/', views.detalle_reserva, name='detalle_reserva'),
    path('<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('<int:reserva_id>/confirmar/', views.confirmar_reserva, name='confirmar_reserva'),
    path('<int:reserva_id>/pagar/', views.marcar_reserva_pagada, name='marcar_reserva_pagada'),
    
    # Reservas fijas (solo dueños)
    path('fijas/cancha/<int:cancha_id>/crear/', views.crear_reserva_fija, name='crear_reserva_fija'),
    path('fijas/<int:reserva_fija_id>/editar/', views.editar_reserva_fija, name='editar_reserva_fija'),
    path('fijas/<int:reserva_fija_id>/cancelar/', views.cancelar_reserva_fija, name='cancelar_reserva_fija'),

    # Liberar una fecha de reserva fija
    path('liberar_reserva_fija/<int:reserva_fija_id>/', views.liberar_reserva_fija_fecha, name='liberar_reserva_fija'),

    # Marcar una ocurrencia de reserva fija como pagada manualmente
    path('fijas/<int:reserva_fija_id>/pagar/<str:fecha>/', views.marcar_reserva_fija_pagada, name='marcar_reserva_fija_pagada'),
    
    # Partidos abiertos
    path('partidos/turno/<int:turno_id>/crear/', views.crear_partido_abierto, name='crear_partido_abierto'),
    path('partidos/<int:partido_id>/', views.detalle_partido, name='detalle_partido'),
    path('partidos/<str:token>/unirse/', views.unirse_partido, name='unirse_partido'),
]
