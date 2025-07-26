import uuid
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EmailValidator

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        validators=[EmailValidator(message="Введите корректный email адрес")]
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False  # Неактивен по умолчанию
        user.role = User.USER_ROLE_CUSTOMER  # Устанавливаем роль по умолчанию!!!
        user.confirmation_token = uuid.uuid4()  # Генерируем токен прямо здесь

        if commit:
            user.save()

        return user