from django.urls import path
from . import views

urlpatterns = [
    path('restaurant/<int:restaurant_id>/book/', views.restaurant_booking, name='restaurant_booking'),
    path('restaurant/<int:restaurant_id>/table/<int:table_id>/available-times/', views.available_times, name='available_times'),

    path('booking-success/', views.booking_success, name='booking_success'),
    path('booking-pending/', views.booking_pending, name='booking_pending'),
    path('booking-failed/', views.booking_failed, name='booking_failed'),  # Добавлен этот маршрут

    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),

    path('confirm/<uuid:token>/', views.confirm_booking, name='confirm_booking'),
]