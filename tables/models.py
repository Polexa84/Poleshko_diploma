from django.db import models
from restaurants.models import Restaurant

class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables', verbose_name='Ресторан')
    number = models.IntegerField(verbose_name='Номер стола')
    capacity = models.IntegerField(verbose_name='Вместимость')
    is_active = models.BooleanField(default=True, verbose_name='Активен')  # Ensure this line is present
    def __str__(self):
        return f"Стол #{self.number} в {self.restaurant.name}"

    class Meta:
        verbose_name = 'Стол'
        verbose_name_plural = 'Столы'