from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.conf import settings
from .models import UserProfile
from .forms import UserRegistrationForm
import uuid

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели пользователя и профиля"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertFalse(self.user.is_active)

    def test_profile_creation(self):
        """Тест автоматического создания профиля"""
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.role, 'customer')
        self.assertFalse(profile.is_active)
        self.assertIsNotNone(profile.confirmation_token)


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
            'password2': 'complexpassword123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save(commit=False, request=self.request)
        user = form.save(commit=True, request=self.request)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Подтверждение регистрации')


class UserProfileTest(TestCase):
    """Тесты функциональности профиля пользователя"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.get(user=self.user)

    def test_profile_str(self):
        """Тест строкового представления профиля"""
        self.assertEqual(str(self.profile), 'testuser (Клиент)')

    def test_superuser_profile_activation(self):
        """Тест автоматической активации профиля суперпользователя"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        admin_profile = UserProfile.objects.get(user=admin)
        self.assertTrue(admin_profile.is_active)


class UserViewsTest(TestCase):
    """Тесты представлений пользователей"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.is_active = True
        self.profile.save()

    def test_registration_view(self):
        """Тест страницы регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        """Тест страницы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)