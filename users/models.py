from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _ # Для локализации

class UserProfile(models.Model):
    # Определяем возможные роли пользователей
    USER_ROLE_CUSTOMER = 'customer'
    USER_ROLE_RESTAURANT_ADMIN = 'restaurant_admin'
    USER_ROLE_SUPER_ADMIN = 'super_admin' # Если не хотим использовать стандартного Superuser

    ROLE_CHOICES = [
        (USER_ROLE_CUSTOMER, _('Клиент')),
        (USER_ROLE_RESTAURANT_ADMIN, _('Администратор ресторана')),
        (USER_ROLE_SUPER_ADMIN, _('Суперадминистратор')), # Или просто полагаться на User.is_staff/is_superuser
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER_ROLE_CUSTOMER,
        verbose_name=_('Роль')
    )
    # Можно добавить другие поля профиля, если потребуется, например:
    # phone_number = models.CharField(max_length=20, blank=True, verbose_name=_('Телефон'))
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, verbose_name=_('Аватар'))

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    def get_absolute_url(self):
        # Возвращаем URL на профиль пользователя, если такой будет реализован
        # Пока можно сделать ссылку на страницу логина или что-то другое
        return reverse('user_profile', args=[str(self.user.id)]) # Нужен будет URL с именем 'user_profile'
