from django.db import models
from django.utils import timezone
from tables.models import Table  # Импортируем модель Table
from django.contrib.auth.models import User  # Импортируем модель User, если используете аутентификацию

class Booking(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bookings', verbose_name='Стол')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, null=True)  # Связь с пользователем
    booking_time = models.DateTimeField(verbose_name='Время бронирования')
    duration = models.DurationField(default=timezone.timedelta(hours=3), verbose_name='Длительность')  # Длительность бронирования (3 часа по умолчанию)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано') #Добавим поле когда создана бронь

    def __str__(self):
        return f"Бронь #{self.id} для стола #{self.table.number} в {self.table.restaurant.name} на {self.booking_time.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'