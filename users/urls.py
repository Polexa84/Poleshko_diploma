from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # URL для регистрации
    path('register/', views.register, name='register'),
    # URL для подтверждения email
    path('confirm/<uuid:token>/', views.confirm_email, name='confirm_email'),  # Добавлено

    # URL для входа
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),

    # URL для выхода
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]