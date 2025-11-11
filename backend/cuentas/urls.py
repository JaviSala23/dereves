from django.urls import path
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('jugador/<int:id>/', views.perfil_publico_jugador, name='perfil_publico'),
]
