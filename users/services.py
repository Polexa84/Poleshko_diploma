from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_confirmation_email(user, request):
    subject = 'Подтверждение регистрации'
    confirmation_url = request.build_absolute_uri(reverse('confirm_email', args=[str(user.confirmation_token)]))
    message = f'Здравствуйте, {user.username}!\n\nПожалуйста, подтвердите свой email, перейдя по ссылке: {confirmation_url}\n\nС уважением, Администрация'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    print("Confirmation email sent successfully!")