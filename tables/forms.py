from django import forms
from .models import Table

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'capacity', 'is_active', 'image']  # Added image field
        labels = {
            'number': 'Номер стола',
            'capacity': 'Вместимость',
            'is_active': 'Активен',
            'image': 'Фото стола',
        }