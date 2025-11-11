from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.dashboard_finanzas, name='dashboard'),
    path('registrar/', views.registrar_transaccion, name='registrar_transaccion'),
    path('transaccion/<int:transaccion_id>/eliminar/', views.eliminar_transaccion, name='eliminar_transaccion'),
    path('reporte/', views.reporte_finanzas, name='reporte'),
    path('exportar/', views.exportar_reporte, name='exportar'),
]
