from django import forms
from django.utils import timezone
from restaurants.models import Restaurant
from datetime import datetime, timedelta
from django.forms.widgets import DateInput

class BookingForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': timezone.now().date().strftime('%Y-%m-%d'),
            }
        ),
        initial=timezone.now().date()
    )

    def clean_date(self):
         date = self.cleaned_data['date']
         if date < timezone.now().date():
            raise forms.ValidationError("Вы не можете выбрать прошедшую дату.")
         return date