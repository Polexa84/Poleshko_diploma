from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from .services import send_confirmation_email # Импортируем сервис

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация успешна! ...')

            # Отправляем письмо с подтверждением
            send_confirmation_email(user, request)

            return render(request, 'users/register_success.html')
        else:
            # Добавляем сообщение об ошибке
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
            return render(request, 'users/register.html', {'form': form})
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
            login(request, user)
            messages.success(request, 'Email успешно подтвержден! Вы вошли в систему.')
            return render(request, 'users/confirmation_success.html')
        else:
            messages.info(request, 'Ваш email уже был подтвержден.')
            return render(request, 'users/confirmation_already_confirmed.html')
    except User.DoesNotExist:
        messages.error(request, 'Неверная ссылка подтверждения.')
        return render(request, 'users/confirmation_failed.html')