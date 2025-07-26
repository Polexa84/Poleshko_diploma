from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.core import mail
from .forms import UserRegistrationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели пользователя"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False  # Явно устанавливаем is_active=False
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertFalse(self.user.is_active)
        self.assertIsNotNone(self.user.confirmation_token)  # Проверяем наличие токена
        self.assertEqual(self.user.role, 'customer') # Проверяем роль по умолчанию

    def register(request):
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(request=request)
                messages.success(request, 'Регистрация успешна! ...')
                return render(request, 'users/register_success.html')
            else:
                # Добавляем сообщение об ошибке
                messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
                return render(request, 'users/register.html', {'form': form})  # Возвращаем render!!!
        else:
            form = UserRegistrationForm()
        return render(request, 'users/register.html', {'form': form})

    def confirm_email(request, token):
        try:
            user = User.objects.get(confirmation_token=token)
            if not user.is_active:
                user.is_active = True
                user.confirmation_token = None  # Очищаем токен
                user.save()
                login(request, user)  # Автоматически логиним пользователя
                messages.success(request,
                                 'Email успешно подтвержден! Вы вошли в систему.')  # Добавляем сообщение об успехе
                return render(request, 'users/confirmation_success.html')  # Страница успешного подтверждения
            else:
                messages.info(request, 'Ваш email уже был подтвержден.')  # Добавляем информационное сообщение
                return render(request, 'users/confirmation_already_confirmed.html')  # Страница, если уже подтверждено
        except User.DoesNotExist:
            messages.error(request, 'Неверная ссылка подтверждения.')  # Добавляем сообщение об ошибке
            return render(request, 'users/confirmation_failed.html')  # Страница, если токен не найден

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

        response = form.save(commit=True, request=self.request)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Подтверждение регистрации')
        self.assertEqual(response.role, 'customer')  # Проверяем роль по умолчанию