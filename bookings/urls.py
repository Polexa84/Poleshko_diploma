from django.urls import path
from . import views

urlpatterns = [
    path('restaurant/<int:restaurant_id>/book/', views.restaurant_booking, name='restaurant_booking'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('restaurant/<int:restaurant_id>/table/<int:table_id>/confirm/<str:booking_time>/', views.booking_confirmation,
         name='booking_confirmation'),  # New URL
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),  # Добавляем URL для удаления
    path('confirm/<uuid:token>/', views.confirm_booking, name='confirm_booking'),
    path('booking/pending/', views.booking_pending, name='booking_pending'),  # Добавьте этот URL
]