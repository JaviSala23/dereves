from django.urls import path
from . import views
from . import dashboard_views

app_name = 'complejos'

urlpatterns = [
    path('', views.lista_complejos, name='lista'),
    path('crear/', views.crear_complejo, name='crear'),
    
    # API para horarios disponibles
    path('api/canchas/<int:cancha_id>/horarios/', views.obtener_horarios_disponibles, name='api_horarios'),
    
    # API para provincias y localidades
    path('api/provincias/', views.obtener_provincias, name='api_provincias'),
    path('api/localidades/', views.obtener_localidades, name='api_localidades'),
    path('api/localidades/agregar/', views.agregar_localidad, name='api_agregar_localidad'),
    
    # Dashboard para dueños
    path('dashboard/', dashboard_views.dashboard_principal, name='dashboard_principal'),
    path('dashboard/complejos/', dashboard_views.mis_complejos_dashboard, name='mis_complejos_dashboard'),
    path('dashboard/reservas/', dashboard_views.gestionar_reservas, name='gestionar_reservas'),
    path('dashboard/<slug:slug>/estadisticas/', dashboard_views.estadisticas_complejo, name='estadisticas'),
    
    # Calendario y gestión de reservas para dueños
    path('<slug:slug>/reservas/', views.calendario_reservas_dueno, name='calendario_reservas_dueno'),
    path('<slug:slug>/reservas/crear/', views.crear_reserva_dueno, name='crear_reserva_dueno'),
    path('<slug:slug>/reservas/fija/crear/', views.crear_reserva_fija_dueno, name='crear_reserva_fija_dueno'),
    path('<slug:slug>/reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva_dueno, name='cancelar_reserva_dueno'),
    
    # Gestión de complejo y canchas
    path('<slug:slug>/gestionar/', views.gestionar_complejo, name='gestionar'),
    path('<slug:slug>/canchas/agregar/', views.agregar_cancha, name='agregar_cancha'),
    path('<slug:slug>/canchas/<int:cancha_id>/editar/', views.editar_cancha, name='editar_cancha'),
    path('<slug:slug>/canchas/<int:cancha_id>/toggle/', views.toggle_cancha, name='toggle_cancha'),
    
    # Detalle y edición
    path('<slug:slug>/', views.detalle_complejo, name='detalle'),
    path('<slug:slug>/editar/', views.editar_complejo, name='editar'),
]
