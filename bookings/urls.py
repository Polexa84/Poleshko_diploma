from django.urls import path
from . import views

urlpatterns = [
    path('restaurant/<int:restaurant_id>/book/', views.restaurant_booking, name='restaurant_booking'),
    path('booking/success/', views.booking_success, name='booking_success'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),  # Добавляем этот URL
]