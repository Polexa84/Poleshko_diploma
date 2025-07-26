import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from tables.models import Table
from restaurants.models import Restaurant

class Booking(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name='Ресторан'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Стол'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Исправлено здесь!
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        blank=True,
        null=True
    )
    booking_time = models.DateTimeField(
        verbose_name='Время бронирования',
        default=timezone.now  # Добавлено значение по умолчанию
    )
    duration = models.DurationField(
        default=timezone.timedelta(hours=3),
        verbose_name='Длительность'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    confirmation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Бронь #{self.id} для стола #{self.table.number} в {self.restaurant.name} на {self.booking_time.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
        ordering = ['-booking_time']  # Добавлена сортировка по умолчанию