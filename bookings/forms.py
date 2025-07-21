from django import forms
from .models import Booking
from django.utils import timezone
from restaurants.models import Restaurant
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class BookingForm(forms.ModelForm):
    booking_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Дата и время бронирования',
    )

    class Meta:
        model = Booking
        fields = ['table', 'booking_time', 'duration']

    def __init__(self, *args, **kwargs):
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        if self.restaurant:
            self.fields['table'].queryset = self.restaurant.tables.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        booking_time = cleaned_data.get('booking_time')
        table = cleaned_data.get('table')
        duration = cleaned_data.get('duration', timedelta(hours=3)) # Получаем продолжительность

        if booking_time and table and self.restaurant:
            # Проверка на прошлое время
            if booking_time < timezone.now():
                raise ValidationError("Нельзя забронировать столик на прошедшее время.")

            # Проверка пересечений бронирований
            existing_bookings = Booking.objects.filter(
                table=table,
                booking_time__lt=booking_time + duration,
                booking_time__gt=booking_time - duration
            ).exclude(pk=self.instance.pk if self.instance else None)

            if existing_bookings.exists():
                # Собираем занятые интервалы
                occupied_intervals = []
                for booking in existing_bookings:
                    occupied_intervals.append({
                        'start': booking.booking_time,
                        'end': booking.booking_time + booking.duration
                    })

                # Выводим конкретное время, на которое уже есть бронь
                error_message = "Этот столик уже забронирован на это время."
                if occupied_intervals:
                    error_message += " Занято время:"
                    for interval in occupied_intervals:
                         error_message += f" с {interval['start'].strftime('%H:%M')} до {interval['end'].strftime('%H:%M')},"
                    error_message = error_message[:-1] # Убираем последнюю запятую

                raise ValidationError(error_message)


            # Проверка на время работы ресторана
            if booking_time.time() < self.restaurant.opening_time or booking_time.time() > self.restaurant.closing_time:
                raise ValidationError(f"Ресторан открыт с {self.restaurant.opening_time:%H:%M} до {self.restaurant.closing_time:%H:%M}.")

        return cleaned_data