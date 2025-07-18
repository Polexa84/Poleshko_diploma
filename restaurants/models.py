from django.db import models
from django.urls import reverse

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='restaurant_images/')
    opening_hours = models.CharField(max_length=100)
    cuisine_type = models.CharField(max_length=100)
    average_check = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True) # Добавляем телефон
    email = models.EmailField(blank=True) # Добавляем email
    website = models.URLField(blank=True) # Добавляем сайт

    def __str__(self):
        return f"{self.name} ({self.city})"

    def get_absolute_url(self):
        return reverse('restaurant_detail', args=[str(self.id)]) # Ссылка на детали ресторана

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