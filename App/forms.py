
from .models import MetaEgreso

from django import forms

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='Seleccionar archivo Excel')

class MetaEgresoForm(forms.ModelForm):
    class Meta:
        model = MetaEgreso
        fields = ['categoria', 'descripcion', 'monto_meta', 'fecha_establecida', 'tipogasto']
        widgets = {
            'fecha_establecida': forms.DateInput(attrs={'type': 'date'}),
        }