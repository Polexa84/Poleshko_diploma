from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import uuid
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

    def save(self, commit=True, request=None):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False # Неактивен по умолчанию

        if commit:
            user.confirmation_token = uuid.uuid4() # Генерируем токен прямо здесь
            user.save()

            # Отправляем письмо с подтверждением
            subject = 'Подтверждение регистрации'
            # используем request для формирования абсолютного URL
            confirmation_url = request.build_absolute_uri(reverse('confirm_email', args=[str(user.confirmation_token)]))
            message = f'Здравствуйте, {user.username}!\n\nПожалуйста, подтвердите свой email, перейдя по ссылке: {confirmation_url}\n\nС уважением, Администрация'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            print("Confirmation email sent successfully!")

        return user