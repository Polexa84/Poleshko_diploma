from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model # Лучше использовать get_user_model
from .models import UserProfile

# Получаем модель пользователя, которая используется в проекте (по умолчанию User)
User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    # Можно добавить поле для роли, если хотим, чтобы пользователь сам выбирал роль при регистрации,
    # но чаще роль назначает админ или она определяется иначе.
    # Для начала, предположим, что все новые пользователи будут "Клиентами".

    class Meta(UserCreationForm.Meta):
        model = User # Указываем, что работаем со стандартной моделью User
        fields = UserCreationForm.Meta.fields + ("email",) # Добавляем email к полям формы

    def save(self, commit=True):
        # Переопределяем метод save, чтобы создать пользователя и его профиль
        user = super().save(commit=False) # Создаем пользователя, но не сохраняем его пока
        user.email = self.cleaned_data['email'] # Устанавливаем email

        if commit:
            user.save()
            # Создаем профиль пользователя, назначая роль "Клиент" по умолчанию
            UserProfile.objects.create(user=user, role=UserProfile.USER_ROLE_CUSTOMER)
        return user