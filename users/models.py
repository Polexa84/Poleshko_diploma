import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_ROLE_CUSTOMER = 'customer'
    USER_ROLE_RESTAURANT_ADMIN = 'restaurant_admin'
    USER_ROLE_SUPER_ADMIN = 'super_admin'

    ROLE_CHOICES = [
        (USER_ROLE_CUSTOMER, _('Клиент')),
        (USER_ROLE_RESTAURANT_ADMIN, _('Администратор ресторана')),
        (USER_ROLE_SUPER_ADMIN, _('Суперадминистратор')),
    ]

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER_ROLE_CUSTOMER,
        verbose_name=_('Роль')
    )
    confirmation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_('Токен подтверждения'),
        null=True,  # Разрешаем NULL в базе данных
        blank=True   # Разрешаем пустые значения в форме
    )

    def __str__(self):
        return self.username