from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from .forms import UserRegistrationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
import uuid

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели пользователя"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False,  # Явно устанавливаем is_active=False
            role=User.USER_ROLE_CUSTOMER
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertFalse(self.user.is_active)
        self.assertIsNotNone(self.user.confirmation_token)  # Проверяем наличие токена
        self.assertEqual(self.user.role, User.USER_ROLE_CUSTOMER)  # Проверяем роль по умолчанию

    def test_user_role_choices(self):
        """Проверка корректности выбора ролей пользователя"""
        role_choices = dict(User.ROLE_CHOICES)
        self.assertIn(User.USER_ROLE_CUSTOMER, role_choices)
        self.assertIn(User.USER_ROLE_RESTAURANT_ADMIN, role_choices)


class UserRegistrationFormTest(TestCase):
    """Тесты формы регистрации пользователя"""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_valid_registration(self):
        """Тест валидной регистрации"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save(commit=True)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.role, User.USER_ROLE_CUSTOMER)  # Проверяем роль по умолчанию

    def test_invalid_registration(self):
        """Тест невалидной регистрации (несовпадающие пароли)"""
        form_data = {
            'username': 'baduser',
            'email': 'bad@example.com',
            'password1': 'password123',
            'password2': 'differentpassword',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Проверяем, что пользователь не был создан
        self.assertEqual(User.objects.count(), 0)


class UserViewsTest(TestCase):
    """Тесты представлений пользователей"""

    def setUp(self):
        self.client = Client()
        # Создаем фиктивного пользователя с фиктивным токеном UUID
        self.test_user = User.objects.create(
            username='testconfirmuser',
            email='testconfirm@example.com',
            password='password123',
            is_active=False,
            confirmation_token=uuid.uuid4()
        )
        self.register_url = reverse('register')
        self.confirm_email_url = reverse('confirm_email', args=[str(self.test_user.confirmation_token)])

    def test_register_view_get(self):
        """Тест GET запроса к странице регистрации"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], UserRegistrationForm)

    def test_confirm_email_view_valid_token(self):
        """Тест подтверждения email с валидным токеном"""
        url = reverse('confirm_email', args=[str(self.test_user.confirmation_token)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/confirmation_success.html')
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_active)

    def test_confirm_email_view_invalid_token(self):
        """Тест подтверждения email с невалидным токеном"""
        invalid_token = uuid.uuid4() # Генерируем новый токен
        url = reverse('confirm_email', args=[str(invalid_token)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/confirmation_failed.html')