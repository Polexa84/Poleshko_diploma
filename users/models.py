import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class UserProfile(models.Model):
    USER_ROLE_CUSTOMER = 'customer'
    USER_ROLE_RESTAURANT_ADMIN = 'restaurant_admin'
    USER_ROLE_SUPER_ADMIN = 'super_admin'

    ROLE_CHOICES = [
        (USER_ROLE_CUSTOMER, _('Клиент')),
        (USER_ROLE_RESTAURANT_ADMIN, _('Администратор ресторана')),
        (USER_ROLE_SUPER_ADMIN, _('Суперадминистратор')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'), related_name='profile')
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER_ROLE_CUSTOMER,
        verbose_name=_('Роль')
    )
    is_active = models.BooleanField(default=False, verbose_name=_('Активный'))
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,
                                          verbose_name=_('Токен подтверждения'))

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    def get_absolute_url(self):
        return reverse('user_profile', args=[str(self.user.id)])

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance) # Создаем профиль
        if instance.is_superuser:
            profile.is_active = True  # Активируем суперпользователя
            profile.save()
        else:
            instance.is_active = False  # Для обычных пользователей требуется подтверждение
            instance.save()