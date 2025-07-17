from django.urls import path
from . import views  # Импортируем views из текущего приложения bookings

urlpatterns = [
    path('bookings/', views.bookings_list, name='bookings'),
]