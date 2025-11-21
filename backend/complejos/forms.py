from django import forms
from .models import Cancha
from cuentas.models import Deporte

class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = [
            'nombre', 'deporte', 'tipo_superficie', 'tipo_pared', 'techada', 'iluminacion',
            'precio_base', 'precio_hora', 'horario_apertura', 'horario_cierre', 'duracion_turno_minutos', 'foto'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo deportes activos si aplica, o todos
        self.fields['deporte'].queryset = Deporte.objects.all()
        self.fields['deporte'].label_from_instance = lambda obj: obj.nombre
