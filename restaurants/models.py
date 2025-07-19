from django.db import models
from django.urls import reverse

class Restaurant(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    location = models.CharField(max_length=255, verbose_name='Местоположение (Город, Адрес)')
    opening_time = models.TimeField(verbose_name='Время открытия')
    closing_time = models.TimeField(verbose_name='Время закрытия')
    cuisine_type = models.CharField(max_length=100, verbose_name='Тип кухни')
    average_check = models.CharField(max_length=50, blank=True, verbose_name='Средний чек')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')

    def __str__(self):
        return f"{self.name} ({self.location})"

    def get_absolute_url(self):
        return reverse('restaurant_detail', args=[str(self.id)])

class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='restaurant_images/', verbose_name='Изображение')

    def __str__(self):
        return f"Изображение для {self.restaurant.name}"

class Slide(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True)
    image = models.ImageField(upload_to='slides/', verbose_name='Изображение')
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Слайд'
        verbose_name_plural = 'Слайды'