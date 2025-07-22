from django import forms
from .models import Booking
from django.utils import timezone
from restaurants.models import Restaurant
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['table']
        widgets = {
            'table': forms.HiddenInput(),  # HiddenInput Widget
        }

    def __init__(self, *args, **kwargs):
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        if self.restaurant:
            self.fields['table'].queryset = self.restaurant.tables.filter(is_active=True)
            if self.initial.get('table'):
                self.fields['table'].widget = forms.HiddenInput()  # Hide table field if initial table is set

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get('table')

        return cleaned_data