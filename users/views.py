from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

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
            return render(request, 'users/register.html', {'form': form})  #  Возвращаем render!!!
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def confirm_email(request, token):
    try:
        profile = UserProfile.objects.get(confirmation_token=token)
        user = profile.user
        if not user.is_active:
            user.is_active = True
            user.save()
            profile.confirmation_token = uuid.uuid4()
            profile.save()
            login(request, user)  # Автоматически логиним пользователя
            messages.success(request, 'Email успешно подтвержден! Вы вошли в систему.')  # Добавляем сообщение об успехе
            return render(request, 'users/confirmation_success.html')  # Страница успешного подтверждения
        else:
            messages.info(request, 'Ваш email уже был подтвержден.')  # Добавляем информационное сообщение
            return render(request, 'users/confirmation_already_confirmed.html')  # Страница, если уже подтверждено
    except UserProfile.DoesNotExist:
        messages.error(request, 'Неверная ссылка подтверждения.')  # Добавляем сообщение об ошибке
        return render(request, 'users/confirmation_failed.html')  # Страница, если токен не найден